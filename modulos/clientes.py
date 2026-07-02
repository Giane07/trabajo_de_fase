"""
Sistema de Gestión de Pedidos Modular
Módulo: modulos/clientes.py
Responsable: Control y Persistencia de Datos de Clientes
"""

import os
import json
import pandas as pd

# Ruta relativa estandarizada para la persistencia del módulo
RUTA_JSON = os.path.join("datos", "clientes.json")

def cargar_clientes():
    """
    Lee el archivo JSON de clientes y retorna su contenido.
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
        print(f"\n[LOG ERROR] Error al leer el archivo de clientes: {e}")
        return []


def guardar_clientes(clientes):
    """
    Escribe la lista actualizada de clientes en el archivo JSON.
    """
    try:
        os.makedirs(os.path.dirname(RUTA_JSON), exist_ok=True)
        with open(RUTA_JSON, "w", encoding="utf-8") as archivo:
            json.dump(clientes, archivo, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"\n[LOG ERROR] No se pudieron persistir los datos de clientes: {e}")


def crear_cliente(id_cliente, nombre, telefono, direccion, origen):
    """
    Valida y registra un nuevo cliente en el sistema.
    """
    # 1. Validación de Campos Vacíos
    campos = {
        "ID": id_cliente, 
        "Nombre": nombre, 
        "Teléfono": telefono, 
        "Dirección": direccion, 
        "Origen": origen
    }
    
    for nombre_campo, valor in campos.items():
        if valor is None or str(valor).strip() == "":
            return False, f"Error: El campo '{nombre_campo}' es obligatorio y no puede estar vacío."
    
    # Normalizar strings
    id_cliente_str = str(id_cliente).strip()
    origen_str = str(origen).strip()
    
    # 2. Validación de Canales de Origen Permitidos
    orígenes_validos = ["Venta Web", "Venta Presencial", "WhatsApp"]
    if origen_str not in orígenes_validos:
        return False, f"Error: El origen '{origen_str}' no es válido. Debe ser uno de estos: {orígenes_validos}."
    
    # 3. Cargar datos existentes para validar duplicados
    lista_clientes = cargar_clientes()
    
    # 4. Validación de ID Único
    id_duplicado = any(str(c.get("id_cliente")).strip() == id_cliente_str for c in lista_clientes)
    if id_duplicado:
        return False, f"Error: Ya existe un cliente registrado con el ID '{id_cliente_str}'."
    
    # 5. Creación de la estructura del nuevo cliente
    nuevo_cliente = {
        "id_cliente": id_cliente_str,
        "nombre": str(nombre).strip(),
        "telefono": str(telefono).strip(),
        "direccion": str(direccion).strip(),
        "origen": origen_str
    }
    
    # 6. Agregar a la lista y persistir en el archivo JSON
    lista_clientes.append(nuevo_cliente)
    guardar_clientes(lista_clientes)
    
    return True, "Cliente registrado con éxito."


def obtener_clientes_df():
    """
    Carga la lista de clientes y la convierte en DataFrame de Pandas.
    """
    lista_clientes = cargar_clientes()
    columnas = ["id_cliente", "nombre", "telefono", "direccion", "origen"]
    df = pd.DataFrame(lista_clientes, columns=columnas)
    return df


# =====================================================================
#  BLOQUE DE PRUEBA INTERACTIVO (¡ESTO ES LO QUE HACÍA FALTA!)
# =====================================================================
if __name__ == '__main__':
    while True:
        print("\n" + "="*40)
        print("  MENÚ DE PRUEBA INTERACTIVO: CLIENTES")
        print("="*40)
        print("1. Registrar un nuevo cliente de prueba")
        print("2. Ver lista de clientes (Consola)")
        print("3. Ver DataFrame de clientes (Pandas)")
        print("4. Salir de la prueba")
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "1":
            print("\n--- REGISTRAR NUEVO CLIENTE ---")
            id_c = input("ID/DNI del Cliente: ")
            nom = input("Nombre completo: ")
            tel = input("Teléfono: ")
            dir_c = input("Dirección: ")
            print("Opciones de origen: Venta Web | Venta Presencial | WhatsApp")
            ori = input("Origen del pedido: ")
            
            exito, mensaje = crear_cliente(id_c, nom, tel, dir_c, ori)
            if exito:
                print(f"\n[ÉXITO] {mensaje}")
            else:
                print(f"\n[FALLO] {mensaje}")
                
        elif opcion == "2":
            print("\n--- LISTA DE CLIENTES EN JSON ---")
            clientes = cargar_clientes()
            if not clientes:
                print("No hay clientes registrados en el archivo JSON.")
            else:
                for c in clientes:
                    print(c)
                    
        elif opcion == "3":
            print("\n--- VISTA TABULAR DE PANDAS (DATAFRAME) ---")
            df_clientes = obtener_clientes_df()
            print(df_clientes)
            
        elif opcion == "4":
            print("\nSaliendo del módulo de pruebas de clientes. ¡Listo para integración!")
            break
        else:
            print("\nOpción inválida. Intenta de nuevo.")