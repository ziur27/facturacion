import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

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
    c = canvas.Canvas(f"factura_{factura[0]}.pdf", pagesize=LETTER)
    c.setFont("Helvetica", 12)
    c.drawString(50, 750, f"Factura ID: {factura[0]}")
    c.drawString(50, 730, f"Fecha: {factura[2]}")
    c.drawString(50, 710, f"Descripción: {factura[3]}")
    c.drawString(50, 690, f"Cantidad: {factura[4]}")
    c.drawString(50, 670, f"Precio: {factura[5]}")
    c.drawString(50, 650, f"Total: {factura[4]*factura[5]}")
    c.save()

# Interfaz principal
st.title("Aplicación de Facturación")

menu = st.sidebar.radio("Menú", ["Crear Cliente", "Ver Clientes", "Crear Factura", "Historial Facturas"])

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
    clientes = pd.read_sql_query("SELECT id, nombre FROM clientes", conn)
    cliente_filtro = st.selectbox("Filtrar por Cliente", ["Todos"] + clientes["nombre"].tolist())

    query = '''SELECT facturas.id, clientes.nombre, facturas.fecha, facturas.descripcion, facturas.cantidad, facturas.precio
               FROM facturas INNER JOIN clientes ON facturas.cliente_id = clientes.id'''

    if cliente_filtro != "Todos":
        query += f" WHERE clientes.nombre = '{cliente_filtro}'"

    facturas = pd.read_sql_query(query, conn)
    conn.close()

    st.table(facturas)

    if st.button("Exportar última factura a PDF") and not facturas.empty:
        create_pdf(facturas.iloc[-1])
        st.success("PDF generado con éxito.")
