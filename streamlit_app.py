import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import base64

# Autenticación básica
def login():
    st.sidebar.title("🔒 Iniciar sesión")
    username = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")
    if st.sidebar.button("Ingresar"):
        if username == "admin" and password == "admin123":
            st.session_state["autenticado"] = True
        else:
            st.error("Credenciales incorrectas")

if "autenticado" not in st.session_state:
    login()
    st.stop()

st.set_page_config(page_title="Facturación 1.0", layout="wide")

# Crear Base de Datos y conexión
def create_db():
    conn = sqlite3.connect('facturacion.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT, direccion TEXT, telefono TEXT, email TEXT, numero_fiscal TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS facturas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER, fecha TEXT, descripcion TEXT,
        cantidad INTEGER, precio REAL, estado TEXT DEFAULT 'Pendiente',
        FOREIGN KEY(cliente_id) REFERENCES clientes(id))''')
    conn.commit()
    conn.close()

# Añadir Cliente
def add_cliente(nombre, direccion, telefono, email, numero_fiscal):
    conn = sqlite3.connect('facturacion.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clientes (nombre, direccion, telefono, email, numero_fiscal) VALUES (?, ?, ?, ?, ?)",
                   (nombre, direccion, telefono, email, numero_fiscal))
    conn.commit()
    conn.close()

# Crear PDF de factura
def create_pdf(factura):
    filename = f"factura_{factura['id']}.pdf"
    c = canvas.Canvas(filename, pagesize=LETTER)
    c.setFont("Helvetica", 12)
    c.drawString(50, 750, f"Factura ID: {factura['id']}")
    c.drawString(50, 730, f"Cliente: {factura['cliente']}")
    c.drawString(50, 710, f"Fecha: {factura['fecha']}")
    c.drawString(50, 690, f"Descripción: {factura['descripcion']}")
    c.drawString(50, 670, f"Cantidad: {factura['cantidad']}")
    c.drawString(50, 650, f"Precio: {factura['precio']}")
    c.drawString(50, 630, f"Total: {factura['cantidad'] * factura['precio']:.2f}")
    c.save()
    return filename

# Mostrar PDF
def mostrar_pdf(filename):
    with open(filename, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="900" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)

# INTERFAZ
st.title("📄 Facturación 1.0")
menu = st.sidebar.selectbox("📌 Menú", ["Crear Cliente", "Ver Clientes", "Crear Factura", "Historial Facturas", "Estadísticas"])
create_db()

if menu == "Crear Cliente":
    st.header("➕ Nuevo Cliente")
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre")
        direccion = st.text_input("Dirección")
        numero_fiscal = st.text_input("Número Fiscal")
    with col2:
        telefono = st.text_input("Teléfono")
        email = st.text_input("Email")
    if st.button("💾 Guardar Cliente"):
        if nombre:
            add_cliente(nombre, direccion, telefono, email, numero_fiscal)
            st.success("Cliente agregado correctamente.")
        else:
            st.warning("El nombre del cliente es obligatorio.")

elif menu == "Ver Clientes":
    st.header("📋 Clientes Registrados")
    conn = sqlite3.connect('facturacion.db')
    clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
    if clientes.empty:
        st.info("No hay clientes registrados.")
    else:
        for i, row in clientes.iterrows():
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
            col1.write(row['id'])
            col2.write(row['nombre'])
            col3.write(row['direccion'])
            col4.write(row['telefono'])
            col5.write(row['email'])
            col6.write(row['numero_fiscal'])
            if col7.button("🗑️ Eliminar", key=f"delete_{row['id']}"):
                try:
                    conn.execute("DELETE FROM clientes WHERE id = ?", (row['id'],))
                    conn.commit()
                    st.success(f"Cliente {row['nombre']} eliminado.")
                    st.stop()
                except sqlite3.IntegrityError:
                    st.error("No se puede eliminar: el cliente tiene facturas asociadas.")
    conn.close()

elif menu == "Crear Factura":
    st.header("📝 Nueva Factura")
    conn = sqlite3.connect('facturacion.db')
    clientes = pd.read_sql_query("SELECT id, nombre FROM clientes", conn)
    if clientes.empty:
        st.warning("Debes crear un cliente primero.")
    else:
        cliente_seleccionado = st.selectbox("Cliente", clientes["nombre"].tolist())
        descripcion = st.text_area("Descripción del Servicio")
        col1, col2 = st.columns(2)
        with col1:
            cantidad = st.number_input("Cantidad", min_value=1, value=1)
        with col2:
            precio = st.number_input("Precio Unitario", min_value=0.0, step=0.01)
        if st.button("📥 Guardar Factura"):
            cliente_id = clientes.loc[clientes['nombre'] == cliente_seleccionado, 'id'].iloc[0]
            fecha = datetime.now().strftime("%Y-%m-%d")
            conn.execute("INSERT INTO facturas (cliente_id, fecha, descripcion, cantidad, precio) VALUES (?, ?, ?, ?, ?)",
                         (cliente_id, fecha, descripcion, cantidad, precio))
            conn.commit()
            conn.close()
            st.success("Factura creada exitosamente.")

elif menu == "Historial Facturas":
    st.header("🗃️ Historial de Facturas")
    conn = sqlite3.connect('facturacion.db')
    facturas = pd.read_sql_query('''
        SELECT facturas.id, clientes.nombre AS cliente, facturas.fecha,
               facturas.descripcion, facturas.cantidad, facturas.precio, facturas.estado
        FROM facturas
        INNER JOIN clientes ON facturas.cliente_id = clientes.id
        ORDER BY facturas.fecha DESC
    ''', conn)
    conn.close()
    if facturas.empty:
        st.info("No hay facturas registradas.")
    else:
        st.dataframe(facturas)
        factura_id = st.selectbox("Selecciona una factura", facturas["id"].tolist())
        factura = facturas[facturas["id"] == factura_id].iloc[0]
        st.write(f"### Factura #{factura['id']} - Cliente: {factura['cliente']}")
        st.write(f"- Fecha: {factura['fecha']}")
        st.write(f"- Descripción: {factura['descripcion']}")
        st.write(f"- Cantidad: {factura['cantidad']}")
        st.write(f"- Precio unitario: ${factura['precio']}")
        st.write(f"- Estado: {factura['estado']}")
        st.write(f"- Total: ${factura['cantidad'] * factura['precio']:.2f}")
        if st.button("📄 Exportar a PDF"):
            archivo = create_pdf(factura)
            mostrar_pdf(archivo)

elif menu == "Estadísticas":
    st.header("📈 Resumen")
    conn = sqlite3.connect('facturacion.db')
    total = pd.read_sql_query("SELECT COUNT(*) FROM facturas", conn).iloc[0, 0]
    suma = pd.read_sql_query("SELECT SUM(cantidad * precio) FROM facturas", conn).iloc[0, 0]
    conn.close()
    st.metric("Total Facturas", total)
    st.metric("Ventas Totales", f"${suma:.2f}" if suma else "$0.00")
