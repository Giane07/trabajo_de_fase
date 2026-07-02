"""
Sistema de Gestión de Pedidos Modular
Módulo: modulos/reportes.py
Responsable: Análisis de Datos, Métricas de Rendimiento y KPIs
"""

import pandas as pd
# Importaciones obligatorias de las funciones de carga de datos de los otros módulos
from modulos.clientes import cargar_clientes
from modulos.stock import cargar_productos
from modulos.pedidos import cargar_pedidos

def obtener_resumen_general():
    """
    Calcula métricas descriptivas básicas contando los registros reales de cada JSON.
    """
    clientes = cargar_clientes()
    productos = cargar_productos()
    pedidos = cargar_pedidos()
    
    resumen = {
        "total_clientes": len(clientes),
        "total_productos": len(productos),
        "total_pedidos": len(pedidos)
    }
    return resumen


def obtener_kpis_pedidos():
    """
    Analiza el estado de los pedidos y calcula los ingresos totales mapeando 
    los precios unitarios desde el inventario de productos.
    """
    pedidos = cargar_pedidos()
    productos = cargar_productos()
    
    # Crear un diccionario rápido de consulta de precios {producto_id: precio}
    precios_dict = {str(p.get("producto_id")).strip(): float(p.get("precio", 0)) for p in productos}
    
    # Inicialización de contadores de estados
    conteo_estados = {
        "Pendiente": 0,
        "Despachado": 0,
        "Entregado": 0
    }
    
    ingresos_totales = 0.0
    
    for ped in pedidos:
        # 1. Contabilizar estados (asegurando el formato correcto)
        estado = str(ped.get("estado", "Pendiente")).strip().capitalize()
        if estado in conteo_estados:
            conteo_estados[estado] += 1
        else:
            conteo_estados["Pendiente"] += 1 # Resguardo por si hay datos vacíos
            
        # 2. Calcular el valor financiero del pedido
        for item in ped.get("productos", []):
            prod_id = str(item.get("producto_id")).strip()
            cantidad = int(item.get("cantidad", 0))
            
            # Buscamos el precio real en nuestro diccionario de inventario
            precio_unitario = precios_dict.get(prod_id, 0.0)
            ingresos_totales += (cantidad * precio_unitario)
            
    resultado = {
        "pedidos_pendientes": conteo_estados["Pendiente"],
        "pedidos_despachados": conteo_estados["Despachado"],
        "pedidos_entregados": conteo_estados["Entregado"],
        "ingresos_totales": ingresos_totales
    }
    return resultado


def obtener_tabla_kpis_df():
    """
    Estructura las métricas financieras y operativas en un DataFrame de Pandas
    para que la interfaz web de Streamlit lo muestre en tablas organizadas.
    """
    kpis = obtener_kpis_pedidos()
    resumen = obtener_resumen_general()
    
    # Creamos una estructura de filas atractiva para análisis ejecutivo
    datos_kpi = [
        {"Indicador / Métrica": "Total Clientes Activos", "Valor": resumen["total_clientes"], "Categoría": "Comercial"},
        {"Indicador / Métrica": "Total Productos en Catálogo", "Valor": resumen["total_productos"], "Categoría": "Inventario"},
        {"Indicador / Métrica": "Total Pedidos Procesados", "Valor": resumen["total_pedidos"], "Categoría": "Operaciones"},
        {"Indicador / Métrica": "Pedidos en Estado 'Pendiente'", "Valor": kpis["pedidos_pendientes"], "Categoría": "Logística"},
        {"Indicador / Métrica": "Pedidos en Estado 'Despachado'", "Valor": kpis["pedidos_despachados"], "Categoría": "Logística"},
        {"Indicador / Métrica": "Pedidos en Estado 'Entregado'", "Valor": kpis["pedidos_entregados"], "Categoría": "Logística"},
        {"Indicador / Métrica": "Ingresos Totales Brutos (S/.)", "Valor": f"{kpis['ingresos_totales']:.2f}", "Categoría": "Financiero"}
    ]
    
    df = pd.DataFrame(datos_kpi)
    return df


# =====================================================================
#  BLOQUE DE PRUEBA INTERACTIVO (TESTING ANALÍTICO EN CONSOLA)
# =====================================================================
if __name__ == '__main__':
    while True:
        print("\n" + "="*40)
        print("  MENÚ DE PRUEBA INTERACTIVO: REPORTES")
        print("="*40)
        print("1. Ver Resumen General (Métricas Descriptivas)")
        print("2. Ver KPIs Operativos e Ingresos Totales")
        print("3. Ver Reporte Consolidado en DataFrame (Pandas)")
        print("4. Salir de la prueba")
        
        opcion = input("\nSelecciona una opción: ").strip()
        
        if opcion == "1":
            print("\n--- RESUMEN GENERAL DEL NEGOCIO ---")
            resumen = obtener_resumen_general()
            print(f"• Clientes registrados: {resumen['total_clientes']}")
            print(f"• Productos en catálogo: {resumen['total_productos']}")
            print(f"• Pedidos totales en sistema: {resumen['total_pedidos']}")
            
        elif opcion == "2":
            print("\n--- KPIs OPERATIVOS Y FINANCIEROS ---")
            kpis = obtener_kpis_pedidos()
            print(f"• Pedidos Pendientes: {kpis['pedidos_pendientes']}")
            print(f"• Pedidos Despachados: {kpis['pedidos_despachados']}")
            print(f"• Pedidos Entregados: {kpis['pedidos_entregados']}")
            print(f"• Ingresos Acumulados: S/. {kpis['ingresos_totales']:.2f}")
            
        elif opcion == "3":
            print("\n--- REPORTE CONSOLIDADO DE RENDIMIENTO (PANDAS) ---")
            df_reporte = obtener_tabla_kpis_df()
            print(df_reporte)
            
        elif opcion == "4":
            print("\nSaliendo del módulo de pruebas de reportes. ¡Análisis completado!")
            break
        else:
            print("\nOpción inválida. Intenta de nuevo.")