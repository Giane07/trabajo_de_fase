"""
Sistema de Gestión de Pedidos Modular
Módulo: modulos/stock.py
Responsable: Control de Disponibilidad y Reserva de Stock
"""

import os
import json
import pandas as pd

# Ruta relativa estandarizada para la persistencia del módulo
RUTA_JSON = os.path.join("datos", "productos.json")

def cargar_productos():
    """
    Lee el archivo JSON de productos y retorna su contenido.
    Retorna una lista vacía [] si el archivo no existe, está vacío o corrupto.
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
        print(f"\n[LOG ERROR] Error al leer el archivo de productos: {e}")
        return []


def guardar_productos(productos):
    """
    Escribe la lista actualizada de productos en el archivo JSON.
    """
    try:
        # Asegurar que la carpeta 'datos/' existe
        os.makedirs(os.path.dirname(RUTA_JSON), exist_ok=True)
        with open(RUTA_JSON, "w", encoding="utf-8") as archivo:
            json.dump(productos, archivo, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"\n[LOG ERROR] No se pudieron persistir los datos de productos: {e}")


def agregar_producto(producto_id, nombre, precio, cantidad_stock):
    """
    Valida y registra un nuevo producto en el sistema inventario.
    """
    # 1. Validación de campos vacíos
    campos = {
        "ID Producto": producto_id,
        "Nombre": nombre,
        "Precio": precio,
        "Stock": cantidad_stock
    }
    
    for nombre_campo, valor in campos.items():
        if valor is None or str(valor).strip() == "":
            return False, f"Error: El campo '{nombre_campo}' es obligatorio y no puede estar vacío."
            
    id_prod_str = str(producto_id).strip()
    
    # 2. Validación de conversión numérica y valores no negativos
    try:
        precio_num = float(precio)
        stock_num = int(cantidad_stock)
    except ValueError:
        return False, "Error: El precio debe ser un número decimal y el stock debe ser un número entero."
        
    if precio_num < 0 or stock_num < 0:
        return False, "Error: El precio y la cantidad de stock no pueden ser valores negativos."
        
    # 3. Validación de ID Único
    lista_productos = cargar_productos()
    id_duplicado = any(str(p.get("producto_id")).strip() == id_prod_str for p in lista_productos)
    
    if id_duplicado:
        return False, f"Error: Ya existe un producto registrado con el ID '{id_prod_str}'."
        
    # 4. Estructura e inserción del nuevo producto
    nuevo_producto = {
        "producto_id": id_prod_str,
        "nombre": str(nombre).strip(),
        "precio": precio_num,
        "cantidad_stock": stock_num
    }
    
    lista_productos.append(nuevo_producto)
    guardar_productos(lista_productos)
    
    return True, "Producto registrado con éxito."


def verificar_stock(producto_id, cantidad_solicitada):
    """
    Verifica si hay stock suficiente en tiempo real para una cantidad solicitada.
    Retorna True si hay stock, de lo contrario False.
    """
    try:
        cant_req = int(cantidad_solicitada)
        if cant_req <= 0:
            return False
    except ValueError:
        return False

    lista_productos = cargar_productos()
    id_prod_str = str(producto_id).strip()
    
    for p in lista_productos:
        if str(p.get("producto_id")).strip() == id_prod_str:
            return p.get("cantidad_stock", 0) >= cant_req
            
    return False # Retorna False si el producto no existe


def descontar_stock(producto_id, cantidad_a_descontar):
    """
    Resta la cantidad del stock real tras confirmarse un pedido o reserva.
    """
    try:
        cant_desc = int(cantidad_a_descontar)
        if cant_desc <= 0:
            return False, "Error: La cantidad a descontar debe ser mayor a cero."
    except ValueError:
        return False, "Error: Cantidad inválida."

    lista_productos = cargar_productos()
    id_prod_str = str(producto_id).strip()
    encontrado = False
    
    for p in lista_productos:
        if str(p.get("producto_id")).strip() == id_prod_str:
            encontrado = True
            if p["cantidad_stock"] >= cant_desc:
                p["cantidad_stock"] -= cant_desc
                guardar_productos(lista_productos)
                return True, f"Stock actualizado con éxito. Nuevo stock: {p['cantidad_stock']}"
            else:
                return False, f"Alerta de quiebre: Stock insuficiente. Disponible: {p['cantidad_stock']}"
                
    if not encontrado:
        return False, "Error: El producto especificado no existe."


def obtener_productos_df():
    """
    Retorna la lista de productos en formato DataFrame de Pandas.
    """
    lista_productos = cargar_productos()
    columnas = ["producto_id", "nombre", "precio", "cantidad_stock"]
    df = pd.DataFrame(lista_productos, columns=columnas)
    return df


# =====================================================================
#  BLOQUE DE PRUEBA INTERACTIVO
# =====================================================================
if __name__ == '__main__':
    while True:
        print("\n" + "="*40)
        print("  MENÚ DE PRUEBA INTERACTIVO: STOCK")
        print("="*40)
        print("1. Registrar un nuevo producto de prueba")
        print("2. Ver lista completa de productos (Consola)")
        print("3. Ver DataFrame de productos (Pandas)")
        print("4. Simular verificación de Stock disponible")
        print("5. Simular descuento manual de Stock")
        print("6. Salir de la prueba")
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "1":
            print("\n--- REGISTRAR NUEVO PRODUCTO ---")
            id_p = input("ID del Producto (ej. P001): ")
            nom = input("Nombre del producto: ")
            pre = input("Precio unitario: ")
            stk = input("Cantidad inicial en Stock: ")
            
            exito, mensaje = agregar_producto(id_p, nom, pre, stk)
            if exito:
                print(f"\n[ÉXITO] {mensaje}")
            else:
                print(f"\n[FALLO] {mensaje}")
                
        elif opcion == "2":
            print("\n--- LISTA DE PRODUCTOS EN JSON ---")
            productos = cargar_productos()
            if not productos:
                print("No hay productos registrados en el archivo productos.json.")
            else:
                for p in productos:
                    print(p)
                    
        elif opcion == "3":
            print("\n--- VISTA TABULAR DE PANDAS (DATAFRAME) ---")
            df_prod = obtener_productos_df()
            print(df_prod)
            
        elif opcion == "4":
            print("\n--- VERIFICACIÓN DE STOCK EN TIEMPO REAL ---")
            id_p = input("ID del Producto a verificar: ")
            cant = input("Cantidad que el cliente desea pedir: ")
            
            if verificar_stock(id_p, cant):
                print(f"\n[OK] ¡Sí hay stock suficiente disponible!")
            else:
                print(f"\n[ALERTA] Stock insuficiente o el producto no existe.")
                
        elif opcion == "5":
            print("\n--- DESCUENTO DE STOCK MANUAL ---")
            id_p = input("ID del Producto a descontar: ")
            cant = input("Cantidad a retirar: ")
            
            exito, mensaje = descontar_stock(id_p, cant)
            if exito:
                print(f"\n[ÉXITO] {mensaje}")
            else:
                print(f"\n[FALLO] {mensaje}")
                
        elif opcion == "6":
            print("\nSaliendo del módulo de pruebas de stock. ¡Listo para integración!")
            break
        else:
            print("\nOpción inválida. Intenta de nuevo.")