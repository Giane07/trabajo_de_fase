"""
Sistema de Gestión de Pedidos Modular
Módulo: modulos/pedidos.py
Responsable: Gestión y Generación de Pedidos en Coordinación con Inventario
"""

import os
import json
import pandas as pd

# Importación de las funciones de stock para coordinar las transacciones
from modulos.stock import verificar_stock, descontar_stock

# Ruta relativa estandarizada para la persistencia del módulo
RUTA_JSON = os.path.join("datos", "pedidos.json")

def cargar_pedidos():
    """
    Lee el archivo JSON de pedidos y retorna su contenido.
    Retorna una lista vacía [] si el archivo no existe o está vacío.
    """
    if not os.path.exists(RUTA_JSON):
        return []
    
    try:
        with open(RUTA_JSON, "r", encoding="utf-8") as archivo:
            contenido = archivo.read().strip()
            if not contenido:
                return []
            return json.loads(contenido)
    except (json.JSONDecodeError, IOError) as e:
        print(f"\n[LOG ERROR] Error al leer el archivo de pedidos: {e}")
        return []


def guardar_pedidos(pedidos):
    """
    Escribe la lista de pedidos en el archivo JSON con formato legible.
    """
    try:
        os.makedirs(os.path.dirname(RUTA_JSON), exist_ok=True)
        with open(RUTA_JSON, "w", encoding="utf-8") as archivo:
            json.dump(pedidos, archivo, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"\n[LOG ERROR] No se pudieron persistir los datos de pedidos: {e}")


def registrar_pedido(id_cliente, lista_productos_solicitados):
    """
    Valida las existencias de stock, genera un código correlativo y registra el pedido.
    
    lista_productos_solicitados debe tener el formato:
    [{"producto_id": "P001", "cantidad": 5}, ...]
    """
    # 1. Validación de cliente
    if not id_cliente or str(id_cliente).strip() == "":
        return False, "Error: El ID del cliente es obligatorio para registrar un pedido."
        
    if not lista_productos_solicitados:
        return False, "Error: El pedido debe contener al menos un producto."

    # 2. Fase de Verificación: Comprobar el stock de CADA producto solicitado primero
    for item in lista_productos_solicitados:
        prod_id = str(item.get("producto_id")).strip()
        try:
            cant = int(item.get("cantidad", 0))
        except ValueError:
            return False, f"Error: Cantidad inválida para el producto {prod_id}."

        if cant <= 0:
            return False, f"Error: La cantidad solicitada del producto {prod_id} debe ser mayor a cero."

        # Llamada al módulo stock
        if not verificar_stock(prod_id, cant):
            return False, f"Error: Stock insuficiente para el producto [{prod_id}]."

    # 3. Fase de Ejecución: Si todos pasaron el filtro, procedemos a descontar el stock
    for item in lista_productos_solicitados:
        prod_id = str(item.get("producto_id")).strip()
        cant = int(item.get("cantidad"))
        descontar_stock(prod_id, cant) # Modifica productos.json directamente

    # 4. Generación automática del ID de pedido correlativo
    lista_pedidos = cargar_pedidos()
    total_pedidos = len(lista_pedidos)
    nuevo_codigo = f"PED-{str(total_pedidos + 1).zfill(3)}" # Genera PED-001, PED-002, etc.

    # 5. Estructurar el nuevo documento de pedido
    nuevo_pedido = {
        "codigo_pedido": nuevo_codigo,
        "id_cliente": str(id_cliente).strip(),
        "productos": lista_productos_solicitados,
        "estado": "Pendiente" # Estado por defecto inicial exigido por el flujo de negocio
    }

    lista_pedidos.append(nuevo_pedido)
    guardar_pedidos(lista_pedidos)

    return True, f"Pedido {nuevo_codigo} registrado con éxito."


def buscar_pedido(codigo_pedido):
    """
    Busca un pedido por su código correlativo único.
    """
    lista_pedidos = cargar_pedidos()
    cod_buscar = str(codigo_pedido).strip().upper()
    
    for p in lista_pedidos:
        if str(p.get("codigo_pedido")).upper() == cod_buscar:
            return p
    return None


def obtener_pedidos_df():
    """
    Retorna la lista de pedidos en formato DataFrame de Pandas para visualización tabular.
    """
    lista_pedidos = cargar_pedidos()
    
    # Si la lista tiene datos, aplanamos un poco la visualización de los productos para la tabla
    tabla_limpia = []
    for p in lista_pedidos:
        # Concatenamos los productos en un string comprensible para que quepa en una sola celda
        resumen_prod = ", ".join([f"{item['producto_id']}(x{item['cantidad']})" for item in p["productos"]])
        tabla_limpia.append({
            "Código Pedido": p["codigo_pedido"],
            "ID Cliente": p["id_cliente"],
            "Productos Solicitados": resumen_prod,
            "Estado Actual": p["estado"]
        })
        
    columnas = ["Código Pedido", "ID Cliente", "Productos Solicitados", "Estado Actual"]
    df = pd.DataFrame(tabla_limpia, columns=columnas)
    return df


# =====================================================================
#  BLOQUE DE PRUEBA INTERACTIVO (TESTING AISLADO)
# =====================================================================
if __name__ == '__main__':
    while True:
        print("\n" + "="*40)
        print("  MENÚ DE PRUEBA INTERACTIVO: PEDIDOS")
        print("="*40)
        print("1. Crear un nuevo Pedido de prueba")
        print("2. Ver lista completa de pedidos (Consola)")
        print("3. Ver DataFrame de pedidos (Pandas)")
        print("4. Buscar un pedido específico por Código")
        print("5. Salir de la prueba")
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "1":
            print("\n--- REGISTRAR NUEVO PEDIDO ---")
            id_cli = input("ID/DNI del Cliente que compra: ")
            id_prd = input("ID del Producto que desea (debe existir en stock.py): ")
            cant_prd = input("Cantidad a comprar: ")
            
            # Formateamos como la estructura de lista requerida
            lista_items = [{"producto_id": id_prd, "cantidad": cant_prd}]
            
            exito, mensaje = registrar_pedido(id_cli, lista_items)
            if exito:
                print(f"\n[ÉXITO] {mensaje}")
            else:
                print(f"\n[FALLO] {mensaje}")
                
        elif opcion == "2":
            print("\n--- LISTA DE PEDIDOS EN JSON ---")
            pedidos = cargar_pedidos()
            if not pedidos:
                print("No hay pedidos registrados en pedidos.json.")
            else:
                for p in pedidos:
                    print(p)
                    
        elif opcion == "3":
            print("\n--- VISTA TABULAR DE PANDAS (DATAFRAME) ---")
            df_ped = obtener_pedidos_df()
            print(df_ped)
            
        elif opcion == "4":
            print("\n--- BUSCAR PEDIDO ---")
            cod_busq = input("Ingresa el código del pedido (ej. PED-001): ")
            pedido_encontrado = buscar_pedido(cod_busq)
            if pedido_encontrado:
                print(f"\n[ENCONTRADO]: {pedido_encontrado}")
            else:
                print("\n[ALERTA] No se encontró ningún pedido con ese código.")
                
        elif opcion == "5":
            print("\nSaliendo del módulo de pruebas de pedidos. ¡Listo para integración!")
            break
        else:
            print("\nOpción inválida. Intenta de nuevo.")