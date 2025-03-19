import streamlit as st
import sqlite3
from datetime import datetime

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

# Interfaz principal
st.title("Aplicación de Facturación")

menu = st.sidebar.selectbox("Menú", ["Crear Cliente", "Ver Clientes"])

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
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()
    conn.close()

    for cliente in clientes:
        st.write(cliente)
