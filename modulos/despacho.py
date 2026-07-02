"""
Sistema de Gestión de Pedidos Modular
Módulo: modulos/despacho.py
Responsable: Control de Estados de Envío y Trazabilidad Logística (Despacho)
"""

import pandas as pd
# Importación obligatoria del módulo central de pedidos para mantener persistencia compartida
from modulos.pedidos import cargar_pedidos, guardar_pedidos

def actualizar_estado_despacho(codigo_pedido, nuevo_estado):
    """
    Busca un pedido por su código correlativo único y actualiza su estado logístico
    bajo estrictas reglas de validación de negocio.
    """
    # 1. Normalización de entradas
    cod_buscar = str(codigo_pedido).strip().upper()
    estado_normalizado = str(nuevo_estado).strip().capitalize() # Asegura formatos como 'Despachado'
    
    # 2. Validación estricta de los estados permitidos por el flujo operativo
    estados_validos = ["Pendiente", "Despachado", "Entregado"]
    if estado_normalizado not in estados_validos:
        return False, f"Error: El estado '{nuevo_estado}' no es válido. Debe ser uno de estos: {estados_validos}."
    
    # 3. Carga transaccional de los pedidos existentes
    lista_pedidos = cargar_pedidos()
    encontrado = False
    
    # 4. Búsqueda y actualización en la estructura en memoria
    for p in lista_pedidos:
        if str(p.get("codigo_pedido")).upper() == cod_buscar:
            p["estado"] = estado_normalizado
            encontrado = True
            break
            
    # 5. Guardado e impacto en el archivo compartido 'pedidos.json'
    if encontrado:
        guardar_pedidos(lista_pedidos)
        return True, f"Estado del pedido {cod_buscar} actualizado a '{estado_normalizado}' con éxito."
    else:
        return False, f"Error: No se encontró ningún pedido registrado con el código '{cod_buscar}'."


def obtener_despachos_df():
    """
    Estructura un DataFrame de Pandas diseñado exclusivamente para el control
    y visualización del área logística/despacho en la interfaz web.
    """
    lista_pedidos = cargar_pedidos()
    
    # Estructuramos la vista específica requerida por control logístico
    tabla_despachos = []
    for p in lista_pedidos:
        tabla_despachos.append({
            "Código Pedido": p.get("codigo_pedido"),
            "ID Cliente": p.get("id_cliente"),
            "Estado Actual": p.get("estado", "Pendiente")
        })
        
    columnas = ["Código Pedido", "ID Cliente", "Estado Actual"]
    df = pd.DataFrame(tabla_despachos, columns=columnas)
    return df


# =====================================================================
#  BLOQUE DE PRUEBA INTERACTIVO (TESTING AISLADO LOGÍSTICO)
# =====================================================================
if __name__ == '__main__':
    while True:
        print("\n" + "="*40)
        print("  MENÚ DE PRUEBA INTERACTIVO: DESPACHO")
        print("="*40)
        print("1. Ver lista de despachos y estados actuales")
        print("2. Ver DataFrame logístico (Pandas)")
        print("3. Cambiar estado de un pedido (Simulación)")
        print("4. Salir de la prueba")
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "1":
            print("\n--- MONITOREO DE PEDIDOS EN JSON ---")
            pedidos = cargar_pedidos()
            if not pedidos:
                print("No se encontraron registros en pedidos.json. Registra un pedido en pedidos.py primero.")
            else:
                for p in pedidos:
                    print(f"Pedido: {p.get('codigo_pedido')} | Cliente: {p.get('id_cliente')} | Estado: {p.get('estado')}")
                    
        elif opcion == "2":
            print("\n--- VISTA TABULAR DE DESPACHO ---")
            df_desp = obtener_despachos_df()
            print(df_desp)
            
        elif opcion == "3":
            print("\n--- ACTUALIZACIÓN DE ESTADO LOGÍSTICO ---")
            cod_p = input("Ingresa el código del pedido (ej. PED-001): ")
            print("Estados válidos: Pendiente | Despachado | Entregado")
            nuevo_est = input("Nuevo estado logístico: ")
            
            exito, mensaje = actualizar_estado_despacho(cod_p, nuevo_est)
            if exito:
                print(f"\n[ÉXITO LOGÍSTICO] {mensaje}")
            else:
                print(f"\n[FALLO EN OPERACIÓN] {mensaje}")
                
        elif opcion == "4":
            print("\nSaliendo del módulo de pruebas de despacho. ¡Listo para integración!")
            break
        else:
            print("\nOpción inválida. Intenta de nuevo.")