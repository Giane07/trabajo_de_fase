import streamlit as st
import pandas as pd
import os

# Importaciones de los módulos del equipo
from modulos.clientes import crear_cliente, obtener_clientes_df, cargar_clientes, obtener_resumen_canales
from modulos.stock import agregar_producto, obtener_productos_df, cargar_productos
from modulos.pedidos import registrar_pedido, obtener_pedidos_df, cargar_pedidos
from modulos.despacho import actualizar_estado_despacho, obtener_despachos_df
from modulos.reportes import obtener_resumen_general, obtener_kpis_pedidos, obtener_tabla_kpis_df
from modulos.incidencias import registrar_no_entregado, obtener_incidencias_df

st.set_page_config(page_title="LogiCheck 360", page_icon="📦", layout="wide", initial_sidebar_state="expanded")
# st.set_page_config(page_title="Control de Pedidos", layout="wide", initial_sidebar_state="expanded")

# --- PANEL LATERAL DE NAVEGACIÓN ---
with st.sidebar:
    st.markdown("## **Control de Pedidos**")
    st.markdown("*Gestión Logística Modular*")
    st.markdown("---")
    
    # Añadimos Incidencias a las opciones
    opciones = ["Inicio", "Clientes", "Stock", "Pedidos", "Despacho", "Incidencias (No Entregados)", "Reportes"]
    seleccion = st.selectbox("Seleccione un Módulo:", opciones)
    
    st.markdown("---")
    st.markdown("**Acceso:** `Administrador General`")

st.markdown("---")

# --- CONTENIDO DINÁMICO ---

if seleccion == "Inicio":
    st.title("📦📦 LogiCheck 360")
    st.markdown("### ¡Bienvenidos al Sistema de Gestión de Entregas Pendientes!")
    st.markdown("""
    Esta plataforma integra los entregables de los 5 roles del equipo de ingeniería:
    - **Módulo de Clientes:** Registro y control de bases de datos de compradores.
    - **Módulo de Stock:** Administración y control de existencias en almacén.
    - **Módulo de Pedidos:** Núcleo transaccional que valida inventario y procesa solicitudes.
    - **Módulo de Despacho:** Trazabilidad operativa del estado de los envíos.
    - **Módulo de Incidencias:** **(Especialidad del Tema)** Control, auditoría y acciones correctivas para pedidos No Entregados.
    - **Módulo de Reportes:** Inteligencia de negocio, métricas clave de fallos e ingresos financieros.
    """)
    
elif seleccion == "Clientes":
    st.title("Módulo: Clientes y Canales")
    col_sub1, col_sub2, _ = st.columns([2, 2, 5])
    with col_sub1: action_ver = st.button("📋 Ver Clientes", use_container_width=True)
    with col_sub2: action_reg = st.button("➕ Registrar Cliente", use_container_width=True)
    
    if 'action_cli' not in st.session_state: st.session_state.action_cli = "ver"
    if action_ver: st.session_state.action_cli = "ver"
    if action_reg: st.session_state.action_cli = "registrar"

    if st.session_state.action_cli == "registrar":
        st.subheader("Registrar Nuevo Cliente")
        with st.form("form_cliente"):
            id_c = st.text_input("ID / Documento del Cliente:")
            nom = st.text_input("Nombre Completo:")
            tel = st.text_input("Teléfono de Contacto:")
            dir_c = st.text_input("Dirección de Entrega:")
            ori = st.selectbox("Origen del Pedido:", ["Venta Web", "Venta Presencial", "WhatsApp"])
            btn_submit = st.form_submit_button("Guardar Cliente")
            if btn_submit:
                exito, mensaje = crear_cliente(id_c, nom, tel, dir_c, ori)
                if exito: st.success(mensaje)
                else: st.error(mensaje)
    else:
        st.subheader("Historial y Base de Datos de Clientes")
        st.dataframe(obtener_clientes_df(), use_container_width=True, hide_index=True)
      # ... después de mostrar el historial ...
        st.markdown("---")
        st.subheader("Resumen por Canal de Captación")
        st.table(obtener_resumen_canales())

elif seleccion == "Stock":
    st.title("Módulo: Control de Disponibilidad (Stock)")
    col_sub1, col_sub2, _ = st.columns([2, 2, 5])
    with col_sub1: action_ver_st = st.button("📦 Ver Inventario", use_container_width=True)
    with col_sub2: action_reg_st = st.button("➕ Registrar Producto", use_container_width=True)
    
    if 'action_stk' not in st.session_state: st.session_state.action_stk = "ver"
    if action_ver_st: st.session_state.action_stk = "ver"
    if action_reg_st: st.session_state.action_stk = "registrar"

    if st.session_state.action_stk == "registrar":
        st.subheader("Registrar Nuevo Producto en Inventario")
        with st.form("form_stock"):
            id_p = st.text_input("ID del Producto (ej. P001):")
            nom_p = st.text_input("Nombre del Producto:")
            pre_p = st.text_input("Precio Unitario:")
            stk_p = st.text_input("Stock Inicial:")
            btn_submit_p = st.form_submit_button("Guardar Producto")
            if btn_submit_p:
                exito, mensaje = agregar_producto(id_p, nom_p, pre_p, stk_p)
                if exito: st.success(mensaje)
                else: st.error(mensaje)
    else:
        st.subheader("Inventario en Tiempo Real")
        st.dataframe(obtener_productos_df(), use_container_width=True, hide_index=True)

elif seleccion == "Pedidos":
    st.title("Módulo: Gestión y Generación de Pedidos")
    col_sub1, col_sub2, _ = st.columns([2, 2, 5])
    with col_sub1: action_ver_pe = st.button("🛒 Ver Pedidos", use_container_width=True)
    with col_sub2: action_reg_pe = st.button("📝 Generar Pedido", use_container_width=True)
    
    if 'action_ped' not in st.session_state: st.session_state.action_ped = "ver"
    if action_ver_pe: st.session_state.action_ped = "ver"
    if action_reg_pe: st.session_state.action_ped = "registrar"

    if st.session_state.action_ped == "registrar":
        st.subheader("Generar Nuevo Pedido")
        lista_clientes = cargar_clientes()
        lista_productos = cargar_productos()
        
        if not lista_clientes or not lista_productos:
            st.warning("⚠️ Se requiere registrar al menos un Cliente y un Producto antes de generar un pedido.")
        else:
            with st.form("form_pedido"):
                opciones_cli = [c["id_cliente"] for c in lista_clientes]
                id_cli_sel = st.selectbox("Seleccione el ID del Cliente:", opciones_cli)
                opciones_prod = [p["producto_id"] for p in lista_productos]
                id_prod_sel = st.selectbox("Seleccione el Producto a Solicitar:", opciones_prod)
                cant_solicitada = st.number_input("Cantidad Requerida:", min_value=1, value=1, step=1)
                btn_submit_pe = st.form_submit_button("Confirmar y Guardar Pedido")
                if btn_submit_pe:
                    lista_items = [{"producto_id": id_prod_sel, "cantidad": int(cant_solicitada)}]
                    exito, mensaje = registrar_pedido(id_cli_sel, lista_items)
                    if exito: st.success(mensaje)
                    else: st.error(mensaje)
    else:
        st.subheader("Historial de Pedidos Registrados")
        st.dataframe(obtener_pedidos_df(), use_container_width=True, hide_index=True)

elif seleccion == "Despacho":
    st.title("Módulo: Control de Despachos e Historial")
    col_sub1, col_sub2, _ = st.columns([2, 2, 5])
    with col_sub1: action_ver_des = st.button("🚚 Ver Trazabilidad", use_container_width=True)
    with col_sub2: action_mod_des = st.button("🔄 Actualizar Estado", use_container_width=True)
    
    if 'action_desp' not in st.session_state: st.session_state.action_desp = "ver"
    if action_ver_des: st.session_state.action_desp = "ver"
    if action_mod_des: st.session_state.action_desp = "actualizar"
    
    if st.session_state.action_desp == "actualizar":
        st.subheader("Actualizar Estado de Envío Logístico")
        df_actual = obtener_despachos_df()
        if df_actual.empty:
            st.warning("⚠️ No hay pedidos en el sistema para actualizar.")
        else:
            with st.form("form_despacho"):
                codigos_disponibles = df_actual["Código Pedido"].tolist()
                cod_sel = st.selectbox("Seleccione el Código de Pedido:", codigos_disponibles)
                nuevo_est = st.selectbox("Seleccione el Nuevo Estado:", ["Pendiente", "Despachado", "Entregado"])
                btn_submit_de = st.form_submit_button("Actualizar Flujo Logístico")
                if btn_submit_de:
                    exito, mensaje = actualizar_estado_despacho(cod_sel, nuevo_est)
                    if exito: st.success(mensaje)
                    else: st.error(mensaje)
    else:
        st.subheader("Monitoreo de Envíos y Despachos")
        st.dataframe(obtener_despachos_df(), use_container_width=True, hide_index=True)

elif seleccion == "Incidencias (No Entregados)":
    st.title("Módulo: Gestión de Pedidos No Entregados")
    col_sub1, col_sub2, _ = st.columns([2, 2, 5])
    with col_sub1: action_ver_inc = st.button("⚠️ Ver Pedidos Fallidos", use_container_width=True)
    with col_sub2: action_reg_inc = st.button("🚨 Registrar Falla de Entrega", use_container_width=True)
    
    if 'action_inc' not in st.session_state: st.session_state.action_inc = "ver"
    if action_ver_inc: st.session_state.action_inc = "ver"
    if action_reg_inc: st.session_state.action_inc = "registrar"
    
    if st.session_state.action_inc == "registrar":
        st.subheader("Reportar Pedido No Entregado")
        lista_p = cargar_pedidos()
        if not lista_p:
            st.warning("⚠️ No hay pedidos registrados para reportar fallas.")
        else:
            with st.form("form_incidencia"):
                codigos_p = [p["codigo_pedido"] for p in lista_p]
                cod_sel_inc = st.selectbox("Seleccione el Código del Pedido afectado:", codigos_p)
                motivo = st.selectbox("Motivo de la No Entrega:", [
                    "Cliente ausente en domicilio",
                    "Dirección de entrega incorrecta / no localizada",
                    "Rechazado por el cliente",
                    "Daño o avería en transporte"
                ])
                accion = st.text_input("Acción Correctiva (ej: Reprogramar envío para mañana, Devolver a almacén):")
                
                btn_submit_inc = st.form_submit_button("Registrar Incidencia")
                if btn_submit_inc:
                    exito, mensaje = registrar_no_entregado(cod_sel_inc, motivo, accion)
                    if exito: st.success(mensaje)
                    else: st.error(mensaje)
    else:
        st.subheader("Libro de Registro de Pedidos No Entregados")
        st.dataframe(obtener_incidencias_df(), use_container_width=True, hide_index=True)

elif seleccion == "Reportes":
    st.title("Módulo: Reportes Ejecutivos e Indicadores (KPIs)")
    kpis = obtener_kpis_pedidos()
    
    st.markdown("### Tarjetas de Rendimiento Analítico")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric(label="Ingresos Totales Brutos", value=f"S/. {kpis['ingresos_totales']:.2f}")
    with c2: st.metric(label="Pedidos Pendientes", value=kpis['pedidos_pendientes'])
    with c3: st.metric(label="Pedidos Despachados", value=kpis['pedidos_despachados'])
    with c4: st.metric(label="Pedidos Entregados", value=kpis['pedidos_entregados'])
    
    st.markdown("---")
    st.subheader("Tabla de Indicadores Consolidados")
    st.dataframe(obtener_tabla_kpis_df(), use_container_width=True, hide_index=True)