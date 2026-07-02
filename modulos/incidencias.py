"""
Sistema de Gestión de Pedidos Modular
Módulo: modulos/incidencias.py
Responsable: Control de Pedidos No Entregados e Incidencias Logísticas
"""

import os
import json
import pandas as pd
from modulos.pedidos import cargar_pedidos, guardar_pedidos

RUTA_JSON_INC = os.path.join("datos", "incidencias.json")

def cargar_incidencias():
    if not os.path.exists(RUTA_JSON_INC):
        return []
    try:
        with open(RUTA_JSON_INC, "r", encoding="utf-8") as archivo:
            contenido = archivo.read().strip()
            return json.loads(contenido) if contenido else []
    except (json.JSONDecodeError, IOError):
        return []

def guardar_incidencias(incidencias):
    try:
        os.makedirs(os.path.dirname(RUTA_JSON_INC), exist_ok=True)
        with open(RUTA_JSON_INC, "w", encoding="utf-8") as archivo:
            json.dump(incidencias, archivo, indent=4, ensure_ascii=False)
    except IOError:
        print("[LOG ERROR] No se pudieron guardar las incidencias.")

def registrar_no_entregado(codigo_pedido, motivo, accion_correctiva):
    """
    Registra un pedido como 'No Entregado', almacena el motivo del fallo
    y cambia el estado del pedido original a 'No Entregado' en pedidos.json.
    """
    if not codigo_pedido or not motivo or not accion_correctiva:
        return False, "Error: Todos los campos son obligatorios."
    
    # 1. Validar que el pedido exista en el sistema central
    lista_pedidos = cargar_pedidos()
    pedido_encontrado = False
    
    for p in lista_pedidos:
        if str(p.get("codigo_pedido")).upper() == str(codigo_pedido).strip().upper():
            p["estado"] = "No Entregado"  # Modificamos el estado al core del tema
            pedido_encontrado = True
            break
            
    if not pedido_encontrado:
        return False, f"Error: El pedido '{codigo_pedido}' no existe."
    
    # 2. Guardar el cambio de estado en pedidos.json
    guardar_pedidos(lista_pedidos)
    
    # 3. Registrar la incidencia en incidencias.json
    lista_incidencias = cargar_incidencias()
    nueva_incidencia = {
        "codigo_pedido": str(codigo_pedido).strip().upper(),
        "motivo_fallo": str(motivo).strip(),
        "accion_correctiva": str(accion_correctiva).strip(),
        "estado_incidencia": "Abierto"
    }
    
    lista_incidencias.append(nueva_incidencia)
    guardar_incidencias(lista_incidencias)
    
    return True, f"Incidencia del pedido {codigo_pedido} registrada como 'No Entregado'."

def obtener_incidencias_df():
    lista = cargar_incidencias()
    columnas = ["codigo_pedido", "motivo_fallo", "accion_correctiva", "estado_incidencia"]
    return pd.DataFrame(lista, columns=columnas)