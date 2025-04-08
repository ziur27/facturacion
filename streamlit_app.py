import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import base64

st.set_page_config(page_title="Facturación Avanzada", layout="wide")

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

# Mostrar PDF en Streamlit
def mostrar_pdf(filename):
    with open(filename, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="900" type="application/pdf">'
    st.markdown(pdf_display_
