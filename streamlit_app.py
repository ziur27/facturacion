import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import smtplib
from email.message import EmailMessage
import base64

# Crear Base de Datos y conexión
def create_db():
    conn = sqlite3.connect('facturacion.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        direccion TEXT,
        telefono TEXT,
        email TEXT,
        numero_fiscal TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS facturas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        fecha TEXT,
        descripcion TEXT,
        cantidad INTEGER,
        precio REAL,
        estado TEXT DEFAULT 'Pendiente',
        FOREIGN KEY(cliente_id) REFERENCES clientes(id)
    )''')
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
    filename = f"factura_{factura[0]}.pdf"
    c = canvas.Canvas(filename, pagesize=LETTER)
    c.setFont("Helvetica", 12)
    c.drawString(50, 750, f"Factura ID: {factura[0]}")
    c.drawString(50, 730, f"Cliente: {factura[1]}")
    c.drawString(50, 710, f"Fecha: {factura[2]}")
    c.drawString(50, 690, f"Descripción: {factura[3]}")
    c.drawString(50, 670, f"Cantidad: {factura[4]}")
    c.drawString(50, 650, f"Precio: {factura[5]}")
    c.drawString(50, 630, f"Total: {factura[4]*factura[5]}")
    c.save()
    return filename

# Mostrar PDF en Streamlit
def mostrar_pdf(filename):
    with open(filename, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="900" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Interfaz principal
st.title("Aplicación de Facturación Avanzada")

menu = st.sidebar.radio("Menú", ["Crear Cliente", "Ver Clientes", "Crear Factura", "Modificar Factura", "Eliminar Factura", "Historial Facturas", "Panel Estadísticas"])

create_db()

if menu == "Crear Cliente":
    st.header("Nuevo Cliente")
    nombre = st.text_input("Nombre")
    direccion = st.text_input("Dirección")
    telefono = st.text_input("Teléfono")
    email = st.text_input("Email")
    numero_fiscal = st.text_input("Número Fiscal")

    if st.button("Guardar Cliente"):
        add_cliente(nombre, direccion, telefono, email, numero_fiscal)
        st.success("Cliente agregado correctamente.")

elif menu == "Ver Clientes":
    st.header("Clientes Registrados")
    conn = sqlite3.connect('facturacion.db')
    clientes = pd.read_sql_query("SELECT * FROM clientes", conn)
    conn.close()
    st.table(clientes)

elif menu == "Crear Factura":
    st.header("Nueva Factura")
    conn = sqlite3.connect('facturacion.db')
    clientes = pd.read_sql_query("SELECT id, nombre FROM clientes", conn)
    cliente_seleccionado = st.selectbox("Selecciona Cliente", clientes["nombre"].tolist())
    descripcion = st.text_area("Descripción")
    cantidad = st.number_input("Cantidad", min_value=1)
    precio = st.number_input("Precio Unitario", min_value=0.0, step=0.01)

    if st.button("Guardar Factura"):
        cliente_id = clientes.loc[clientes['nombre'] == cliente_seleccionado, 'id'].iloc[0]
        fecha = datetime.now().strftime("%Y-%m-%d")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO facturas (cliente_id, fecha, descripcion, cantidad, precio) VALUES (?, ?, ?, ?, ?)",
                       (cliente_id, fecha, descripcion, cantidad, precio))
        conn.commit()
        conn.close()
        st.success("Factura creada exitosamente.")

elif menu == "Historial Facturas":
    st.header("Historial de Facturas")
    conn = sqlite3.connect('facturacion.db')
    facturas = pd.read_sql_query('''SELECT facturas.id, clientes.nombre, facturas.fecha, facturas.descripcion, facturas.cantidad, facturas.precio, facturas.estado
                                    FROM facturas INNER JOIN clientes ON facturas.cliente_id = clientes.id''', conn)
    conn.close()
    st.dataframe(facturas)

    if st.button("Exportar última factura a PDF") and not facturas.empty:
        archivo = create_pdf(facturas.iloc[-1])
        mostrar_pdf(archivo)
        st.success(f"PDF generado: {archivo}")

elif menu == "Panel Estadísticas":
    st.header("Resumen Estadístico")
    conn = sqlite3.connect('facturacion.db')
    total_facturas = pd.read_sql_query("SELECT COUNT(*) FROM facturas", conn).iloc[0,0]
    ventas_totales = pd.read_sql_query("SELECT SUM(cantidad * precio) FROM facturas", conn).iloc[0,0]
    conn.close()
    st.metric("Total Facturas", total_facturas)
    st.metric("Ventas Totales", ventas_totales if ventas_totales else 0)

st.sidebar.markdown("---")
st.sidebar.write("Desarrollado por Marlon Ruiz")
