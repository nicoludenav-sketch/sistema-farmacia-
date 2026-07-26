import streamlit as st
import sqlite3
import base64
from io import BytesIO
from datetime import datetime, timedelta, timezone

# ========================= CONFIGURACIÓN DE PÁGINA =========================
st.set_page_config(page_title="SaludPlus - Sistema de Farmacia", page_icon="💊", layout="wide")

# ========================= HORA LOCAL (ECUADOR) =========================
def hora_ecuador():
    """
    Devuelve la fecha y hora actual en la zona horaria de Ecuador (UTC-5),
    sin depender del huso horario configurado en el servidor donde corre la app
    (por eso antes se veía la hora adelantada, ej. 3am). Ecuador no aplica
    horario de verano, así que el offset de -5 horas es siempre fijo.
    Devuelve un datetime "naive" (sin tzinfo) para ser compatible con el resto
    del código, que ya maneja fechas sin zona horaria.
    """
    return (datetime.now(timezone.utc) - timedelta(hours=5)).replace(tzinfo=None)


# ========================= BASE DE DATOS SQLITE =========================
def conectar_db():
    conn = sqlite3.connect('farmacia.db')
    conn.row_factory = sqlite3.Row
    return conn


def crear_tablas():
    conn = conectar_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS medicamentos (
        codigo TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        precio REAL NOT NULL,
        stock INTEGER NOT NULL,
        fecha_vencimiento TEXT NOT NULL,
        categoria TEXT NOT NULL,
        es_vencido INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        correo TEXT NOT NULL,
        contrasena TEXT NOT NULL,
        rol TEXT NOT NULL,
        sueldo REAL NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS proveedores (
        id_proveedor INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        direccion TEXT,
        telefono TEXT,
        empresa TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS ventas (
        id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_medicamento TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        total REAL NOT NULL,
        fecha TEXT NOT NULL,
        FOREIGN KEY (codigo_medicamento) REFERENCES medicamentos(codigo)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS compras_proveedores (
        id_compra INTEGER PRIMARY KEY AUTOINCREMENT,
        id_proveedor INTEGER NOT NULL,
        codigo_medicamento TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        valor_unitario REAL NOT NULL,
        total REAL NOT NULL,
        fecha TEXT NOT NULL,
        FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor),
        FOREIGN KEY (codigo_medicamento) REFERENCES medicamentos(codigo)
    )''')
    conn.commit()
    conn.close()


def inicializar_datos():
    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM medicamentos")
    if c.fetchone()[0] == 0:
        medicamentos = [
            ("M001", "Paracetamol 500mg", 3.50, 150, "10/12/2026", "Analgésicos/Antiinflamatorios"),
            ("M002", "Ibuprofeno 400mg", 5.00, 130, "15/08/2026", "Analgésicos/Antiinflamatorios"),
            ("M003", "Aspirina 100mg", 2.50, 4, "01/11/2025", "Analgésicos/Antiinflamatorios"),
            ("M004", "Naproxeno 250mg", 6.80, 80, "20/01/2027", "Analgésicos/Antiinflamatorios"),
            ("M005", "Diclofenaco 50mg", 7.20, 3, "05/09/2025", "Analgésicos/Antiinflamatorios"),
            ("M006", "Amoxicilina 500mg", 15.30, 130, "20/08/2026", "Antibióticos"),
            ("M007", "Azitromicina 250mg", 22.50, 60, "15/03/2027", "Antibióticos"),
            ("M008", "Ciprofloxacino 500mg", 18.90, 45, "10/10/2026", "Antibióticos"),
            ("M009", "Metronidazol 250mg", 12.40, 2, "28/02/2026", "Antibióticos"),
            ("M010", "Omeprazol 20mg", 12.00, 50, "10/12/2024", "Gastrointestinales"),
            ("M011", "Ranitidina 150mg", 8.50, 70, "05/06/2026", "Gastrointestinales"),
            ("M012", "Loperamida 2mg", 6.30, 90, "18/09/2026", "Gastrointestinales"),
            ("M013", "Simeticona 125mg", 9.80, 55, "22/11/2026", "Gastrointestinales"),
            ("M014", "Pasta Dental Colgate", 4.20, 200, "01/01/2028", "Aseo e Higiene"),
            ("M015", "Jabón Antibacterial", 3.80, 180, "15/06/2027", "Aseo e Higiene"),
            ("M016", "Papel Higiénico (4u)", 5.50, 160, "01/01/2029", "Aseo e Higiene"),
            ("M017", "Alcohol en Gel 500ml", 7.90, 120, "30/04/2027", "Aseo e Higiene"),
            ("M018", "Enjuague Bucal 500ml", 11.20, 75, "15/08/2027", "Aseo e Higiene"),
            ("M019", "Vitamina C 1000mg", 14.50, 100, "20/12/2026", "Vitaminas y Antialérgicos"),
            ("M020", "Loratadina 10mg", 10.80, 85, "10/05/2027", "Vitaminas y Antialérgicos"),
        ]
        c.executemany("INSERT INTO medicamentos VALUES (?,?,?,?,?,?,0)", medicamentos)

    c.execute("SELECT COUNT(*) FROM proveedores")
    if c.fetchone()[0] == 0:
        proveedores = [
            ("Juan Ruiz", "Av. Principal 123", "0991234567", "Farmacéutica del Sur"),
            ("María Torres", "Calle Central 456", "0987654321", "Laboratorios Andinos")
        ]
        c.executemany("INSERT INTO proveedores VALUES (NULL,?,?,?,?)", proveedores)

    conn.commit()
    conn.close()


crear_tablas()
inicializar_datos()


# ========================= ESTILOS =========================
def agregar_estilos():
    st.markdown("""
    <style>
    /* ✅ NUEVO: oculta la barra superior de Streamlit y quita el espacio en blanco */
    header[data-testid="stHeader"] {
        height: 0rem;
        visibility: hidden;
    }

    /* FONDO NARANJA SUAVE */
    .stApp {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 50%, #ffcc80 100%);
        background-attachment: fixed;
    }

    /* ✅ NUEVO: padding superior reducido para eliminar el espacio en blanco arriba */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 2rem;
    }

    /* TEXTOS: AZUL MARINO OSCURO PARA BUEN CONTRASTE */
    .stApp, p, span, label, .stMarkdown, .stCode, li, div {
        color: #0d47a1 !important;
    }

    /* TÍTULOS MÁS OSCUROS Y DESTACADOS */
    h1, h2, h3, h4, h5, h6 {
        color: #0d47a1 !important;
        font-weight: 700 !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.9);
    }

    /* CONTENEDORES BLANCOS SEMI-TRANSPARENTES */
    .stExpander, .stAlert, [data-testid="stForm"],
    .stTextInput > div, .stNumberInput > div, .stSelectbox > div {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 12px;
    }

    /* INPUTS CON LETRA OSCURA */
    .stTextInput input, .stNumberInput input, .stSelectbox input {
        color: #0d47a1 !important;
        border-radius: 10px;
    }

    /* BOTONES AZULES QUE CONTRASTAN CON NARANJA */
    .stButton > button {
        width: 100%;
        height: 45px;
        border-radius: 10px;
        background: #1976d2 !important;
        color: white !important;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }

    .stButton > button:hover {
        background: #0d47a1 !important;
        transform: translateY(-2px);
        box-shadow: 0 5px 12px rgba(25, 118, 210, 0.4);
    }

    /* FACTURAS */
    .factura {
        background: white;
        padding: 20px;
        border-radius: 10px;
        border: 2px dashed #1976d2;
        font-family: monospace;
    }

    /* ALERTAS: ASEGURAR LETRA LEGIBLE */
    .stAlert p, .stAlert div {
        color: #0d47a1 !important;
    }

    /* ETIQUETAS DE ESTADO EN PRODUCTOS */
    .etiqueta {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: bold;
        margin-right: 8px;
        margin-top: 6px;
    }
    .etiqueta-stock-bajo {
        background: #fff3cd;
        color: #856404 !important;
        border: 1px solid #ffeaa7;
    }
    .etiqueta-ultima {
        background: #f8d7da;
        color: #721c24 !important;
        border: 1px solid #f5c6cb;
    }
    .etiqueta-vencido {
        background: #f5c6cb;
        color: #721c24 !important;
        border: 1px solid #f1b0b7;
    }
    .etiqueta-proximo {
        background: #ffeeba;
        color: #856404 !important;
        border: 1px solid #ffe08a;
    }
    .etiqueta-ok {
        background: #d4edda;
        color: #155724 !important;
        border: 1px solid #c3e6cb;
    }
    </style>
    """, unsafe_allow_html=True)


agregar_estilos()

# ========================= IMÁGENES =========================
# ✅ NUEVO: Logo de SaludPlus incrustado directamente en el código (base64).
# Así el logo SIEMPRE se ve, sin importar dónde despliegues la app (Streamlit
# Cloud, tu PC, etc.) porque no depende de subir un archivo de imagen aparte.
_LOGO_SALUDPLUS_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAASwAAAEsCAYAAAB5fY51AAEAAElEQVR42qz9d7wlR3Utjq9d3X3SjXMnjzRBOQuhDAiERBBBRJNsnnEOz9k44PQcn214Bvs58ozBxphgg8k5ChFEkgQSEsoS0kiT000ndVft3x/VYVd19blXfH/iIzRzwzl9uqt27b322muR0YaZAEL4"
    "H2YGiECwP8NEALP4AYhfpvwLk/4J/0zxsvnbTfhtyt92rfeZdDkEZi7fx/6Zmt+bxWtRda1rvj3Z9/n/2z/OvXav3f+x4k/V/RK/WnwOkL2PgdeV95u9V61epnp9+SAJXL8/Dc+ids/FtRTfK56N8wLFZVPTa4h7TwBxfr3iB4uXLJ5T8LUa7rtzS0h+uMAHnXB/m27S"
    "Wvtg4mIv30+u86Z9567RSZfK5bpZ6+vFq7j7TKw4b+WE3798fOINyRjjrkda67bkH5B+gA1HAIz3Hut8mFVQ4fxZ0NqbG49/oUwMFN61Fg+aZAQro6C88+v8jPljDAUhb4dVP8NOBGp8L4bdtM7PiE1cLaX6a8jvOT+37sfu/j6KgEbupvE/d7Vpqx/m/BsUus9rLT0R"
    "BIr3cg6fNV9r8g/Un9u6I9XE9fD/+ZAT+6DxNZ0F4n2DCUze7zUG8eomN+8qFithcnR0DxmCKn9AYV3LkME/+DPgQGZE4q76mVv5S95CaNzMgVUqAkvjzwVORHJ3bDCu+dfE/n0KvA2hHvD89y0PBecW5L+cB6ny+oqvUT1Ay89A/udYbzD3nln4+a11O93f50mBH5Mf"
    "s/+53EDYfFnsn9T5fXQeATV8Bg6/KoGa18MaN5h5nfc+dIG8xrpf3yW4v0tNP0y1fKjpdYkAkGq8tOqz+FUSBTP10D1VtdObmxdH6I7LG0rBjcj1FBQcvqtEgUVOztepeRWX10r5Bi5P7cd74JG3yfLXqQeEQFDwM1Hv4zn3q0jHWZQmeVRzg6EocZjtSUiBle/tAi7S"
    "b+bAYeAGCRtIOPDseeLuYsP1BUlrRLDHceCxF92a9pX7vJo2C1e4wxob3rkfFL5wefo7ZVXD/WLm8jqV+L2mn7cZYCCKkgiWocjMXkAlueHV44h2zoYIrDP3XtpiTcIBvMZjJ2+lNiQK4npVLapR4ARjEe25flPLC3ZKJLHYuPqgNoBQ82kcKA2CQUAkZcVCYASCKImA"
    "529yZqfMAHM4+csXDnnBwXCFN9RAh6Yk0LkGbq6OuR6Mys/CCJ66ZYnoHSITf08mXOSefOUdlcHSO7RIZI6KnLTJOVGZec3UwjnIirU0KWFoWifiYHDWE1P5efz1UAvWgUCEQFBnEfgnrd0yAMEtv4l8/K1+n+Vf7R4ADEz9njDA4jALVUPspoThIMuBRUmog8zs7h0S"
    "pWD1vSawch0VGLs4IUkMiyfgAmWQoeb6uABFiUggovBfaN1Ions9k5HQZswnjBI6lZ0IsjyhhyB/p4SAgu/bjNAyE9aEOFhsOFrj8/n3hsXCCtVUJfbYfF/LS/K/592n0DWQnxVR4N7lQY7lYVe+VxMAt8a68X/NuSf+50COx4iF23hvvQIgVOYEg+rjx/lCr1bAAMED"
    "nmpw5OPIWt3bXS2ZhnuRXwezl/k3ltPh+z9p31RLc3IZpEKHHnupHhE1ZwwyOaM6SEJNEV1mQ4F0cxJmVSsTJtzkIIZYyyqrqyTmPJNikVVy+T2IDU2hgDDhJtEapRKXC4PXhaOGg2IBVorswQUZ3L/7GXNTsCvuEweupAj2XGVkTvbi/Cg5wY1Ivhd50IF/yFKg/GE3"
    "SNfaShTc6A6IPylQ0VrwJ6+RKQawWW4CeeoYGSHUkuY6iuNDAw3v6TQyyMv8iZoxQPaaS/L+UDNYKJ8ZcbVvOPSZiGv3IBiwHDzFL6Mk4MguBkA0IRjmZZTxs/wiffTwpvoC4wqM4EAArd1Y9vALCoCWqC3u+vep2theu5fzY4nhZSnlryq4rUEv0/MXuZfBlJ+LGnC7"
    "8t6FehNc3vMCA+MG5Jp87I/r6X4FKHtNZAodGgyaFKWZ4VMSoJTo0HE4w5YlbYGXOc9UZHYeNhp87g6El5fkNOkIYPeU47W6gg2YteTsyDKNAlkK+ymH/3nEZ2YOX7uzf733LHE8coKdD6f4EACtJ2hLSkoAnpFBsd5goYZgRc5jUE3QS4EXFRhW0SuQN4NE/c8B7KLC"
    "DtybHQQbOXzj2XsATus90Hmo4h9XeL1349dKn1lkUhX+U2UvtY5bHiVrJ2txxT72GcoYA+UXvCwpiCcV9yV0ahWYSuDrTtCm6h4TlcQDp3xUCDZxymcvlryL/8mmgVNfM4zxe+5rPBlii9EEDwELKFMY0Aq2DKsY4sMW7F5/EdWpGb+d2AosCWXV9VBTKkNwCWb5Z1De"
    "55D7gpi9oIiq2RJKPnI6R3lYCbCbvDLZfw0iCt/jWkOqeh2/4UGhrmAgo/VDJKniPnhpeMnPkR03CAJYcVPyn5+UaLFYNCUoRypIGvODRRWAqN61JDTjNOUDFF3G/Os1elTD95rQBQocvkFAf0KvldZa4BQiY8IFNUUW0hSMyi5TQ3nX3MmqZykc6ldw1dkhJlFqkdtg"
    "gODPgZs3vNyUTVABxGfyaCvsIUfcwEQmf/PVMnwKHCL4gf/hwJM37JFrWTbd6tc9KbNhkZmXn63gmTVcCQeynto6boBaeD1BulY5iMql9qRCuyTQV2IGaW04jK2QIJN5NQFzyXgPnTIOuVN+AKXCnTiZpjtAc/P2roHyDnpINRCQ6fFR8CaC/iKwUJldc44X0jrQzvU3"
    "IZyy3gcweRJISoH7STVgnZQSG3syIO8sjfWUQ6HXWA+1hL1Fup6GQ8Nrr+s61/M85CFIa6D+opyrAdVNHavQWveDlv9ZArjd47tfa6yfNe5JfXqCmz8DN3cna5/JWYfwaBmBEgKghnSV3BNfnsKBetdpxRMBxtRwBPaCFTst0jDI6rRrZbrt349J3bKGB+oAvMX9cDAD"
    "BE++Mr/w8bFQOSb6kSzoIk4DIgybNJ/gHBigCR0mXmnKzmeiWlZmU3uqbURqeG2s9f7UgDGFP1S4vJrw+uHTvWHz1kbMQuMicg2Qtw49fNfHc0AO36qx/iGP0dfIy3Ihl1CmTEAY4IcXBIB18+EaeWIN+BtNODiDyRPXM9xqqsPLio0xQdIHN9Xofi3t1ONrnPZ5+trU"
    "2S+KMqdT1Xhq5quf4P/2RPyTnZ5uFWo4dBL4TYAaUB5aIbS+zK3pc4l+tT95E7qvJU2gIYP0TzDKyxFqoBH4FASLc1CNJMlUbVoFcjrExcYyIhuTPXRqKAGcrHpCJhfGIRk1msLjGsjjaj3JyqJpkweur+lazaRDr+iaNQRbFs2UIM/L+YwO6g2iHNgR7+lSlNi5142V"
    "RfH7RYW05n2tD4SGXpfY4yZOeKlyLM8Yw+uZC1ozjW7IZmrzYV4pU20bqgHqbsszgE6yEREcJXZCzk2pylcOnqC07tOgqQQpsjGDH3RqiSeWYjVeTyjTk/wmP9A2LfCGNN4PCCxOWVV0QxuqnMxkAICIlN0YKnxHjDEw+btE+TgHg6FIwRhTzfmZyWuwLMknbuTHUaay"
    "APjzwzMYUCasjzpc0QCqe+W5rF74B1mPXnZqu/SCc1ZMEtKkcowmf571lvWTSupJQUr8XIB1UwUspvpojeyQhbME76YWG8DHctaonRuzjsdTc4tNSl7nrcwqQpkgi7x0gmyFLA2b43sD7uXdJ4I7xMuNGVz9MJiIY8gM2B9A9RbferAdk9elkVJOoDmcLuLAeBn7Rsew"
    "f3gcR4ZLODFexSAdYnnUhzaMdpwgIoVYKWxqTWNzew4n9TZiR3cBJ3c2Ymt73glmmdEgUUJJOBKTYIqJ2JL7M/66kMPka2JzIbmLYABl8KS1Xs7lBfaJ3wgKZNLy+TZmQw2BLkhoXSNZIac65/WV4uss3d3kol6ac2BvxWXXNlCvFg/YH06lxpaxPCVEO5NC7F2/a9MA"
    "zq11wgQyDchAW3QyaXLrvGTqY1IJyO71ej/bPOfoNipCRMnguhFd2DXhHqJm0qfPrwKcA0Iu5GI4OSKFKMcGT6R93NPfh7tW9+LOpb24d3E/jg+WsTJcxThNYbRBpjMYbex5pY29lxGBIgXDDKWAKE7QTlrYmMxg9/QWXLjhFFyxcCYu3LAHU0mnfH6GDZTM4rzmilOG"
    "kYelTNgY7AdwB0dCcKpBvgoz6gerU/YG1uwEjKmOKDRwqoBg2V8jV7PQYshLrgoOyuk1/kTKGmCW2wwLM+6bgLG1YnyB3HGAdc8UTgTImNCoaKAr5XGqnMyg6YTyT0Z2kSaCOI1CJ4ME4iXfpAnL8E9Sb8H4h3WosynT/4kjP6Hr8E8lP/CHcKamk8gvEZo6OGs0FVji"
    "SuJaS3mVss1ss+NiOHZoxrhj9VHcdOJe3HzkQTy8eACLq4sYDkfgNAMZKks+EoPmtrnCAOdlnSKwsZkZw6oLGaNhlAHHhF6ri1NmtuFpW8/Ds3ZchEs2nlE+H220DVwTI9GEkF7cBuWJrTWNPa2Z0dZxMvJKZvgluSjGSjIzMaiMtBQs5XgdZZqfRHBz7JjcoKQJh788"
    "3JyS1lNe4ByQCeGNXP9Lqa03qbvr30ciWxLyhEDpP1Bn0/lAeuDkcWj46wVEvdOKRRCiptm3tfA1WgOMX0eTgNfbASk4XQFsj+T4yjowwfDM3eT3mAhQB0p8w1yWfUfGS/ji0t344pE78d0DD+LY0iJ0mgHalFpmSpHTKDEANBtkJsvpU5bioYiglLKETgOQAQxb7MqU"
    "2TcjIwNNBtNJFxdtPBWvOu1qPPukS9CN22BmaDYlzrUmlrOegN6Qg7HgLtUDRgjUF5uwKQBOynj9wVXmiZBIUMuqRolgoVnXnEUFdeV4HSV3EOrAhBHQ8DdrycMk6KmGYXkbINj5aKiRg6JlXHUhCMoD09fPHQqR5+hxd3/WIpCsYxMEMh6geapirdcLjUwR6ly02im3"
    "Rgew+JpaT5boBapD40V88th38MkDt+G+Q3vRX1wBZwZKKUSRKl8zY42hHmOUjqC1RsxAR8XoRV3EUIhAiIigCRjrFOMswwqPMdYZUp0hiiN02h20oxZiKDAbIUvCGOgRiIALNp2CnzrnOrxkz1MQqQiZ1iAiVxFiEh1iPZhpUwdZQgnOAUL1gzzwfqHObHBgPMAXDHb8"
    "UBG5EYAsnJBU2z+oY7Nl53Gduly1Xg2L2NUQvBtEL9fTOLD3TwV3lM2wZDo3icQmIrIMZH4XpXwWE4h9IcWEtQKWfJGq7CP3xQjBEnZSgJt4Kga7oD+gqoAT1F3wsGlRywyrrsjJdfZ7bZMEWtcFTqUUFrM+PnX8u/joY9/E3Qe/j8HqAJTZMQh7eBkMsxRDPQYbjYWo"
    "h92djThr/iScuWEnTp8/GZt6s5hvTaOjWoiiCDEpZEZjnKUY6DGODpZwZPUE7jryML53/GHcu7IPjwyOYBUp4qSFKdVGxAqsDQwbgBkjMwZHhCu3nYVfueDFeNpJT8jB+cyGxUZ1ADnZkm9ypcB557EebNwlxB6lgALrsqY0G1Im8KkMtYYHas/lBzpo18J8880fksIO"
    "arZhHQoQk8idocOhtnO9pIqaO+XuGidBa0BAhgOBB9OQcjdmAjUcK0yDIEEancxKZ18DwqefuCfNOgKWo0Hu/07tc3va2XAfVmML3D0G82ceOPkk4B7MllCfRPZOODfICYwin+crcKGvLd6Hf3vsRty+736sHF8GwFCRQqQUMjZYGvcxHo9xcjyHJ288C9ecfAEu2nIm"
    "ds1thUri+ucriMBsqgXmjdHAAKvDVdx/bC9ufuwufO6Rb+Mbxx/ACTNEr9VFL2qD2YDZQAHoY4w4Unj5qVfhty/+YWzuzUMb42RaTcG+CDbGyZQmdKJLCK763VBLn8h2UGnioR4CitxgF6SrBOWFfbyIG9RNAxKqNa5YA2blrZuJkIlEx9eY7GAhNshgqJzLxfD4lHAb"
    "Q1xSltwoSlprntgaFWmnagCTURPxp1ob1T1V2A0uoSDREGSaStAyZV4rUwqUWjVsysN8nNYuNU+uU8MAMvzT1CfqTaIzBOkfPr7lvnBTGWjAiEhhKRvgPw9/Ax948GvYf2g/TKpLbCojg+XRKnoU48pNZ+KFu56Ep5/0BCxMzQlqg4ZmU84TusBvtXHKuURmGCF+F6sI"
    "raRlP1tmcM+hh/Hxe7+CD9z/Fdw1OoJOr4vpqAWjjRWqI8biqI/TZrfiT5/047huz+X5LJ6x487rICzXD1tUOuXMOTA/GS/w6Te1513inpZsG6ZhyKXgUmmCsFOoTGyAVoLPvQT5PVFCciuTSYYpQdpRABqSCUt4gslrVpWdcwcTcZt6QR5WA/6xXuC61iqmOgBfpX8/"
    "mDB/4V+BJrIbr+8BssiCaI2SK8xlaRA7WyPIMBgKDfd2bdAA/5+8CPJFq0jhruFj+H97b8DXHvguhsurIGXxKcMGRwZLmOYYL9l1GV599jNxwdbTy5dIdQbk68MxECjGirwZC38jyyyx+NfkHbFu0gZFEZaXl/Cpe7+Ot93xSXxr9WF0e1PocoxMpyAQhtkIrAx+4Qkv"
    "xO9e+iOIoxiZ0Zak2nRYNGQa8vSX5bOfvTeLNKqc32eEaKV4H59N7nC06uKTzgRCbQ2hUpCoyRTJGi8AsIf23LpmJicISDb8vqxuONAt9Rdy6UnjoRZN5WipOFpKydScMfwuIDdyS2rkRDlikv+QkeUaaDK7fkK2598QQp3YuWb3aI2hYPik2UJahrz2MU3mhcHbDDXC"
    "4Bol69rKqxMyPLFYCYQvrt6Df7r/07jrofthMguAR0RY1UNk/SGu23oRfvmiF+PcLafmtAIDhsnVGCQ1xQ9OkqvEbseLAQRUFGQgN8ZAG4NWnKDd7mDY7+P9t30eb7z1/bjfHMfG3hxgctBdEY6Nl/DMHU/APz3jtdg8NV8Grea1tP6Avxbxs47h1Dchw7sHCLPXm6XA"
    "vdcIgvMehiTTlGDFQmFSt4+rNhzwQfZ9oJMtJ0vQgP+tNZw9abC/cZYwuKHkCzbyn9Ao0xuc5WtklwckkJvSfARmHyd9jjUX41pyvFRuTpqQfdZwvbWY+j5RcB24AftkV5HqV+U5478Wv4W33fNZ7HvkMbACIopgYHB8sIwLe9vwuie8HNecelmZTRFRHgRYaNZX2SVz"
    "gPzDqFmF1dx/SOir5d8zXG1SbQyiKEK33cXhI4fwVze9G2998Aa0ZnqYUi1kJkOiIhwdLOGcuZPw9ue9Dmcu7EKmM0QqaoYaJgSJ8h6KptralBNv7pDXPsjRQP2Z2AwKHOw1GKGxhETjKBLXZH5qeud52as8XfyGsbDAlAk3zayyNyg7oTLyqRy0lpHq2r3OcKt17Tbm"
    "WpmGx3tp4tdMyGrW5Gc9Hk7PGgG1seEQmlsDu9w1BMi4/oJs0DszUv1VjBUXDzrjDP965Kt45/c+h6MHDoMShUgRVtMRRssr+Pkzn4PXXv5K9NrdfDwGgqwpmhGOGgQ7JOCq5GMnsRNScm5zVIYKrqoZqZKU6QxJkqCTdPH5u76G3/rKW/CAOYFNrVmkaYqYFJayPrZ1"
    "5/DO5/4uLtp+JlKdIc6DVghEbsQLQ4dBw7oLdcSJfrD1VSN70g9IwWnghDVSOBqZ5BUG6qwpb2ptUgeRPNgl6Hg7cT5z0ogcVaB7LZI1dV5KbW9GcIC4DCRoIJ9O4GI5p0Xo1OKAEH64u9HEgm/kWMkbGRDObwY1uTGL9LMklmqlj0cmZZ2YlmStE4CMDf75yA34j9s/"
    "h5Ujx0GtGIoIx0ZL2J5N4Q2X/ziuPfOKkpypoNzBWKcByIFAU5fBLUijwS4uu9K5viIwZIBjG4w1G8z2ZnHw6EH8+mf+Hh89+G1snt4IrTPEUYRVM8SsauM/r/8DXLzjbGT518Py+vZ1VaEBthaHa61yXRaFawSKSTiQg6v+gJzCNTmKPtAubOVkhtkI0zTRJibtg6YW"
    "flNG6ONtEg8sfkUbwzUb7xyQLDowNeVGvzQUp9TkzMZNuZtv8lq5sovkh9j3Pt6FSeB6IGuhBlZdpVNf/YyzcCcFtDUm0ScGU//avGuG15E1YLztyJfx79/9NBaPnIBKbDA63D+BJ3f34B+u+VVs37AFqdaIfP+7Mriys9GLT6qNLg8s2byQmbM8peXwF8FKGbPnUVTz"
    "shR/zUyGVtJGQjH+9BP/hL++6xPYsGkLoDUUEVazARaiHj700j/D2Vv2wBgDpTzDDO95hom69UOyvr8mj381QiHr6OYBApTPHZb84eMaduvMOLr7spEv5jeEguNJHo/Dw9ZCDjgTRRFqtCbUiBtrQSceDyv/NVWZN1ADEa0GpDWh+47VFzcz19fAGNZFpGugYvhwgSM3"
    "E+pkrFUWrNU1Yd+0ITDOAYRb3rLsCJxYgu7kzG2V9JGiGwiF/zjxNbzlto/j2MHDUEkCRYQDK0fwss2X4m+u/SW0Wu0c91FO169mGsBcw6MiFbufZS3Kv1iwWmcY63HemRSNCPKH9l26is6/Od2Zxt995h34g1vfjdlNC6DMdi6X0z72dDbgE6/6P9g2u7nG1Vp3BtIE"
    "N0wCkRs5W80YaaOibvn94hljcofv8eKwgp9ks+HmRKPG2M/3jrOXgMn8LRbTw9TA3eD1q0CQ0cZjI64BwAf+XPOdo0lT3XWqAtXSRT9QBOa41pmI0XozmPW0c8WpTJNS5EkdyYZGwMTGQiAehK6t4Fl9YukO/M2dH8G+hx+BSiKoiHBw6ShevePJeNO1vwhDBGMMYqVc"
    "E3lGMMthB5hmfO34PVjlsQ0kxlgOF1HJtWJmsLFThtYEIy9RswwXTu3Cng0nY5SOylS/0bwjABQbNpiZnsXbP/8+/Oo334bphQ3AWCOKFY6PV/DUDWfi/a/8C7Rbbcikb90YpdcZX6ux4uuqU7D6QHAfNUoF0fq10YLA/BpBOSQzUxwQ0hvw8UgRrQ8HbuAJhpp5a3YJ"
    "a7tbfKyQJs+EtnuzqmaApd5Q5pUqi8aETRSElPK6uU0/yM+txfeaBCQ2TQKsMTiNCYKHTf8YNohUhNsGj+KP734fHrjvXiBSoEjh4MoRvHrLlXjTM38VhkzlEi0VBMqHZTwgvXr9WEV404Mfxtvu/xxG2RjaGBhtys9uYKwwnzE5253LTIHAGCLFlv0ZPvPSv8XJO3Zh"
    "NBpWAH+TpRVchoTF5jRmp+fwti+8D7/yjX/Bhg0bgUwjiiMcWj2Onz3zmfjbF/xmM91hHV3apmfeBDg3PadgwJsQKF3qTJ3aUCtl/SpjIi4aDhi1Q3AtntXjbGKVvyc9HdbIAh2ISnRmVajNWfyWKan+TTeXa5o8hGZjUxL6Q0HfuBKTChy4DQuMa++ByaaSE9YsB7S9"
    "2F8A/oIUOBpL30aJ64RmFScsiqaMKpyj2u9HFOFwtoz/9+jn8eCDD4AjhTiOcHS0iOctnI+/esYvQufBqgwSZX3JIM/b2oPYEVOExXQVnzp4M44fOIL+kUUMjy1jdGIVoxOrGBxfxujYCtITfaSLA2TLA2TLQ2QrA4yXBxgu9RENCfct7cNHv/opRCXw7djwWBVZSCNb"
    "1K4sIoWl5UX81DUvxx+e/VIcPXIYUZIgzTJsmtqAf7nr03j3rZ9ErCI7m+hhmI7Nljjd0cT2ltLQoXXoHeTEXGtcBHLG8EMnScglV8whNEJG4nWFVVt43Qc8ARnlPpd8RLdD3IxgrHkABL5O8DwT5EFV+kWKZ2GqC1EV38JLx1gAkEIIPlgiIZjRe/gSKp/DQLuZA2L/"
    "oU5LVaZwMACwbyI5wc3WFx90O5l1U4lJC5XEgmG5cDxulX+NPgNcLppKo6vZeaW4FA2Dtx/+Cm6+77vQRiOOFI6nqzg/3oq/v+bXQFFcjmdwWJ5OBFz5+sJnkhiRZqQmqwxwI4AjAIrAyv4d+d+Nsp/VlksK2jCo1cLScBlHDxwqjkQnkyrR0Fpp6JaNighLK0t43fN/"
    "Bj+2/ck4tHgESRTDZBoz03P4nS+9BQ8cehiRiuqmnuT59onAQk3rJVQW1TIAVEKNYj1UJSa5CYAY5akZSsh10JhdE0Kik9Kz0PH/DBqvWhyLhEx1ZYMmPoYfdL017QekmqeiEJj0RUFrCsfkNzmqq1XywzvZhIzUfkCShgMc0GFnrgUrgCZwNwiKldO+XMtVpbDU8qfr"
    "g9pbXnAIgamkVA0MJ+90RUjLijkYxJrcyFEYm9b8F6kGcFYlJk28EYoIn1m6Ax+7/xsYrAwQxREGZoypIeNvn/qLmOpOlTrpzquJgVjnrHJ+iEXgKvz02JZ/MPmgMpf/NYZzyRgDNqYcZOa888jGdgkHwwHG47HH1CKnecQSlGVU1yDu0Uo2wJt+6Dfw5GQnjo/6UExI"
    "WOGIHuJ1n/wHGK29LiWVr7mWmgevJ5OY0PJ31EGZGyc8aI3khIpMk8lbm2tcUw3laTCVIelnXlfTZTTJ46A8cpz15E2JmKb7STR5ddcOalESNv7OJBsh5+J5gqNG7h5MoYlyL62VG9gJBHk0JnZOMfI6guQHp0Y+inc6itIhuGCLIA4vmHmnK3mu2CHZ47XkmhEC5oN1"
    "vi3vHhsdxzse+RKOHDwCiggghZXVFfz5JT+Os7bsQaozxzHX+CW1Z6PO5fAy6lZRpKyXodcldC3OXUZ8IerHigHDGA+HyHQKo7X3BpWHdGMBLEwViAg6zdDqdfEPL/xNzK4yhqShM42F1gw+tvdWvOeWzyBS1tgilCH4z9XZ9GsJTKJZHJH8g6xcc9z8jLmRL5n/KE+u"
    "vqRTur/e/OyZG/Am77rZoyTVRvfcRxdsHtAasEr9PngS4hwoCWvblD2Aj6sJfCc9JproJOy6Lhcs1sANDEhGs+TE+FSZwKlBHiP5cdXaTOJNRdrqZULyPvAEn8K1DCjL0nDNPm5Tt6fafO898k3c9fD9gDGIVIxjw0W8YseVeNE5T8uB58jNHP1y1I9JPKm7S84GsvJV"
    "pur0cmXrxaZ6xiweqtE2qHAoa2aBzAmulxPGxNcjpbA6WMU5e87GH132w1g8cQxKRdA6Q7c7hb+86V04vrxoZU0cHMmzdq/ZytPamAzqKh8ks4xA2T3ZLJW9x+1dn9+YKOVZvDEbxz2bw16VFHYQd/xASwCR68C+w4Zfd0669l4Mla3iTVRgJ1VxRgCNfrnYaGwZwLjY"
    "KTt5Yv1PTsknOw1cZmnuicHBB0NNZWVAuN+5UmljHnINEuVyjegW0AN3FlhTtuoPLHPDRhGAq2ELPt/RfxSf3nsLstUR4rwU3KFm8LtXvNqaPzjqdMKd1bl3E1pBPmudRLBmWO32UkomAEozu4cREVSknPeuyA0sKBRBmNGj7nDZcFjsn8CPP/nFePaGc3B8tAQYRjdK"
    "cPfKPvzTV99bKlIoahAHkjhkoMsVwpdCpSB7B3vBqarwTkx0yOXAWmP2GdeekUmAJlMbVwxk7Cz11UOZmVdCc8hcg71mgVj7vFbTLGBwgwBOLl9EOf0w8h6S2LhE9RuxnmHemnFE6MGL/0rPTRfUpnrXzv/Xl41tohmErLG8YOt0/JoWsY8VBObOQicfN7SgyU9v/K4V"
    "uX80zPjA4Zvx6IF99kkqwspwCb9+3ouxeXoBJrfOItmFlaVF2ZFlt6HBbnxzGrmcd224ng07QYvdXqt0TVYqymOdD7aLgy3ECasbAldlpGEgUfjDq38c7ZUMOlLItMZ0dwpv+c7Hsf/YISilULB4rFsLOQdUUza1phGJ76BdHnaosiCH/8SulrvT+aIa3knCAaeptGIv"
    "aHJo8zsNKSfyh8tDWd0EnNg5VOGILl+5XkQB5bhaietzmk9oaJUXAYvYTZHDD4/qCcA6yxgKuCrX9ZIYtUI+EESCLf4mK+21slAfVHeXz/rKNK8t3gQoNlVZ/kBS3jJyFgGzHyCscuP3hvtw077vwgxTxCrCcrqKJ07vwg+ddbWdDSSF4GBffr3sHU7uici5gQBXCy1/"
    "qRxuh877fJYiqq3YXk4WNWXwsmRPNvYni01sjPa6f5X9G8HHAqugRSIwVuwHq02/3F/B5WdejB877WocXTkOUhE6UQt7xyfwb9/4KAhUKoU6yrxAec1NOCb7VIg1SsPSkgxitCmkFFsuEFM/IbzqJJgRBw5Ev7qYWLX5QaxJ5aRhU5RYczDVAmq6qU2ltrP/OHxCy5KQ"
    "AzKuLi4uAlrx36KzFnjjeqlU1ZnVWIKQsWCqzXH53CiSabvMgBo4WZKXxYG0n2o3ypsPW+vzyU3vcUpqVUyD4WndHqqh0RFYLJ8/dhsOHjli5+YISEcj/NK51yOJE0GRcPgqYk0yHJkYJ2S5uI70LDRsyqFkzUWYMlXgEoHKVZ4RmFRBLvV1vLmZs1TCE8SBNUq5aKjC"
    "IBvh55/0MizoGCMyMFpjemoa77rzM1haWbIAvPyM4ObSKSSbEtp4PuAusi4iVyKQsH44RUIS5HCtmuBFqpWE9cbAhBOdJnH+4MjOVIepqTTQnGxs7Y4r+RVbeQ+o8bdUcahTrTblZoNScSNr2EzD0DDDL58IlbMjCbl0FnGMgYB9vfLKOJJpfTAIUPMt8LA0lvyXgmU/"
    "gcFOIUyrISujprbyhHvl39/CZHTv6Chu2H8HxoMRoijCUjrApTOn4FmnXJ5jV6peCXvZisxgKIil+CdvEeSKRWrK7JjgYWMlZmzKko3zbiyLTpoEwf2B6BpILrh8crykGqEB+sM+zt55Bl6658lY6i9BKUI3TnDP6kF85Ds3VHrhXmZSm+AIwAwOCdgDtiUUUZtq8MlM"
    "oW5ZgF8omz5O+QrR7fWvI7T3AkTqJhJrWcr5vy/laww7ZSWXkU5ed/5ZyG1mkZdg1Bx/AutIXovyXaJrN5sDfSS/KxFMTxHAcARJDvlpKRUVhFECfAyK3GFLeTON7OzJkymgucOhhyqwKikXQqE2dQPPpinDCnYPA8HKqd0D95fZfdcvL96LB4/ut5euCKPxAK864+mI"
    "4hjaGHd/yEaGRJaYguW9w3/ysiU/c8qZjUDtcGG3+1psMFOpC7AzFiQlgMNlj2SeuPuUi20DRQojk+Inn/g8zI6t3RgyRtRq4923fwZG65Ik6R+y9DjgBIei4K/zhkolSOBk126aAqRTeMx19qk1oSxNKCKEcOMgQZYR2HcSj/NwtqJMoxC+5vWx5MjdpMM/sD/Yz7Ak"
    "KEb+RvdZuBOE6quToQHPI0GgK4DEEOYl2a++aQWH+FpVgAyOwNTKq8DogvOeza1XariRwRvOkhI5gb/j4SmhJkXxfbshM3zl6D0YLvcBIqzqEU5uzeO6PZflXbNKCMTJjOCefj5wXTvhnIFoG2xUqczJTa3gciSx4ma5QH9VfpsScHevUgbGKvOqt/wrhr79WFZCeXU4"
    "wCWnXoBrNp2NxeEqwITpThffOHIf7n7swbJj2LSGfbIlB9cS17k4fsgPlXgQAPYEeyWfV9hYHTR0pRtDbwBPdllF1IzLERpgD3aoD0opce3VmqO1HHZkJtrwo4qaMoCm1LKBo1KApUEZFYlRkBjiXAsHQANAyIFJc6pHbOdm+Fbl8iHLGUhuoF04woWopeEU6ihSQJNJ"
    "ao55AVNyariGqeVjyQTcMzyAO49+30qrRArLwz6u234x5nuz0EaLcowdFoODY8mOpPxPgzBf0cUiJ7MShFMWBxBXc28lnlXpkAAq0OVrwkwLnjSjPkLWsOiZGVGrhRed81RkqwMwWfb7Iqf41L1fczNi9honfheX6zr/Trksb16wnUu10pGbOi6C9yClWRAqMdfYq/L1"
    "mT3FV3ZpCZLt4nC/AtBQrRyuyiav2kCtHGa/kmtSsgjMLxc/r6rMn5s3qAdAsgC0awaqzIIswQ3BngL+DRw4hRC0UULNJ44mdvAk1uQHjiaaBvtjF4HFTKI7GOqsElzGvnMvA5/fiFnKCZRTfGvxARw9fhxRzvzvcITn77nCw0IkWC83Fbkk4BqIIlnvcjLBayzUCOo+"
    "xyu/h0a8rinmaqhqqJAoV9kncLolpRymcCNnzg/L1U4VEVaHfTzt9EuwI57ByGQwxiBKEnz2gVtspqgij2sXOLBqLHUEs+VGQxU/UxPdRvLzKQpsVkmbAJrLT2/2L1gVyIYOeQeGo33cTNrkIBerTiwrnys1W7BRgAFAE3Dd4ucFfh1WZCB/s4c0nCT/JF98ROTN5zXM"
    "DQX8zORNU36g8RcMuRjQ+ifK6zeEQ6VfoARtctxxZvNEgGIPoPebBc599vMN715o1rjlxAMY9ocgIgz0GKdNb8UTtp5R2rSBJIRRnHZku3pGI+OcllD+3X7Ndv40NEz+dw1t7Nczo5GZrJoldE5tdrqhYsqnDFplsC7mC8nSIzKtkRkNnV+Dyd83Y/v1LL8ezcb+Oe9Q"
    "mnw2UWYNkq09SsfYtflkXLblTPTTIRhAO0pw++GHsPfofmtnJxsGVM+0Gjty6zEVccrhwNpxysSwKxSaAHynFHMDHa9DmcRJNEJEWpmo+PBLqMrwPpdnMTiZAC+NlP1EJZDzxH7bOMTurmE1k1LyUCfFj0/k5sGTtNI5EJlDbWXZOaEGIb5SXwtUc5txrIrE+5I8GRtm"
    "oHyNIgppz/sPGFifjld+3doYREph/2gR9y8eAGca1G5hOB7hiu2no9vuIDO6TJlZqJACgGaNJEqa+8yhvzvZjoJmnZdq5DnksJM12YDmvWjxxzRDkjKmVQczURdzca+me+QQDphAJDXk7focmTGG6djiJY4xb1HyGsRRjKfuvhAfOvwdIOkhpggHBifw7Ufuxs7NO6zg"
    "IerZC631rOSB7VFhqPZadU3zSWupfB1PzYBqUIwIqDzBFqKJM1hbb57u1+PQiqtvafIyuMkCoBOjKtUCFmFdM0ChVNm7EUS0jqCa17wKpTsGwdv4E0TtOKzl6t1orl1XkIIBeJhbNV3uM3BVyOWjNrYhMbiQqGF9AVXv06zsKGV57ls9iIPLx0FgGACsNS7bfJYHqNo0"
    "l8QhlUQJ7jjxEPalx8vsomhYFFSJ4q0NrCFFAYoTMSKOsS89jiU9gip3HrngN0LOOiIjzgyo28J3skdxVvYA4pUOOmm7hP/dpoBTg5drQxHA2uC01lacsrAT/dEgtz933PygoDA2KS4/+RxMfV1BGw3FBBMxbnnke3jhJdc27xNmNJ4l7PKQgoezY1EVqByd8pIca7RS"
    "3oUqeegwHcbLAJoCTUhwssktO8A5C+3FkAae0wEsBB1dB/pGrJqbKi6q7pFh648ZkyAPkp9tNDlhhGYJxeatdfNqPC0IbWRhV7WOEYhJEb7KdKhO75V4CKGOEgl2JgUDRn2JkZ9tkjyp3Pa3orCjsEPbwGSTVAC4Z2UfVoerUEohNRl6iHHBwikeFlj5OBm2mcb79n4J"
    "r3/gAzh07Ag0TLmQSJhvlh26wtpcWrJrBrHCeGVUn+UU5gkSyGZ7AZVxgc7Qmp/Hp7sHccNt/w9cWN4b+3NWqdRmPYWeOwMwZHlcBgzFDIoVph5dxX9f/5e44sLLsTpYLYebpY38MB3jjM27sINm8Oh4jKkkhmq3cdv++y2ORSo0OunZrbFDLSFfNTeksCt13Yjr6qBO"
    "5mYcRIucQV9yqTqNmb4fjBqCFXlrcxJaspbuvaxG/MFx9hRYQwapsvRrwKBJlu156RzLMS5qyCKCnCZae3NNTveqrmHIuksuhLXcP2qSMrWIQ2IQjh6HjLLYsM5LCyDdCTSB0yvktFtbM2s6vZWl3gOrB8Cj1G5Ik2Jnaw47pjfVbNqq1roCZwYfOfJNPLzvMZjVDIbc"
    "oUGSVALmMniSvPxclQGqTt+QpZjTjsr5UbLzqEDIVobITghgn8uZH1FOyvIJMMYSsQwDSaeFw2YZ7//qR3HleZdZomygv5PpDHNTc9g9sxn39x9CTyVoxS08tHQQw+EAnV4vJ5E26LCVa7NqFVGgpKIgN0UuZRcIc/eZxH7I2/R1CkJ9nzTQHECB95m87rnBkYmb9ryv"
    "WNJgueffp5penMhSmSrdrwK+kfWmqpU3LL44wc14vdLDa4Ft9fZuXaCfAuqdQQ4JB/ghzkJqeA1GEOQuTkdy3sPtZtDjoxu63LZmho34dlVijo3GvtWjQGpVBzKdYVdnAdOdHrIsE1JAPpUDiBUhNRqqrUAJWfQy/5cLldCIgFiBYsqVRMl+LVcWpUhVIzLFvGAJLpt8"
    "KJrLQFWy6MuBacHXSex7ISL7PrGyX0sInAAmZnAEcGwzLEQMjgFOGFoZUCfBCBn27dtX17riwkVao520cOrGHWDOwBEhVjH2rx7H/uOHURWbocM20HkLDcj7IDyoruHvHdTctJnluiBREDSo7voDyYximJ0CZ+U6wPimkZomvlhAvCBoIuHdJ8nQp0KRVGy5GgnVB919"
    "ThRPKMPWdNFYl9X7hIBIVWrslE1C3NuR+WWZxnMNF2D2ghajnso6ALuwgBQW6gU3SA6zSrzINSesH1EsvleWFOXnY4eHQGAYIykgDEXAYtbH0dEikGogiZBmGU6d2VLJzbiDLPn+sW9u2IAV53GDXcoBpPegawJB7BHXBcbEUnvd4aX5JEgu3XM4BNKKUpa5ojiU5E7O"
    "kUVRmnFmwBmj3+9D9RIkcVwvqRmAUtgzsyVP0QgqYywP+zi4eBR7duyyHobOWmdh9lCNADlWaiJF5gABk6UTNsPxayRIuRg4ulLyPhclkMwA2WvwUMnzYwfvYU+uiMmlAHGAtkyBriSHMCt5nybhzY7HqSs33iiznpPJ2cd5ZMBa7yxgrWQuDEw9Mqb/NTfKe/NU3vto"
    "1gAIESknq3KASvJuMYVPCGqaEKXJJ4rjFRdInmqvS/7naibw1YbPha9gzbGoDo5hSfexOFgBNINiCz5vmdpYBRcB8zLy7lr+7I0x+RyfcvTDyGsGNvHj6qMLLLpzla6Vkeop7GkuOS6+7qFTLmaHIiFpLl4zJTXQ4xTGaCuDbBikasxAMBhbZzcCmixuZYCxNjiweBhE"
    "hEhFwXstn3XTf5ueNwWrB6pjlc0wqvh7NGkXBr0NG1WC/TW8RpZFnCtyGKuG4Sln1tx2QolPKNiRqKJqBG+vDK9lWETWhVf55MkG7zSHGe6lgzL9cyyDEOiKeFIzTECcG3QabTDIhjVn66ZUjYPK51QrD/1GDzd3TyeXsrWZvDrm3ggdcIB2g7BTk7z2WEU4NDiBQZqK"
    "YEOY70yLk7TKAlw13nz4WFezfAWAzF4GRU53j50uX3nieoJXVJtPZ1dpgxkuWUHV+yFFKmACZRO8kVarYlOWpGxYmIFK0FZBgzHfnkJk7P1RCuCuwuGVExiPRxiOx1CREsKalOOSFUUn2G/3mjTuWq1dCSZ45tRKfzhMhdArehwv8s/WgI6aH/NRNxmWZR0RoRUliOO4"
    "3KOmwFIDmRHW01n0BAYQSnwmw+OIC4GxOjeDgkkGe23MRuNRv70vT2ZRjjGj7PB89sFv4iMPfQ0PLx/AcjYoU28HUC6UEfIMQpfGCMYZ0lSCyuDyq/I8hFlYIVJtMZLI8qjAaKSEtZGKrKbq6pSZJYs+fHWPFKnStMGw7bwVp2Q1Ewc7YpO/tjYG2ThF0m2jMzeNEzm+"
    "QczY1Jn1sh5RhoqlqKBABoCWqQsJFIddDMzJ1lwdayYWNAJ3XrIgqRY3yJf2LQ4sFp1cSRL0WFgBCWNTWYEJ3a0ahSz/mjYGc+0pxLDPkxVjdssG/OGH/xmv/8g7wO0IUSsC4ggUWx9HFStQrKCSyP5dEUgBKoqsWqpSJdla5XNGnLfdIdyflFKl+GVh0GFCzlEeXEDi"
    "5LNYoQGJ/NOwyZVkCXmD1Q7rlzr6xpsY4gAWRbaBIsH+wu4rv4apqI3TZ7bjOadfgRef93QkcWLpIaSCUFZIPdiXc+ImzTjyZJkbUojY11Gv2o4iuPgpXq1DhMC0e8FRUX7/yGEBK0U4MVjGr9z4t/jSkTsx0+5C5R0pnS+CMmBJE4jidblqmzuZNrvqDWKP2RgiIYZy"
    "46qKyyO0s6L8vYw/lkIelUCmygXA6p+SpKBQYUlO/4Kr8s0YUwrfZcxIhyNM62lsmpsBxbmlFlcnHrNLT/FPc0WWq8RBdQVXLqSWBkK6VocIpoEMy8dnGXX6s7BTYa5OARb0dWcg2VMarFx8ysVb0x9jZsRRLKRsGBErHDhyGNCAmusiasdQSYQoiRElEVQcQSUKURIh"
    "imNEkQJFhCSOQErZ0tOb0eV8JAhCdbUs9cuun3HItRK/rGVWLHJcEfQNWz0xO0lCpYsQ+fQiR+KnWLv1xpMFvV0TESooMTC4+9j38d57v4g3f+OD+KcX/hbO3nZKyYkK6Mk2gPYBwuhErJsay564xt4tPzwFpV9rbazid2r65nBveGjeihiDdIxXf/ovcH+2H2fMb8fe"
    "IwcxysueUjuJ5E2psgNmXyNTWqqLMsOjHlRubuyZyEp18RKvruyVGFZi168BUVEBKg2o+gNwM3NyAP2yhOJwWTUejdBTbS9t5rrCA8vit+AylaPp8JUZXAxLgO1SjUxoNRF7NLNixjAIzLsBviZEmV8r5cPj5UhPycEqpH2qmUZmAErKOZtcGRWeiqhsnkgxR4A0kKQE"
    "PdZQcQYaM9BmmMiAYgWOFEysYCKFNKI86yIMFdWkpmutemZnaLn0K66pvrCvLAPFVOskMhtHfJLhZaJFNiU05QguR6rSmYfHtOcaMZpEsCCyhOP5pIcvP3I7XvTW38QX/uc/YsfCVkGEDg+H+6omxC7jLDjzW8YTbpStipsZrFhXu54m0RWaQBkAOrc+f+sdH8fNS/fh"
    "3A0n4c69D6CdtCrNL9kq9YmVTLVZzarAoapFmsuSMEs+vVCA5Cplh8i0JC5mmbY5jyiqsA6ZNbllmULd5BK5sB5q+AYbLitHLsuK/AumiPcKXJzuIqNlY2oYSAgt0UaXoLeRnb6yvApnZsQs7qnrBszwbJ6o0mn3n788BJxTVAYi+ZM1Mw52r8Gwm505ry0zy6LDWHXe"
    "KOfqV9I0OSUjsptKFTr3xNWzLUZOVJVaycydBARSDn9xJVZJVD+qZNnuCvBKhdLIA6fZUbNgRMGGUaWHSRW/TvwukZsZkWiUUETFNBZSk2I8SLGxPYN7j30ff/Kpt+Itr/6DPMtSDc3/CcyCEMOd1seNZGZ3lpDW4ktJxuqapMuQFA1KTCoihVRneP99N2Lb1Bz2HjmI"
    "VpSUG9vFM2SbkwQhsZIwcUqxYts74nemOg+53s53Szs35zJwu2Gcs7dVbc7MPdEF6iN8+goMSGILnuSMKCclyz4zBmUjzACagVU9dsnOztR8dV1ZluUlV1RmSZLgyaKPLDXPORTIDLt25hy6j/WMq0Y69H6fWMp31RUqIT0PORygHJUKYwPOymiQl00VCwVs7Kc0Bmxy"
    "0NcUaqpUZtNE+ZhSntWZYsMX98gz2zAVMFrmtkzFoDYHsvrqg3DgwzijTfAkYLwE28nYSP4YOwdHjQ7Evma9TArsGN2YU7TbXXz4u1/Cnx4/jG0bNpeUEAmhGN98pSGerGuONvCPqjo1AWpDg+zq4xqM5DqyUXzAR5cO4eHVwyCylAYieHrgVGX3woWkrCjILfdCbHQK"
    "wv5Ng6JO0eTO/8qCspyb5JzcJ4KnkR6MXJZkTtOexWuVJyCcEsx1obH6+ZlOK4eZvGuzb+VIRcbz+zdSzofyDWk8j8lCh92RuDVu1sMcJhF6krgwblZUXzos7pVk2XvWWEWJIyE2Uz2UQv+/VAQRLdFiXrOA6mIiHFg8jtQYW3IxLA1irL0sr+J8VXLO4nka270uvSLy"
    "N5Dq0VzXWgKC5ipiVi4wQsaVa2ld4lxac4uXKPv25FFtSPAbyZc14lKttc6/qcpJZqva34piHF46hgePPFbhad5rhdgCjvJEKKbUnIImdQnXw0QXCL8DzNeY4fUxGpeCRU621M9GGOkUxrTB2pQLoFbicO7gwpJMGa5Na7Kx0vxCiI0xc4CkQnU9dSaHgutwRR0RNOlD"
    "VWUfsmw1CIi4iaAlJVkcSWSL6MJkBqZUZLBA+tHBkhsQGI6aa7W280AEVXasalC5IOoSe610DgH0LknVIUtKLz4nQIuWvEMAayCwsOd8Jp6+UraDh4C0UOGuQ0rhxNIJsBL0y7EGxhm4k+QZT0WkLTeLsVhZSREwtlSqaWFRdQTWlKGK5ypGe5y8wOMb1+WNPXLtREmB"
    "AsyW3VeqYZIOdCGt18pujXL4cOUcaPFVbZBmKcLMzzo9wgi4qXG+eI2Krh6waEJ6JkXwQzIXIfWBBqE9n5GiYMl82TizxD9GbeCoAFQpNH3Hbt3PwfYtXF0quAvMA2XyDIoFmbGiqjsdHeLGlrxsChA86WgnsXeBf2Iqg1pVulS3Mk1HMGlmMRhju197V444mEaZ4sM/"
    "/ag8vaskjd2gjirwOvhUuZiNoE17QbLGdKcyGFSlpdtg8BVKvd2JuqBS/hmKQWchNcwlllQBOAQCGcYji4dArZb9bJGCHg1htLFYDVVrsRJazAN7WdJVHRj3sBbqCsVYjKxWyKNrE2qfzSENs4cnySkCuPsQzKKP5TvfkmC3c4N8MgVLafa6zGUDxAAm5/HVNfFlYuBK"
    "8jTHg1AZ6GV6AbpUvFYJyR5fhJnXFDOrZWFN5RgROGPosQYbC/KRf9gyeTyP0EKG47hSjlI4J3ydec++A4dX/igh/SJ/xrDb9vKpC/C7WuygbKK09EFsU8nNMtewHz3WMOkYUaSg0wyRivDo6lGMR0NEUVSWcv4CZgZaKhYa+m45YBsS7HS5KFd3LK+f6uWOpB+Ug29S"
    "uI/9Eaicn2XYxWUcJ596sK4Y8hXgXrDarV2YEbwfwfRXCuPxGA8u7UfUTgBju4B6mNppAVV1xhx6jpsmlb6dlQsynAAlR8KK6QL7ucnTsPfTERfrIW891OXEROacZyxyNxLXdxoFMEUELoPZnbBwtoaxOBy0ATKDBmNElzWwTnwqSN72lrCEoGI/8IcQfYcIGoqYEy7K"
    "1/uRvK6YFKAN0lGKKBJ8LcFcdtxEfIlegtc+9qiMRSvVgREkUA9nnq5c7CxOPtEKLuIJy0Xtt6FLtriblYWc9rhs2ddLLpLlfo496Exj1B8iaccYD0doJREeHRzFgZVj2LWwHaN0JORiqvukiLCyuATECq2oA00GrI09MSFdbLiMKUVyoPJsriShj8c2QBhRrpaaVX4T"
    "hCv2eH7PDAMqSUoOUZlFsLfB2FUvLW+KAaK4DR6nSIeDvCR0M/OC0BvHMY4tHsN9J/ahs9ACZ3lpvToMpeGW3xSpKjAYtqWk5EaxlyUoUXmIbLMo6x0upTdtUdWE5HU73ayV3ePQYbqz1D0TckHFPTSeAUhdtZy8MraO9jBZvmQ2MiBNpYUcTWq2Ye2qDQgZXUyWm45r"
    "+A8Qtlj3Gey+dIVMc5uUCLz32dSdxVzcwb6l49g4Nw0VRxbLKgirhTGDzE+YnO5U7u1UH4jjeresDGjsgYAkFpTQMSqZ3oYDpEW/FCTRCXQXR0kU9EVgyC9b638vLN1zWhr6y6uYntoIZkYrinF8uIR7jz+KXZtyBU0iJ6M0bBC1YjxZ7cYHv/NejLrTyDjLx1uK6ER1"
    "BQnjBnMYBtoR2ju3IVIqD1qS9Mg1oYvyv3mWYZhBUYTh/iPAiVUgjqrXDmk55ZCBX3qMNaNzYogrXnopUmP1vvwuKbNBO+nhzn3fxWPpErrxZrDOAAb0ib41yTVi/MwwoMRQOBnAKMsFNBYAM8RQZC3UDIRpiPL5hygZ7lK0vibZ4/yZnIBh75elYyhn2NwtMUnUkMFZ"
    "2uLS/HnMyrW3on+Qy7IvgqUigl5JMVweYzaZwo65TfV9Lrv4fuYlDFokAdkZDfMzTmcaxisJm5yh2VGmhCPQ5zJW4bTDJ2Zd+WmujcaG3hwumNqNex57BPHYjk0orjIhy3uBkHGxC9ieKuScUqwEcY7I0aninFtFBJfkKGVnhBpkaY7KoqtWaqUr8VndriICGu1crifP"
    "6ig4xuQO8Zfte21LnrjTwvLiMqY3L4CVXUiZAm4+cDeeecblFTGwcLEBQZHCcDzEb17z09g5nMEd992JVqttreMds958zEPrksmss6z83BErHD12AB/KHsWJngJlxgXZ4Sk1sJcXsAHiGOmx43jS0TlcfcazMTIZkiRBRCp/xhXPzLCuAn+BvZmcIWc0ztx1Ns4+9WwY"
    "GDvv5p3MhhntKMEt3/8eBi1ghhSyJMdMlwZAO855bQqkIlAcQSX2X8S2nKTYXg9FlI/jUIUjyQBiPK1VlrNbqGXQrpmDyMQhxsByOgFJaoKTfXrGuOQ5X3kwCIxxu66OyGCxCJSABnKOnwZMloE1wYz6eOKeJ2LPlpMcJQ3LV2uwAfSI5eSrOIQSKuFVyaB6SYiQ31vI"
    "VQaBaCj5Jn5qZ2dvAl2V6p9fueyH8MEbPonRlAFrhhlrEURyQmUpc1xosnujpgzb3s61SUjZebCS8iBa3aUllYwQxUIxtntGssPCxmktR3Fs5wwVVbNsRdpOwimnDAbKVauAiwkpyUYuAmEuTczgKrvL4alRf4jNO7cj7rRgjEESx/jGgbug09Sd8RIMdzBjZMZ45fNf"
    "hac+9hj6/VWHJU1UDRJrbUeCwMV4EOf0xQhDHuLm7/8bjjzyIGLHednF24hd1rzYHzD9Ea694Hl48ZOeh342RDtp2YCjKn/JCu4yVdYKlJ1NpZQdWyJgbmYGcZI4KhDFxjBpiq9+/3YkUx1Aa1CsYAZj6BN9UJyARhkQRUASAa0IJlFApOoZp3JTouJAdCWPirltry3P"
    "gcZPocJaytl4TYQ8ABTBu1gDFTu9gCRIrCUxG8tco1iUTY+ySSFek1xibDnNofP1ESkrm720iv/1qz8NFUXQWkOpKOezuTBRSCDFHfCvM9nDI4T114pdEi27tvWh2jNkQlHrKXt274ArIQvbkjfG4KnnXIa3vuR1+Ok3/z5Mq1MOB/u29ZYRjnqHxC/D8kVOIRZtCSir"
    "cLeEJbueA83g+mnoyALXcDGqAwOFwaCvJySDWsG8lo/aWGYx90cYXbqK1klzGJ9YRTdu4Y4Tj+DBI4/itK17kKYj+N52hfnGcDzA3MIcko51h/bn2wremPFIpZoNIlJoUw/8MCzwGqmSnyTTTKrr0wg3KPvN1GhwBGyYW0C73YaSJ33gubCDcxXDuYQkTtDudBDHSb7n"
    "qWTbt9sdPLJ/L75x4C5MnTwLkxqoJMbw8DL4wCrQaduAHUW2c6io7HcQSwDB1UsvqSyqOvRY8L/Kho0id/bA06iCcEBvHADlhvErRzCCagiXZJxWlYgotcilTlBA74RsNQylFLLRCEma4a1/8EZce/nV0MbkOvoNvoIBihP5ruzBSZiAKqprc43YdfmhUmaGG8T1ne97"
    "OBeH8C+gJsdCUCUjNjMaP/7CH8H03Cxe/de/hTRRiOK4KgmMnbFSZKfLYTjHufyWe8WnIee+BT68PNVC5EhHOdHnZRBCq6toqbPJsSoj+osONlTnPUGcclwTwUMlMgUbeJYeOYStJy9gkGboJF0cNsv4/IPfwhnbTymDCyA6VGJnxXGMudn5stPJAlmVM5DVGrD/VVBY"
    "ylbLoWtfALBOcxD304hFrQhxFKHd6WJhwwJ63V5lB+eVSTJrYGcgW1haCUWN4iW00Zhrd3HjbTfhUVrBlmgjsnQMMoTxg4ehDICW7ZpSrMBK2q/59DeqhmkoHyJXAUqA48MnJJikqkXNl5YcOoHTcZUX4RGuKbCxnUEQb3i9XIPkYmhSnaPEzApcjxiqnUAPh5hWLbz7"
    "r96CFzz92ci07U6XYDyU8HNAs8GEFC7w5pN9uzzy64SS3mAK4qjHKwIaJYlLGWXPIYd8eVR/XsBho1e248WIzsuuvh6dpIVXvvFXMUgIURRbDAWAHg2ghyML0oqTupZzys1OXpZTo/R4p5p/WjgUCp+vFJiBkB2z8l8Tzo3Zy17lg/YAeydgGgJGGQ5970Fsu+IsRFEM"
    "Zka728EnHv4WfvqylyBSMaRkEPnPw0k8ycPw6lbE1evkGI5iR53UbRiwy/sSnLIyI4hQymWU+FEp/ubxrVjyjIyTiTAKaV0WezPPvJWCHo3x/ttuQLx5A2A0EBP0aIjRgwcAkwH9vr0OrVx79JAGv8x+FYVrHZIlXa2jEhCfIo+L0CDbLVt1xOI9KCCixj6DOgzFkLfG"
    "iwSg27FlqGGoJIYe9bE5mcb73vAWXH3pk5BmKeIohiuOUpWklfUYBfa/pBKJw7Q2ytMsRlgOP5M4AXzpYPZ8/jjg+EwTqkOf+kABykOsrNzv9U9+Nj7wO2/Gy974a1hNNOIoQtrv47T2Rjz9vItgYNvOzuAwXNJi0YJXhfRGHjSqgVMGKHK0rrmwumJYkFVFlWMJicKQ"
    "qmHW0tRCUrLyiVE50oB8YxXs8iI9rrtmu11FY4ycfoTOMqRpiraKcXDlGB46eBidLZsw6K9iKu7g1sXv45a9d+KKU5+A4XhoAwxclyMC+QydchC46syiLEeLLlip0aTIZgw5Cxy1IeVAcHbK9pxIWpzQhSSLUMKUEsMFjMDSFIOF5hhVYzqybJzqTeE7d96GLy3eg9nt"
    "O6H7KSiOsPrAfpxsFnDq+VYiJU5ixEliy5uyqSIGXYisuF9ugabINjEsw17BkYUSuoQkgkuBy9kOo/JAZ/Hci+wtzyQMe9QYCK0sMRrmaI5xdRBVcUNgermJLWCVVpnY+l2SwvLqCr708B1YgUEcJ8j6fZw8uxEffMNbcekFT6yCVR1FqVc6ELp5QarTOpRJQ9/jgjgq"
    "sodGi58Auz0EpEn5U18+OUwita8SRxHSLMV1lz8d73vt3+Clr/8FjJIYNBjjFU95Fq6/4mlYGQ3KDMIRyeNiQFlqcOeFuDc0Ud3IKnsoan2/w1e+FoX8Psghn7IY0SlBcykuxxInkCaZcDJbziV1TPFfwzBGI80yZFojiiIsLy7iL+/7ELBrG0wfSAxhFAHvuPOzuOLU"
    "iyrwngS9YII2vtTNLEaOSKb5LNKIonTkgOuyw/mpxESKGEiGc3stWGnikuKpalld+TJUXV/p6FNmkCTaZSghhk6U4K1ffC8GczFmxgYpDBQipHcfxoV7zsPpZ52OSEVotVpIIqt5lUQJKLKHS6QUoihCFCkr2kfKfk3Zv0dRBKWK4NXgqSmyKrmeIBQeXK6Vi9M5ZOOA"
    "KreRs5fFyqd6jkLOBIPktVW8QG0M5ro9nPjAMr5+4H5kKyPsmduCj/7tf+D8M85BlmWlCS+HzHEdNyoBLQVgJfLd22sGHhJ7Y9dt2s6GVliArxha80ODZx4pLkr5Vu8BnfgKopCvXf1cEidIswzPufIavO+3/x6vfONrsRozpmenQUkCHg/sRpZwphzwFJR+A+QCgL4M"
    "ihF+cXB8rEgCkcUoi5OZ+FUkO/faaVs7Y3UmfztPLprqjsCVGml+0hYDw/mg7ygbY2ZmFrtWurj/0UPo9npI0xSz3Rl84sAtuPPRe3DuyWdiNB45biRcSNE6OlweCZdRx+cq1mSVVLK72UiUZOSN2dRIk9KXgYDJx7BPaq4PU5cAeJFddafw3bu/iw/c91VsOGsHsmEK"
    "FUcYHl3C7Alg82lbsDLsY6rdhdJ2HRhtA2NEEZQSGbKJoIjt14wCVGwzPGNHeVRkaThEdclnZ6wEyiZcKicfCxYIHCMPf4SMQJK5p1wSahncnG64TYCjXJivDAJGQgA2HVSw5TNnGkxA0m7DjFZx+qY9+MjfvgPnnH4W0ixDEsfeaA9Xey8wSgNvjzhNvIDBjRLjYvWx"
    "LFdAIbZlSngIkfyWpMzAvBJPcrOK0RzXKJRK8hoL8N7fsHEUIdMZnv/kZ+L9v/cPeNH/eg1a3Q42bdgIKIt5sYdhVeRKO26hmdGNYnSjBGOdWS0oB3zmSoAMlRW9omq01oW4hLCfYYeVXXB+fFyH5JyXp4pKcGU9JDNc58RZkwfXwlwUOZjcHw5gUo2nb7kAd975Fcw/"
    "5TysLo/QbrVwosX4l9s+iv978m86Br8S1pMGoWXcFjNw7E/k5u1zC4y7zPYi05KyxuxPRpTBKu+gEFemGCKDKPuaXI9QLJpCJF1YJMGQCFpr9JIO3vzJ92BxYwubWSEjjShRWLlzL56yYTfmZmaRZSk6cRvdVtvywKLIZk5KIYkixHGcZ1kx4kghUvnXYpFZ5VlWJDC4"
    "QhWj6Ho6bHeHIEquQoWjpAtPhbR6kDYw5tl7rkgLwR2MVIRYRYiVQgqDQTYqy1B33eYSznlDQRuN6XYHS0uL2DO3HZ9683tw2q5TkekMcRQJ2SUh20iymRJy82nwKAww4y0fyzWclWNPMsuKq85qoCsoa82m0RsvKCHMcQ9iz/WWfw7EKxu0rrv0aXjn6/4R/cVFtNot"
    "9Hq9XOrXPf0tm8GUN2kubuPe4WF87tjtuH15H5bNSBg/S61P9woVREAmlQdYdgh4zNJs1MXRfBNO8lwpinulcpJexbdCKeHLpsjJuGSAF+W10QZ6dQS9PASnI6zuPw5iRjzVhjYG891ZfHj/LfiRh27H5adeiMGwD5XjdcTkiDjL8pCERpcUxSDZDWZXgIrZb7uzNysp"
    "DlVye8Qy+Je8IM8goU5xYDGJIImU9vuGDaanZ3DzHbfgP7//JWw4+yRkoxRIFMarqzD3H8U9s4QH774RiBRUO0bUTkCJ1XKHIiCOoJIYqhXl/oyRHSNq2Z+zHo3Vv5SXhK6xihGSRq7iJ3nVhjUkMGJTliCYMwdbHj6snEaGzdxJ9IkIPY5wWnsBV287FxfsOAPL43Gu"
    "8FFNeZSO3+RSZ55+/mX4nz/zizZYZRmiKGqgmcilwECd/FOnPzUZVAjnKPaQF4f8nf9+XKXr63FC5prEqe+UUQPQJC8jMBTpvLP4gUhZctrLnv58HDl0ACdOHMNUd6rEAdyRGksqZDboqAj/vO8mvP3Yt7E47iPVxmZ0BmAyngp1wGUXAeNKQbazsYZqFlZly5gli8Bt"
    "UoSG01lyuQS/y9pyuZ5/VoInBeIUmGdgcwfH7t+LzZefheVDxxCnhFFC+MuvvwvvPfmsikxbBgSh/+7MefLEA6ZWuhXUDXj3gDnYQKDSIbsiy4rCpmpkAHV5Hxms/JLEE9ePNPAnH/wHjHdMYypjjAmgVozVrz8AHmQ4ONcHBgOg0wJaCZBFts6iKCceRYCKraysssYU"
    "SBLL1QJZAw8I6oKiulVSKVmMwPyegCGMoIWEpI7ISTM8sbRAHClmtzKNrw7vwbse/hpeftKl+LUrX5kbmWhhcCECRF6VLC8t43W/9JvYun07dI6VNgHgDi0BFGYG+FLJnkGF35DjGv2IqwRCfNi4tkH9ctDnTGCyLDL5zhm+LryYT3JUd5gc88qS0WwMSCn0elNOBuMO"
    "ldpu4HTcwh/f9VG85djN2JxMY2tnDv1sjNXRML9o5Sg0OBLLzEJLiJxOOjxVSWJyba/KEsDVlPe8tjxfvgAlgEQLO/cPZJF5sQEMJTBJnp3t2oIDtz+EDaeejChSSEcppqMOvnz8XvzbNz+En73qlVgdrFr7NNfLy3ENkoeRzLwYlSRNbeYhMDdYlkASxPdGmAoqS3G/"
    "Si1euM+E4ZMa6wPExWWlWYrNC5vwj+/+Z3z6+B3YdsZpSAcjUCvC+PAyRrc9Bprt2e5kEgFxDKY4X+fW9trEMaiTgFoxOFZAOwa1k4r57memUGWH0rGcY/dwqwUu41qfFUP0xbgZ1SCcwMB14HWJAdYEpRVUO4FRjP98+CY8dvgw/vbFv4wsiREpcrTSyk6tIuieRmby"
    "sawJeusSLgo5WPsuVbVqLOSy5Xvg+fRPS/iyJaHvO+dQGAIpHAUcMJrakk6wEtG2WpSmaiN7WkJlNCeyoxudjmP1JMbMoMGYa/fwkYdvxpv3fhk7NmwGM2NgxpiZmsLcdA9ZpqtGf03Ww52RNHLYyCe6S2nfWlFJZbcSDvXC92isxjeMyQdc5Xwau068zFZdgY0tIbQx"
    "0GkGPTuN/txRPPqFb2PndZdgpT8GgTA7O4c3ffdDeNrui3HWyadjOBpaI0yBq4SIKOxFZ3IyIPani6pmjdh4lWidcUFzk3cJnXJaConXxxHLsRP29y2Vw8SZ1pidmcPtd96GP/7i27Bw/m7o4bg8L1Zvuh+IY9BCD9SOQTNtUCu2pV8nQdRtIe62EU21oNqJzari3OpL"
    "ReXIUDEW5GTE0m+A/EBLDj5ZlfZy5tC4EkVlJlqHZkw5lE2OybB8XaUZqydWMVwdgDSj1ZrDlx++Df/2lY/il5/7aqyO+ojjxGuMWepGlmWWrkGqwsb8By6TjiasesIsMQfctkpM0vt5t2lXrdmYgvw4WjMYBUcDQ4TRJhq+RyUIYVllZ6C8yaY0TpBMdsrT2rc+8GVk"
    "mjEYjIB2hJ0bNoLGGfYfOYI0G+cluxxVyMsZRR4exW5DgOV576X8nvsIiwKfHS2vitMkV7Ypu69+N7wKcOy7LBiGHmcwmUZ02jYs3XAblu7fh84pW5AOx0gowvIU4Tdv+Ee872V/DhUnNlOlurV6UF9M+CQ6ySfnBATJH5LDyU4GVqjhC5VZU5hqsMjkZbmQd2vhmj27"
    "2nBVFmyMQdKKMV7p4+fe9gcYnbYBc0YhhUbUaWH1of1IHzwKOnUL0InB3RjoxKBWBCT2z+jEMAkBWkMPDTgqyKGCQC1AZDj2bXDKWZBLpHYPN+/2MgcGMKRxBde6ts6eNu5wP3KuWNJLYFhjfHgFOmNQaxrvvu1GvPSSa7F50xaoSJV2ZCrPuKIogs7aTle5lvJKTCr/"
    "bAUzoEYG9dgCjMAUjDe+UzNTFdMWqA0/+zUnmgmyHJjEbgpW7A8/+xHXtwgSagNSmjeKI7DRhUxWWdpRrj7Si2I8unwMtx79PuIoxomVVZzU2wwzSHHnffciiqMKCaFQeWEhyUIUjjkgLOaMm4jy1bNfCjvZU20MwvGr5jpXi0SVyATBL7O6TVyMKCmCOnMH9t90B/ac"
    "/HQgsZMDPdXB11Yfxu9/8h/x1y/5bfTHfZCpLxpucNmR4npcTCbkOJpD6iw3Xj7pL/SZPOc+W2KnRnCIfCv6iYutDIDEua8jATOdabzm//wibu4ew0nTuzAaDYFWhPFojOUb7wNtmAZiVT2fzMAoBVYW7zHDMSjTgMq9JyMLZTlMTL9dXqwPEwJIyFlbhVpnAQeQM5Pq"
    "5eHskdcDulGOVDy7dIZC/z9qW66iGYwBIhxdXsQd378f127cYje9sh3OQhM/iiKkrQwqgFtNSlRkoEKjYKccGyKnAcG+comYrSyhG+8lYwepn9SCFKeinLvzZ+Vq1vbGNM4J+WM7kvFcJBTWXjxPzU21cki450QqwuJoBaujAVSnY4czYfD9/Y/atrVSYNYgUmUntiK7"
    "wZGWgTcrKS3bXQFC9swv/OKQAqeUqrAj+UQV3BlIz3RA+XU9RSDFYEXgVCPevoDxI0dw6Iu3Y9vzL8VwcRkmM5hvz+Ltj30VJ332X/Eb1/0kVgeriDydJE+Eq5GwXmRZMceIMlOaP5DjJyACuTOCVNw7SwfQWeY6IHv+la77MznYatkVZoON85vwe3/7h3jnsW/gpPPO"
    "wrA/sJsgjrD42e+CV1OoU+bsSyS5u7NSoETZTmArLt2ekZulEkyuTeiVJyQZ5SSCuD+3S65ZsCOdXElhS4+iQmhSsVwS1DCiwy5XsKRC5PQQNlb+WRF4mEK1YmgY7D92BP3VPjrTXVCSWEWT3DauyLqaGm9r4dYyaBUyRQ5BNP9/48WCMPvA1bUnLy6o5hBKwQFyn7Va"
    "492ENN6D5aP82YANFFXuyUVtXUzplzV8rqNkF4+ymZc2iIkszpNpRETlOIIc4yoVtpSUvq1Yxi5/iDzGsasj1CD7VTYUSo5k5W/vmTDA4eGQ8LLiXDjOCEdhKHgCbAbxebuw9PB+nPjOQ0h6XXCmoVON+dkNeMOdH8S/3vBfmOpOQUt8gjxAmAL2S6JP16YEJw4cQQqr"
    "bcWdCKYTg1sRTEIwEUFHZE1IcyNSrQBNDKMA041ghivoRW2Y3CexNq8JBhrPaRs0tDHYuLAJb/iX/4PX3/5+nHT2mchWBjAGoHaC1dsfRvbdA1A75uzsYisCtSJQTEBClqLQUvbvEcAxYGLAKKswWu4KsmC4gad0W1qCuQ0VSXtx3J9EBgRA4JwMRk4OLtjvVHVPOU+x"
    "i6+z1KDOr61UWPVti9hYo438r2maoj9YRZqmZXVCSpVruTT0CMQQ1QTrSIE9uMPcKM1xXcs7AM3TNOxTg/wxIPZdcxhujwcItuVCw4kTOgdhioMo+0rnVG5kzEqCXMXRcJ11KoQyb70bbzJddh3Ajv4QuD7PyrIXDxIzYqEUmTwTCq7RQaRPsPw7eUM7DA8XE/dKkuMV"
    "WVFMKILqJYjO24VDX74d0UwX7a1z0KMxoDWmN23E79z6Thhm/PS1r8LqoA+FOjE2MAAoRl4yzLSn8XMnPxt/+q2/A3dGdsNEynKJMuNO/hfXbBjIdL6xMly180pcdeFTMNYpYjFTWDNqpfp1mZyztHFhM9709r/BH3zz37Hj0vOhh0O7HloJBnuPoP+Fe6B2bAA6icWq"
    "WgqIVRW4cjt6RGT/zcUfmTyiL7ujSYy60GL1dCo8p5J/9rAaz6bOVRVxVRrKWUF4Dki1xWccYJx9b4US77KOS+PxCFnWtWRZsadKYrD8hFyNs02uD605rxzLU96EzHorOSJqzO5KI1UWHYPamJCX+oWGdn2RPwc4k6RJqcsuRnycAiDgSEJENdRSErLtAuFc2gXCFBN1"
    "5jY1ZIwFNmEknOb+P4vuWc1pyEvf/aH8Qr+dAwdDBWu4n9MRAyB2T6ByCFYBUa51vm0OvLQFBz51M3a86EmIN3ShxykwBnob5vG6b70dS6tLeO31P4vBeAitMyiKJC/BKQHlPKsiQn+0il9+wU/hGadfjvseesDSkHKwl3Oxv6LMyUxWao8xG+gsQ0QxTtqxGxQrdHod"
    "RHHscOGc7JodRSpkWltpnN4M/vif/jf+93fei20Xnw8zHtsSrhVjfHwFyx+7DZjpgRd69gVaVk0UrQiUxFDtxILukVUbZUUVn0oMEpcNCuPxw3yrA5/+A+F+TZVbEIkSvAputd1UIVrMbsMGdXEGx43I6fNWJTbl/KxiKkFrG7gKccaC6mBpRLJDX1UiPiG6SSevhtn6"
    "NKdJRNIGDMyfi3R4WCHPQfaIYhyQQIXT9fFm0xz3Za40tQR1omKOUy1rKet8omBkLsZyClaXkfrX5HVZyktwNZvIlR1yzB8LaWMjoK9yhIQ4dAwItR52sjT2dL1t8K7ARoKnYe1oIZHnzViVBFAKiBkwGdTpW2FWRjjw8W9h+0ufDNWJkQ0zKAAzmzfjz+75IA4sH8Wf"
    "v+TXodpd9Ad9xDnYyn5GyOx4CRIUlgerOPWMszC/eQuWl5YcDStjqhLPFPLScqQpbxi02x1MT0+j1UrcjJQrbFHu1XGWYWZqBuPVPn7iz38Z7zj0dWy/8ByYwQgaDEpijFcGWPrIrTbl3D5n10snBrUSy6lqRVDtCNSKbQCLlAXXFQQPsJLllXR7iVmWQ7mCIuWsHXK7"
    "h5WpRtU5rhIjDnOrinc0VJqfOh3EclCanByLnXkqgUmZYqTMuBLNItv3ExY0TG+E9r7L45zsCy+DO9eYCR5nVsJHeVIS1440csFiCkTBmmYBUX362jsZWIjIlbU3VyMFATuPWpeBQ1RC4UtYir6x5/enPFGxwNBvfclwqTLgdDEF5KMgF7vkMLlmAVwTlXRLL84zKEf5"
    "oPyDAuUD3+HB37z8jQjcikCjFNG5JyO79SEc+Pg3seV5l0IlEXSagjPGwtateNvhm3D/Wx/DG1/06zh112lYWV0RWAW5gZg980+QHbaenkGv27UuypB2Zuxy1qT6AFsJ3mJOT6nIYdo7ZruEfK4S2LywBXd879v4mbf8AW7uHMdJ552FtD+ABqBaCbLhEEsfuxW8PAZO"
    "3WIfVS+xvKuWxdionRNDxSgOK7EpySWT+xmuZcKzU9izSEddfXsBystYXDU7A3iQh7wIlruj5WjkLjdOSV0pWwhD3vzQMIWct8CPJQxKAVah54nXnCV5Xo21ksufHJHxovYLUn66Gm8r9qwKVceNYzoUsoT3I24dOHWNKeCUWcH3DMau0E9SNdJCMvhURVzF26pm9Dgk"
    "lubbaLNsLZPnEWcBzmrAU4Co5GJQ7HDvKjDVlONA7Ni6OwRnj5xK8KzGiwNG5XmoIqg4BiWE+Im7oY3GwY9/C9lgDNVJwADGwzHmZjbgRnoMz3nnr+Pdn38fpttd9DpdZEY7DYrQCBEJkmscxWi12mgnbXRabbTbHXTEv91OB91OF71uF71uD71uF91OB+1WC1GkqqzF"
    "Q1nZMDKdYao3hZnOFP75ff+Ca//2Z/HdbRm279mF8XAAQxZgHy2v4sSHb4E5MgDt2WzvRSeByjlWaCuoTmKDVaxKzKooAwvVgzI1R6VhJUnPFUPdoxRITp/sjLJw8JZSUY0jSEDNb0vefyPGt9j9WSIv23dJMy7/y2fM8aT9jBpB3Ge8B+lKjURN/2coQJwKEfkrWKk+"
    "E4FSKwBBS3hv24bnztz6VqafPgdS+grKweJ6oGRIjQf3XlWhz1o2oQRoifxxGJn6C8Y2ezeQXKZ66fOWl25EAZkQDmf5lWyMEErI2cnsB0J2ZUPcLpTvnCLOU5ULzSUK1IlAnQjxE3bDGINDH/sW0uN9RN0W2DDGwzGmow6Wt7Tx8994M1795tfi7ofuxuzULOIkQaZ1"
    "XmaTe3IGF1WY1FGN9vgKmeQU+7KAYTZIdYZWu42N85tw+/e+gxf+2Y/hF7/0T8B5OzHfmcF4YKkL3EowPHACix+6BfrYEDh1MzjOy8BOArQtuE7tBNTOs6rYUhdY2SyfvUkjlgoJVK1X9mJS/Z7Ao7h4nKxAM1Ril+TjoIYdG7my0eMFHnmwVVgyO907FhUISXhGSIo3"
    "bnKuY9Psdwl9pWESTodSjy3QyCPJ4YIYypakUc8qTyFwI1n4ktVYudwk6Rr6eYk9sUsBkMPTQhFz8hC2N0cmLlqVrVT/stwRIxf2ZudPlaMxUDueZEARU++Vi7IAq7npvJEBqRptKHuDQjlTntal5X2hoOqJ/pWcuwJAbcV5ORQhOvsksCIc+tg3sfLgAagkBoORGo1Y"
    "R1jYvgMf0/fjunf+Jv74v96EY0cOY3ZmFu1WG6nW0Fq7HDEO96oqfiV5FA05feOqZBRrRWuDzGi02x1snFvAvkf34tf+/vfwnLf8Mr7cO4od556FODVIs9T+VhRj9Z69WPrgN4FVDdq9EZwooJsAnQTcyjlX7RjUiW2HMMrn0UiYVHPdLIQL3JFJVDrklHwlhUEMgBtp"
    "+sruz7l1nQDkZfbt6KGxS43hQOeMydmzlDMZimwMLOg6+ehbEbQKgwzDUtjP1OMWwfUGZA5rXoUCGrvkcA70vKy2HXmk6Wq6gIQarcpt1mK3XPUmrANgGwXrWHLLRSEar0i5QJyUMyDhSkOTckd2xP2lBpMbTKqFyIId7brh+ORW45SdVOAZzI4rbiUXXNAdOAy4Be8N"
    "qpETrxlecy/3Bl3J46hUnouy6ne14ZUicAK7YbsaOP9kmAcP4dhnvoPx+bsxe8FuqHYErRlmkGG+M4tsB/DXj30e7/vXr+KVp12FH7nyBTh91xkAMfqjPsbjNMf3K/VMkkAnuTm3010iV9TaGIZmDYDQSlqY7fbAmcad996Jf/3Cf+G/7v0SDm+IsfmCU9ADYzweABFy"
    "0qnB0tfvxugbD0JNTYG3zVrBhXYM5P9SK7ZZVTcfdi5LQHJ0yphIjNqIjKWQ2qGKcsAFRkoBjAaVnFPRNOAQ5OCSRdzDk6qg5eJCLqmWXLF7UbILgD/A0i8ks+WpSuVzI1eTy5/akM9PdMAppBYaiBLFujXCIdvRX5McSY/x7ydKcRCnapI0Dk2gky+6Bo9Yys5mdOfN"
    "uEYMq4vQowTRudwE5KXDIgNjFpvelWxxlU5zawWK3FM//3v5QJkq34HSRp48p13Oh5jzsrVUqSiEAe0gbSm1UhBghc47fJdb9lvoueCaIFARi4wmJxKSUpYxTQq6BZhphhpl4HO3Q/VaWLn5QYz2ncDCU89Fa8sM9DBFlmlQpLBxfiOOzWV4w6Ofwtve9Tk8Z8uFePE5"
    "1+DKsy/BhoWNAAijbIhxOraiiEJttgKWq9GKcpi8sF7LpZG77Q5aSQswjIOHD+BTX/40/vvWz+CG/d/FibkY8+dux1ZE0KMRUgIoiqDaCYb7TmDxy3dBP3QUavM8MN+1gaiViKzS/ld1Y1sSJqq83ypns4/ZIM0yQFt+GEUR4ihCjMh6UxY6ZVTJsJARnfhIWdzSUNUJ"
    "9YxFK0kiUznqFDEkVx8obNIUITdN5dztmeuTIF6GxgyHK1WnH7gVAuUBmr2aoSR5OnAIQXJUnXXpAOb1aolqtnVwPAPqYL5sSE3uMIrRHG+mz+dGNPEuyAMdAxmay8PyU3DfpogaikBpaU0Oj1zW4izGIXwDBIeMyKirpeYPvD9agasEXxgC5NNy5NuF29GOVpRA6vpK"
    "wH6UpdB6hISUvdyIctNWoBt3qkXt8LjEMKmy2Nl42C9M7yqbdHZPPQ1tXVAMA3EHvW4HiDNgMILZPgdihfT+Qzj0iVswfdmpmDltO6JOC1prpGmGGMCWhS0Yk8G7Fm/Huz/1NZz+mTlcs+eJeOrpF+PCk8/GSVt2oNObs2VW3jY3rKGF/m85lZC7T1vtXo2l5SXc/9h9"
    "+PaDd+KLd30dX953Bx6JV0Eb5zB3zk5sZYV0NEKKrDxAODM4fPs9SL/2AGisQDsXYKZaoCgC2onlWOX8KtWzKgxScC9WMcbQGK4uAQTMd2axub0Rs+1pZCbDseEiDo1WMRgvA602OknPVfQscrJcKcOMVy1hVouAkbShWNWMGYk98IkUMk6B/sBGRCPqOYqg2h2LH1I4"
    "a+cQ78/j0Emgnhg12WUni2LUhuJ92y2ENO5CcjLwzEFkbAHVAzC5fqWEsF2gvK6YvWHcoONNiKHaMNBcGhuEXHKkUBeLfCqgCFERjOWQg5/KmRoQzaVqJvtCC46eOeVSMJTX+ikBcxTh36/5VWyd21jatQOmtAVUXjtbs0EnbuPG+7+N37/9vehOzYC1zhei/f2xHuK8"
    "mW3426f/HOK8M6WNRqIS/Nutn8bbHrwRU90ZaJMFQjjKlnTHMN5+7a/h5LktVqu+4D4JJJ+gMEiH2L90HN/efx++8OCtuHN4APFUDy3dQhpnwKYpqOmTwUeWsfz1e7H6wH7MXXI65nZtgzEZ9DDFeJxBMbCxMw+zcw570xHecujreNveL2OB2zi1sxGnb9iBMzftxs7Z"
    "bdgyt4C5zhRaUVJO8GtjMMiGOLZ0AoeXjuP7x/bh+4v78b1je/Hw6iGciFJgqoPeKfPY3N0Kk2pkoxRjthSNSCXg1GD5vv1Y/fr3MLfSRmd6Iw5tTEGdtpWB6SY2UMWRBdl7CagXg5K4pGfEUYyVdAUzaONVZ16L68+9CpfuPAdbZjai3WrDsMFqfxWPnjiIL93/bbz7"
    "O5/F1w7eDZqZQSdOkBltM1m2jmBTGeOfn/86nLRxK7QxaEUxFpeX8GMfeiOOqhQRV8qZEvsj2Ew7y4Y4Z2Y7/u6HfgkqssFcG41WlOC93/ws/uGWDyOangMbnY+eeRiY81+qUQEInsBIWYkYYZDCLgEZEAKS9QkOn9dbjbvDVdooZX05WDY3EUMNiapIqjZ4lV6FYUm7"
    "dhYKBNws+dJACRMjLA2QudR9l3rVHr+KvaFHYsrlgLxBa9R5Y+QZQiA3fGSWAmFckTmJoMlgNunhRec8FUmrjcfzz/jQIvjeg8ATZ5zxFKUIur+Kn7vi2Xj6aZfUfm+HmsV/fuezyKYA0nCwKelskhmNaR3jOWc8CfPTc+u6pp8A0F9Zwfu/8zn83k3vwKNmGVPdDsaR"
    "AhICeguI5qdAdx/A0vtuxvFT57Bw5TmY2b4AZAZ6MEaWWppDl2JMz28ERRFSaNyW9vHNwZ3Q994KGmVIDNAyQKyRy/5aK7U0ZgyVho4UuBVBtVrobOigs3UbNsGaH+gsw3hlYLOhdoSICWaosfzwQazcdDfUo31cd+lV+NFXvgaPHdqH33nPG0EbWnbcptsqmeyqa4MV"
    "WpEwpVBYWTqGl57xFPzps38e5+080x1qMYyYgPZ8GwvzC7hwzzn4n099Gd77jU/gd7/wVjysB+i2ppCNrMS2joDZ7hSuv+BqzEzPigWgMf8vf4Ej8xnQbgl4wSUfgwi8soqfftJz8MwLnlJ7ZqdOb8c7b/wIFnu60L5wFkTll+IqQlSEZg9VpXpP3zeTkPmHCXgIhrSu"
    "SGhilUlKMDHwxz2ap1mcyf8JsFRcJ6964HkoaAW+VigZhToJFBi58Cn7DIPJEiPsWsN7lAPHETdvkTvjhaWDjntyyAfPRmNpuIINSQKtTT6qQPmgbpXCFu9vRfpjrAwHwNFVmHEGiivgc4gM22Y24iXnWHtvbUxp/mkA7Dn5FFy7cBY+snQfZqbnkGrtYWyVSy4TsJoO"
    "MMszZYkKMLTRYraywLoUDBidqSn86FUvxpN2X4jr3/XbeABLSLotsFLg/hA6Brafvht/ctWP4oNf/AS+8LFbcWxbG9NnnILZhXlEnQRQEQxbqyzKNKAZvaiF6V4HNEXQ+f3XZCy+lmteEQNtRWhTjqnlcjjMBmacIS2ggkghiiNoMLKVEZYfPoT+bQ8gOjzG03ZeiOt/"
    "7Xk4+9xzEUUxdm7bjrO/dibuSg8jme6BW8qK8bVjoBXbMk2pfDicMDx+HH/ylB/DH77wFwECxunY9d4k9wC0FuzADz/txXjKGRfjZf/+u/jW6qNoJVMwOrXqcTGhPx5giqeRZRniOMbKYAXZMAVGBtwJlXF2rWWssTC1AT908TOQaY1Mp3m5zNCGcdJJO/H8M6/Eux79"
    "GtT8fJ51SycneCu4TnQuSnR4rkSVCigcyhKXVCNec64v0EIU+nLcUB+Eg53TRFvnP8yQiqNwxLqCgUlYg3Og1qUgfR/B2rieIlK9w+Tg6xRwjQ+IoJVgp5hbFMPGJNw4ZN5qmGHIlGaZrCrjy0iFRS1aubDg7PSM/SzaWMkXEKJIIRuv4MVnXoft85vtLJyKBL3eoq0/"
    "den1+MjH/jfMzAaAs9KItXKmqQJlTFFuwmHK9DtO6n2TTGeIKcrHWlKcvvNUvO0Fv41nvPM3YWamEEUE02lDjzUoTnDxJRfjysuuwPfu/R4+/MVP4PNf/gb2jRaBbRswd8ZJ6GyfQzzfs1ymzMCk2jLcC32s3AGHVTViZYr+a8FNIyqlXAgKSA14nGG8tIrR4UWM9h5B"
    "tv8EWn2DFzzhKlz3I8/EqaecYg8LAO1WjO3btuF/PP2F+P0v/AvUhq4t6duWtlB0/KyYY4zByjH8+dN+Er93/c8j1RkIhCRO7L1RUT7sCxGsdBnMRuMRdm3fhY/81BvxrH95Lb43PIQ4SaxFXGY73/JfK/msAGVcZyZxBisVQY+X8YJzn4ndW0/GOLPD34UoIeX37iev"
    "fgne/S9fgtmYa8jLwXx2ePaugi1ChHSBI5V8Q/JYFuFAVR/m9+JDSK/MVWxqjiXkV1ouLaJJjooIiOs4eAWmKYQVG3giDaHS8XYllwXABlewL0hJpUCSVcu8pOyLdMElOf0luF6mAu5Fgqdgh3eZXCMKIkKapfjyLV/F6nA1F+bPXZy1sWzs7hS+/r1bbSmSVUCXJoN4"
    "zPjhM54mXq9QGLWWTIYZz3ri03DeDSfhrtEA3ajljE9AzHgVInDls1FWyvaTX/0sFpcW7SeNFE7dthOXnndxKUiXxDEyneEp512O5295Aj5w6NvoTs+CSQMLU1BRF3Mb5kEaOOecc3H6KafhlY++CF+9+Ru48dab8O0v3YWlLV0k81NobZ5DMt1FFMeI2y2oXtsC3zk2"
    "R5HNQMp50cwAGYMyG9h0liIbjpEdW0F6YAnjAyegjywDgzFUFINHQ7zk2pfi13/qF7E86ANsEEVdTPV6aHfa6ExP4VXPejH+7vaP4PBUhBbZ4WVW1ZgDQWGwegKvOOPp+L3rfx7jLEWUP1NtNJI4wWgwxDe+ezPufeQhRKRwwWln4tILL0WURBin49KBeW56DruWWrhj"
    "PATNt4AMhRiMW/IpysUfyT1sBT5ryJb9P3rRdS6RM8/8oRS0MXjKE67AxbO7ccvqEcStTgX8c5O2PtcMcgtzwmLG1qopGGew2xl8hOdTCVcrZBKrHR7eVAgsTtK98s1ofNs2ed/8EBEHyzxfRUHMHtXFubweBtUzoTIIFExxoiCNoZBPC7OG3fGH0NxTORNWtnzzKXXy"
    "FhFxrsrAFfu+xi63fxgOBvjJf/w9PDw+aG9XanJZElV1SpWC2jALNgbKWFut4XCAS+Z240m7LigDDNiKDZanutboTk3h1eddg9+7/b2INm+FScdN6Slqki/pGP/zH/8ADx9/FOh1gekWEEX4oTOfin/7pddjamqmLKEZwHNPuxwf2Pt1YEsMGrPNdqIE09PTmGpP4ejx"
    "I1imJZy0cydevuNkvPIFL8Mnv/Ap/K/3/x3SQYbxQ0dyySWCiiNEcx2o+R4QK6TjDFErtiMx7QhMQLY6hlkcAMdXrYWWZpilATBMi4UEiiPQxnlwTOiOZ/HCZz8Pmg1mZqbRaXXQ6/WQJDG6nS7iVgsLcwt40dlX4S0PfA7xhg1Wm6vgpjEhhcZ81MMbnvOLYFQegdoY"
    "JEmCT9z4afzuO96I249+HxhlgGaodgtX77kAf/mTv4MrnngZAOCe++/Fq//oF3DL4vcRnbML2hh3LMYhI8PBkkiqqZLVmkrHI1yy+Qw89YxLoLUu/Q0pikpt93GWot3t4lUXPwO3fP4tUDunYDITpmmyN2PgmZUSuxLPRnTTTTVuEZwscag1kl/VlDEFQHIOzCDXuIX+"
    "KncqOtchmnKD2zhI9qKwJpZDPXBePDCQxCQVT0W7U76Sq4vFgcGG6jRjyRvN+aDFzZcEu4ryW+r250GrJH2yx1wvRP7YpRYUzYCZbZsQL8yjqxLoVNtJ/67NLAwBlDJ4lJVD1kpF4GyE15z/DCRJC5nRiGDLyw98+sN4+pVXY2FuvgzcP3zZc/AXt74fQ9aI/SkYrrJW"
    "x2EYdjh4emoG0c4z0Nk0A24roJ3g/Q/chGu//CH8wnNfg3GWlRvqzO2nWImRhKCy3PU4s/hcr9MFNm7GzNQMVvt9rK6uYDga4xUveAU+e9/N+NKh2xH1ZsGrI/A4A8YZsoNL4GPL6HGMHa15rKycgCEGEoWk20Yv6aJtprG5tx33PfYQ9vdPQM30gNkW0M7daSIFxQrZ"
    "8RO46twn4eJzL8TIaEz1pjA3N4eDBw9i48ZN6PV6luumCK+6/Dq87VsfQzYvokXOsxoPlvCq85+PPVt3Ic1SRFEMozWSJMG7P/Cf+B9vei347C1onbsTpCKQttynG449gGv//Mfxkd9+M1qI8fL//fM4GA8Rn7UTphNZrpTxKAK18subQSzmPKMIWB3i1Rc+A61WG8PR"
    "EHEUg2LChz76YVz15Kdg08ZNFopgg5c97Xr8+Y3vwWKaleA7MxziJ1OgVKuIYB5EQq5lvUOslmV7vdIhLy5IPpYPA1FTFjbh7+RLVrFPQXLnGONGdIuEPJ5Xu/qlXkXBF2UeNUzwOHBhNY5CvqifzLoEgF5Pf3NyXkFM5arV74xFFNwmJRDqUt2Ba1438pEOsxEyo9GP"
    "FXSkgZhLdYVExYgSm6mQtkFvpMfY2l3Ay869FlKmbzAY4LXv+D946+aNeMbFV5Xux3t2noLnbr0Q7zvxXbRm58GcubNnLjvWyXCZbHdNdRMYw0jSCIOpWewbHq/KxzzQJVEMpLoatM7s6E3BQG632mgnLXS7PcxOz+TSMwle94qfw9f/6peRbUzAnRgwFseKNSE7cgw/"
    "8axX4sVPuw4Hjx5BNk6hswxxEmNqahpRFGPz/Ab80T+8Hvvv+RZoYRomskENygYsjhNg2MePPvel2LR5M0Y6Q687hfm5Dfi53/81/NbP/xqufOLlSNMxxuMxnnzhFbh821n4en8/OrPTyHJcwyhr2/XSc69x3GqiOMbDex/GL/y/PwZO24r2lk1WYZRg8S8NtLdvRX/j"
    "AC95x+9hfOwERlsixAsng9sKKlE1OaLwZK1Qq6CKXJzpMTZ2NuBlFz2jfB5KKaSjMX7nnX+FN22cxvOf/AxoY1Vi9+w+BS8898l4x4M3IprdgEynwrXbm6IohjVqiYfc6Owo/Do+SQIKqpO23cOdAkwCpyxtMp/xuZsej0uWm460kmj5F9LSKjy7PGFeCFzTsCF/ZCDU"
    "kiTK9Xuqafhq3JDcAdK6U1bFxSp7u64yRPkwjCnlO6icjqdSO6hwVnYDQf5ATV3uQymF06a2Y4+ax2nxPM5IFnBGsgGnYg6npzPojIqD1556EQjZyjKee/ITsH1uM7SpsIObvv01PHzgAXzizpuEKL+92B+/7HmgxT4MqvS9GIKtZFo8LJWAVYyhWymW1QireoATRw6i"
    "s2LwoguutidSFJVdse/vfwRYHiBO85IhL8uiSEGpCERW9qXdbqM3PYWNGzchbiW45qqn44cvew5MfwXxxhlgroNoQw9Zi3HW7nPww9e9BO3eFPbsOgW79+zBybt2Yev2bZjbMI/Z+Xn0ZmeAqRYw1wZNtUC9FqjXBk23oWa60NOEJ1xyMV7yrBeiPdXD7OwcZmdncc+9"
    "d+Mjd96AT37vprLTq1mj3evip69+CTgb2fnBvMxIswwL6OHMzbtywiqV3eF3ffa/sdheRbJ9IzRyy7TiYFWEjA2SuI2VDW2kezYh3rYRpmctv6yag6mpJITGWv1vKAA8WMF1p1yInZt3INUZAAsRfP22b+KeI/fho9/5YjV6lb/Ojz7l+aB+Bl1oHLmiJFX2EVR68L4v"
    "7OmIxFA0c2OHMCCZ4DTdZPlZ06oj/9rqag9yblDywkgEY3/UC9SEYdWCEwlGqmd6iIBVPTVQIEj4zVB1AhL5s0sBBi9XSojM/rwWCcyqcumpSkfRcVPkcJycNFtMtFO+2Du9Hj78+/9sR1FQ0SfGJkNbxfild/8l3rb/JkzNzSPTKXSkQAz88DnX1DrM7/vKp4A9m/DJ"
    "h2/Fn6ysYGZ6unxY11z4ZJz72ZNx16iPThKXIClNam5EEa47+0nYO5shmUqgtcamrT38zKUvwGWnX5QrSkbItAYR4Ybbv2YpBxnKMkFFNkhB2WkzVVqwK6RpiqleD3ES4Y9+5jfw8T+8FcdmIqhxN5dGTvE7P/Tz2LN7N5YHfSSRNTdgYzAaj8p1u2l+AVMbZoGNHdCG"
    "jqVHRApIIkTdNrTp42ee/QpMz89jOBrYBqqK8N5PfxBZ1+D9d3wJv7n0k+hNTcGwfQ4vftJ1+JOvvROPcoq4IAuPRtjc2YKFmbkKz8zLuJvuuBm0aQ7oRHYkR1WHXiFpzJoRwao6sOJSAouK7lqhP9U480qeiYiVEaKM8ZqLnye+Zl/h3Z/4b1Crg0989yYcPHgAmzdv"
    "sVmW0bjqgitxwewu3N4/ijhpQbNwI/JchOUQfJmV5M7S5AQaK1gvx3hIEiK4mV5Zd1vKrbn8NZljTUzeOJxHaSBPdTg8t1xf+yp0340z3kLBMYC6DAvCbySyJwUlZs78ureRuBEYjapS3WptmJLlXl5wobII41iEF3hVBY5yTemBxcnUarfQ7XYx1ZtCr9uzf+700Ol2"
    "MbuigYNL1sgShBGPcMHWPbhqzxOhjT3d4yjGsaNH8ZH7voHk9J241xzGDffdUnJ/MqPR7fXwmgufCbO4aGWFM+MQXx3lILbyOUmc4J9f+3p84qffiA+/6i/xsR/5P3j7j/wxnnLmJSXnK81SxFGEBx95CO+75TNQWzeV5q3VRDw5m27/gf24487vIk4SECmkaYZTTjsD"
    "v/uSn4IZ9NGam4U2Qzzvoqfh1c95KbozM9i6eSs2bdqETrsNzYxdO3djy5Zt2LhpMzZsWLDdxNk2aKELNd9FNNdBNN1G1mKctOkkvPLy5+RdzRba7TaG/T7e+9VPQG3dgbseewg33HZT2aXNtMbCxk14+RlXwRw6gYiVXbTaYLY3hal210l90uEQh48cAXe7VmU0KWb5"
    "JEZoDSgKddRSrQEQ3g4UKAOLnSSDCOXrQUEPB3jiptPx9LMvz4F7oJW0cOTIQXzka18AzW/C3iMH8OlbvwQV2c5ulmXo9Lp41UXXAMcXgSh25I9Kt+ha1gVH4khWERTgPRip+UYVQ58aMSfPdKIWrysbL9VoikrBmWUfw+KA2QWhUmVxXoBCHSqaEFQ8/zRmDtb4TfT/"
    "JlZrvRj1Jtr9VxOpM7OnKQTxlLly3WVTWYiTY4wheE1Zhkzbf7XRyHSGNEuR6cxu/lEGTjUUFEw2xKvPudYK4mld4lQfvvHj2N8/gM6GaZjZCO/63udqluYvv/RZmDUtjNLUBlZ57+AOohYPXWtrMa7ZIGONcZZaF998YSRxgtXlZfzsX/8WTkwptGanrBZUEag8eVsi"
    "wlJ/BX/xtr9BltpGQhK3oI3B/3zu/8D53V0Y91fQGhH+8Pk/i6TTwcz0LLq9KczNL+Ct73snbrnrdkzPzGJ6ehazs3NIul37WVoJaKYDzLTAPeu0bPqruH7Ppdg0tzEfkrbl0o3fuQl3LD+MaMsCzEyE99z+ufwjlwZYePXlz0d70SBNcwygk2AcsR1sFmWLimJ0p6ZK"
    "QmmRHVQabAhkGbkqiKnca5oOZkLYPAFKAf0BfuSJz0a73YHWWekC9blvfhn7cAJqyyyw0MZ777gRAKw5BFkfxZdf/XzMoGtJzPmYTl2QD7UBaebQyJxIKqVkc/GxjVlzjgWCIsSBYBJy1AkaKa8lu+wFYElTUhKkCjmzNr6plwY65a4YzGUpFEbscrn8lmhAMrYsO7lu"
    "3CDBe1ViVlUAcgBKdvWGirmqIhMrAoFnZQpmIEkSJHGCOIoRqQhxFKPb7iCOYrR7XWsZxcBwNMKCmsUPX/CsHD+ypZXONP77cx9FO+mgMzSYpx6+cs8tuP/RB5HEcdl2P2XHHjxj63nIFhcdU0syDPgSyflHj6KoMsaENcmMoghgYDga4iu33IRrXvtyfP7gd9Hes8OO"
    "suS1AxkrOwJP3GJmagofv/tr+OhNX0ASJ+Vh052awp9c91PQ9z6EV118Ha44+4kYpymUUmi12ti3/zG88V//Hq3pnk06IoU4jqsNoU0OslsbsCwiqJTxsvOuLkdlClz0v2/4JNrzM+gZQndqGl9+8BY88tgjVn+eGWma4qIzzsfVJ52LbNy3w87tBEcHK1jqr5QdZs0G"
    "USvBE845F+C0pJc4etRCHdT69VnVhqKkqmehfmOGqva/qdIebTJs6M3hZRddWzrJqCiCMQYfvOFT6MzNoxfFmJpewC377sP3H3ukpL1kWYrT95yB5555GXhxCVEU5Zcg/A/Yo7PLhr2jk+9hwwTP6h6eBLhL33BnDykceCBMVDxvRgeY9+KKNFYNZnVechZLTSoOsdFD"
    "LFXv69Lip8KjqHYKSc7IRGPGoO2y4yGbk0AD+o7FlzSV7N7C643Y0XmogPkiiBpX8UGRwng8xP/6uzdgX/8oWp0OTKqtEw0ROr0OPr/3OxYbUQS9uITnnvsM7NywDZnWliFPNkP729e9HoYISSuGUoTxeIxNcxvBJieBGgMo4DVPeDY++IGvAZs3AfkoCee2ZVJgtKA4"
    "HDx0EIPBKjYvbLZZhLgZR44cwYv+9KdwbGuC9pmngDq5gkG5xUylZifui2KANs3iz7/0HrzgymsQtxM77K0zvPDpz8V1H3safvGpL6tkpxlIIoU3/sf/w3K8YoO439GMVekCzgSoWCEdDXHhyWfiKedcnjv4VMPzf/gTr8Xv6F8G57pZDIMNcxtslgLAGA1qd/ATV70I"
    "n/nE68GtGIkGDiwexYMHHsGmDTZji8gGgB952ovx99/9pHUAynLFUVWk7Jb7p1ox0tEqkGWI2jPAWNufiaTKXjD5d/8xQBRHSEeLuP6sa7F7606MxkNEKiqbU2/69T/BX2Rjq0cYxWBmbJrfgCxLc54gAzHw6iufi/d+7yswCzkuVeBTtRLVBd/Z01Irs0XmeiJE7Ha6"
    "qHlEhyaM7JGfgPiOWw3NuJAaBQVeIzehYHcIcQKOFLqImmuGY/nDwta9CfBqFu5zp8Qlnd9VKXWiuKlKv0LZk0pVRXfcQE7Vl7Nu8v2VNVz4j5s/iUdxFIhbljhaPNuEgE1zSKY2I4vsg331+c+ozt/83sRxjNN3n9ZQTed3Jg9az77kapx14y7cxyO0ogic5RmgdmkN"
    "RIThcIiXvPbHcPsj9+DaS67CB97wNkvEzDuNJ590Ml7/k7+Ln/3U/4WasealLp2kznAusK3ZuRl8e/wg3v31j+PHn/5SjLNxObb0X3/8T+j1psrXi+MY37vre3jrTR8EPeGUnHmO8p4DsPN+ibLqGAaW1pCN8JqnPBfdbhfD8RCxigHWgIqwc8dJ9Tigddn1i6IYhhnP"
    "v+wZOOPGf8f96QBdE6PfX8Wnv/sVXHHOxdZ4M4qhtcYVF12OX7v0pfibb/wXWttPQhQpG7TyLrchQrp8GD964fXY3JrBX3/lP0GdOSQqQmZMzmQ31fqTmK/fRTT5RAMrvOay5zrPunAgPznw+XQOMRT7KdMZrr30aTj7Aztw93AFcR7YZMuohMyJHLkhDxjKFVGNuzfY"
    "VToJU9Ex0YKLQ+VfoAprCk41Eil7MlWOgGcBulNFPqt0ltil/QeAMkwijeUdEpc6EnaNbZytDKFZ7Anoy9atzlv1RqTFhj1Rbe+Blt5tfmldfa65hY2ITzkFnbNOQ/vcM9C+6Gx0nnAmOmefjtbWzYiiCCMzxrnbT8M1Z14GBvLUnnOekxWMG41HGA4HGI2GSLPUaisV"
    "HDNmpDpDb2Yar77gGpjFJZsdFEaJgidTLjRjcESvYPWMBXx0+Ta8/QvvR6QiaLaAe2Y0fub6H8UrzngqBquLiKIEnGtlMQdSdTlUrg1owzT+9KZ348ixI7nDjc3F5+Y32Nk6VIoZf/zWN2K5l4E3TkPFKocUrU6WHXImG6TyfZ+lKRa6G/DDlz0XDEZUDgHbkac0TTEa"
    "DzEaDzEej+1/s7GVbM67uVprzMzO4VWnXAXefwwYGVDUwX/e+jkMVlYQR0kZXNIswxte89v4pctfjvGx4xgOTmCUDTDOVjHqLyI9ehj/4+zn4F9e/nt408t/A2+9/rcwvTrCeNi3zSLDdXxFzvQV8515ANErq3jChlNx9VmXQxtdaoJprZFlKUbjMYajEYajIYajIQaD"
    "PsbjsaXB5K3lNE0xPTuLV136LODEEkjF8Kn1BUWIJCudVK1JxsZUwRXsUocmyLrD5yg24cc+f9MH3dfwHPTJqZLLJikQSi461zCAalgWN+jUsGdJXaaATbb1zLVAx8E5Jl9Iv5ozJ2ZHvoIlV4RdkJ+l04kkY/pFJYcDqRmNkWWptV1XxorVKYaJrNU4MgYfX8IrTnsy"
    "Ou2OHaQtpstji3slcYx2q41Op4t2u4MkTqzdVR7YmLl0Qn71pc/BzDJhNBzZzCoiq//kY3fMiFsJaLaH1lk78UffeDf27t9rg5bRthEWEf7+Nb+P3WYW49EIUd5NKzYYkz/dmn9mY6A4xkMnHsObPv5viPMREqWotJlnBtqtNm786hfx/m98Cq1NW0pekz+ywvmGZ0WI"
    "SIGXlvHC067EjgVbPltsCWi12mglLSRJgnarg3arg1arhXarg07b3jtXypHx8iufg+6SwWiUotXu4q6Vx/DWL/43IqVKqzCwAceEv//5P8JNv/hP+JXzXoDrFs7G9TueiN+68uX4zM/+X/zHa/4UioBROsJPPesV+MIv/T2eOLsTPBzlKq7FrCjVOsnMBohs+agUAcsr"
    "eOW5T7OTDpkdvjZGo9Pp2jXQaqHTblcOQ90eut0eOu1Oef/iKAIDeOVTnoveOIHOjIBYqDx8m+SobWPJeNk8501P4wpdNoWswhl6UpdPMN9DqsTsj+SEwPkST/PNk6sYYYxxjVTdERuquWSUw4he6kfrkJ9x6lo/6JUW9OzY0Us5F/IzNa7A+NLlR/CrCkKmq+LsasuX"
    "qhO+QYYXjM1I28n5SLknQb54x6wxTR284rxry2s1zIiiCP/63/+BT9x8A3oz09CcBzdjAVgDg+2zW/C/f+F30G63y6zk1F2n4eqZ0/Gxw3ehvXETxmSs0kF+7YZNbkLAQCcGzxJacQv71CJ+54N/j3f9/BtgDFvZFq2xZdMWvOHan8GrPvQXSDZvBnRqP7fiEjcqhnjL"
    "O2gMeHGIpDWFN9/yEfzU038Ip+08BVprd7peG/zJe/4RZssU4nYL4/FyObBLhfIEADNMgdQ2aLKIoMaMH73wOmewN4pjfOCTH8a7PvE+dLo9sCJQQjDaWIliAjZNz+P1v/aH6HZ7YDYYp2Ocd8a5ePrOJ+CTx+9EMjeHeOsC/teX3o4nn/IEXHLeE9EfrCKJk5Lm8aTz"
    "L8WTzr8UnGagKC7JPcPRqDSBHoxHuPTsi/DUmdPx7UfvRWvrRiCDDUqy4yxpDfnwd8YGM9NzeOlF19gSLy/d2q02/vVdb8cnvvF5dGZnYLS238sVL9I0xa4tO/CXv/FHSFp2cmE8HuPsU8/ENbvPx8cP34Fkfs5mYQhMfnipEsHrLXiE0QIvZF6DODqpqx/gU4Xs6Uus"
    "uylOeH6FcvBZZlhxrZj05ghrnoihIPSD/OML8flpI4XpDcyhq5KlYX7umlLtp8aal4bQVD1NqNh29UqNU2Y7na8F9cH6tpcvZ8HVZTzrzMtx9o5TMc4yREpBKcJg0MeffeDN+H7/ADA/XV12iUkRsDzA9ddeh6df9CRLTjUMihO8+vLr8LH3fhO8sBkYa6BdtaSZuZq+"
    "jyKgRdCs0evN4D3f/xpe+OWP4pVXvxBpliEihVE6wiue+nx8+LYv4T2P3ITuhvmS9WzJkeyYeBg2MIMUSFtodVpYbK/gzz73Nvz7T/w5tNaIFCHTBp12B+/71Adxw75vIzljJ3RLAStZ6bRT5kDM4LEGhnY2LkOKy3edg6vOuARplpZ2DCbTeP0H34Jvff9WoDtta8d2"
    "ZNdFamxJudrHC5/5PDzziquhMwOjDVQ3wk9e/WJ88r+/A92LQUZjcV7hJW/+dXzwp9+ESy66BMPREARCHEUYjYclT41Yl+tckR1Ij1sJulGCv/6Pf8Lfff6diM/cbTM1rSuTiZwAajg36jUAMoNIxdBmEc877yqccfKpJTYXRTGGgwH+8n1vxv3pPiDu2ueqqowUEQH3"
    "ZXjRc1+Ap138ZOh0BK010GrhNVe/AB9/xy3gBWVVbd2yoGaVzB5DXFZCUszPcfZpYhWRi087o2E+pclPaJoSl1A8EAkNI/CxAEFrcIYh6y3ImlxEwwVxSEOLJ5P/aULgC45Fs8upMqZi7Ra+8lyaT/qkV1PnceVAaQRlh1JBlqpB1qRCxXGltSSxMV2YSAA/c8n15QCu"
    "ySWMv/DNL+Hh4WF0zj8L7TN3o3XWbrTP3oPOeaegc8GpmDrnVKizT8L7vndjHrDzgMmM5z7pmTht7iQMsyFUyqChLlNl65psr48ytlkbCKw1oo0z+K0vvw37j+xHEscwlCtEKIW/fuVrsTuew1jlA9z5e0ZRVElGF4t8bE/xTAHtTRvxnvtvxJdv/zrarTaYFNrtNpaX"
    "l/G/3vk3oO1zoJnEssgTZeVWRNZGRIjiJC9FAYxH+MkrX4BWu11OECRxgptvvwXfeeQutC85F90L96B73inonrkbnbN3o3X+Keidswfqot14/31ftdeoyGaRRuO5V1yLczfuRmpGYGYk1MLeDYxn/dXP4R3vfyc6SQftdhsqL60pZ6VrnYGNAZGlZnS7PfQXV/Arf/Zb"
    "+I3/eAPU6SeBe4kd6lZ2XpUKD8jIaqWpKLLBp5/BpAYqI/zEZdfbn1M2k1ZK4cvfvAkP6iNonXcmWqftRHLWbiRn7UFy1i7E5+5G58LToM7bhv+85TOln0CSxNBs8LwnPQtnze1E1u9DGQ4rpQhsluC6Oxf4FTsEaa79Kia8LoU6fSK7WsPe0BvpW4d4H9UFEZQLNHDY"
    "gzCAM4UkJeDIUjiaqRV9AN57iXkkrEUf5aahU7izdsLUlLiQ0TBlO5hZGqhWgPw4S7Gysoxxf4DB8gpGq32MVlaRJXbAuOTB5F0hZYDxcIjzpnbgydvOwWgwRNofYNQfYLQ6wFs+8h7wbAfoxTAwMNAW/zIamjUyyoDZHj6095vYu+8RZMMhBisrWFo8jrneDF5ywVUw"
    "4yFUO8F4nGJx8QTG/QGGq6sY94cY9QfIRhkwzKx0DwMtJNjLS/iN9/81+ovLGK6sYrQ6wMrSIrZt2oo/eOqPQK/0LSY21hiPxxgM+kgHQ/uzgwGWFxeR5mUoR1aXLm1F+MNPvRWLR49heXER4/4Qf/Ov/4B79t2PZMOcvYURAbNtDNMhzGiMweoqhqt9ZKMxsrYCei2M"
    "+yNsxCyevecypIMR9HCM4WofZpzi3Z/9INKOfV9NBjpiaBgbVDhDxhrodvHxh76Jhx9+CHo4xmi1j8HKKqY6U3jhnsuBxWXbcR2kSKiF47um8GPv/VM85zd/BB/+7Mdw9NBhtBPrSG1dqafQ7XTRihPse+wxvOW9b8cVP3M9/v6z70K0axuok4DJ2OAeKWRk0F9dxXgw"
    "xGjFPotjR49iOBgBGsiWV3Hm1DY8aff5GK72kfaHGKysYtwf4D++8EGYbmzLIzIwiqFhzTuM0UjHIzC18JG7voq9ex8GxilGq6voLy1jqtvDc069GDi+bCVpZDPJM4xgOYQtBAw4bw7ILEt2tENwiJ8ocGDOWBJJ2aM/lH6Gkrvl8bh4Qgwgj9BLpkhPGHV1UI8E1uSc"
    "EWxfSqV6U3QKOJwNekPWxZghsXWpMTpDf7ACnWVlQCxuujEGSZTg3oOP4Cnv/gOMWwqRAea2bcDSoeM2a1BUk1uW72zHxGxaduowQefoEHqQQrHCONZ4EEvA7i1QraimI2+0wTRHOPmoVdC0Wrga2SjD/UcPgE/fgmjLLApfQoehkf8h4wwnLQGzywZ6aEAjjTiJcCga"
    "4vCeWcTTHWAwxs5DBt2VMbjXRqQUBqMhHjx+CNEpW6DmunZBaVsGZ6MhTllK0FrVMCMNihWiqQT9bIiHehrx5jlgnIIIOKXfQnJ8aBnVhrA67OPh1gDxKdtAynaYECtok2LnIUarb8Ck8PDh/dAbu4h3bLBGpkqBE8K2YYwNB1PLlB8aQDEeyI4i27EBqpUgZmD3uI1o"
    "eQQ2BAxs6Xpfehij7bOIp7tWTkgV4oWmwmLyoLFzv8H0CW214rstxEmE/UtHcXghhtrQAzSDtH0NShTSQ0eAx5ZxUmsB5598Gs7atgcz3WmwMThx4gTuOvAg7jjwEA6nx4ENM0jm5qFbloqBCKWiLBFjz6CNzmoGnRooDfQHfTw8XgTt2QJuEXq9FvasJDDHhzCDFDRm"
    "cMS4f3QEvG0DaK5XNYRK1Y1qtpbTFLtXE0z3c/wuhxgOrC7i6EIMmu+5Bqf+yZ4o8IkBaN8SVK8DvbKKX3vSS/DsJz4ZSa+NuZlZTE1NodVKoFSEKI4xGPSxecs2bNy42aFWkJ+4yDlBJw6E1TgnzsP6laefBJFPiGUx/ByQMnYuYy2Nm6b6lEVqx2sN3zgeqy5ulcdV"
    "Y6robFANklYdEVXdWK5KRChXMqgcxigslvLT6v72AJhdBRKT4yYRqDcHBSrLPxY+cARgiVPc2RsAamwzF2ZgbID5TVDTbRsMhdwxSBCJtUZECo/OpIBZtaLVcWaveaqNOCJwloEiwoNzKaD6QDK2B0EPiDdsBLViW24V56Y2iDsd3N8eA50+MND2GlrWgCJOukCaWvxK"
    "KdzTWQF6q1ZvJWOgDUQz84ASZNpMI4ojPDw/tO8PAm3cjCjJda2MzTrJEB6Nh3h0Qx8YaiDKgFQDc1NI2vlsota4O1kGpoYWyGYrpIcts4hnekJFQHBwiuw41YgIeGRqDGR9a57aUvbzzSuodmJfqyAMGwaPM7QWNoI3LOCx5RU8dvw2fPqxbwGZsT+bMdBpAwtTSOZ2"
    "gZPISs8U2mom5zvl41IPxEtAMrTBTANoAyreAMS2YFkdpbhT9YHOID+t82HruTmodst+SbHVUmNyJLFh7CjRw90hkA1KwwkAwIYIqtcq124VrMihJbHHUocsJOCPJAn+Ik/Ym34ZVwQu4Zoj7Axr6lJ+AkReA44EoZzl5AtJuzDKbb489S7luWKggW8RjKS+XOoaGZkP"
    "0lnbPeX5pHllnKitjTFlplXZYzMynYpIzahWYE63Y8ueLoXH85+LVQLasACerciapugiCpNMiQVERKCpaWCGqnuWE1FtA8DUxBBJjBuxse+LDRvyId588eTZKTINJkLS7VhlUZ0vi9zfkHU1JM3F18FIkg54oWMzDVM5WhfjI4UOeqvdBTZ18+vNLd3zGTqOco85w0DK"
    "SKIOMNetnkExRGyqMYvEKGB6DtxlYNrYjU6c61UBiCLEFIM6PRtoZvP1UpiLkpAeyA8TI/FMA8SdDjDVK70HYWCvn5zdWl6mzjQARjQ9DZqesaKOxdpgANoehlqo45bdNANhhsqIog4w36vUJIXBBjFDZQBFLWC+U5pyFCoNhXpEgSazI3FUVQ8qboM2dqsh9TywsfGo"
    "Oj79qMBzjUeLhKkaNQUvy9hS13j7zWcBwNPRIllFEcKM9yaepsS7AiM5ruxMPfTEDVQ4Z+aP/DRN5SdaiKkqo2jgwmuR1jNkrA9PW5kX47Bzc7C9WMx5CkukQJkBa4PR8gCqFUEPUrsTVBFgjBjVIUeBURVtXqMFu5arqF+OZ3iNhIL9bISSWt5RZPH5fPFCZy4t084J"
    "U0qFFMGAit/XOTk23wjFYFXRDFJiAj/LasPhcri7KL8NmyoIFp/RU/+v5kMrvbGSzErCYLaYIBml9jpMZQRSdn0Kww5tux2kIGzZhYm7MdUGlOuIqmdPhiqia4lBUMU/IqffAhTORMylhj8VEsvC8IEFtltYwTlXkm92YjkAXEg1M4zOs1q/+67gdoulAomQc+LyglEp"
    "RxRD2n6jTCYcnM9rLg1yriKXZF2jjRCxtS5OTAQqCMwNyYcv2Fdw7Cu3aA4Em6IKEWq/+dpWTfPJPj4WkGaOXcthDzwPlIEs5gZDSoO8husO1ZxyinSSJnQpTC4fY0qukpwuH6cp5tvTWFBt7B+vIoJCemAJaroNmmrbYKB15fYhAXtiYUlOssWSL1IqeTqcz5051mmF"
    "xpZsxxSfW8lTo9iw5HtX27/nc4clu5fIlYmt9BSsVpNwLwK5/gP2FJbt7DwGOR5xxYGeB+QoFzmU61+W1qoIWtUpXrbj86/bTS7UP4uALS6ymIEsMkGwsplV+XmqiMGFhbuEFopnBVcTrbi2KunIO73FT8rpBgIMi2ddZJWeYi6LBIyJvM6VbL9b15syY3ZNNWWLq7zH"
    "pWSNIAoWB450nwmPyJEt56X+eXFJrTbo2CrMsVVgpmP3axRhtt3FOBujrTsw2sAYu4dMvqeN4brVvd8oE+MxXARYds833/ew4jo2+BzyGgb13sxk7Ix3e+M17DHSQzKoHJq0Ds0TydcQXDsGhTkfIhtLtUaat5/thjSiBmekWmPj9ByeuLAL+x+6Bao9hUxF0A8fAXUS"
    "YNam1qQssU9KiVAx+a7INZ+kqpVbunpIzgoJG3KZTpfOt1wKw8GxLCPHDbjKxlANj5MXBD0tI3LikXfCgkVVJBQu8tK/kJWhPAM0xI4VV8VdI/gyiaXQYTkZIdvaytXgz0tKZ3YdAEgLvSYxDE+e/kZeRjvqAiQGbIXzceEOU3hNVnstf06m+BkWemzy/7Srew5X+ZLk"
    "YCu7mZ5D1GRTu+9S9dNLSMBG0gT88TcSUxymjAqOflyxhvIDigyApRWYfceBVpKPq2XY3J3BltkFDMZD9MwUUp0i1bGdOsibUuN0nHevc4kfI+ZWQ6M3ovJyjGRkiSp4VBSaNQxMuwQTF/GlmMWmbYroTuBybLTyMsqb0K5OVhc4C3kZhi5Ms7FjKvnPTakWQIkFgcG2"
    "a1NiAoxUZehFLfzKxc/D5x+8FZliqIhgNs3APHYU2HfMfr5I5VlBxfglL2UvswZmIZRWHyZ1AgncsSAUnckiva/J3BivNJR1iFjYJbPeWngxpOqkCIC5F2IpQ+PI5+YyKaTyEqiYNctfqygHnXlLqsoxQn06wRlwp+o9azr+5GZ/xXUpmYmiJiBIpYa/yOSU+ExalNOm"
    "OliMjObymRqU987dMK7YJBclHVDZh3GDHrK8Zl8yWADZtUFk8obMSFjBk2tJz94BZZyRlUJksJDFoUoUtdWyDQClwOkQzz3tImye3QCKFLpRjK5K0FWxJbSqGDEijAxhKm7bmc6ouM0aESjI0wypt7DQjq/Ov0J3i9bEwknEkmoJuflX7EdCJ4oKwpgDkuU/o5pIsb6o"
    "vDgxqMGPsJw9Z6vptJoNcefiXiyPBhiPhkjH43xan50pcc0Gii3ONbW5hyu2n4EvPfY9xJsWQCsa2DgDdDq2i1ZI6ZSyqsY9rQosQ4CaLE90ZqfkAHnBl4vgQCJDgpPxNAY/OeMopW5RBVJXNVKcTkVDoCB+FovdmFLityhtqSw3xTM2VeZUDYMXhgAscCVRwrJrfVvW"
    "NKow6qTS54OUKHm4KmNdxe0qU2BXpK0qLThvSMT1gMUkZ1Ak9yj/fa5oA9VGEVmMDF4OJIDa2Esdn5XohakyH1QYntRXK+8L3OFekFxrspNdKZRU0sOiFi6kcgpM0djDzqQptpspbJvfiO8cfgjtThsPjo6iOz2Nbrdj51Bz4utoNMJ9D69gfnEeW6cXcPbGnUgiS1pV"
    "hcMV1UUQnK6exK/8REaUjMpLWKhpkqZUbhAhxRh5hyjs9iyClt+yZAFYh7Im11Bavod/ecXrKHxk7zfxzw99DnuHxywIrvLyL60MHYohVJNnAkwEzQa0nOLQDXdgOWJgQw9qkAHD1F5fnAMiGQuQ2f345Y2WGIfjbOqt0nxD2m6drjAtVRT75PoomvrBXA4HGzeDKoT2"
    "oiL4qcpIg0JPWAZYU6mqVjih7T+QUBststSaqoU4ZJg9NVYJLZiKvEiRaFNrcX2KasPlEC5JBaBPcKVOvGQkZwhYE9tKDikPDUrcABOIKGw8BrLnfxepkhdXBnWJAxbvVJ/0ymdK84PBb16U9yfXd2e3O05C7tuTIbHBVonxGk9DkIqyvRjvyceDONWg5QF4qY9491aY"
    "jR0ks220eh2gnSCaaqHVTuxnVgRKIsRJDK0z6FGGqaiNsxZOwu9c+io8bdeFuaQPTVRzoCaqk+RyNWhc+eUie6WlfGQVcXRSuiY5E1JKdR1pXl2ML/yPNUxQ+PBj38Tr7vovTCFGq6BWkcefElbapjwwbadoNBxhaXkFi3fvRf/AUaSjsW37p8Oy/Q2dL/CIqhIDhYas"
    "qeotRah7LnLVpWNRYkUKSPPXKgZhy/uk8uBV+TGWn0mWR+xms4XRqBmP7I2IowqU1eyT1kTZ5G1KRW6gLQIq23a5Kn7FsKtUKUtW37VbUTWiRFVnk9jyxkwBqlMIi/Mnc6kiH5aaUqbqFjga5fbEl+9fBnhpD0+5mmoxqkVcdtlIuYwX+3wIxmRugIX3Zydi+DQdEfRR"
    "8bcKZyKQFYRkXTStlIfxCcUT0yAjzl65W2zuqLofNLYzjxRFiLZtQLJ1Dt2FKXRmuojbCaI4gooVKFKl45V9drloQD6YP4oMsv4Y73/u7+Ly3edXEjmh6sgT3GMRpEIUiTVCQfMwY8l0f3yv0NiOlJHUiaqy7GkKXgT0RwO88PN/jnsf2Yvs+CrGbIAxl2C723Mr2tEF"
    "aJwv+jSXduklMKtDpCt9pKsr+Lk9T8X5m0/B8ZVFkGJErQRMgM6yfOg4X9TI7cjJyqBUbh/KKhWQ7Urq1I6LUK61/dkHv41Hlo4hMTbr02BkrKELwmtOv9DGQBvBm5Itf3A+f1Ylf8poXLH5dPSSdi5nQ9CZtuoFeRlgjEGqNcZs9d2NrrSPOOepWZ+GSgYYCjBpikdP"
    "HMWAdIU7MLu2j1JvzBhResrDDJbqogjQjCg12NydhWrFUEksDGC5pIUw57pP+cB3IY9s5/Tye26KbpZ9f0UEHQMHzZIlnI51/nnqXeeKs4GAHBKcAElk2fSb2lPotbqONRvymc2qN2jBbeaKSmNnDHO+nslLYGJL3cgYShF0zNjPfSvImJmqCeTEPHJlmrxSSwqzS+FH"
    "yu8zZ2yJpfNdqDgGaYulKrImvhy5XWi3tMxvWaKg2jG6vQ4WdR+vPOVKvP0n/zQfFlc1RyuHR7lOzqavzjDR0cED4mOWtTKopHtyw5vXZB/Ic2cNkk7Dmg9Vm5PLtH3fd+7FgfsfQZwHFNYQ5M4KF1AloEslwa8ALo1h6MEIlBnojoKKMzysFqHT/dgxN4tekqDT6iBR"
    "USlmp1SEpBh8Lv6X31CTb6AknxXncl7Lvnc6GuH9B+/AqDuNjBSMspvbirFVAKzRplJ+5KobxqZSkSSyADuRHcvoDhivftYPYabTw2g8hGE7SKuc+c68S6dUjhFxZUCbd9sIyC2k8t+PEig2+OOPvQ0P9o+C4jgvGakCSdlTo5TCjhL8zbMSggKPM8yhi1+/9tXothOo"
    "SOVcOg3p9s2iA6e1hjEVtkEF/SEH/3Tedo9VhFE2xp985R1YHWZ28DvPFllVz81VpYVLC/HVNYmgWEH3+3jqE56MF190DY4vnYBShDhS9rnlaZs06bVJntWsV8rVVS/oFJnWyNIUEUUwYPzBp96K5fEQSPNDpMQ6vQzY1P0NuMz23AYNx6rkjHGkYMYZaGWALDNAql29"
    "+bzpJPd3QYgt70tkbc4GTMhWVrC3/0C1F8itOEh5NB6fHdCQTUlmgckxLQ5UZuzjg2DEFTCJupOGdzIVnRgpI8Ehnpak2Id4JJ6dkDYGSRTj1mPfx+DkOeze/USoqOoqcq4pBDE/KAmvVHRkiKwBQ6SQ9VP0jy9BH1vFK3ddhDFSHBksoT9cQS9pYarVRYwIca5W0IoS"
    "xLnmdoTcqCFnw4+MNb+cjbpVmzlHdaZbbfznvTfh7uXH0J6bhVbaYdQjonKRECKXjpB3rgpAmKI8a9RAFCkMzAjndvbg/0fZf8ftkl3lgeiz9q6qN3z55NB9OudWdyuigDJCJIEtbDLYYGAAe5zwzFw8P2zujOfOONuMx/a1jbHBYJNExpKQhCSUWqGTulsd1enk9MU3"
    "VdXe6/6xQ61dVd8RV79fq7tPf+F936pae61nPeHYgaOY2xKjwrlGKBWSVfwKmjS0VvIT8Q+nG9+1zhIgiAEUWY5Lsy1cvXGEwh51BnXy8JOJv0xgaxp+Edv0LKLIWEBlDIbFGm657WYMswK1NU2sGjXjMIlxlj0ZNRgDBpoDRcCVIr6u2eDIVw7jhekmiuEAZuAPlZpj"
    "EC7JkZGFakAETjRUCQJZgl0M8HB1Dt+3sYrVjdV4f+r4u9m7Oxg/HhGUUhFHkw9/wFY5OoMQDq9t4DsuvQ2//PAHkR1eg4HTCAaPfef+YRPaRAQoGE2Ai5TzBFw2V+BpjaX1FWQrQ9C4QDbKoUj7ZZN3zfCQAokRnQKdx0eTcficDKFeLHBpNMSL2+dx4/oxbwqpmqR2"
    "7uFR9XjlUauBIcEgoB6H0pS73JLmJF9LlCaw9oRFEHpWlW3zPTlOJOvfbtNmwMh1hi9cfR4/9th/QnZiHQNo74fI0WaDOPVt6gBy4evI3QQDUthZsfh7b/8+/PUHvg2lraCYUPsgznBysqA4NATEZrwNHuIcRiIvYzDWoMgynJ1cxd+bfBKHrrsXmT/tWHRWiRd1i2PG"
    "wro2uQa1k7PYcoa/9Y4fwXtvfSOuzvcanmbwpnetoT+hkISJBBPByJxHkNtY1MZgOR/gT888ifr8QawPBo4B7jEha9NNLMvNo7hJ01UhgQxjYWusrxzC617zWhSZ81OH3IxR070GeknAz6wvwO1BIXxehhkrOsfdp+/DS1efwvLyMoz2zPI62Zw0i4xIQmvJoURhZMsY"
    "W8L5xRzF9Rt4+6n7sLeYRrpPTCdG4zBKJDahwme92eQ3IxuIkOkMP3P9CXzYvIzLhcEg1036dNzqCgZ9eKyseIBb81PoIkkBXDOs1li9+ThsKEqK4pZSqSaDMvDVILh0kcIT7iFjUdAyLqPCD3/65/Ff3v63cHL5sLB7Rr+Up5fu0ExntkfC17fg2+9/Wff30D6sdPS3"
    "ei0aRAO+9ewrOeUvBb7Vo5sv4q889AswChhYBcPGf3hWtPJCjNqyv2DRQ1q4bm2z2sH7j70Wf+2+b8HmdEesz6kRMHPqthW6KnnCqdg1AuQtjN2faawOlvC/fvE3cMlOcHC4jNrjGiDn5kkySRqCliBGE9YqjjDhM1RKY1LOcefGSbz7pldjakoUWS4kUjKAQDDEWxxP"
    "3YYttX/YVI1RMcRLe5ewsBVWaARDNkqTFHXIBe59x01e2sHFpUmmoZm9wDpHkeWw2nZvbCnzEGMW93CdKPDtwDCWsTxaxh3HT+GP5s9AD3OwcXgeZTbRIAbUqUmwkj5QqmPHklOGHczxqfNP4lvueBNKNk02KqW8KG5tTBNWd6vjCA9nZWrccux6/M03fjt+5qH/hvH4"
    "AExZRp5e6DKJtL+W1FBUqMfKW973FlA5oQJjujfF6oFVVAsnbie/xiSLlquu3M5xyqHkINliLOsBntw+i+//k3+OX3vn38HR5QMez4or8lYVbXCtQGFgKfG5lllCgCESXQd1C1bwyqEe1z+6BpbVa48abkhukytTEaX1xeor26fxww/9B0xtibHKUXKd6kwE4ZC4Ecux"
    "R1sDOS0cUIoIU1PjlF7HP3jge1F7czgJmyIC3uk2Q2KxzZUVv09ADGuDJXz+4lfxm6c/jwNLq86kjb39jFKO2ypjz8QJDJ/kw0LQG7/QulFjVlX49pu/DgdGa7g630GmszSAQ4iom5+eZjdyD7bgwGw3Oj85OQ8UzgzQQvuXIcivkkjGjMC8o3hwNGEHYSAlysDagedZ"
    "lsNYA0okWD10l+CWESQqrbBcHa6RNdBZhjuO3Qh11hkrkifpElNcQkA4aZBkhAclgpA8MSPKcsZLY/zxuUfxP893MciLeHB23W7TJ0M+WFI7J+tLkeeYmhJ/5Q3fjl88/Rm8UO1gmOdukRPua9UA0SSCJYiao1tOASpQXHzDk+UKe3sTjEZuI8jsx85208MkxNzNdBKu"
    "JBmOJhE1M9bzZXxleg5/6dP/Er/69r+DA8OVWLSSDCGSPvN+IdQim3fA+DbVgSQvuyeqvmF8U68F6r5WhMmLEF1ZYh2R4rIsrGAypfHVnfP4kS/9B+zYBZayAhU3rpoSY5Cs6YZ5rYS0yoGvSjlhdmVq/O/3fjeOLB3AwlQuD44c7qM8OE3e3TMEZ5LfpLi/u39W5HyI"
    "HLnOfy350FJS+CeP/wGm2jjczG/JSLmVscq0+x7yXBclOEn+dToMQwFag5R22JTSsIpwYLSCv3Dr16Nig0xrB5T7v7TS8S/l33d4H1r590gqYl3KkwO1D3bNsgwlWzw9vYBRMfRlr3k9pF3gJ2VuvFbafT9pHV00SWv/Ndp/jwJlKr7n5PVqhxMq//0q+Wf337TOXCiH"
    "/28601DeWdW9du1CWZXCrQeux0AP3OgTtpN5Bspy8Xq0uw7htWkN0hko0/73N6+ZMhfuOhqM8PT8Ar5w4WksDcfuHvCfq1LuNbrXG15X89rce1TQOnfbZZLXS0GThmHG4fVD+Fv3fRuq+dRhTGHRocJrpAbbysJnGj4P7Rcy4t7JxF/+/t28vOnAKJ2Ja6ric9MA/eTv"
    "TfLPgC9kGs2fa6BCjfViCQ/tvowf+dS/wl45h/bQSHKEClJu28ivz7hvv06LWoz/pGCl2kbhLNBzmu/nDsrESURUVzQticnOsvf8bBM/+vAv4kK9h2VdiOy31s+gxi0gMrSjwl5sCgnIswyb9QQ/fuM78N7rXou9cuI2gdQ81ETygVbxgXYXzeFB4evieEEKBPe1FoyV"
    "4TI+dPohfOjyY1gfLsH4LV3kY2kN9gXJnXBKrOz9TRI2Nv7f3U2koLMME1vhrYfvwj2HbsbClNAqiyBv71/+PWklH5RwI/q/wu9XCgM9wNVqitPzTQxU5ugc8bWE4hRu2OYzCj+zKQS+gGmKXw+Qe+/+4VHis3TvQTeHgfjLFVMdCwSRjvbD2v9ZpjPUYFy3egQbg2UX"
    "ZqG023D6Qgt5QCgVD4b4lxZ/5otjLCyZhikUPnTmERexpprPvDnExOfk7xdF7sAJRntK+7/L71POfnt3PsH33P0u3LtyPSZ1icwXQeVff/N5qvgX/GsO94hS8mt90dXu0NVao7IWu1s7btMeXocKh7xfApG8F5slBwR9gsm7MilCZWts6CV86vIz+InP/H+xMJXIaPwz"
    "cKJk8/G13IX75l//zwp9Vg9CgiNpDH2/NM7ZIPDXYFUwHDl0c7GHH3v4F/HC4gpWswGqEDklxsDwgUbZhLhgUAQOpEQo70ueYZdLvGbpevxPd3wbFvUUWfA9p2ZVHi5MWEU33Zx7cEDhJgwPOcUbjhRBa4WFqfAvnvwQcp03q+Bw88hCJU5B0pkLjNAa8B7r8J1Z8FZn"
    "v8lhYnzXLV/vtnvkmO5N5ydutNARavFQiT9Xyfcoj48AgyzHi3sXccVMUegsvs7w0IWbO0IDyh0OLE92/xdlrtty74VitwtZ/FVzKEQgG00BD6/dFQ/3uWvR5RJpXwRcl3Ji9RCuXz2Mmi10njUPrFJQ8kFuXY8APIciQKFz9N03EbAyHOOTl5/C5ekWClXEzyMWfl9U"
    "tWruk9C5KtGlK19AYgH278uwwfp4FX/9vm9GXZdQed4ULNFlu+9x3SLLa63E69bhvgyfj2vj8zzHdD5FNV8gK/JmjlThsG8+jyhRUqIoir8Cb5eJULHFgcEy/vDiw/gbn/8FqJauPWlQpIldqxJxCx5qbxfZE20pUkSaH6yaXLVWJaR0zON9SpGN2EiLFMzdYkWkMKtL"
    "/NRjv4THJmewno9csRI0idCKRlIcie1G6FQks9t3TpaA3Cj8w1d9H5aKsScYa6+DEoVINQ+wlp2A/x1hZAw/V/n/5jYcwHiwhN998Yt4cPsFrA6WItAbX7d4TST+WY4p8Z/lzUGA0hoz1Lhh6RDeffIB1LZ04yaoee2qGWnj5yN4Ms1o23QBzdcG5DLDM9tnMYdxRTF2"
    "Sr4bioUrdIfyZhajdHjI/PeHm16JcSi8llg8IV63/DqlWu+RRLGh+DNBjOVihBuWDrnO1ndXYcSDUn6U1XGMj2NW7LioGQlDF+VDOYZqgOenl/D5y89iVAz9EkKOhvL96XgdQ/eotYQCmp8fDpNcZ5hUM3zvfe/Ga4/cjImtXMiJVuL1BpiA4vfHApuJQpzcq+I9aQVV"
    "ZNi6ug0yzaYyCOWbrl41qofApVMqee7SZ45Qw+LoaA2/cfbz+JmHf8VlTELYTHmQl/rUMMJdlPZzdUkWMl1qlYpkReqpM0q1bE047cB61YCCVCbX0n7U/FuP/yo+vf1VHCyWULGJD6sMT5RFCtSMaqD0FAtjWKYzbJUT/M0bvxGvPnwL5vUcmbjp46hHDXYUuw7xYCnR"
    "ocTf40dC9pHz03KOf/38RzEaDl2x0ip5yMLpmzxwsW0PxUAnp2X4Oq01JnaBbzp6Pw6tbKCytRs3SIyV8q9WUQ+Fl0QBaAqGKMYgfHn3tHu4xGgUcDBFOjK8w0MTcQ6tkw6yGfFIYIIO1JeFhhRB+cJLSK8pPDYYCmToviQGF34n+4J7y+pxGHDEw9zD5l4f4t/DddDp"
    "GBv/W/OAc4AJQKiJ8UenvyQe1ha+GT+TcOiFbqopzEp+5rJjJ0foXR6t4KcfeB9qrkFZ1hwM/jUqjxMmnbsosrLrjxBDvMfcmFoZg50rW875RKXXMkwr5F9/OKSaKUZMDVp0XkSorMXBwSr+/Ysfwz97/PegSTVupoJfR0SdBOrER0/i5GFTzNzjhtJAVlmy7WjbPbQA"
    "tHZmYXcepf1HQVL4X7/yW/jDq4/jcLGEytbCYTOsQ+WIxtFnqSGShS2Kil+vQdit53jL2m34idu/EVXtuxK/GWpb2SjvCBe2Io3nhBXuabLbDM4FBsN8iF946iN4dHIaBwdLqAORLtEC7q/mb5aP/mvD7wsUB6UwogLffur1jt4QFwvUUgN7WkPADknFNXUwoSPh2URC"
    "W5gBMHWJpyeXUOQD99BFLNRGLpaCgo1aSmr9ekpcYaIzr99KkWoedCVlM6p7l5D8nCNTXYYzkNjAMdgXkbs2rnPLFKX9Vkoh5BlLZj61NqoJ4Vjy1jy73DBjqRjh4+cex8XpJjaGy+46t0KFJX2itYJrHeLCTytsPVlhWs7w/rvejjc/9RE8uPMyVnQRY+TJO/kxNWJp"
    "6lAGHBajgizdXxzLHENnsyzD3nSG0WSEYmXsOVANUZnbFjvkqQcajWtHbEP8PcYN9+zQYBX/6Nk/wOHRGn7wlrejtt6OJtJB2ttUpDFhPdK+a+WcMrPYS8f7hpNEDu5p3bjVjtE+PzwQQzUp/PwLH8WvXvg8juQuAZla3QLiCKU6403A4OWYQr49t4owpAL/+91/EYXO"
    "Y1FSyfdLTAfJaalEFyWBR4rYlytwRZbjymQL/+rZP8ZyMXQPRquzUlqlbXULR2lwHH/KCbxFZxoLNrh75STecOQO1HXlRyhxwqMBRxvDOtWkN4tuCpSOi8rrInOd4Uq5h9OLbQzy3L1ereII2Ywk5LdfOhk1GuBaaNvECKk8PkdeupJ0KGq/kTW8PkreB8TGGGLpAGbc"
    "snoc43zYdLihW6MwWqXAddywaYdzKdFpK9/RsSJYAgqd4+X5VTx48WnkxSBqCJXsnOX7CEud+JFQ3DwrucxB87XMwGA4xF+/95thrYXKs+ZaeOyK4iayhY0SRUwvdI/w+lBSFLl9jglP2NzagUJYMDRjbLgerAW+FUZM3WB9EVMj3eCbngm9NljC3/vKb+ATF55AprRI"
    "/YYksPUTTVsbQu5pfNq1RVFyclCKESVWIsKEz1oBdzUpHG1gzbBFRgofOPsQ/sXLH8XB3G3UmBrAO4Lg4aLLWVgKPqllEOfZw1vVFH/11Ltw78YplKb0YC0Sv3FCSpEgwbiWkoqkgIr/bthC6wy/8tVP4YXqCkZ5ETeVjQBWxRsgvF4Ss78slM7NQY4Xbqyd2wrfdPIB"
    "jIYj1GzFSNeMfvCoHOKIIV47PEZE5Ce6ZkPoBK8MleV4eXoVl80Ehcob+ohqQPCIu3mL6AavomSbKN0vKY4wlK7N0Xf4+J+D5rNBC6uUi4NQbB027Ojfx1cOYnWw7LBRQSuRWzyS9JF4GAr8zRdUbtFoiAg2I3z0/OONSFkJlj6aeyqBMqCSZVEYidvjvCKFTCmU5QLv"
    "u/3NeMOBm7DHNbTH41gJykGy1fTvSW4OtUoWJHKEBAFaaSy4xs72DvKiaO5NiRWCOpihPIBCMVaqaSwUuQ5QwdFs/toj/xnPbJ+FVjrNPGwv6toTmzT4bLk9dDiHjR/8/oz2vhaeWpKJ5mdIpwbHtfrC1gv42a/+Llb1wM+5kkcV/q4EftXIClgQz1kC/wRoUtgzJV47"
    "PoX/4eZ3orY1tN+CsbBwCV1I5x0Ix04JKgKpiNbRJQpcmmzhF09/CqvDMUyIJ29xWeAB3rD+h+gOOXjGk3g91KzhDTFWizHed/J1fhxMi154QJrlgCxSzU0X7G4alr38ne7GfnbvPKZcOf2harqr5r00D7PETCi5bhIDUenN7klnMn2YAtdL2M0E+kE8GsT7Ct0wC0w0"
    "/BzDFgcHKzg0XHbusuIBi+4K8vWpwHOj+DAzOaJp8I1nWazAGI9G+OTmV7Az28NAF/Gzgyy6CbNeJF6T+BwoNQQMIy8pgmHGaDDET971HlSmgs4zj7+lBZXE/dTZQItiHKeUcMhnrnvK8hxbe9so5wtkWR4PWIiuFNQURombskgkT5c9KqaFD1SObTPDX/vSL2Bzvrtv"
    "CjTtz13o+mf1YeTMnjja8dzBn80uomef6VwCXGU/M93C33zqN0BgaAAm4EYsggLECaWorXeS4HujdXJWMARbG/yvt70Pw3wQjddI+oMTifpErWVAAHflAyMKZvTTdlSM//zip/BivYWRzmHJNqZxYjkgx5J4yiIdMaHa3QSgSWPKNe5dOYl7DpyCscaTXSl5+JDwzkR3"
    "kxT88CApEVVOjQsqgMd3zrgxAKKQxi1tw/NJRhGiuP5He8SLAK0YKaQJm2q86pNRHeK9JK9VHizigvhuy7DFSrGEG5YOomLrt8Akvqe9mGm6D5e67Fnx/qG31BwmUAqsFYb5EC/Mr+KzF5+GynQi32q6dSXOnfQ+aPzlSXSIJAqco25UVYX33/Zm3LdyElNTxYVNw0UU"
    "ZE9PKCXRAbcPzBheIgqXA+Q1rlzddHe9PzAb8N7/Ha3rJrqq2PUlfK3AhrdYzYZ4YnoOP/PIr0atK/eZ/bXyIDrqmVYtalOyVKLLayflcE+EddvDuQdgBwELU+HvPP2buFjtYESZL1apc2LS8yTs2GT2a3R4/kZWSuFquYf3H34Abz5yO+q4TWudYi13zOShBpIOBJ2O"
    "xFXITGe4uLeJ//TSZ7Caj1x31RlPW467nVHHBWdCpS6cseYowtyUePehu5BpHYmo6ea0PYJQ7KTS8UshuZ/EmliTCzx9avcccp1Fb7mEh0MqweZ00lk1n2Psd8SYGEm2ihqhs/hgiLqjMoR7QxN4QBEL0i2qBvyBCEW4efmYK1hRfiK2u4FrRxDeU6qxAgcEJSXwy8R2"
    "1CrUDHzs/JfFwSALUvOaG8sUbv03JSAJlby/8B5rW2N5tIQfufXtmJcLaKUbp1fxlyU0hojCgTahJ1Da2csuM9MZFuUCuzu70FmwQkm38Erc90TU2RyFzWQTf9a4zFbW4ECxjN+7+Cj+9TMfjJvDRELWgpv2w7I6o2R7b9POHetoz7i/++obJY3HXv7Bc3+IT+88hzU9"
    "QOktTQKOEp0KIFeZlOScNZ0SRzFoeB81DA5lY/zNW98b1f3xAYg+OiqOhs3PFdl3PVbHchXm2l13o/3SC5/BK9VVDEhH3lmCrUURaJuoKjqboM3phM06vdayKvDu468S8gMWWIlqrRrT0ZmS9lBuPtNNVqY09qoZXl5cwcCPz8mpL254EqoCiAMjfpZy/EDKk0vEaz4E"
    "1J3f6N6wgkiKFuDe/FyRiBMwOQDXDTe8DbxcSCC55mlxRPowQ3ReATtSrkJYZgz1AJ+4+BQmixlylcVdWTwYxPuQmKi83lLmRkmH5u1SVAZrDL7r9rfgxtEBzGtv563SQp4sh/wGMfKnqNuJQo6T/nXoPMPW9jbqqmpgA6iOHK/BfptfQu21NzV0n/B7K2uxlo/xD5/5"
    "A3z8fADhg4Gl7ZI5ZeBEj2ynD6hS3VOiDyzrVjxKviyA085k7QPnHsIvn/88jmRLqIyJ4QKtNgQQuYCyhZSEsbTUkHvozAI/et3bcWrpsC+QKhEtkrfL2C+cljr/30Xo2D/gV+e7+NVzn8NqMYKJGxDVz+agxslCAu/oPDyIR6eCwsxWuHv5BO7buNERFSOw3l6St7SV"
    "wreqjS8mDr+iWL44vYxL5R6GlMf30ilQrdQbhvBMo/Tis+i6Gq9xRGvj1LqfGl8sop4Rvk136PAfkvvtuqVDTVBri7sntabp5+Teo/V0ABaLHUnHsEwYUI5nts7jS5eeh9I6HoQJyN2hOVBc/cePUlGKfwGJL1hpahxdOYjvvPENmNQLaJU5yEL+LhFiwUmRUt1CLDEv"
    "cdApVqiMxfb2nqP+JOJ80SlHJ1DylBGbPoU9SxV4eg8zoFWG/9cT/w0XZlt+Iyo7Nu71hO/rqHqJo+2OifedHzmhK1jheBAsQjKl8PzeBfyfL3wIB4dLUfvjCINOjK4AaN8DkO97yZuHBb5Q+GdiiNnaca4WtsaN+UH80HVvjizkLo7HSa6gNAxsgFwW4xyliSnBS4oI"
    "v/HS53FmvokVXTR6Pd8xSCJkXGfHrVbT3egWcVBSFRQRZtUCbz9yD/Isg7G2E2Lb6c5bHUyC10nMitJwFQB4cusVzMoShc6g/Upfi4ebhP10CF2IjRQaMD+c3P5TaDpkbgDzTgWi/ah6lGQ2EtK8uvYIH/785NIGRpTBMlKSrKJof+KuFcVgDsUMxW7UlDIgDbGR9E+x"
    "ZmDONT554anWheCe7qoLuxFaXWl45Egln0Nwp/i+W96CldEIhiBWKSmTKZLS/XuLnxqnn1tCIg6ZhYaRkcJkMgVbiyzP/P0L8Zz68ZAp/TP/mVFjLyZeR/hc3atcyoc4bXbws4//euO53zf6fc30567FVdY4rnACfII7NuqdmyiJPSLCvC7x00/8Oq7OdrA2GGNha2+i"
    "xi74AY0vEYuCJ/srFxZAojPyRcY/ANvzCf7aje/A+mAZtakdLiNrjUjJjB5I1ERWtb3tmVsKSA6aR8LuYopfPv1pDPIc84UfbGM3yIl1E8uTM9qRdD3AAiUk6KWgCJqBNx28TdjPcEuCxeiGajXkP/oaVtQAXLqQ0vjy5ssoqwq1saiJwcYKI0NOPo+w7W3C+gTCSCKV"
    "KkTYA6isC6CgtstGEsrUtwfilg0PCT5gQ7hlkRV5YryB5WKAvapErlTy+TUi/lZKt4yqopQYmxgPWAvLBlme4083n3bW1IEhS00GX18B7iS4hVuAqYP7MruHvjY1XnX4JrzpwE348MWnsYIC1hg0ZtyRASwSqpufFxjizC0sMPySmIpEqK3B9tUtHD52CHOfUxAKS2No"
    "adPcWDQeWSGklpAGBYfXYmrno/WBV76IN6zegh+9492orY3urZ0i1ZeoIy2rBGSV7TsvEvYF28NHIYMUtFL4rcuPYHNU44GVGzHn2ld+G4MibOumlCC7c5u08c+5ZdGsfcE6Nd/Ad5/8Onfyh03aNV5j2465T97UfrvW3yD//dxjmI2Buw+cwrxaRMDdEkfXUncTqaaw"
    "erY0OPXBivbO4r0rRTAauHF2CK87eLPYKBFapo6dZ+P/38yQXLmidd7u4vYbbsBYFzBwlr+WjbhZ00VL8x7lIqbZMDEzTG1gKgMYi6oAVtVSfJFOC3kNy9l9tBH70JHFfyWs50u46cBRXFRzFKyc7XASRBpY+BwuU0KIlsaH1j/UNrqpOo+uA0WG02YXz26exR0HroP1"
    "Rodf673I+KroULrfrp8dQ1+RxvuO348HZ6dxdGUDi/ncucQqSn3PQpYHCWNLtIqhuAcbRj/H88NWBgMobBw+iNpyo3IQcXdBbhObCrYNutNylYmKFO/Sy2wxHg/wH858Cu898QCuXznoPbT2cW1ou8D0YC4MIIPyqhRxWoe4ucRcrnUPsWzB/N8/+MinMd89gwvFAGVV"
    "NR0gySrc3S6GB93aJvHXttwoc6VgNeO+0fVYv3uArZ1NzxBIT3IZ8slI06lYCLXlM2BD0KZv72trsZQN8ImHPo3J9llkK6uotbuBXQyiTUBwCsm74TUbIxJoWFjmuvdjvTtFpjNYZXBEr2FUK+wudmBsHUdhUn0PRqpCCA6RkrrRjmI3pobWGvOqxPNffQ6LwqCcGxdU"
    "EDoXQeMIXVV4III/Uex4rE06J8vWFyyXyj3lAaZ3bEONqgi2MtI0GGoIatERNNy4HQfSNDva3SfeWz87t4vK7sLUjNpYyEz4JIFcdKbWWi8vahY/Lp2neSDdcU7IiwK7W5t4ZPgoTt6zjHm1iKJ57BcKzIx+xFS+z3RzbazFIBvgRjNG8cImFksV6rqORnpNEG/TjbII"
    "5o06SwnpiLwA9u8HmTsQF9M5XnnxCtY3NlDXdWN1JDDa6IQaPjdRwEiqXsRkxswuUao2KIoCL529gC+tPobrX/fO7mfV7qz2SdihJKreNvau0ra2CZJQ1+ZmhZZQA5vnLuHzT3wWGIxFUCm6DqLXMvPqesAGJA+gEgdv0qjLBfamuz7qjxs3ScHGJxYFS6QtS3N7uaVk"
    "kXdYs8VgaQ3TC1fx9KNfBFbXnO0lUdJad15jPL6EtYZtBWsK7AyZBuwco+N3olzMMZlPwNbEwq6S5GH5PmwcxRIn1bbOs4mEdpIZrXDmuZfxzOZZoFYuoCCEILSKsIxzF7N797q376/JDHr1OMy3LrBTVzB1LXSO4V5TYktKnYfZhiQhEnbSvkAFVIeJMMhzXHjmNJ6+"
    "8iLA2mc1cnqftYue8KWP73k/6k4IeZhNYO6aYba3i+3ZXlOwZOQZ9Y3v3PkIZWqQDCA21mBltAIznePco88B+cADS5S+5l5vup4s0IjbiRFYeyskwcQ+U7/QZGmq9s/g/RtJRtdYM9y4Bi5XssiAvSloUYvrS+lojjQxnno0zTLqK2uPS3JTyMlFb2ULJveB/2FZDjUc"
    "o8iHqKOLqUVvLj1sGzhqoS8usSa8cE2EegaoBXtipYqzd/uRbca8ZqYPDxe1Az1jsCYLO12vxB8NQeurGA2WUMPEehPDGAKyKhPv481lk8hxlpXUvwZFhHpmoRaMui4T3/gwGCsmAbGEx164rQq76j56imTVW7bISkDZDNmggKVWhiSLqHhO4+kbp2TuAjWed6WIYABk"
    "gyJa9di2g237daHpuombaxe60BCQ4N6bbhwqfNHQrEHIkReFx+KQLla4se2VWA9kwe8LS7FOEE2kYHThJCre3SJY/oCto88EWk6bw9g3SaDpyJsLy1GnyABoMIAej9KAEhY/U9o2d0L5Wrgct0Bo1Yz6RATKs+SZZol9kcAA5WPDrUmGWoeYf1CU1jBV3fK0QurG0CKM"
    "pgnR6HyuWZpsTNdGFfYjufvXY6oatjYweYjiCsA3C2MvoWMX4Ht8IJKTin0SDoG1hiWPlxj3l27ZMHPLXlU2QknhZUrBWSvabSKfIehPBe0wK2vEjd4nLxAx8Rz957l1o4WLZBvGdW1gyhp1VcGyabY6YnwOry/hb3ELRGjZUMetbxitLKOyNep5CVvXsLl2Y5VtvrdL"
    "FOak2HKrO2aIXEiCez/e2tfWNaBsxPpSPhTHLiMpin7kjiim/3e5COIAELNHA+cVuDLgzPrNrvueTnJ1W+8qinOSciOfcR8Xz6Vx6eHJUGBbXaY4lMCpPhecpln4BHIWhzYHPLGuwWyic4NsCikZr9v07fT+oDaeFTiKVtyTyjP+Odr2N+4kLYeR4AcXMxT8b7Fo4bXc"
    "dJysAK6NG8HRhpi4k3KeLv66UKaP+RIImgyXaJO4iMRF3qeoGdMAgH2jHstC1ZrnIzjdAs7j5+vGF8opeZBEZoIYgxuyK4mhqXnIOvukjkV90ymJDsc2U11nFg//XSSrJBcpBjf0nHxBJAuTdNbNs2XRyQNEyp3jHvkUJ8XNv7ZMu1Zdq2i0xiK2K4YbxUvRjq0XhUOA"
    "hRHUzhQozxweFK+LoBa0Jg4Li3agA8s2yRfDZNLzsfBx06q9U4FNO0U5RnHSAcj1CpKvZUFcZiEpYhL5TGyTe1POBK2Vj8DuRKG2rdAKH3rb3K8ibxM9wDl3JS8kN96cdl7JpMQpIN9kWLbwBDmRxOxYbr1DbnXecoPcdRzlFiWHWzSHZDvd2i6H955J4ljCBt1npcbX"
    "WOqQPzlgxLZGloh4E/YKETuzbYcgyQyVNTl8iZ80yQ9f4gopRaC53q3IIZl9Eg5Ny/BHvjAxhFw0J5w1EsWQWWb5yb1+E2ZK/uHXftyI2YDMcbPajNQ9p7Y8Y1spQ8xdTooiV0xQC3U8t25mcSMyt9fPndVQguM0GkcLa2ySzi1HmSTGiWUmQLoJC7IlFt1de/pArgEt"
    "lgW25bvU/t7Wn8fxkVqJShC8TBWoIWkHKvsGL3BtRa6RoCFwC4/hjsQtitCRxl11Onu0cDoGuHNXtCBk7sLD1LYS7oFoBHHCCcaT3Mi+BEnx/ZY7kOA1tcmCsNrnXcXMyBoMpIckKvgQjQRG3Le0Dw5nW3U4ptX2v0XZAxF3lIlxikJlfUxTpxa36OYsWv1uu45O34VO"
    "DHfcLhmOcfax2xP5bZAPojSOa4Hi1Gb2MkdphZLkQ/QtI9pF3IKZ0o9BnJTpW2EhLledlTcsdzsR6jdTi9iWPHnbr82yG9HEC2kwMaTjpcyb9ON8cNsI4bnNQcvJKJIIyuVYkpj2cecZovY+gUVHJbstgU3CkuCk+QMJzXaTLcdMR+bmMLR91zy5L0k0NOKg7Xv+k9Vc"
    "PyDe4X/Jwp10uBR1j+0rTGDYJPlbbOAleCWbpcRiPXSGnqwqdHCdfUTfkjUByKgjBcwoyQPjKAZtct1anjXdfqTh+rRXlGKM6J74lJAkk8TcVlCkk7q4EaaeL1yacM+FIgF0SqDXytka1HOYcBN4EVN4HV7mihUlDNFEi245PcW4/SBymtScjIjUuDckpE3JfeH0hCD0"
    "FEi0Ipa4gVfCqKCcVyOX1m1xSJAJ/daNQsdj03GQZaHfd2vkf96iBqiJa5NEz+Ye4u7TJac1bhFouUuHjcWnNkBlRWfdB3pTQgWQnPpORyo6rYD9oTaoFlUkUzY/XxyYQr2SLidbxLDYswj+BDV4Y1XXXrjPzRSRPFJtvROnTrT7HaIRr+XkECClPLk7YFzBW1T2bOGz"
    "oxZ22TqMfahr6Fjbz2JfV0V9bPdWOyYJpKqHEJXo+LiTyIsO0z2osk8uHwCZOlq4yItLiWdzc0MlrzFcJBYX2FdptgwMcmyfv4DZdJo4BiSIBLdB+xaWlDprCaZwc4o5Fb3FlbPnfdy3Bzu5OUVZtLxxxrccCYck3k8MgQ0WuCxa5kJjurONxXyRnl7xl3CnOHUmasGa"
    "sAG4Fhswa51n1PbVTWxfvgzoDFynD3e0w6Wm+jKnqdpJtDy3nxdy/CxmzLb33EiodYv5wQkzm4MPuLjPwnXr5i+lB5lSCtPpHFevbAFKg60VmA8nz5r0DG+KNHexVXCK8Vh/3WYlppu77v0ILh+1H1axbW0TcZlTJjkzks+S2TmDnD9/ASgXcVsc8CtJECX05PyFZ0Ue"
    "YFbOFylGpkqD0V4F1qozXXTEt0gXGNSifnNPN0t+eaIGBY6uH2opUaizBJEmocnoH/mZ3NUStrU+3H5wqH3/JDAaHjhxW4yEAtg9wFZsn+TKHy2+UtJWtsA9j4uBGasTg9l0iizLhcJCtTYVrsAlL526/TPvQ8jUOsfWzjaGuxWADKY2zcPVvttYbgJFcbWCOcwi1p2l"
    "ZMfdRyuXJtje3kamMxjLKVjO6QOPtiSEOe2oEB6kRlwLdsXj/CuvYKVqxinutJrUAWWJ0yZBXvuE38bWXW8wlucWezt70Vtf7DsFKC5w0fjZcARrbbL4YXENvUdZluHCubMY7VQedG+PLe2C1cIh5X1JopMMB4n1Tahl5JyjvrrtKBqNt4q4v4SAPxYoGws4J0C/dMBN"
    "iQRWEXbPXsLAZLDWRM2evLepLQiWh4oEusM4Fuk1FMduYotjtsAbx8fBdR2dJ4hSwnUqJm/xGkRT08vRA4D5AjeuHMY9p25tmhyh90sMGnth8VYoTbtgsYiP7rg2MKWniPiBARt5791fh7WlNRhT+wtvXaGRq+pgwMdp58MJiNhyIvDSheHlEnfgAL78zFMYDkewtiEU"
    "Qshf5O9C6+HHPtBQ9KA3BqPRCF987BEcq0c4Ug/czWOR3BB0rQcCzY2fZOByuoWxbDHaqXA7DuBLX34Uee71YzYF2KX7aToG9nQIiU7OuyyQU9I/8sTjuDc7DDIWVokcSJYavTYjm9Nxtv1+A+nWPxO6NHjV8CgeeeLLLqre1OnHHotEc9CwAOO5hdtEp4hgnesP1Exr"
    "fOnRh/HA0jEXZa8FTmK8bKo9kiUHRg80KIoVrMNLuV7g1asncfHseWzvbqMoiqRTlCMl98yvjDa9gtEYX3h/L2uR5xnOX76IS2cu4p78MOyibAJT2lULPd12X1KyL1YkDyBSYFvh3vERvG7tBmQLbjIa0OZjdXqUVGDcObgj/wIqy8CTPfz5e96C5fESjDGJc0SiS23j"
    "5kK1r1rdmEoLkC8y6HJupNVJ4yXueYNKwViD6w8ew4/f9w2w29vIVC62Ql16W6AAyAeDBK9HrjEoU+DpFG+qD+C6Q8fwhYe+hCuXL2M4HEaOR+TlRA5Uul1KGOad7YN/ScZiOBzi/Llz+NJDD+PQ2hreQcfAZe0+ONPqshKwN32YmVO9FbVuNKU1eDrDG6oNnDpyHJ99"
    "8LM4/cor8T2xoG4wutIm5r4nToK4FmxdAR4vjfCVJ7+CF8+cxj0bJ3DnYgRra5dwEm2tqdVBtkmyQQAbDhROirCCguUK9+dHcOfhU3jky4/h5ZdewmA4hK1NR+CQFi6K9I1mZOJIMCWRtmNMjfHSEp5++mk89+ILuHXtKO6vV2Ft7ZwjRKdObWyaW4UDoThB6O78NpoB"
    "wzVWJ4y3HrgFO4sFPvOZz2K8tCQ+exYCBrEpTZ7+tENhlhKopptUWuNPP/mnqNji69duwvKcUZMjDqN1tMsiQS3danKTSSsj6xJ2DCwOmSHeeORWHF49iLcMT8CWcyhoXxwp7aITOK5l/2GFTIc9QyCQbW2JI0sb+B/f9wMJUz3VKbHIcBAkUhL3cOtdKRaqbxZ6oLhm"
    "bMd+iUtFgrNE5E6Kv/tNfxn3H7wF5e42sixLk0+A2D2QPIIY6UgYPjBjobMMhmrcUa/ivbe8Gpxr5Frhw3/8YdSmdsk5xka/prYvX2d7gn5qhbUW+SDHfD7HH/z+74FNhVoDr1k7jrcVJ1BVU2gClOWOPCV5yARGwlF7leINWimYao47y2W87egdqIhR5Bof/OB/R1lV"
    "yLLM1wMlcMRWxyjkHV1GijuWTV1jPB7h7Nlz+OhHP4qV5SUg0/i20c3YWCjUyjq3i1YzIsHd5NpBCoOboqMZqO0Cxxc5vvXQ3c5nnYA/+KM/RFXXyPMc1pgWQCxGUuoe6yRu2jAOWmMwHA5x+fIVfPSjH8F4OEAFi29dvgXXTQvUtvIWzrI+UVMk2rSdZob31816IJpg"
    "hgpqUeI7Vu/EKM8xHo/wxBNP4NHHHsPS8nJc/KTjXotrhFb3QY03PaBg2ak2lpaW8ODnHsTzzz2L0XiEjfEKvnP9DtB0CkNwMWxJZJbaTycTHUlIOoWAocnlBgx25/ieo6/CeDjCHDW+6ciduKkao+YKWuXJJrGNk3PPAdk+iIIFDV/Zxr/8wf8FN5y4HjZIqqgr6+G2"
    "rYw8baiLWOmf+7m//3PiLBABiI2ivcOXSM4PSmhz48EI33Dba/CHD38Cl2fbKMZLzcNmk5Ved+WT+JQTdJah3t7Cjbs5fuyWr0c2GkIRYTQcYm9vF2fPncWtt9yCPM+cgJNU+sEkfKuWNk4sFaxljMZjTCcT/N7v/i4uX72M5eWxu/kzjQdWTmAyn+EFswkqCihLAhik"
    "DtFFemuFjjF4ByHTMNUM90yW8b0nXgPOXYzW0ngJu7s7uHD+Au64407kxcA7Q/p9juVEu9Vk9iEREkegkhlLSyOcP38Ov/M7v4OqrjAcFGAC1kbLuHdwCE/uncckY2Skm+6xbVrVAWCFJ5TvDAyXOLYH/PDB12NQuMSfYVFgOp3i9JmzuOOO25HlOeqq8ha7jTQJ6Jq0"
    "EbEwn6OIAY7HY2xe3cTv/M5vY76YYzQcIcszjEYj3Dc8jOeunsW2rh2+GXV01NGrdd6T7xbC+7E5MJiX+MH1+3HbweuxQI1BlqMoCjz7zNNYX1vDiRMnUJalY6e05UeE1tzuHacSSyaG1hrD4RBf/MLn8dnPfRrL4zG095Q/tXYY19EIj+2eQT3U7hpJKg/L+5i6XZVY"
    "WyidwZDFeFrhh4+9FjcdPI65KaGVgi5y3L96Ai9uXsSVeg9ZVrisQ8Udw84ODk8pd09nGrWtwRcv459999/Gj73v+5wFlNI9STbpKduY/NG+NC2HZzsgKBGntsNVSfgGtSlb7f9Zy9Ba4atnX8IP/eL/G5++/BVgeQ05cnBVg63j6LBC2j6LhBtShKpeABcu4ztPvQnv"
    "OHQrZosZlM7cm2f3OyaTCdZX1/GOd74Lhw4fRrWoYKxp8TkgTNcark0AerMsg85yvPzSi/iTj30Mk+kU49EIFhbahyxkOsNyVuBD55/Eb+8+AzPMoFUWQVkI1b+09JD2zUwEyzUwmeEd+gS+5bpXoyILay0yn5CilcZ8Psehw0fw7ne9GxsHDmCxmKOu6sY1oSeGDWLD"
    "RkTI8wJKEZ588kl88hOfhIXFcDBwJ61WYKUxzgfYmezgP5/7Ep7LJkA2gPaYW9O9cUMcZPE8UEivMcDuBPfwBt5/8nUoigEqWyP328FMZ5hM9rC6uob3vOc9OHHyJBaLBeq6FkWWO8sbtpzoJ7NMI9MZnn/+q/j4Jz6G+XyG0XAEkE+YJkKuNebTCX7j3KN4lK4CwwE0"
    "K4fXCUZ5FKfLM4zcYseAgXqGI9UA33/8DTh54Cj2yjny6MzpnDjKssTrXv8G3Hf//dBKo6qq1pIg1bk3GK3vSJXGYDDAdDbH5z77GTz11JMYjkZQOiQGaVgC1gdLeH7zLH75zBdxqSiBbIDMNgWcBflWhrQ0zYez3MFijhvtEr771BtwdO0gZtUcmdbeWdV1/OVsjg9e"
    "eAp/evlZYGOMvBiCjQVbI+Q3LYJvKNZKo2YD7GzhMC/hX/6l/xnf+03fCWON4P4JO59eVkw7hAK9wmsyxjD1CQR7yFssSaQtc62UO2ihlUY5n+P//uAv459+8rdwrtwFshwYDqC09vgJIrfFEMBsgMUCmMxxpz6I/+nd34sf+Y4fwK/+2i/h7NlX3E2KIGNxZL3ZbAYG"
    "cPfd9+C22+/AyvIqABs1hwEPIqSpMFpnYGZcuXIZX37sMTz11FeQZTmGo5ETtmvvpemtcy0zxpThuctn8AdXnsKXecvZdeQ5QBoKQsNlXUdkgyOAMcCiwm31Et574C7cdvgkZlz5qHPtwzY1gpNBuSgBMO6+627cceedWFpZAVvr7EZiJiQlxNkQ2W7qGufPX8AjDz+M"
    "l156CePxCFmeO2fNkGvnb9ScFMxijk+dfwof23sFV3MDDFzUlAo0Dcg1fZDF1EBZ4fBc4Z3Dm/DqY7fB5AoMN2Jq7T5f6wvgbD6HIo17770Xd911F1bXVgEGqrp2oHxYW4t4c60VdOau0aWLl/DII4/g+eefw2AwQJ5n0Z5H+YJlrAExo2CFhy6/hA9ffRpn9QwockBl"
    "IEtQckEQ3hP591PVWFoAX5cfx9tP3IvR0hIqGBQ6i+6r0nppbzLB0aNHcf/9D+D4yRPIsxx1XaOuK29fw0k6NJG7RlopzGZzvPjiC3j88ccx2ZtgNB55/qNsQBRqZgx1hsnuLj58+st4cH4O04KBQeGukXUwDQn7HjfEWIdF1xXWqxzvWLsZb7vuHlCeoeIKuc4jP4/Z"
    "orYWs+kU3/P+78PDp5/Bz/3Wv8FTkwvAcgEMhi6E1TZbXPZRaNZaYL4AZnMUJsP33f92/P0f+hu48dRNMMa4bhrYn2cVJEXtLjghx1KiUSRrbCLbueb/RMGSvW8qhfErWrbRRvf8hXP4b5/+I/zhVz6HRzdfwZVq5roNU3vSn0KWFTi6tIY3HL0F77/vrfiO138DVjbW"
    "YazFb//Wr+PK5UvIMuULlmCCsPN7ms/mKIoch48cwckTJ7GxsYHRaASdaWidecDWoKxqTCZ7uHzpEk6/8grOnj2LsipRDIe+eChkeYZca9d9KZf+wdZiUZfISQNVjac3z+HhrdN4enEFl2mBheKGku+SJTCwCgdR4JZiDfcvX4ebN46D8hxlvUCuNLIsh84yVxy1BjOj"
    "rh3WU1c1ZrMpRsMBjh4/gePHT+DggYMYj8fIMu8cQArWGsznc2xvb+P8+fM4feYMzl+4ALZuhFI+GTnPcmRaQynfwQCoTY3aWAyZsDPdxSNbp/H45AJO2wl2dYUajjQZTlWywBrluFGv4lVLx3D3xvUYFCNM6zlyraGVhs6U73p0NHKD70Tn8wVGgwFOnjyJ48ePYW1t"
    "FaPRGHmRR/dKBsMYg929XZw/dw4vvfQyLly4CMsGIz8yhXDPPMviQ8FgWGNhCVjKhtib7OHRC8/jkckZvFTvYteUqIJo2dklgCywbBVO5Mu4Z+UE7ts4hYPjdUzNAmBGkWWxyChFQorkPpL5fIaqLrGxvoGTJ07iyNEjWFlZQ1Fk0DqD0o6UWZYV5rMZtrY2cf7CBbzy"
    "yivY2d3GcDDEYDD0qeG6cSARB39Z12BmjJTGlb1tPHL1NB6fnMe5eg97tnR+WXXjbKEYWKUBri+Wce/KcTxw6FasraxiZkqQ366SCvI2GzmUe3u7eN+3fyfuvvte7G5t4Q8+91H81pc+is+feQZnNq/AmqrxRlYaYI3V0RJuXz+Bd9/xGnz3W78Zr777fgDuIMr8/Swl"
    "N+3QVPozeGE1cBOnI2H/N/Rs91JqeZSIdL7d3+SGLbLoOglcOH8WL1w4jbNbl3Fx6woKnePI2kEcWz+Im45dj4OHD8evreoaBOCP/vD3sL11FVrrKHylGBbgxiprLcrFAov5HLUx0FphOBhhMBx6calBXRssFgssFnNUVQkiwqAYuNgjHx+mtUamNfI8R57l0NoVBWMM"
    "amNQ1QbGGgyyHDkrTOYzXJlsYnM+wW45x3Q+Q64zLA/GWC/G2BguYZgPUSmgtBUIjExlyLQrpHmRuwfQjx21MbDGeidQi6ossVgswAwUgwFGw1F8TY7uZTCfLzCdTlBXFbI8x3A4dO/JOlxBZznyPEfmLVmCkLU2NUxtUPnTsICzA9ldTHF5voXtxQx7swmMtRgXQ6zm"
    "IxwarWB9vAaV55jZ0rtmKGhFUFo3XY8fw4JzZW1s5KiV5RxVWYJIYTAcYjAYeIyVwEyYz2eYTKeYz2Yg5TDLrChAilD4wqt1Bq3IHyiN2NsVYmctXECDyxo78x1cne1iezHHznwCC2BYDLCaDXFgsIyVwRLyvEBFFrU18ecqpfzv0iKbkWCtGw2NtajqCrPpFOViAaUI"
    "w9ESRqNRPIBMXaOqaiyqEnVZgmGRZTmKIgNA0ModjHmeu4PV3weO3mJh2DrTSB85N6AMi/kMW5NtXJntYrdaYLqYgYgwLoZYLkY4PF7F8mAMVRQo2d1HmXb3mNIqzfxkRyre2dnBu7/hm3Hn3Xf7qDH3v6uXL+GZV76KC9tXcOHqZVTG4MDqOo6uHcJNx07ixutOgTJn"
    "XFxb43MP6ZpjHfbTRF4DL4/WSdZalnau7S/u7bxSy8F+F0Gk3Zb15EX1NaxljR8PQuCmtQZ//KE/wu7OlitYod0OWXLWcbSsMajqyo1OxqCuKlS185S3lmPqtNJ+ZAkx7ORSPnTmTrhMu44nz/ImRcQXBmNNLI7GWlTGnWxk3O+3xibGbjUzjO8yiCie1No/BJnKXBCA"
    "Us3aghnGv4fwu5jdiFmZGnXtRqhQQNmyf086GsuRculCRP7Ps1BIVGJ3Ytm5bBprYSyjtqbBKqPwu3FJdVvrZnsYwl7dZ+jel/JJy0q5WGWG9eOx+xyscS1KbWuYyo1QtRd9h/EgRiV6rym3+3APdThIVAh8JSS0GWvdqFIb97ODyJw8iVL5rWhtnSus9YdEwEWdEF3F"
    "9+IKlooHGnlGv/XFqqpqd3iE31vX3v7IecKzF7e7g8Ndo7BQ0KSQaYUsy0C+CEvxNMH6exfxd9T+8CQfnhFwX2tDt8QITvAUouR1KL7+HhA4FBEhyzJsb+/gbW9/F+68625/GLrPVItmY7//1cY0PmWtjqija0xCKBoqDv1ZcC0IA79I3aRUntz2qyHa31m8XdyCv477"
    "cHW0001sc9EIf0NiBzxGFUSpw+EA5WLQeGmTmIHR+L8XpoCpa1dYisLdlLbhZtmWpt0lrLgTTindFBJ/gdu+3K54uAJSG4PCF5W6rmA0QQcag/8tmr0LdYx6dw94pnUzCgrsKpoWWo6Fm30Bs+H3CaqE9X/uPNYdcO/wMBU7hIDZhb8SKYQgaFqPZ4SHrja1tw32Ny60"
    "M6z0D5Xy8VOKGmzQbYNI/C5KpDfWWnBduxOfNWxRgAOx1NNaLLOnqdjYBWT+ANFZ5sZ0nXnAvXGWIzFG1cZC1wpFnvtR0cBa46RVHCLP3YGVKYWhKpqkGdUULRWSdWJ8e7MRttYiNznqvPb3XDjITLSQltbbAc9SvnsLDh2Kmlh6lQTSuosTCqFzYTWwVsMEm+1w7awB"
    "NHtcmJCrJvnayXDd1OAMCKmhr/j3o1WGwXDoaEj+SQ7JR/HAbEtDRAqUbmFVUqjNIl+zW5FSb4Z2Z9aXe5pJBL8RzyKxcm+LEBNHwBawL6slUbdKutgu1SKISSkJdWxUisEAw8HAdwgqsaxpSL02PhTB4I/FDRSlf8Hszt+IMW7df/ChaHU3jQSNsBW00P53GGuQhSTd"
    "YFzG7mRMhLYEEGkBsreTnSkSJQHH9wpOABmzf081jBFhHVbKmULkeHPjq5gCLdOTQ8ZgiidoISnJM43a5hE85iSdQEXg1Z3A5N+TjqNtW2EfHRisgc0zwFr30IkOLoz6lkOXbfymUcduR1FThOP7REtTYgk5EbRqipPNmvfReJJzDGFtfk4o7D7CLHZx6Qjl3FV1jIzX"
    "mUZt3OGhjIm4HcscxRBbr6jpTpWOXXw8BCC5Wl7zb40vVsqNhgktx0YuGFNQnTQgtiIC+XFQi0TvRkngR83BIAHJSUbjtalCnLqsxPScxAGCYzaBTPNJhkHxbFFvw8Ot+D0K9jKiCAi2Kbdffa93DRL3QGrljvVp+KhlztWxSG0VzOFwCFON4wPN1viuB+LB9SEPtmGj"
    "h9HNGAOlFYq8EEUqpOg2qTdhk6ZUk3/X4Qj5sSgA8U1xav6bVNgnEVkkkn6oxWOLsfUqGUPlWBjeCxvjf4+MTm+6Va1bIaKdiHh0XQrY/+wwurXU+EHV716PiZbSVeVeY5EX/rU32sImfy/8LA2SY67o0t2I5cDa4cgB0ewzGmPHRki2vdp3cdZy41btr4eMWrOC6Go8"
    "NBC6eiu4U0rk+bntsB9xIQ0OSXjPcwy1sNa4omX9hk4k6zT2Pul1IBFe2gTEpsUxdvU+eMNhgozFokRZlk4b6ANXWaS1h+chLCiazEaVStUIyDLtOHI9RM39MCdpJ97YHLciigU1Jb3tUulfFOonzjF9HRZ7exkxU9K1MKZWYWGZlhEuqB+l9vUhSfh6LIinzfZFpVpm"
    "DIoBzHAkorXy5oQQqv+w/YLwXjeexLi9tYlnn3sOe9NZQslI+TgtNq7g37CUY/YkZYf53Upfo2A366kVIZw1bfv9iKKUcKHkGD7AsgCHGzgIq4lEECz24bA0fk/yYGp7K4V8DXgTPOsrrhIdYBh5HHhuMRgUuOH6U7ju5EnMy9JbIbe8m+R7CpIiGzAW5c3t3MGyvr6G"
    "7a0tPPPsc5jOF0Ikq3x3jWbholIJCYnC55jVjeuZbWnSOHHObZx2ZcFQQeuoUka2opCDTFEPGjA66z+beOCEQqkoSbiW3QVDBMUq3XTjaOyFwv0UustBnuPwwQM4cuQwyqpy3EefyyhpLyHJOnamgmvZ2JE7nKoYVCCt9n9mk2e6dQ/1cxJSg7++DWHi/NLKSOoPJGpy"
    "Ca9JL+3hT6DvRfjRrCN9aLeCnIYfKMkpEgEu4c0WRYG6KvxJ4y1zA8gquqloXeu/2VpGnmv88Uc+hv/867+Nc9vbzk3CA8o2yGiEcVzHKxnNAybsD9IXyLaJRkqAxsatAkLG1Jw6+0VFNWGyLPfoTaYYUqt6TlX7UjfVZvZHTIGlwWYsuuHfbZL4Qo15ndBhZFpjY2UV"
    "3/bOt+Mvf+93uWVHXSfLCrRj1lo+VSHHblwU+Piffhq//nt/iDMXL0UPryC1kRa8LPSHUvAtPfUh4s8aVYaKuj9udU0yoEQSpW1j8NQYF6om7TsWSnAcBRM3C3mwIA2QapKPSJgShg6k+X7ZgVm32sfycIh3f/0b8f1/8S8g9yqCEPrCoquOI20sWLbprKnRtWqd/5ma"
    "FVlsmvdCrXGxWSCxhJpEB0jiZ1luC5oY+7VOWQTG2lbIsgr2BB5KYSmjHyBr6RQ6Shz4CPto6t9KNQ03dlj7hovRSQYWtiXy4RiOhvi1X/sN/KN/9x8x3FjHyoED7hRhdpiAmJG5D6dL3ldfGnNTsFIJFqWWJb3Wc8K+g3uMbkQhskg9ouRcH3MPuRUpJR5QRdQj50/b"
    "cuo6yLTAeU7F0b4DWRDwi//9g5iVJf7Gj/0IptOpozWoWBYbQbpMrBIRa+PxCB/43d/Hv/3VX8NoeRkbBw8kvldEUpIk3D5FHmOaPIiWTxWJUa6Lf3YI090YmX3GmRZPKDybITSXhWyqjxfEXc91CZekGA9HZ4cA8P/2xz6BeV3jp/+HH8csCLBV3nSERGKZkOobG92w"
    "25xnWdZ5hrvsc+7gUEnjImsD0kVe26xPfq9qO5+KRUr7ucywT7Fp2z5gn4K0L0er1+RGJO7K1AxqtY8twpjW2sU4eUzDGuuTZ5o3JwuWtRZZnuPc2TP4hV//TYwPbmBldVVgco74pqIok1ojHxqWMiExmEva30T9j1Q46s30EhypyXwW4YnUH8Qp/HyVaJPbpt3cFmNT"
    "epGbOC1uZBzg/iTvKKulxJI4SYIWBm5wlrU4cvwoPvDxT+Atr30Ab37TGzGZzDyO5gtWwPio5adlLYpBgfPnL+DX/+CDWDt4AMPhIKoEyEtv5IEaOhvTtvakayjeez487iscSQHkNmWxswnvi9sMn56V7iPt69rra9OydJJSZ//v1liH3Xmccm1jA3/yhS/iTQ/cj3e8"
    "7euxtzfxHDiV6o4C+K4ocYsI90rggrUf8Y6OuCNQplS8LnPMPMGbrzXBtVJz2g2RvI/DPZilBVJUxNZGsMOjSH5BW8DceKC3Qyyop1In1rE9hTHPMliTxYLFGfvVsWpGJmoeYGMNVpaW8DtffAib8zmOnDwJ9nwTpTPUiwWq+QwIbotW2MAKGxBqnYIkVOty/JOXhTk9"
    "6SNe4DcztmXAR+ieajIJJ9y6NqlrlGBCLvdBpgk11A8WBQKcuiVAIQZFdHI6YzGUHZzrHHVeYDBa8tIn415fpvHgw1/GN7zzXViUVdy0hu0fkjHCA97WYDwa44uPPIo9U+HIwQ3/8xR0kYGYXSwZW7AxDvOiVgKOXABRSwospDgkHMNUdMLbfyNFnJrryci0oEtktBtk"
    "3xETpQeZ7Hj2IR0FOgsnoHxTiJXW0HmBqqrF5pKRDYf49EMP493veAeKwaDZNIYRjhrqgMMMhRGgzx10ROlMBNpQfwOSFFROMwmTO4fSuDTxc9nafXFt7vPHax2YWfP7OamoCWovsYxwg3Rk1NQ8PBEj2YeI2tokppiRzNNzX6PzHNrUUNYmqFxqMuf/rhgwhDzPcfbC"
    "JWTDEbJi4E6SosDm6Vdw8fnnMFpehRoMQFp5MqpMhBYjqbGpWZnAH9pHrXvPqidFJC38aT4ZOgBm4kGlVMTsovaAUnscB2R7s8RAqFWNNz9kxyacJdiTPAncg0X4DsumEfNKKZSmxPDgARw+dgL1fAHyDqCXdrZBipzUxqc7MzNIy/mpwbbIOH7V2fMXkRUFdJ6BayAv"
    "CpTTKV748uOYT6dgGUFPwn9GJtEgdczgXmy4JydJ4FXctxAn6ftuo/d+r0emPLTbljCtGKwORNAJdxAUa1+gDl53HQ6cPOkdGBy2l+c5rmztwDKjGAzTyYiAdqpUAnHY4LDrqSOk+jXD3EfiVB4Pi5EWHXOdvukKPayBJFCVUmDVYdyqgYewD3XBsiS9dXMN90vkkJ1Y"
    "G6BLovWox7WbW9Hy8Xo5UNBSLTZ3KbbSnqd1ljlwWmfI8hxQhMV8gYtPP4173/U+3Pb178by0gBZlrey5YLGKo2xkrWffcCm20iZpv0PxUpwi7gVShE+JcspLmQYkeTYAJQBhFXxZLcsvc0pjh/OoJ8wHhZR9+aKhg2ejFCZclIqNtidzHxCuUIw/46GepwWzuY9W2iV"
    "oZ5P8NiHfwvTyS7Go2XYqoria6UbrlmSrtwasQE31mV55rlMXrfnMctnH38SNstw4v5XgWsTNZFhjyE3tyx81hEKZdctLnHKlRtC6f+VrPZbwD1DRmqFQ9Wm96LsDpRqhavaLslajGawKQcr3h9KYe/ceVx4/nmsHz2KYjxuFkxKg7wkCoqa/qZng9eUTJ9KpCgaFQTV"
    "QqeTasMBRMIAkYR4mdODIyxFqMVRasECAMVJLM4lLaWMDLPI9tsO7sfXacZWeXJwr8CRqJtQk5Zfugbc1RQ7nWno2jHFZbijLCW2FdHl5BTO34i06yTqagfDA4dw17u+FePVZYwGmU+5kmnQgksVXTgFvk5B3xyoBk0IB4uHW7XItMHSpLENF4Q/y95JIHCImvFFhr5a"
    "GeYROh4Ez0DG8niEXAXhuWC1W/ardXdST6ZT8ADInBK6wRpESAhDvgdhA2MZKwcP4+bXvw3nn/x07ORU5tj7mXZsdEXtuENRrPxoRORIt4HBrjxTngHUdY0Dt9yG4dpaJPW65J9wrjfFhpkTBYSkD6D1vuQBm0S9BWpDmxvkiaKp0kR8XjLdpnWvW6L4vdKuJ1g+cE86"
    "c8OsaUI9wkQyv3QFeZYhzwvUpnRUh0xHDSxpFbfmQanRkRFHvFZ5x1JyusweCQ714GkSYCdKMbk+3lTvvo/bFCpK7pMuS6FZMGVJIemV3/Q4RPQuPfb3eqAOYJuww8SDzFBQHc8crdwJUnPaYcloehX9utzNmWW5O5Uzx0QGOUW8GgygFDDIlNPlCV8flkUnuohSkoIS"
    "7W0DYdUnHHOrA0PPyRzYyDb8PCsfuoaWwSyWCcLrPBTlgOWBVNRRLo2HKLS7yRWQBjtQiEFk7E1nmM5nrs02Dmi0Mp5MdgQEsY0NN6pFNZ+5IlMU3iK70UdqL/+InQqJbaHcGgXSom7cKrT2r4k9wdaf+ip+ViYtTmhCGYKaAde6d3vHlXRMZ3I6ynj9PbtUPnpMabI0"
    "oTuic1IbZXw8pcniSS/ICbhPcDSGmB1Jyvu3KVh2QhytXKFSmdd1ypxRJaCIpOFQMaxXBQ6gov7nvhV40iWOCz5meyEezhVqZYe2ZDuJ0yz3xC5QQ+/I2jPivpe7jRZyzyiJVG7Tx3Ddb2UaGMxWaMiab1MgraBZN0u15J7xXK4wGmn41Xr4SwnmuluVs1yfUg8wlYSw"
    "ctJpyHGBBcNYMvc5wbZSjpSMO2KZItRaxjejR9MFgsLp6X6PqQ2WRkOMhsPIXeJWqrUT4CrM5gtM53OvX6QOzBlwEw6EV06H5dD9kc7cd+qGH0TwJoTa6zLbLpPJvq25ceN1Cl5loYtUhKzIkeW5A9xDWk6eQ+msERD4kZe5tXDoGQkT1rWMdWfbqAF6gF9pjthQBinp"
    "qJEEaXgmvHjgJP8u7WY50nviZs1amKp23a/jHUB5/aTyxnvB3SIA8MqTXIlJEKODA0YTgpxsaf29F8TR1yKNNnutNPma5GSFlG9CPdbXMtydWjSm8EiymHbaapGM0IDl1z6hUlvhtFQyEvDjWlSJawgb5agpC1o4sVn7wmS5sbVm8idezDaPMgvlMQmlNCR0ppRuUjnQ"
    "ymQD0iw5kbmQZOjFumV7R0e5K2SB7wUWdjPDc+LPLgJFmth74oZFLgi21rhitbQ0arBH2/hnBzqB1gqLssLedNFo/Vj6YCLlmkmyp+hAwu/nWFCy+FmSj9nKMi8mJ+UJuT08nnCT14j6TSc6JjCriIFmmbPhsSIzcnfzCqq6jg92E/bKKXZFXZwrIZ+2DxCxYVSKotdq"
    "EwTDwl4ZgBz6gzSMKOHdycwGCYLLPMbw2pW354EiDMZLGAxGYOuBdy/GTh5P/0wExr9S5DmGYmkV5WBKLtLjdXGvQTf6yZ7JKXEJbVNhOsGn3KXMMHfHyk4DlHaWSQdL4jUQoo6yRVGQ3urp8oKBdhZ6GvPdmkrlirN/DbqfcLrVYZECkY1MYw71kdgRJL0NCTNAxkaA"
    "NhAYndumuwE0oYcM6jAkTk5Wr7i3Im5KFBbEr2/AQhs3paFxStNukrh1bgDzLq2gO25HUBzk0nBGQyyvLLkx0HuDBfkNx4UFoTYWO5OZd7RsEwh7tlfsN2JhfOgEZjZWzIACBbNGaixmlO+wuMVibpw4AK05OghEW5ogQSRE7RsrC60z7G1tQesRTtx+FxazvZYXeGti"
    "EdtUIp/4Ih88D247Rxbr/90VTcuMQZ6hUATb2uTKw70OovomctKHbbh/Nl5ziZaAmFrdcyTiaoU8z/HC418C8gI6K1xR1qrhUynVvD+PH5J30EW4/wMYLooktThpTSfNzfVqz1fU3NckN7KRRtKHTVGSGs/+w5JE314lDwFtbwcW9ItUmpMkYog3m3yg1MKv+laHghgq"
    "ekCm/s4jidemPiq+AxDchSEQqxSmEwaCcdwjv64PJ7kikPZR7EpFwXBi+YuGO8atWGMS9CVuJfq2q4u1ts3rFB8+p6Q9mQDc4aG3pDliQCEP8g+HA1esmLubVWHMVtcG27sT3wBTJI9KaJ/RcuiIJLquej90NezpJmwUoFQU9uosj+6Z3JZ1iaIV47SocUNwAQyha1XJ"
    "8kbnOWBrvPqbvhv3f8v7QdUUUN4qWWnfBQvgusWKJ6ksQCtj03cjme8yBlmGQ8tLCDbcYifmpDqecV4ZAwuCicJqoDaNiNz6qLUQ2iYdOWTPEQjGtq4xWl7Fx//z/4NHPvth6CyHqatk7ArFWXlrIkXBuULHyxXkccQQDQO3sERKNuPS5aEPuG6chmlfelY4IRRRy/6d"
    "Y6pVV7MsMLAWiVqStoPOM+vFlzr62XZ5TFtERot02tkouL9ZoIkTb52OcURJOivX1ShKxaMUWfJtjIwbsqpyuBe8SX4oWCQizdJRqKEYBH8fC4CVB8ltM2JYAWRrz5OysdUOxUuufruShDQwFLFfa8ZKmwSMhm7BWINBXmBtZdl7VSUaDoFnO0ua7d2JuAytbg/7Je9y"
    "U9zCtaJw7ZzSoKprUK4BVp7PpRIvLFJK0Fsa4IIEtEziYFGZjhgWW0dqdT9Tg5TvArIc82oBbedYKVzxcLd67RvDVpAtWp2uwF4a3zJxaDIw0BqHRxkwn7iFhrBGkaIeYiCHXOm7EIuqbrzeLDszvZQ2RwCbxHYF8dAwyMliUOR+a0pgFQ4EbzuktaNLhDEyeJ1pFXWP"
    "pEiS7hpgWziENAWMfXcsJcCcMvT7mO+yLrTNAAipdRS1QpJF90YC0+pVfLTkcVn7C6U2kDqYyv67F0JPl0RNIQnOj9xemQpCI/VkocUTWbTVUVXPPcsANG6YSusmyZpU7LiiiLjlNsje/G0yL6GoafnDKZZrhbRnstidOfvi2hgYZpDS0IowzLJE1yexsXCYBFsabm1U"
    "mgAe+QASjHX2umurq62S25A74mltGdu7Exix4g4mhg0m4yoyUfrQNuBnQxYm2/CFFosyOgTU1IwmShwK0W6EBHeJpWSIvA0LhA+VclYxSljiaAVAR9sXAoFJg8lG4kUDoqvkUwnPExN3/d3ENk0Tw1jXGRxYWYpOGVru7fo0n9FKyG3zKsOO5e6/1PixyfaE6TIEv87/"
    "FgOLzPtXKt1YHpEOh6/Ho5TbpQeaSrTfkTpbKUnyic9hXGAh9wnjKok8R+rR/yYlX3wWJOQ3JBZfkQ1PhD4xcSSZM3qMsPA1DPzaF6Gt5elUtValBfo9s1jeNNTBp6jnKnLPm2yKVYs0Sulo2nR4lHxfMwkoj6H4n8c2qvcBwDAw0Arf98ZXY2k0QG0MFlWFuq7x+Cvn"
    "8aWXL2CYZ7DiYf6+Nz2AQ6vLqEyN6bzCoqzwypUtfPK50yiyYIli+4mYaNbmFikImwigPT6lFLCxsuKQNZsm+8piSCDs7k1hfPqMZdlPCcF3Qwlq684Tux+GjUVzUVZQ2vUWIVHIZbZJ7p1wVXCrq45Mi/zDR4qi46bDY6z7eb46khBDNJbIiNtAFhtm9KhRFaUdJYmn"
    "JNyq1j/Qh1fGHqC2rrux3D8WQQof3ANbefePANFZKTKk8Pso4S6xSNZhaTUTfatEQQpbREWRhBs6K4cDatjaJi4SIRqOJX0DFOPihLZs/xSa/ayipHIDLT1hi+/W+W+Uboo7jHTsB3ZFDCuVyVzr9SftGqW6rTYFLLGUEC+07ZEjR8O0feVWAfa4CqG72QNEUaN4OjnJ"
    "nMewqKEQcDDA47h0gTGMQ+vL+JbX3QMoDTY1Nnf3cHVzC9u7e/jkUy8iXxkD5IDsUa7x7W+4D+PRCGxqbO/u4eylqxhpxocffw5qkEOFTksA65E8GjCvyFhgQRwVmIO3djmwvg6lyOvtpE2HjdY7pDX29uYuWCLIjtxvEx+kTW8aZiEJ5Xg9nNuljd3YbD6HNdbRCqyN"
    "IzfCIkQWmDASwrtGxHWG6HLhXVjDdk6Mz4GeIXHRsMJvWOsNEM7hQezQNZBoGBtfK3ivdIdJHVsZo9AqmgHCtqgQYjscbI1sDL2w0eueOWxn/ZhnU9U3c1eSEh6F0EGGg4BFIY5Sal/Y2bIobmmH1NLB9ahHhMcZN/bcPa1Jx4UhMS1oEUu5l8BF3YScdqeJ1DWlN9a+"
    "02H1dEgJ0bP1C6lHZ9grf+xlv3adAtIVIXrheWrmplYoI0UQPjECa9DXpoCFzoq7DaL23J9FVcOw65a29ibYnc1R1ga1tShrg0wpF3oBi+3JFLnWmC5K7MxmmCzmWNTOS76qDfLglMkN1sdo1s7SAz4q6KUjgv+69bU1ZFkGY+r4NXUtcC5rkWcK0+kMs0XZ2OiEbERL"
    "MNbjQhH74djRMhq7XYIC2xDT5L52Xi5grHWHiPWrPO24P0wKHFjdYYwBOnbbSNy9fRfBwpBPEci2CIyU5terWNjETolSr+5Q/Dtk58TOJZQBxuHlMYrM40KERMfawR4B76nu/qT2ds9SMM6e8GkFR6RpaLgjT2EOi6BgUOU/C24IySS0nJYUlLLNBIEG3w2/LCx2KGKI"
    "FPFjt73jyEWLKyjqjVLuOoQKTXBc4lArTEIQn6UNeF80PbWsfLjl7CrrS9Zp46gn2rsHmN9P3BjHt32zMKhdqvalOqR6InHDyxPjGsryqN+jJh49jmXMsGzi6R9+zDDPMBgUWJQVcu3wjVwTNoYFtNJNZ8SMYZFjPBw4hr5yTHJFwMaocAEIxP7Ebj78MGKxl/U09AJK"
    "lwCic11bXkGRZ7DWJDjBYOQ6q4qdk8FkMcPe3CBTLtbMm+24LNdsDjN079daA7MwGPIqiBXQWkEYXcMsz1BXNeyihl0YoM6RqwHYuiQaKAWCduaFECZz0fZXWvZapHuhVEYjrYlDhwEgYmLwjq0JJ6ePHyg3uxFh57juTwuP+wwPL48xyLVLQKbGt8sCqU5RisBChJ0f"
    "A5UoYgF7tImwKt0My+04t4ikYZSUpn4NTaNJRmeDGA3XsNQbMXebWR4+E8cxQ+L02xukjF6EpwvEg5JkdUi+Gno8sHpsZCS/wd3fXWkfdTosbsNU1PH94f10f0DC1biGDqLzjvt0hk3bKRwXe7eo1HJG4ITnIw3niGWfJjocfyVrw8gU4czVXfz+g4/ixMoI23u72J1M"
    "UVY1Hjp9BTrzMWNaI88LTGrGBz77CO4+fgg7kwlmc5e396VXLqJiRuYFr6EoWnHrN4xoTjrJkFyj/DVdW1nBcDREbSqRPEzIxoTXv+cADAzO71zGdLKHp168AN4+Frds4S1bY3HpnqcxPgVsX53i0tVdzM7v4u69t+KAOY6aSpBSMMTIbYaLa89j695zUFOFq2euojx3"
    "GQdnN+BmegssVfFm16oNfFFzw1HKJaa2oFvctA3L2qUfq8i76y5hYlHg7ma7KVapT5a1sUzGe8ZYxuHlkcMkbQMAGzDmxmc+Bv1mGJ+8T9dQaTCs61j99xjbUF6swHYoRJ0JXmPCHBcbS+vTkqzsjOSDa0yix5QGfZ2JpUXZ6WQFMvdfu54tXW+xkuHJvD9Z9Fp5gx0Z"
    "YBtI7XFiznoUhgn2tO/qW3ydanE0+rsxYVa3j7ixw5LnnsLPjUVuOPFawi0kPuKExA64yykQ2zul8PKVLVgw7rj+OE5fKnApy7G9M8ErW3tYlBWKIocBI88IF3emqC3j7lPHce7qNq5s72Bvb4ILO1PszKbYGBbuZoZziXSWIL6TYLnkcGOYJnIyE2sxqypsrK5jNBy5"
    "HLpgJwwLa12UEzSgoVHaGpcn26htjaquoGkgSIMKhiyqvILOhrCZhbFzWFqgNCWq2oC1x6kUYKFgdA2u/EM8ZvDAot6ao6zm0ANBY1EKQB21Yirwi1rE4mi50xrdGma5EkeJv0cUJQdV3GrJwAk05GE0LjE+zqvZxjaXnGIQxcGlJYxy57GmfIcwN4yRznDfxkb0brfs"
    "yo0W4Pqzm5tYeM2jAcMkImgk2Kht1inJljxiqGn2Uww4SbYNhFZCFYskH9V1bOk4jbTX/FEv0Rl3e6lV6Ckg++FMfQqWNrVBqh32qwXcZzKJfXhYMgWn/YtFdZe5gMls2yugFjY1tJ9wOvVMitwhsX6NBchLHPbt4qSHTxTiNjwcJ6eg6HypiLC1t4fv+bpX4Vteczcs"
    "AzecOIajBzewub2Ln1xdwr/92IM4uzPDyniEK9s7+POvvgs/9PbXAUS47shhHN5Yw+b2Ln5iZRm/8Cefx8Mvn8PK0hjDPMff/5734tDKCoyxkENY8DS3llHCoCJGphT++LNfxhdOX0ZtKvdehQMBs4WtLeaLChqMyXSChSkdVFVbVMpAh9QVsFv2l4SdvQkmu3MspnOY"
    "yQJUEypbQxFDkX8wCdDZEFtmjmzHYr43A+YLUGVhYMA1Q2WIQug4Xnhyb8oJ63H5pFaqSsBTiBPKSlPfqGGEW7HpIytoIISOhXVPl2B9SMOBpSGWC43a2qh6cKC5ws2jBT742H/EQlvkWrvk5dqCrCt0Nx88jjdf/1586MwWBpmCsXLUR0Lz5ZZERFINrPBEi0aAnqiR"
    "aR0nhajVVARoJ9FhIthkHFRCyyg7JelL5/8tCX6hjuVNe4Jpvo579MSOUaBEN5hGEcmtbH8BShxHExN+SpQd4XcljqNt24e2qLHPLydJjuEmaYX7qqx48DqvWrJcuWXVAe4B49MxA3HoUoLDLnGu5jSxgncVxsad+Rz3nzqOH3rn16GqrSOE+tTeLM+wOh7hm++7Hf/+"
    "kw9hZzrDTYfW8JPf+BbkeQ5jHR6WKYXCk/6+dwITgQAArzRJREFU/TV34ZlzF7GoDQ4tL+GeG47jYmZQ1oydhcUxaBxRCrVPoKnqGle4RKaBw8UYJzfW8elnT8NaxmBQiKKtoJXF5uYMhy/dgJuPbuDU6CCuzjbxkUtfxdPzEmvDDMq4zyTTCjuVwVunr8M3H7wNp80V"
    "XKo3sWWn+NRzM5jM5ellWgEGKKnCgSsb+Jm3/CTs3gJnzl/EYmmKT8zP4+z2Asuc+xSrkKbMHe4OtU0Zub0cIWHnQgLXQcKrSjZ98vBKILeG2iE98Fno4AJ+UxuDA+MRVge5WyCQG68VuWJ0YLSCl648iL/70X8BHFx3zFAQUDFQWcDWODxexke/8w1YLGpkukhspDkK"
    "nhNvihC8EzeI8WssRVDaddaMUebSpsPW3MS6pjwf0ZFIWeCCsnGNpGqx6GjUJ9ZJlEiaaNK+/ZWMC0v1dcInL2oW2yOneM8tSCe1R6d9bdiph0oVHUelxey+PeF+CdDS85k55chIEhh3K/S1wHySblDMwgkx+cGinokWW6SfUBwx3J+b4DNkbSy4i7rG/TdeB6YMlksQ"
    "hzh6g6oyuLS9i+VBgfXRAC9d3cEDr70Lg+EQZVVHk7KyrlEbg8m8xNJwiBMHDuDZK9sO6GTCwljsVBW0BYaWYTx/xoSxxwLLpFB4dr9lwrysUOSZB7ndiTqtLU4uLeF9t70aB1dWsLM+xeWVLSzN1vGvz38RlbHQcPymyhJGWY6feuO34HV33owrl7dw4coVXNmeYGfy"
    "IB5+5QKWitxZMBNwZfMKfvitr8cPveqbMN2e4uzRK9idTLGkvoJf/MxD3prEwpoalHnulLHozyvhJBmoUSoIHZoSXZVw34iJMRKE9q4ikl4QdICpTq1JsgkPqDEW66MRVocD1H4MjB1upDwAmgmjpXUsDdbBypkpUu5+v6kNVpBjWtaYLkoMR3m0Ug5qhwjRsxAaC0mW"
    "lYaOvhBYT+od5k3ystauA3QFidE1NhCrrRaGxeiGIHMbfW9xs5KMygQW5q5msD3KtShV7X+h1v1A++FdnXqCDkCfya9JCAd9P2Q/J4a2VXL4CL4W8N5HlwBFIDyduJF4xpPcqiVpANySZlCa3CtveBfB58YnwIl44Y3tvIWsYgtblyCuUShGrly7nmndkPdAqLlCXZeo"
    "qwWsqTHMMmSZC1DYmS3w1ItnsbY8xnhRgqsaZ73Jnvs5jEVtUFYVKssosgznt3ZQgZ1OjglsDBQRDBM2hjl+9v3vwcb6GHvzOWplkI00Xn/njfgrbPF///FnkY9GYBjMyhn+yQ/+Obzurpsxmc9ABbC8OgQywl/9xq/HP/ydj+C5y1tY1UNc2d7GN997O/6X7/kWTMsZ"
    "Sl1jbWOMkku8477bsTmd4QNf+jJWANiqhB54DaF3N0gdoVsHCaVBFLGLZ+qutaUwO2ygSLhX+k7Ghj/nJn3YglugsePMrQ4KrI+K2FnJCcUyo7KM2lgMtIYZADXX4NLz1bQbu4wCrC8etQfgVbuL5K4NQMzOhLDpIfaCdb+dLjKwNajYp0cpCZvLLXPX5ona2/3eItMH"
    "CAv30F73KO42JImEILVBj94YclqifciofQT0dmqWPPD8q0lAd9qvkl6jgPUTF7h3ZIQA56mPHUv7fbacMti/1uoRLNJaUqdPR+bjGG7qO3NoAE9MaxzdrnBcAc/MFri4mOOlyTYuX7W4eHEA2Bx7eohRMcMLdYZP7jKuU4ynJwaX5hYv7mQ4v53h/CUNYsbW1KJQCjvz"
    "EoXWuP7IIWxNJqiN9SJm9rHsjCUv7ynrGlpr7JYVppXBWp57jaG3V9mb4M+/+dW44fgR7M2mYK5hTAVFjMlijluPreGGg0s4u1vCGsbbbz+Ft7/qVpTVAgSGUxcxdqcTzOdzvPXOU3jmT6+iqissKcKPf8s7ULMbUZTSsFxDZRl25jt43S3X46OPPoHpbA421jOsFZhV"
    "QvqjoCagls6xdfQ2a2vugLuJ1k6K6ZWKbq0cgWWhmmhZ2FfWus54PHB4U8igFLwkZmBhDGZVjbFS4IF2Gj6vC7QAlIa7SbSCDtY9HHBQm7htJIOWIJEGTFE6NRCAUaGjnIrEpjicwVYGgQjL8mjwKATcitCykmm9ImGBk4TbtkZC6uibGg3wvnQnboURt8BzKfe71ii4"
    "b2OUujX026DKKtgRRLfJpcm3t4oLdU+hduQX2itptLLa2t/bYS1R2lX5f5Y+6MFMjYWrJJigGJiywmWjscoVtojwZXUWj6uXsEx34VKVuRPY698WOsM2E9aNxQsLg/Mzg/M1Y5M1zpUKc2NRVDWUqTEqRji2sYZhpnFstOS6JhCqusKiKl3r73WKO2WJylqsjwYYkRMw"
    "Q9z8W9vbODReAUAYZ0uomaH0AjqrkHOF3NRYzkcwdgYmwo1HTgCUQXGGAQFKj7E2XMJuTpjtXMGSHgFMKC2wPh7i5OrI/RyqYbiGQglVAHsDQC0YI03YnldRld/m2wQ4QAUipKc5cL+sPvEWS3BNJXhI7WRyFqxz6QXekofWljHOc2yMC9ReHqUCo5zZE0ep6bAid61Z"
    "ArBwNLU+aUgTYaBS7ybyCwsfbN0BqdsupCF3Z5hnidNI8HFwh2o/rSB2M8LGOXVfELbl5CVG7Whw7tk4dhBxTrlgoqtKFnAd8z6BgfUx26WOkbkH75Y1LF3cZB1tzzVGvT7KfntdmRSwVnJHh3Yvkm2jPEFRmo4cGs3Wu1JJ3FP3slJL19aQ71TczLF1WkLlC2Wh3E2U"
    "gfG6cY3bB6uoR7fj9ycDXKIZRpphjQOpVQR2Le4Z7eKWfIG9kcIfzxlXFIOs9TFYjMrU2J0vkM3m+OOdF2E0Y6nIQVWORZXBGoURKSxpwp1ZAWM8g93UMDWBMYTSGnt7e6hL4Imrf4ojm89hMWdcmZzHvCxx/upFbG7XWMwrXJgugewAUANcmHwOD539HKYl4fSlp7Eo"
    "LSb1HNP5CjavGpy/OAb4KJiAhRrgD65qXG+BJ7cVzkwybM0MdGUwuaiwtw1s2wJ5brEg5bsMm3TVJFll1CUuBqpckl/Scv4mlvcMp6zrhKCZet5LZwtrgVGe4dDSwPGnfHFaMKO0Brl/bZWtUVqLaWVBXGINFbCw4JF70QHaDjIerg1KY7BVlaB6gNqlnEH7Ka6yjIFW"
    "yIhATIm3fTpoEfJcJ+nlgefqvNwbFUPiZSWkVCmAxHF05vYGrmcrGA9rUmIuugZHqk8A3h4R0ceNQ+JGLH8u920LEzWEEEnvy8PqA9p7sKZkhkVz0rXbRWnYT23qRMA2OuTCPlCwAQAl7619Okc+sjUeryBhCkZNqoqPt5chqoYVJjXjKhGe2dXYLTdwfjrH6ckChSbU"
    "lbuZ6sUc87rGngFmxDg3J1ibY3vKmC8cwdN62Qxbg6qqsVfVyMoaFStUlkGlw9B2jRNyzK11oQVuNRUZ9eQ7g9mixKxcIKMCT+9+Cuu7GsfxRkzsFrbMDFvYwWOXH8W5neexW74Xub0FNTQuVV/AU1ufwTLeAp0fhtYKB+g4vnz5v+PRi49iceUOsPk+cGVQ5YTPTDK8"
    "eqSBjFEMNQYAvrxZ40++aoFFgeuMxpJSYJWDaOFJrpIQyq0wUiSdc6RNSfNOsYlSLU6PCsTnlqyGhUc2J+iuw6wGmcaB8SDpbEprsZpr3Lu+AcCg8u1QToTaGozzIZ49A5iZARW+WAWNpL/fF7bCSqHx/luuQz7MsTDuHhpphZwUZhb41NlLqCwjj0A8tRQb7Jw/2BlE"
    "Kn/IG05Jp1Kb3BzuDaaXjHmQo3gLVkmS1EWmoOCONenSLQySWjYv7YCZtgVMmxzaB+Hso0PuGag7jVQm15/7oULUYrh2V9foJYFxe20hyKPUAtmpR5+TrFXjg9B9hRQYyZSmb8RMv/gguY4g3CQxtNQ/JdYa1P5nzVlhwRabdQaG4zuV1qK2BqauMS1LzJgxZ8LLixF2"
    "Fwbb0wqGK8Ba5Eqh1BqmrmGVk5sMM40HxkdhnD0DJjVjTzNWswzXabe9rI3rKLUiKD86zucLTGYzl3jMFgM9REEZbhy9HQc2juP8Yhfzg8CF8/8IO9NLWORjVBO3ybNlBlMNcXJwHY4P3owSjKFexfP5M3g6ewZKLWG3qkFsYPMMqwXh1Ihwa8aY1RZlxfj1zQU+U0+w"
    "pBhsKtRkXTCsp37IUI1GndZNZabg1cSc8pYSaoRQTER7lObpi1HtxADZuCELX1Jbg1xrHPK20TZ5rhXuX1P4Vw/+f/DC1iUo6xKZsmHh2yPGC1cuoihG4NoIF2SPDzGwa0v8+Id+DsdW1lGzha2cWV+WZ5jbEm89dhfec+sP4XdeuYQDo2FMYGr84xl5nnsam9hW+u21"
    "8e6xTY/Quu+ZUsmNFz8HI0T3Z15uxu0SZdvrACR+2D0e7NQ3GYnCk1CY9iF7pi4d+6RJy0LGcquZ1oNMdjyqR5zYDldFj+d6UpcYXR1R26W0vZkk2te8KwFiO+WaW6NmaxztPDRuHGRjwXnjtmmtAzktATUs5mxxsQLmlbvopbHYqxmTeYlsUYIZKI3F1BoYIuSKYABs"
    "G+BSaTEzBhYKrDO/LWVkWqPQGq/M93C2KjEtGTnnuDlfgrYAuIYxjjWdaY1ME1SWYWEsqt09dx5q9kx5BVjGUzt/gO3pJVzZ3cSZzQu4ONuBzoYRBK7rEou9OfamBvPdL2H7q78M5hLbk23sDZbBdgBbzmGrCgYW1XwBsowlRTgzB85NGVfnjFcWzuOrLg1MtYBRJpJt"
    "SSnA2EZ+EkS3PelH0X2y4wIjjSD71foNfmx9rFqzFQx3gWEg1wpHVkaRNU4C4xrmA2xOz+Pff+WDqKx2n3uuwAPvS1Vb5DVhWBSJ5lS0dQBpfPrq0+Arpplt2SPzpsRLl17Bu099J+qqBsYhXr4p4plW7p84NcyzJkTGMRY1Q6kMDBO7JlaqBUQ3KdLSQkliUVb0CUQs"
    "sMR9RryIt6SSIboGQM49xafXnUFyr9qTWmtjyPuA8MyMjCjV5fE+okP0eFT1tnzUrdB9tDQ3S3Nbc3DNDUGHSd+OGpcgqWewSw8u8uZP1hqHW4kPeFpVOKUMvnGFUS8sDipHa1hUwKWBxYvlHHvZFB8xc5wtS9xEFd67ZDE2Bidywu6ccaUosTWocSVjEGp86CWLl5RG"
    "nmlk3spjjTWMVdi1FstK4aaMkMFgbtgHswJKMYidbqyua2jYGNel8wyZHkHDYm6uYrs6i6kpYaiEyhVooaHYjWlsDdjWUJawp3KcP3YYC2Mw2VrF5nQBVVZebKyj48PpPYNPXbWYLYAzexbntkucvlKiyHIY4zvkuoStSheEoJXTLkpHZfYWWUhiK1uCd47s69hZSZl7"
    "BHrTPGEW1AcWASqWgVwRji6PfFajdL5wxcJYJ0bfwBiLIoOznBLWMZp9p+PRMcut7Bz3vxU1bIYGTzJXBpjOc6zoJdcBGufYYdnx6ywYeaY9rcGpHaAUjLdRdgx0xtbeDLPaQmcaVJpGscENRpVAL8ww1qRyF+ohfvdJppI2SgS99hno0TUw7n1qQ0K12GdkTJ5vIdfh"
    "Hv1w02FJNvufidaQBlCgD0JrK7xjNYGPqmqCG4NrwtdkKwjwsW1S03j+qJTGwG3pBKMyBlzXMCGB2RrsTucYWYOTwwwLsjhWGNSGMCuB9VmNLK8xHQEfrmrszGZYMSVuyyzmYJwYZpgphR3L2AHjfOna/Y9UJSaVwdKwgFaEyhpcTwOc1BmysRP6zq0T2tZsYdhC+0fX"
    "WMbedIpJWSHzT21WZCiNQc01DCrMqgV2yivYWdTYW5SoUMOoEgtTYjFboKwJla6hhtu4ZDZxJtvD1anBRTPF1qIG8wx1VmGB3LluQuGZKePyNqEsFXanhKt7jO2FxkwNUSsgswZmNnEFi/JGZkWUuKSCkWbyhMzI9lKEUt96FtviaEvVwmwaxjj7MZmQKYXDy6O49YPw"
    "57do7Lmr2qCGRZ1ZaOcVE8dOG7oLKTURiT2hehqbUjFCZxh1hQxUtY0JScyus1JeW9hQHmyDWTGwtTcHDR1tok8gLcNhGUGp0TikqOAVl6TVUeLHlizRJLbIfc/0NeiTKfXxmvpB6tsQ9hRCausM+zqs3vaszflKqmPaOglXpY4fVbvwsTePU6Tx8Cu/iifPfQhvuukn"
    "cfPhN8LYGor0PtJw+S8Kvb6qyafnLoYmJbghwf6EUWjCaJD7QqJQVTWW8xynL23iubMX40ZoUdXYm82wuzfBzDDO70yxPBziVdedwNnLW3j4hTMOA1EuRmsym2NRlpjNa1ze2kE1L3H74Q0Mc41XLl7BEWuxubMHYxhZkGD4UAljXcEqVOY6K2gcXxphXuTIcw2dub/X"
    "pcbYHkK5t4lqyhjV17nlgaqxVBCq2mA0OonJxhggjQPqDlA1xdY8Rz5bw4qxyDWwMiYcKSrs8SkcOHYQKq+RscVgtgmbKWSTKQbTBQ5bi0VeYz6uAN4BVjLo1cPY2bKozSzpYvclBrcltyK2Pqb8xG2jfMy8T5Q8seOWtyGJKiIcGA+dxEWQTuMChl0hscSgjICBBjKC"
    "rbziwchcyJZGkjsUv8ZYkCjR8EEB7MRuqIyN3X6RZcg0OQttSW0Qm77N6RxlbbGsncyaFZItaVPchQsJAh1CCd2t6yfjRAaRp4BuWInscP+s/7NsoNvPqoR3rhHGvN+4CPqz/f6sDZKrvjnzGnMne55HcHtsSwLS/xkoleHJs7+L33v0J2CY8czFj+AHXv8buO3om2Gs"
    "+yBsMGIh6uFZcXRRlC0ukwT3BYGNmj8mIuSKce/Rg7j+hutw56mT2FgZQ5H2q3CHP2nl8uFUrrGUjbG0PAYBuPXm6/GuNz4ApVxhCP5ClbFArrGcL2FNO47UsRNHcO89t2KQZci1dp1RbTAeDmIGHwlQmYmRkYu8MtbiG157L9716ru915aO7HtioDTe4WGJ00Q3L2bj"
    "N3PEPwi5e5CsQW2cjChTLk8wkBG1tnF8W1QGC3MVii0yWGRaIVc5gA3UZhXT6vsxGI7xyY9/DL/08d8VgavdMb3pxFuWyWiBvH2LGiWcPTiNibO+yFt23lAHl4dwPE8PYnP68wLCRuw0okp7J1BjXdK0NGSxLeM/TtIixZ8Fb2W0guEQcUsX6usy/0LnFQoL+y5NKYXN"
    "vQWqqkamSJCd01BfucnjNrDbuCjJT1daukcBcdTzysVGi5WedkeSZW9dSC5lCS0pyWRIhMz93KxuE9SmR1Bn0xxeU9aWBHEbUL+GZjAB4wVBjpTqgObsTfMX9R4+8dw/BtkljLIlVLSDX3voR/ETb/kwDq6e9CZ1qrdTY0jyp3xp3Eh6Ol8rbUsIlOcgYkc1WCyQ5Rrj"
    "IoeOiTruBJHr3kafSKi9IV5IGrHWndzxv4fNo3anX2kNKuHprhQ5oXE8KW28MSxbGBMY8I3nuzE1KpOeUixcVmWoq+Um4spZIc/hIbBItizNIo7QRADVSghVAZDjp9Xstm4zU7uRx1NBNBhza5piEjfH8mHp0lOoZS0T7hnl5U6WhVUwqbYwy+s/myQbEOPQ8hiZ1n67"
    "5iY8klSZFsapSUOzRsYMIg3OGhY6rL+e4cAUuj8SxUor3UAQIQiVnKRL+w2dApwFkHLXVWb22YCNkcL2ZIFFWSPTCmxMtJJ2TH504BaWtH6O0SPNiEqNEJxbAxy3AmPk86uIrq0dYdds7MzO49mLD+Ku4+/EuFgVyUWd1WA/Z6uPCdBLEZW5ik2hy5Ji1WN/nDITqLuO"
    "7PNp7h0L3Q3y2Plfx8WdJzHIN7Awcyg9wu7iJfzOwz+Lv/K2X2yNnO2xjxOnBnmCB4qfz+NqLgKLEHYf9Lk8KLAyGmA8GmA4KDAaFBjkmf+a1iWWWAJRL7ukfUM6gzj3ehQ1NriaCLlPQ0mSiiMnzZ3EJqb1UIeRhpZGLeHDcFcTJgmYbUVA20CQxMmm4Iup5wYZr52z"
    "xqIYjjDKs5jiYgPuxOjnEAnuHCUPYXryUiseqnvCNzI7ay0Ora2gyLRTAygRYit+tG18V6GYoRi4fPUqajKO7Zn70aYGMK+BPMfSaNwA7iFbwDY+MLvlLmCNm7MqP04WCuAK2/k6MuUOwFwrlMYmD7Ar/I66sDtdYFbWyJRKrk/w5+/SDRove5bBC7ITZOohWsvUa9mj"
    "taPeqOuSIIrVi5cfxK987kdwbucZ3HXsffixt/1X5DrfB9zqAeW951ybw9kuUIH31ge8Z9jXXOJrYxL9q1HaB3gjGFvjyXO/CaICrAxszajLGoU9iMdO/xYeeem78eobvwnGmmYuZyRC2LQL7JPltOkq3BQVMOZVjS+/fBYvbO3hoedfhFYaRaaRezypyZ51mXIh7FNG"
    "YrDMMUymZPZSoEay1IwaFnmWIcuyKLhty5qsZ8eXVeXCGVSznm5GhcaCWL5FVvDuE+Kht6LgUnPDxxxEK05y9r5ZkmscvO/hnTD9z9K6wAvPPol8OEQlWz/RDVHf8qVNQmRR8NEW6PfQWig4f1psLA+Razeah+0vxHgsFy4hT2K3LjHaOIJ//Ka/gme3zmAwHDrhtgVs"
    "VUNXhCc2X8af7H4FBeXuEGRpokeArfC9N70Dp9aPYFGWrg1VQJ4PsKgqvPvm12KnBKz34GDmhO9jPX1oMi8xWVTINHltZONSIbV+YYkQxkRrLTjTcg5LZSxe3hM7n7YnFyX8kQbp681kIJ8glOHK7nP4lQd/ADuzS9gYncCT538fD734O3jjrd/dTEXt57Cvw4pk7R4/"
    "rMQymRIaUxwJ28A4tb2sQqVrrRxlSGofozNltbvZ99zWF3Bu8zEQBqiNJ0kahwVoTfjYU/8S913/nkjk5B5zP05Se9EKqURyk7Dseny3UFY1njx9ESi2US/mMRswwiU+ITm8NcupvWwS0SXF1ZKhzFIKRE7KQ4zRaBQzApk5KY6hQ1osSizK2tsGMyyJUYC7D2V4koM2"
    "LYkSC0GrENHiofAwN/HtAcAWLp3NUoxjgGxzcRWqyRXcc9cKmCdiafw1gFNuhZJSQ2hILWM4DScIV977ka8vjTDIFeratiLjGmGvZIyHMVkT43efv4R7D38Hbj1kYYwLFTHWoLY1Tqxt4H3qOXz4A38dg/Ggg70YMFaQ4/9850/jS69UKE3lMSqgUApFXmBzNsUfPfUM"
    "Tp48iqquk+YHHrOazEvszcsY2Nsdg2jfpiU5UKTjqIwvE3KiDpshXmNKjUx7cKZQJCszw289/FPYmV3EIF9FWVco8hE+/8Kv4A03/8XuRNbHy+pL3pGM91hABfxJLXsqyJgvQvoNCYmL2z4MXanO/qyp+P1PX/ogJvMJCrUOY2uYuok+H+QreHHrM3jizMdx36l3t6q2"
    "L6YyjfMalH455lor1uB+o5Ur5fzZ1ViMEJyIuUMsGCdVEdHvy/oCyNySOMjbzGdJaQKGw2GTqRf8uCh9KOvauTiMh4PEcdGCEkxFVmjudLW2Ja1sxk338QkngOAkGXyPRJBAYEqHU5hEZ0lKY8Z7LhzCNCN4xzec2kvtEMWVjjfUYkszc+/Gmi1jaTBAnmlUxnjWvHiM"
    "/Wfa9qUi5bEpY6EKjY+cPYv5fOFSkCoDyxa1rXHj2i7edv3cYWrR6TFtHDIivHD1Cv7jo69guFQgU25RMs4zFIqQEeHE8SMYFYNYMFgA8HuiWFGLTtAcZJEFKrhRvA/m0yy7CGmsXtDhshU+GS0pjTQA7ODObKBVho8///N4+vynsZQfQmkWYBAGahkvXP48zlz9Cq4/"
    "dE/6vLY889r2Nyn2ja4GGT1BmXEkDHwZITLkfb4+OguGChmKlqL+xJooRtWw1uDFKw/C2gyGXTRSbRlsGFq7wlLbEp957ldx36l3d/AXtM6PdvMqHSXioiHTYEUdrokzTAtuoyoxgojKdhk1RGlXJ51KWVjzplbRDsRVRChGg5QTFmuJb+mVcsZ/07nXNMInxcB7TYUo"
    "pU696iguE1eAmLnIXbV8tDppOmhmn/Dc4dOpOOaGrs3GkbK75JCje/qgpcUrPKDOkUKM2cLFM9n2+U65MgZD1daNudE2wInR89OHR5S1E6JrAKcOHfDe6e7wcFwug8PDZWg1BWIAbgDNBKu8yLA8HOKO649iaXUM7T36cw+6K08QZu+VFbEpIkwXFfZmpU8FYuFBR02C"
    "u0oPkUTh13HiRVPwbTvLkiN22gkfFvIeGxKu2xMK3HLh/M7T+MTT/wYF1lDbClXtrn+mCkwXV/H46Y/i+kP3uLAV0WDsSzrdz120FcxK1HXGcVpC2SwFhnAHn0rxCLSDFPlaBDO/DZmfxeWd5wHOYeBmdmM8B0YRjLHQPMIz5/8Um7sXsbFyJLUeoRRsRj88mLTNmc6a"
    "B4Uh5nLBG1E+tDO4OwpCq2ynUy2lFet86YrpGcu+E9RQGI9GbpPnDKbiKpw8NkLKeU/N5rPIuk70d/Gk5ejhlCQXoxUdyv6W5TBCua2UIiGS9XHTSm6eQlEMonGlwD7GSyvti5V/f0pDeeNB+bkCIgyVGiM37vSDJGK7fJip1Ha2YPnGhdRGz6gEYPYdhitCIs/Ob3HL"
    "2sb0G8C5j1pxMisCjHUOr8wAGeElnlg4M7I8R66zyBdgX/hr1Vhzx3iUsM0GYVEZ7M0W0f+8sWdprHEo6C0THJGjQWEKd4hO1Nsfx8M2qlaamSrKnYWAWnZ2vcxQED7+1M9jb7qFgV5FbSpUlUuXqqwBSOOrVz4H4K/HYpWmY3M35gvotUvuLXQdZRc1fliKmtk3wdET"
    "b270KvFjXpw8TYU5GBFwZfI89qZbIAyiBIUZqKwBW4I1BIUCV6an8fTZz+ONd3xbBGMFuJF0eSyNozs8oMb3KoYCwFEuXOKtO42d/SyBtO6xv0nX883415AX4wgTXSG8z5IiDIdjv6k0TigM5xToor+anzybOe8qnWfRLpdUT1akzzRUvjAFW5LmXBEFzX80yhoMMx/L"
    "lTnR7bSsYHXWBH34ImetBZkKY+VufJ1raCowqb1uzhLIKpDOXTEMnlFxCyzBbgJ39jLizynN3ePEIVbiW0iY84oQAzaiM603YbQIoR4cLW0WoVglcAcJTKVxyoTvVFRpoTTAYrlhLYMsAQuLylhncAhyBRqETFFXf+dv36p2xUp7vCnKhoQym4gSi55I1eGWX75PhE4Y"
    "74K2IzFeQg/AK8mwchlPqauDJo1z28/giXN/iCJbhrW122Ab9tInC0UFzmw+jdligtFgqSmisbNrjYZCJ5jYJUuGay9zvXldmRKr+ES8/TUyUGU3JmfndrRQSOPbmp5FaSpkahi5RtYCZW1BSsPU7g3U9QLPnn8Qb7zj25LRITHH8A88CSYwJ22t+/SttTB1Bba+YMSV"
    "sEiOJqeHI7kNQotO4DsmEqeUtRwtR5jb0Z6M4WgMrTXYGhC0eO0UnSkIhNliASiFXDvBrW5lvQlaTcOV8q9JSe/zJkvI8YCIsLdY4P/4/j+Hd9x3F7Z2J5jXFapFiQ988kv4rw8+guWloWNfs+v0yukU//xHvwevuf0m7M2cQ8R8vsBvfOJL+MBDj2N5VMAYA60z34ma"
    "ZEHOjZalE44reb0ShI7jdTLrUuJlJqcIJZYBliFsUdxvCLIZMFAZA2NbmtYO7NpcT0BhYWpU0z1wNoAaEIwpYRYVCuQoa8IWl5hVlWB0A5mW7qjBVYK9lzxjd1YmiV0q3H8awoxPlJmWdRILEba05omdGbfIpIxe/WDi4io1RZ0gEQtA4wsv/Tfszq5gmK27MdeyHwnD"
    "5jLDld1zuDo5i5OD28QSqZ2chGtL/2TRamHS7YVD1rEB4R7gqqPQ5rj5i0CvV9ATqV4D+is7p1FWNVTOriVnJzKta0eFMZYBrkHI8dWLD7vZWumIb8jNQUIq6yHUEtILwU2cSeRpQSTmapUl0y1BOiVyZ4tD3MR6B0wMopgOisKB+oATB3MT5w1rYxdRVgZMhDzPBO7P"
    "TWwSJbkxSTp00JHJoAAlnkpSCqqqcN3hAzhy6ABGwwJXdnawUBYHVpZAOoPOM8A0m8CcgJuOH8XJY4exvTfF5c0t1HWFQZE7/Ee76620htYaxI19T9eAjRMuGbfGT4kZCgpRawsmNrUCfzTGoqZgRWIjlmpFd72ovVWLpy0w9SjQhJCaFGG7nOM1B47i9cfuQkkKU57j"
    "TUdfjVUs4SPPfBILXeH+4zfj0NIa6noTuR7Fh9w29vNO8OxF1JP5wsNgKnbeLvWmgcnYd4jMgT5i/D3FHb5aE9YKp4VMOHiOgsPo89prHpaAs8lBXR66ijLMywmeOP1BkB2grmswLKraoq4cxFczg6ExW+xic3IWJw/c1mGts3gWWWgXI+dOGBBIlnySmdjGsGRr2F7h"
    "72f54jx4NObVxGnzsiUolYkH2KR4EYDJbAtVZZGR66oAf+NVjDoDghMwcYFLuy9hNt/D0mgl+TA54fk0K+AwmikpwA06tXgSOiwnFIww1yulXFGRXJ82kbbn4FJR4tCEWIAt8rzwN03T0rMcof3X1sYxdbTWvmOEMBrkCBmqwD1qrenb0k1KyUrQsahwBFeNNXFT6vAz"
    "7YI3PD6UeUcBkEaWOZcJWEZVloAxTban9rYyrYeIxUCS0CKIen0fw2tWlJbjZjHguy9FIK3Ang1eVhWUYqgs83pRhhU4R2mMT5xR/nJzKyege3IrUticTfHk5hA//63/ArPFDGOyuG7lIIw1+K47vwnTLMOB1QP4o6+cQVFk0OQWJGG8scmGi1BWFbR2Q6NqhaA2zii+"
    "w2UnLdKakCktou7bFE9GuFvi4qDtnhKtltrJUpIYLcZ3bqx7wvP90pWHcWHrGSh2BQsElJUbCWvDqP3bXFQVdqebqWNKm+gt+FVhumCWYy8nWHjKzUrrTibb4q4oMa1b5NesRAqfffHf4wsv/QfkaoBhfgBHlu7BbUfeixsOvgGDbOg5Ykas7BmLkpEpwNrA6GbUNcPU"
    "Thfmtk4Ke/MdzKsplkYr0bQt6Y+9yJXaq/uWcFbeGJ3cu/gJUoJldOTlvW4UiNXCYWKuQOXZEJlS8X0HyUbwgKJYYN2WNI9mdoS6xQJQSqUXnFgITAFiHXkyhI45NIgIxWCAF89exKnDB3F1bw87u7uoyxJXd/dcZ2Js7FwAAmuF58+cx8rSCNPZDJvbO9jc3sZ0NnWb"
    "rYg5oBGuCWVBRGF8knVXO+w4BsmCm3zHIXhzARQOrrCLnQnsaAQGQQ8GyJbGKLRLEuKydMXT0wFqa1DbhixMiUC5/ywOVkTLucbTuxM8ev4Cnr24ie+85ThWsxxXd7bxwuYM/+WrW7jt2A7GgxwH11bc76EufOBi41wAbq7TB5GFqygL2Y+1ThC/Nho6twailseYWGIF"
    "oIWkHlUGQAi/dxF1xmL8osi/E44Z4r08e/ZzmM6mGA2GDv4gQlV5KMdwPDRr6+LteulFXhtJSM0720nQXztYq4GcshR96xcgtisiGHji7G9iZ/Y8NI9Qmafx4qVP4cEX/gPWx7fjNdf/IN548w9gmI9R1Qu3ZbI5yopR5M5oDexOJ2MAa5S3h3XFbFpNsTfbxcHVo5Hd"
    "m3CpWQL/3GnLuc/qhtINIrHM4KHEJqcjB4m+8uLnMcWREmBkWdZ0S6rZIO0aRuXBWY4jjW/0/G/LlcYIvpsI84Rgg8cuRbR5Fq0FSHK4OBnK7rzEZ596Hu9+/f1QDFSLCruTGR766kuON2NMzMUr8hxndqf44rMv4Q333IHpfIHFosLV3Sm+fPo8qCgcbsXtMYXkRyu8"
    "wtue4iL5Gy27YzGey6tgjcHumUsYmAw0BQYFYX7hPL76iY8ApsSNd78KB07djL3dXSilUHvHzsh0l2RY6b5ALP57Ay8Ya7ExGmJPa7zn4Dpee3QVL5w7i3KxwHUHDuA7Vw/ghWmFg+MhFrW8Tmm7tiirWGOM7SIsFil/z7KFVoTxaACwhfKBJOjJMmguPoQcqll+qB6y"
    "acSWQgEJQRny0G/5Xb5w4VHUNVBlbsGQKaCqGNYAtQIqA5Bi2Fo0C9SSgtl01ncLI91LeWhvh6mVBxCDVPu5n10wK2yTLAw0Kdxy8BtxbutLyPQY1mTQfoW+ufcM/uCxn8Znn/+PeO9dP4vX3PitTmqVrboZuDYwXLuX77cttXHJu2CC8V5QsUvxkhUCt4zgBKVAJJc0"
    "5MNGw2UTFTsn7O0QRMnC6gSA91JPSUbUCtQI3VmWZdBKxbhzxzg3qAC8ZbXGemYAJt9dMqypAe/2kGng5a0KD5k1ZAjhnxDLARYLjkYXFzZkiUDWr9g1FHYmE9y8voSf/u5vw5GDGziwvoLjhw/i0pWr+Mvf8Gb8X7/xR5guZhgOBsi0xu6ixFvvuAE/+ee/EYc21rG2"
    "suRyFIdD/KV3vRn/5qOfxcIyMqBxwYyjrDhOJAky5tQJaZBgjTUbKgUZ5Bn4Z2ZWYbE5wZFTNyPL3YEwf+kVvPLiy5jPZ3jw1/4rvv57fwA3v+tbMN3b8Z2ulyi1NI1p10HJhi1kUGpFOD9d4JaVIb7nthP43/77Z/D06fNYWx6Dil38b9/4emxsT/HgxW0cGA07RpIM"
    "h0vaJO2GEzGypKIEOZZShKXhwIWWtGVuJCaC3pU/J+qAhMckPMksG0/SlltJEkaaouAu5njlynMwnKOunSLFKEZVOZfZyjBqAyhrYWsI9wbEJZsTtPfby+wn+UvulZaSJXRZWfvNhzaTW+vP5k26R/+eY9+BB1/416htCVKMRbkAswJhiLEe4uruM/jFT38vvnL2R/G9"
    "b/onOLJ6MypTozLO5gR+Y1bVjKy2DYkQDKIijpWSeZ1sn2QABndcxD1Ya9N2XJyo5MW9tlrA5MpTO7yFCwHw9sZlWaL22sYIAIORFwUIChkBma2d7bLnnDExLGnA1vjbGzu4viibLsNa11bWzk0SgwwPX3gRPzq5FfXaemMsLIh4VohXgwkDl5za6TivG0BZVGwwyjV+"
    "/ie+HzccP4rK1DGOPs8z3Hn9MfzVb34b/uHvfwwYDrEwFtetLuFf/9QP4uDGOsqqQlmVUKSwtrqMr7vrZtTW4J9/8NPQwxwKzjKFEqUxCwM/bopXjxKCeiW3qZ1K6B6sNdjZ3YG1xjnFgpBlBQbjMQbFGB/8N/8K33XLnRgdPQmuFomELJEvSZxJbsX9Q6QVYXNR4aaV"
    "Ib7zlmP4J594FGdKxvHrr0OmFCpj8Q8+9hD+3nteD1IKn7uwhcPjoSM/+99U1Ra1MdCg2EVZsQGluJFnp/fzv3dpOAg3rNCGpCmOjLRoSbCj4V1xOhFRs7Uf5qtQyAE2MLZCZeaobenrnEqak735FjYnF2GswqJ02KU1rsNSuXdQta4jZZthebThR12DXA/ckm1yGi9c"
    "+hxeuvwlnN9+AWU9w+tufD++/vYfiu+fBQ5NfUwE6srtMkpmSuqylluKedexGBxZuxW3HHoXnjj3ARR6DUprzOcmVlhNY6yMFD77yr/BbnkR77zlb6PID2I6m4NYR3zBGkJVNU6ONSqsDA5jebTWEmN62xfD3r+KwGx8RyOlB+l62HkONdRZiWcpnWPp+E0YDPPoVkoM"
    "mLpEtXUJIMZ1x45inBeuhfb4U21qnL6y6SgLKwdhiyXP58pgmVDOZzBXz4IUY2+xQGUr55lV196iOcCzCkMibC8MyukCNpthWOSOlEkQfkvholhYw6AC0Me8FlMYINVzi8F2gd2dXfzUe96Cu246hUVVIVMqui3keYZZVeOB227CO+++A3/y1dMAA3/1m9+BgxvrqGoT"
    "ZVBEhOFwgJ3JFA/cfD1ed+o4PvPVV7CxkgnhtwSwA2TQdIddfyTJtkavtQmBwcZADwtUXOPMK8+BlIKtK6zfcAvyIsfk8gWsHzgCVhmeffghvPpbb8RiPoNSSpBrRRwYIXY+RGkARq4UtsoKNy4P8T23Hsc/+9STeH5njuMba7HYHRgOMJkt8E8+8Qh++m33gWDxp+e3"
    "cGg8Alun2ljUtd8ONthZWJi0PwJj/Rg4KES2oCThcqphiOpxSkKFEzcvTmPqyasyMp3jiYt/iNM7T2KsN3B0+Q4cW7kbK8VhVNUUhhdJcSjNHPN6jto66xoQQ5NCXTPyjGAMOxza1hgWa9hYOu685rIBXrjwRXzquV/AU+c+gt3FeU+xUViYGc5uPYevu+l7URS5J7lS"
    "h0S6n9touHBZV6jckzWIzh4YIOD+678fXz73Ad9uMrKCMJ87yoJWFra2WM6O4OHTH8Dl7bPIsY6d2UsoMIIlAmn30FGFyCaeVSWuX7sO49FKWOCiqivkOscgX4FSGSozh+EahV6CtQtYrkVHyJ0K7fBhSs5y2Bp25Ti27v9zyJRFZR2HBwzM5iWGn/5VHMim+Lq3vgXr"
    "Gwext1hE5585Gzz2S7+D0XQbk/v/PDbXboYyc+SO3gxM59h94uexvp6B3/79oKNrMIvKbb2sTUYGOxqhGn8I9ceeA6xFXVUu047CJpKEJ5eFKQ30IeDsW3dxcW8KJgWzqIHcAmdmuOUTB5DTEt5w2w3+dCcsKtdhOcG50/Ff3Zvh3lMn8OFnXsah5SFe7b/eWANjjE9w"
    "MajqGkpr1Azcff1RfOKp52DMGNYXNqXcoUPeAz0a78klURLx1aXISJwrQce0xsYNJ3DxhZdhvDXM6v1vwLHXvx2v/NL/A2sNsjzHpcubuHJ1G8sFmi1oCwAOTPcAbYTROifC1UWJ29bG+As3H8PPf+ZJvLQ9wfH1JSwvL8MaE3/P0fEAV7cU/uGfPIq/8dZ7wMfW8clz"
    "2zgyHqIsy4Y+Jzen0vUoAObeMnlY5N4JQ96r3Ok+WfRbHa9dj4FFDEhMHpYtCj3E5dmL+N2v/A0sqilgFJQeYnlwAjdufD1efewv4paDr8WE5jCm8r9FgclBM8b6YBTFqGqASxvVF/NygY3VG3HdwduwOTmP33v4/8DDL/8a6nqCQb6MQq8DDOSZRm2v4vU3fDeKoohu"
    "LH3GCw0XVAa1Nm82a/OtoqaMeoF//98ct+jmQ2/BkeUHcGH3UWhaAnOFYqixt1f79j3DfFEit2s4vf0wVK5Q1zlYmUBLhgWjrCnyP2ZzgxsPvwqZ1qhNCQKhoCUYO8MzVz6FZy5+Aud2voLd8hJOrN2Hb7/355BTahjYEBE5wbzCaaWIUJHG9UsKf+HGGtOqgrHO/C3P"
    "FGYLxn97MMd0Osf5aoEXZrvgWQllGQsFaG1QljXKy9uwexXuO2rxP97KKDLCly7V+HdPEkwxRlnNMTh2I/SxAyATtkSOqU5wxnxmUGCx8QiMeQo5GxAzFBsocq+TSS4U3MM4XczwttH1+MYD92FmGIt5CaUV/vjKl/CpnadwdGWMjZUlxwqHhUKNig0yssgVYaAJpSIs"
    "D3KwcSdxoQiKjft68oG2WqEkgKxBXVUYZnnTITJ7RwmP9KbpU145wd2uvZcaiFT6FR5XthitjHHi9ptRLirMt7YwHhRQeYHlQ4dhL19AtZihWsxwdXsH+foIRZ4nkrFgckhiWcFeGqaVwuVFhTvWxvjuW4/j5z/zJF68uosjq2OsrCy7zk9lDuogh69urK9gYYB/8CeP"
    "4e++434sXZ/j9587hwOjgXMVbSs8U6o+LJxlcuFDVCOPTgj0jbFxe5YmstuEoRAJ1R5vlUsLQsNU1WqIAa0jy4Zg7fy4ZvNzePiVX8Ijp38T9xz6Drzm8A/i5o37wGxR6AGIc8zLGtr6ogqLqrLR8x6ssLdX4sYb3oCnz30cv/inP47d6gxGxRqGgwOo6hrgClopzOo5"
    "lotTeO+rfgp9WYMdxwJ5X/A+fljtOJ6+HyK7Mcs1Mp3jrmPvwyvbD2KUrQDGzeiDgcLurkGReQdNy2AuMBwSVpYZlzcXKDIFqhim9iQ4RbDEsJXG625+NywbZLpAbQw+f+bX8OAL/wlnN58E5TW0zgAwzu48gTff+KM4tX4rFtUsHWst0oADbuLHFREqJtywkuMv3b0K"
    "VJPmwymG4LnBB39vgIu7GttscbquodhlE9assMwliBl7dY4lZqxqxjpqZMixCoBrBtnaLSl2rgBLAC3mzq0SjcMm2IJmGdTeJupygR07Qj5QKFhD6zwuAVzXUwNKYz0jVHqC167fgR8+9i5MzQzzssQ4L8Bnt/Hx7FkgKzCxhJkhTGvGztyJzK1VWNgMu8iwyxmmrGEt"
    "YzGf4+LCYlSy44exApChYsaMFa7Ma1yY1U6i44Fh7mxkuQHjpQqiE78GoRxAa0wUI31Yh1sgz3MMRkNkZLG8vITDG8vYhsHMGpi6QlUuUFYGdV2jyHJ0SAzCzC8Uh0wrXJ0vcMf6Et5/81H80089jtPbUxxaHWN5dSV53USNXM0QcGBjCRVb/ONPfhk/8/ZX4X03H8Xv"
    "PX8eB8ZDb90slslyuceMYZEhz7JGNymeS+tHyyC5Ymop08SmlZKuwsEZLMF0bzpQmQUOjm/EjatvxxOXfg3DfAN1VYOQYZSvo6orfOH0f8Ejp/8Q36X+Md5x+PuwNFpFUR/GdPcMBnnu08wsKr8ZtcwgVYMxQKmfx7/7+PdjMt/DuDgIW9corWP2ZzlBkcbu7Cq+8YG/"
    "j7WlQ2l2Q+82cx+Zja/cWdT0BMuUa8yQaWy0+4d7T3wrPvH8P4Phyj2gtft0C51hb1KjGFCkLFQLxuqKxtVNwnRqkGsFWzvrXc4UajvDibVb8drb3gZFGq9ceRIfePTv4tmLHwVVGYbFEqy/YIbnODy4EwfH16GsF+nFC9IN2+jvCE0ghbGMQjOeOl/ip3/jInamU8zY"
    "5QAeHGdgW+PcFqO2Oe7eexzvwlXYyRRcAXObweYreGS+hyobY5znePAS421PGCzqGsvDDEcKdukytUH9J78K5h0XqaUUkBXAYAhkGRQzBqgxfvBxULmEv/eWF3ByeReWcpBfbVvjLFDYAmUN/MpTb8ZsuIqff/Ej+Ldf/BD2TInaWgxGQ+iLJVaHy7Bc4RNXLba2gBd3"
    "Cb99XgOGsChrzBeEejLA+asArmRAucCUFf7pGY17oVFVBpdLC1tZXJ4anNsGzl8Ati8xsqsuSisum5ja+5pmy0qU2iej8TtKtar+IWOVdCZhiFRauU2aVtBawQLIhyMonTkVROBwwcL6zoRbWXNMzYaO4Q7HK7MSd66N8f6bjuL/+uRjOLc1waHlEZZ8ZyUNGmMn6TEx"
    "RQrHD67gqib8o48/ir/ztvvw7Tcfxa8/exZHlpeixXZcVPn7f1BkKPLMif7DIsU2n0cIUqX2xjRYEkUFBLU2+Ep0VwFGaCQ7lms8cP134akrv+UUC1mOsqzdIWgVxvkGLM3wXx76MVzeex5/4S0/i7X8FPZ2v4BszdFLAKdKAQGkgXJhcMN1y5jlj6GcaQyyFdS2Ql1Z"
    "KAUMBgQYhZKm2Bjfjrfe/gOpt0qAmxL6AqVFPIQcizk467Mo2b9YUcIMZmtxdPU2nNp4M56+8Mco1AoMVzAVI8sJWhFmixp5rh3ZzDIMMdaWcpzenAEDcn8OIMsIe2WJv/iG78T6ygF87tnfxK998W+h4v9fa28eb1tWlYd+Y8611m5Od9tq762W6qmCom+lURAQEFAj"
    "CpGI7TPGmATUJ/piE7uoERMTYyC+mIAKqICaCCiKEGkKqCqohqqC6m/fnXtPs/dq5pzj/TGbNedaa59bvPfq97tUce+55+y99mzG+MbXbGKU7wYLA1VrsAZklmFezvH8J70G02wZs3odUvjIKW7TO9wkkDm1u1GOMHlkvcaX71S4fq/Cgd0ZBAH3Ha9x7zEFc26GAiVu"
    "XL4QNx64HOXmWZDW0JyjkBO8Sx7DKVaYK+C6JY1feFGBmWIcmmn83l0KORGM0eCNszBXXInZLS/BCK6klxl4cx35pz8MGkmY7Q3s5QZvvuKLWMU6lIY9yJ1tOsZAngPVWeCDZ67ExkUrOLZ1Em9ceRpu2H0pcpnhb8/dj78+dQ8uod2o5zNUzNgywGoGvPUAYyQk1iRh"
    "ozT4pc+TbcNrA9lU0KKAEYQiA8jYRVQSsM2MDSaUIkNFGdgIjAEorW21IjrkANOaFgZc3XQstcktW4r5IimekUzW0CYbIxJ5gwSEkIG4m3hpJQdie4HBWN3fmbLGDbuW8a1X7Mevf+ouHD27jbVJgenKcjJ6j8fphmMBLlA1CkvjHHL3Kn7lE3fiR59zHb7t2kvxgQeO"
    "YH8w/3P6RgZySSgy4fBLTtxfU7dRqwCJtZWMSPdDiBKeuynqnXLEDUVqtYUDu56OC1efgSPnvggpliAyQjWD430ZwOTIRY4//Mz/BYExnnrNS/Hxe+wBpxgwmqEahhR2crhvb4FLL8yxPbfkaA0FpWzrXRSAVlZat1Vu42W3fj9WprssTCRkANx73DJKsbxeqAkB2bC1"
    "AyWVSlBV9/hrBpIEnnbgu3HX4Y8gz6z3kGFAK4PRVGB2BjbUwBBYAY1mTEYSo1yirqwqvtEAmRpL2Rq+8xv+OT774Pvx3z79fSjkFBmtoGlUIIUKKaB0g7G4GE858Apsl2dtBUUaxOS8hhwXx5g2j9BtFBiG0hpkCEJqjLjCDzxvCf/4OXsBSPzPO87ih/7kJGS9jUad"
    "w4UXXINLLr0EzZE7kBEw330jiASm49vAahPzhrErF/jum3KgqfDAusG777VBBqYqYZRGdvxhLN22CZmNwKqBqSqY2Rb0bAs8LqC0AXiEs1f9B+RLwKzW9rAy1tBPSMZoPMLJE+t49O8fRnniDHim8ZqbnobvuvIFdvPe9yH8dXUnlG7ANWNbGdQGGGcSe/VxHGgexaEz"
    "GU6pfZg1OYSuwewIjlJgtRBYEoSZq7aVIadXM8iEhCxGoCyz012lXbSYiKLprS0vR6OwmNbAHXtYjiAIY4z7fDrR6p2prqU02QMjlwJCZlZaJSxvzvus+ZUqvFd68HcSOFs1uHX/Gl5/xYX4xb+9A4+d3cS+5TFW11asiJk5TVNOfKIsD0kpBdVoSCJMxzlWVpfxy5+4"
    "Ez/xoqfirTcexHvufQx7JhMbcuoqunGetURKtB74hlN31EYbNMwdnlhLeqVEnJYCzcYpK7zZIROCUHkkR7h236vxyPpnMBFLdjpaCMxnjf16LaAVY22yFx+47efwtAPfhz17LkSpz4FNBu3gmxIGeSZw4KIRzp1T7gK2RgONAVbG0hUEArWeY7U4iOdd8496TPp+S8ip"
    "i8SChPksLud7mTOElDLQIZMKsj5JN178UuwbX4dTWw9BYmzdRI2N6c5HElvbDcaFhNbOA0sYrOzKcPzEHDb6IcPxk9v48Vf9LM7U9+Ndn3wrlkerYENQ3EA1dhqVF3YKV+kZbtzzCqxmF2BenkOeFQCTbRlMBLZGFjfc8cUmIkAYGJa457DCx7+8hTwTuPdoaSUeWoN0"
    "A1WXaJoK2ytX2agtNhDGaqtI1yirBucqRlU2KBVwtnagtOMNERhoKsgzx+1ragyoaUDaTguNsIEPGRMmV78Jo2WgrtvSV0hLr8oJyFdPQYt/C5qX1hCOG2w2M7ABNuczoKqt3Aa2zS4IqBTjD07vxa4auGtd4NB2jkZtWYwNBBQjiNHYGuIBaNheINr98g4/kAVI5oEw"
    "ap1NacDkiEO6DbXsxbjYATpjeG10iNeirncWxaRI+3tS2PYw2NA4E8BG2UlolkloAPO6CdmFGQGlqvGsi/fimy/dhZ/9m8/j0LltLBUSPBqhMgaVMWEqK8kHiFCwrfEBp3XdeNqUhTsEYbKyhF/429vx0y95Kt500+X44/sPW3WBMRiP7IbPhcBYZiFkhL0e0NmxGMOB"
    "h5cQz+MKNZqk+uAViv48KsQiQilQN1u4eu8LkD+4G8o0Di5hFKMc21sNhEBQYAhR4Ctn/sSGB29pCLaHmVIMXWtcds0UTa2gjQ0DFmxQNYzlSebizAiSJLaqs3jBZW/G3pWLwmQw7L3Ihijml3Fi8xh1Su59Zl2LnG4KdEpoGKiyWGNcLOP5V34/3vu5f46VyRKYbcug"
    "NCCkxTy2Zw1yKaGNzfHLxwIkBZQBtjZLXLv3yXjZs16N3/3EGzDKJ9DaxkAoZaAVYzqV0IospwoC1+x+EapyG4o0BOngbS2lTP2NeoRFl5ALa/a2Os7wwTsrfPCOdcDY9nUpE9ggYUlqBLDIIIpJ64muFQRspHypFJqyBJkMmRAYSeEi4m2eoBTSGfjZ8tu4pOfgXOqk"
    "OWQ2sP0P34JMbmNeMySx3ZQiBxuNjUbj9MkSZuNqZBfuBqCRGVs1SBJWqOx1lyLDRBDGAiDSkJThGO1HVlTYrRqc2nDLIitAWQEWNpNYMaPU7KorO243rgqw/vWRf5WbaIVMwsSNAUn8WKIocTFcCQXFfx9uWX8kRDK17nJLpZRuWm1dERqlobU9SCsFLI8krtmzB8Rs"
    "eWjEmJLBy/ZP8EdfuBeXrKzilgv3Yzyd2srE/Tzjqj/pBctChI0vwNBKhRwAzf75aAjsQ1M3+OxjJ/Gmm1fwxiv24o6zcyyNp5BCoJACW3WNh9Y3rZe7x1kTnzXvXGH6MXfsL1sNdhIpj/slXu2xTYunwYFQN3PsHR/ARSu34JHTn0RBq9Z2iQgyyzGbV8ilcPFyArWZ"
    "Y23NYH3dBmpoRSgrg11rOZaXCfOSIYTFmJraoMgzpwl1uBkBhgs8++pvTz44in31Bsw/4/BaivW0CMnPSLxIqacQ38Gu3VVZhg2ef/2b8ff3vQdHNu5GJifWJsMQlDLIM4mNsxqY2ApLMSPLbcleNwrbpcYPvubn8Lf3/wec2XocK+P91sCfDapSY2U5h3aBlw3mWM4P"
    "4qLpDZiV55DlOYzQMEZYC3UnRG5reWc0x8Ev2AVSAMgzZNLRDEhAmwxsANVoZz9jCaoiugQ0G3DT2GAJ2CBO0zhrDyGQSwkhJJSzdCe/OK1oEqxMKyRsT33IZhvqzBehZAXBNoHKK/ybCmgU0JwGqLkAZHYDSoEbbW9+KTEqciAjkAFIZJhIgbEA5gwbtKCUvdmZQYJB"
    "WQGRZXbErzWURmBt+0pGuHw9YkAYBWIT6QLtQCBY50QTQXu0ifbi4IgQCiAxy+LWlDHYyzi8ioaqCt9CRiIbz5UCAXOtcf2eZfzgU6/CofWHMVMVMgAn1tdBtcD7/+YeXHfTDTiwb+I0w5VdDw7K8OqsIO/pdBn2kDYtTZZaFrvdO1Pc8dDtePSrX8UNV1+Diy86ACZG"
    "rRpcdulBHLlgD/7bXQ+iyPMWm0oOLE4OMuqk0GhtwCQSO6veXm11xkGKZtiAjMTVu16Erx7/uE3rMYDWGllOoNK6okopwIZRzYFMZpjIAutnKwhpffT37R+jZg0NAmuLbTWasDwRqBvtLjSJqtnAZXuejRsOPNuZAMgBY4HW441iK/IFSfS2JQzfILKeoH5iGYYM4sME"
    "gzHKJ/i2Z/4ifv2jr8aSGEM1NoKpqWwlA5KYzTSyXFqaPwOTUY5Tm3M8/epvwN79Od7/93+Itck+VJXtq2czhek4d6EPls5fNjNcsfZUjGgJZX0OEyHCTR8y/qiTLOImJ60HkbPREPaW1rBj/+BOqpW1jSlGyASBtLJzRgeOKq1h6toFMFj8pvFkJBLWQlbrUGn5sAZy"
    "vk6t7xBBsEGjFXRZoVETcOZEqmSj8rQi1IZgMoLIXa5dXQGaoaWlgjSsIE1kgqYanKoZZxvgTAMcbQBdMzZqg1Ix5kZigw0KDUyaGoYrHKuA1VrYBWiAuWZsKYMtZbDZKJybV5hUFVaMQmJQQpZ9bZJAhWjKFukuidNAT+aO31H0GSb20BEkYZwiwuPy3gKbpLQCaG3w"
    "hmsO4Lc++1/wi1/+M0yogJmX0I/NQOcA3iWQPzyFkgxaygApAG1gancBeG+tyCGERNsmsmEYrUOga2z6AcPgSiM3EvXpEuKvFcSTdoFWc6iyxn5M8PHv/W3csmcFnzmxjl2TkQPhfewtt/wqL+I2jMAC8BM0oiTGjmOybJJ5GRsXEGq1jStWnoMcu9GoBobJtoHKoBgJ"
    "bG4akDTQmmAUoakZS+Mcp6oaOteYTCSmy4S6NjZ0lgTKkjEZS8wr5bhfDJkLbFcNXnbTDyPP8mA3NRhTD15s6hdb1jAGYr66OFXPE4uDljCmyNnRs8YtV3wDXvSkH8JH7v4trBQXoWkaS+/XBnIkUG5qUGaBcFUbFDmh2gKe/tyX4LOPvMf6b9f2z+ta24lDRtCe/0GA"
    "VjkOjp6Bup7ByCgIwTkvBuEtRw4HlDJmKQZUgq7QPxgD4WRDJG3pbVQDgzxUZ8ZVS2QUMhCWCsLyNANA2FVbTAZG2YOuUWBhQkag4ciwzjlTlopDRiCRgTbCd0poFFkGvnXaQyYEslyCRoR90xWsFMuAYUxYgpSBzDJQo/GcZYUnT2tUssLF0kA1Gk2tUJY1zq6VOL2x"
    "jdNH1/Gn9RwZA2/cVeLSXSWgNRpDKBuDs1sNzm5WOL1c4dRkjqO0jY/fU2FpNAVJAZFL5wBgOhBxx9WSIrwiTf8c8Ohtad/xxCiu1HREckbk7cUAlvMMVX0O7/7KXyMrRpBagKYTyAsl1GqNbN8SCEBGxpWxInjrI8+i6Z1xXD43ihcIbH4yIrWs8QebYbDMocHIVlZA"
    "hiGmNoBkMprg8JHD+PMv/S2uv/hVOH7yNHZfcSlYc5RYhHBIcQy8dxxEY382jp6pz+mMuV0IfpWERs+xd3IFDi4/D/ef+ShyuWaZ7JpBGSMrBMqqgSQJpawER46A6YrE2c0au/faAZFWdpCglDUvIGHto6xPnsB8voHLdz8bz7v2tU4gL3oyu363Rj0/ecQ2yh6LZO7Q"
    "OqgTJ544xNFAArH/IwHDGt/9/H+Nex7+LB489VlMi30wpgmZeSIjzEuNPBPOVqbBpJxgPAa+cvjTkLyEqrGTh3mpsWs1R6Xc6JcIDc2wgifh4skNmDdbGIlJ0renRsqxL26aFq21gmEFI0pUCpDGtTDugzVZhpJycF0iIw1JBqLcDA94Os5BWYaZEciKAvdXOd7+DxUM"
    "BI6XBmdqiVzbhVNAgeoSGRPIGAjdhgc0yiBDDqEaaGMwzbaQG20vV2Ot4EkDUHZfQQN1qVELAu/N8J7jn8bdm4+B5xqfOHwPuKlRK4VGCTwp17huJUed1bhxymgUoWoENmeMI9zgDJd44EyJ7bKGNIRbRxWuWiUoY5NfyoqxlTM2C8bJDDibC3xuvcGH5iWyUYVGG8is"
    "aNn4UVCDn1DFdkXU9WBByoznOJfOPR+jXQtkLMdKCAFJBKN0SwFoeQFWB9coaKMx5hzUlODMYWC7Rsh2j9302O32hsGkWoJmGBiY4E5LHlIw0UWoHV0m5uvHnDMrFQAXjsPEgCEJKgorLp6V2FjfhD7g9LTeWcT79Adv/NYFP4TCBndfbrMqub/XbRhJ65nVBl9oPPXi"
    "b8M9Jz8OAeN0rQzV2GFGXQFSGjCThRCEwXhVgDetvU9V2dgwFoR5xZhMhJXXCbKJS8zY3tJ4wzf+JIq8cPFfnUR5WgwxIbIA6qaA2+EJDWNULUK/OHewDYlwomijMR5N8S9f8wf46f/xSpytDyGXKzC6hnZhqfO5K/010DQa43wNj5y6HRvqHLJsApKMcm4V4lVjAv9F"
    "kMRMz/H0C1+GkZig0fO++2iMvg0UiQxribGrECiKJTBqaHUM45xCnICUOSAqbO/OwHOJhx49hIwI27M52JHuMkm4cLnAkw/uxzg7hY35Mj58dwUYayp3A88x2rsEUI5HaYQlUaDUDAkD42x4WDO0NBghw/HVi7EbwOObI8zHJeyQ0XoPsTN3kJJxvCJcsP8S7FpeQ3l6"
    "gjtnD+C2+h5gzsggcZM4gNW1VfAkw4f/7jbQeBnbszm0Ns4lQ2Ne1ji3uYWmbnDXA4/jxosvhGCFD/zd5/Hi5wJNVcOwQd0oNI1CWdc4s7GFal7i7geP4rpLL8a4GOHcxjbqqvJzqhaPwECoZoIuOCk9dSaMXU9ftviKzfOTyPIcKi8gJDmfKUey9HgT2/eXkbRTUkQy"
    "EgGQi1zjQlrCZAMIQ5BMMAK2WmeDjKxLqTHaVqsukksZA+mGNZB2xA9juUYtKGxgwMgyCXaifGPse4D0vl+2sNMOWiCXT2idJEz7uMh2FMEm2vmueMu0EBjrrIaCBz7RQF6nCyQRGapqC1ftfToOLj0bD5/9FAq5AsXKTgGdsUA518hyG+LLBihyQsZWVN6UVrZVsrGV"
    "v7AQAhlGLgqcOnsSL7/5h/GCm14FrVWwUR8+nFKHUerlkWEAwxqCqmhAy0MxRmyjn2SH8Cfdizt44VX42e/8E/z0H74aM3UKGU+tq6i2lUNTuRAJyqCLLTy8/hlM1zI0jQIZoCwVpmOJunZ4lBBQmGOqL8f1u78Bldl200B03ZhCFUhJhciBm1VkAi+8+QZcffUVOHjh"
    "HkxGIyxNxiFTLpcSmRCQ8jtQK4NZo3COCLxs7W40ESpm/MyPfA/yzFr2stEAJAzbg08jB73mrRAEVNrgCHNrdUOp+6MxjOulwK/IHEYRSuLIXRSufbHv7yJm/IfvZnuTNVYFb0SMWxibZiIJtdKoWYMmOaSx4RZCENYAXCr2gwi45SnXopACmRSYVzVqbcAjAbDAeFJg"
    "yd30ey7ai6Zp8ORbrkEhJZgkPvHxv8F7PvMXAHI3/aMoALWrIaQIsrCHlQ8MDTbSzNFn2G4yVVWYb2xjtLwMrWtAEqjcQq4qZEURDJTYcDjE0LFogRAwObBebUFAYHU8BbixVU45ByQg11awsryMc+UmiA0yQajVpv3+DWMiV7C9fQ7gBhgJZKMlmJmG2TgHSGmBtbzA"
    "0u5d2DRbzkIIIB5h4gJGAILMsnAQes95EcipDjKg1gXUQYTtVUwtkM5JWrNo5US+QnOVou8cyHu/GYMXXP4WfO3MZ2EkQ2uCUpYYKkhAK2Nhf7JVLhvCeJyBmVAr2zk3CsgKglaO2iBybMzP4bK9T8EPveKXLNvfsQjito8iE4KEe9DlgKKXOpp6ug+rU3kw8FCSxKw6"
    "h0Nn78GpzUcxr7cAJiyN9uGClatw0dpVuPbgzfi1N30EP/bul2Bbn0FOy1BNY9uN2k4mGECxzBBFg9qpa5rKj8xdMAVZFvysrPHyA9+JkSigdY08K6wnE0To6ykmLEYmcoYNhJ+QZRmElHZhCwFkGRQJMAkIIaDJ1Vratrn5aBTAbKekAMCYM6NsdBi/Ay3eEaxMDDsd"
    "FoEhIhwHIXbd26Eo3UDKlvdDkR1OnDjTOKoB587z3G97sm2Y1gxWBtKN43Ogr/Ane4OzAba1hjAGwtEEpPcCj6yFpRGAyGHAmKkGeS6gXZ4jImO+2Hqasci8jUADQCsHVlG7eI0xWD90Ehfs2ocJTWBkDvHVr+L0Y4dgZiXgaCPFym6Xf4nICYOg2cAYYStZyvDbz/xh"
    "HJ6dxn966C9gWOOtN70Kz7j4BhQyw5997e/xV0dvwzue9l04Wq7jcyfuxY/c+Drsmq6gqmv8/MffhTc+99tx3QWXA8T4jS/8EfbtX8H33fgaHNs+jX2TNdx54gH8+7s/gB+89Q147ZUvwONnTuA3P/UePLhxBKvT1XB4CnRY3a6FNoZdVekOpmiC6MXMSVKTz0VMdONt"
    "vkDs8u1zGLIsw3a9jSt2PwW37Hs9PnfsPZiKPWgaA+O0wEIIVJW2jHVtp4mjiaUgCWElYkoxsowcR1KioTkyXsXbXvv7WJ3ushQEKQerpDYlmnqFdQxLDYkEM2BBBdaNKXclW9XM8bF7fxu3P/p+nJ0dQ1XP0WjLlWIiCDHCrsnluPGiF+OVT/lh/Ifv/wf8s//4cpwp"
    "H8E4X7aaL8edMYaR5xJNbT+wTBDmc43xREBpbwSQYXN+FldOvgHX7XkW5tWGzftzkoxgJJeQz5DkIhpXfTAxZJZhbTrB2vIUy0tTTCdjTEdt5HiYMLpDUCDiF3hmMlLphghTsAhY9IsuDr6MPaM8p5LaiaEPK4ij5YPrRCfR18T2lVE6UHv7emeKmDWcWkUnlU0IMbUT"
    "KEFx2rIzo9Ma87rG0mQJe3etQI5yUG0Sb3mKFls0p3KYCvU5N6798YVZSMghoC5rEEuMl1ehmgaq0Tj9+CF74TBj89w6mizDylVXg5sagqyOzxmyWVNGEDZmm3jhwWfgx571ndBNg48c+hy+fOZ+vPXWV2N1NMZnD38JH37jb+Lq33k9XnfNS/FoeQzHqjP4P57xHfiD"
    "2z6IYxsnIFnibS96C+46fA/yLMdH/tE78RMfeyemkzHe/qzvxd1HH8BnTn0Zv/wNP4L/8wXfh/d87kN46TXPwLfe8CI85/feguM8AwoRML62CnKWM8ZWRNpwG8dBHffiyE7fsLXBtvw407EapjBV858dhWBegUxmKOstfOPV34evnvwiTs4eQMarMKwtfUhYW5m6cYlD"
    "yqazW8yV7FAJbhjGAlo0mFcVfvXN78cNl91qsURV4/CZr+LM9mGUja1s16YX4uLdT8Ke5QtcylGSRpIw27sM98GWsE0t7i8qr8Z/8Pjt+PCd/xq7pxcBJrcbnQEu4PgmCsfO3o+Hjt6Bj9z+X/Gqp/4Yfu17/wxvf/d34kz9EIp8bOUNTtCbS8u1EgJoYG1YR2OJRhsI"
    "kaHUm5iqA3jJwX+MutlGMcodMQiOWNkynhOHRkaSGMKOiFYqhb+/816sPvQ4pqMc+SjHqCiQuQojnvx4wLXdfPYAMM4tFWR5SiJSyLNxnJfOhmV2B5urSjIS0K6KiI1WhDO+CzmL/uCNXOc4svuliGbieVa+RbIVHAV3S+7YTJOjYjBFQbTRghBoWxUflGCTYHIcPvQg"
    "siyHMWXgObaJOJRgUjxwmJNos+ZFzBgyHCLMmAjzjbM49KhGJm3kG7mFPK8rmGKEq1/17UA2sqlIRCDH9CdJYUJmZhXect0r8ZcP/D0OLF2A77r2Zfjy0S9jpirUXOFsPcdjZ47i9NY6ZqrEdr2NRjVQRuPI5gl85diDOD07i1rX+NMvfgQKGr/7xn+DT5+4Bx/+2j/g"
    "FVe/AP/6U/8FH3zkkzBv+xx+/qO/g5/781/BpRdfj/ve/ud409NfhV/5wnuBUWZbWgerGGOigshSKTKH3SG+lBw+5gOPVeScG/zhjZfmRNbVbjAQQHcYGFZuzRjkQuJbrn4b3vXZHwePKjDnLljDLpKqtux+1vY1aDcAaxQjzwnaSIA0trfn+Dff/T684KZX4v7Hb8cn"
    "73sf7j3yCazPHoXiGUDK2vlghHGxhpfe9AP49mf9pCXQDgzwCIudarN0wuBLtKGoafsgrth/C55+6XfhS0c+iKVinw2aZGVlEcbLIEZYLsYoyxq///Gfxx2XfwLf+PRX4X2feheUtK6MjWIYBYyW7CGVSUtcyzIBpYAsy6CoApoVvOaaf46pnIIEMMlXMC2mGBUed4o6"
    "46g19Ld9lNlpI8OVxhfvfxDMEkY3tkXMBEhmkQg38kt3jPTYYzuJeIyEum2keupRS65KE6CQPB1aTGNCxUSJ4LW1NRkGIJMTwoK2njvk3rdIcgy5fR9h/OQPexFpZakVEXeUDyF6ywCmPoubblp1UzDuuHlQYvVLUbguRdUUyGOULScrntSJyQi8NMLJE0ctZikNDjz9"
    "hVi69CqsMWHXVddCjicwdYnxeM0+Q3fRSPeAS1a4aHk/Xn7Vs/Deu/8KGUu87srn46c/+5+gJeNgsQ/7aAWZFLjhksvBwrbARhkIAzzr4idj9/IufOTEnZhXJX71dW/H0ngZb/vwr+PxzeO4dt/lIAJGkwkuWN4PCMKjpw8BssD67Bw2ym2sZGPrNisphEEgsvAOa8ZN"
    "EOdV7daHcRNCk8h0WEcE05bTE3hscSyWxzUBYJRNkIsxatTIaIxT5TFcvHIAr73hX+L9d/8SxmOAOYM2NkataQyMU3dIQdDKZSc2jFwKNKywsV3it97yl7j+spvwC3/0Xbj70MegaAuT0RhFMcZELjlemwX0t8qj+NiX3o3X3PpjWBqvhMu9S2+gOKQk4HIUEUfju5Wi"
    "frkTtTMdreD7X/QuvO+zF+CTD/5nLI32gIW70SpGOW9Qa2XDGg2wb2UP7j38KRw6dT8u3n0pHjvxELJcBJfFLCfUjQEbgaYh5AXBaIG5qVCXjN/+nj+FPpnh4eP3QOdznNx6HHklsUvtxVUX3owin4Kh2rYn2nBtqnBUlTBjXBTWU4vGELm0yc/ednkAxzOhLUMiT6FO"
    "tYNudJM3NIhy+ZKWKbIxCRs6jmJKNGSpfCo4ljNSsJo5iaDjWFvGaYqMJ9W2b4mS5AYGojUQVYwkUG3NLHHWRC0hpQzmNHGpC4tyFJYQc59aTM4Yg71XH0S+MrGE3XIb00suw+6bnwkz33a+UBpru3djPJlAs829tPvUQIAwm2/hzde9AruW1vC8i25GURS4fv+VeOau"
    "a5HnOR45cxjv/vwH8D3PfQNecPBpEETIjADNLa73ri/+KY6Zc1hdWsb+lT341b/+Xbzpmd+KG/ZfCTObQ602GGcjTESB4xuH8A8P345/95qfxGw+x2tu/kZctLQX77/zr5GZAqqaWafWhEtlqRmCCLNZjbmTb7FJcwnjz40Tkm4c4pD+nl9bkiQAgaObD+LU1mEorUBa"
    "QjQjmDrDsy57OSQk3vWFd2BpZQTJhQXeNYeKi2Cn1sYw2Fi75I11hd/6/g8BcoYf+r2nwmALS5M1LMk9ABnH07J2M4Iz1GqOjHfhR77p9+xhFekKMZSvgT4PNFtMaOceKEok7Og3y/DmF/5bTIpd+Mu7fgkr472AERCkUYwy6BKYz+pgSjbOV7GttsCoMMrGmM9K2yJJ"
    "y9/QjoDmU2dKU6OeC/zGmz+ItV0r+M+ffQdObN+P7XIdmmqInCFphLXpRXjLs34N1+65GZobSGRpRQBfBhvHs3KsczZgQWkaMZsewoJOq4I4mJIWjO3dzzZu02vnnBmMvCjO8KMIb0p3tU8DYv/1wXWii1JGrhqRcV7shxT1BB1HT+4EvHI0Fk+xLg9qa8MuOZjcxIoi"
    "aVeXsd4VzFOvyOcO78QHFBBZTaiUErsv2AcGYXZuHcyMpSID0QiUFciLAqPxCEII6x7i3To0w9QGsjR4yp6r8ftf+HP84F/8ElaKJbz/O34JT1m9Ep/+2h349hu/Ee964y/jj770V/jvd/9PPPWCa/DoiUM4s3UOdx2+H//nS38QTd3gBz/yK/jS0Qdw+/rD+MJH/h3+"
    "4yt/Ek/e/SQc3TqLu48/gDPbNrXnTX/xs/iNF/8z/PY/+hmcmW3gO973Nnxp/UGsjFaxsbkBVStXVUdYlCDMqwab8xrFtGhxKJhe5qQnlcZSHorBLoqdzA0ECcz1Ft7zhbfh0TN3QKEEk4FuCFxPMM324oLJ9bh598vwc6/6Y7zzb/4lzqljGNMEMNaZQkjr6GGUxdpE"
    "Rji1Pse/+/4/hubj+Nn3/wD2rq1hTLtgjMFc1RCCMR5bXFjKHE2zDTZT/KtXvw9PufKFLfCexqD2J4OJT1Ykfk5vvygTjRD5Sbd4DhuDb3v2TyOjCf70jv8L09EuazNsDLKcMJkW2NionSEZwEZAU4PxBKjnEk2tIScWP2mUvV1lJlCZBkYV+NGX/QLuPvpR/Mr//E8o"
    "lhkFFRZoRw4JiTwTOLnxEMq6tNo909hpIIve7MCn0LADW0g4FjuhZTqHkiQGeUTY2CS8ZY9JnYeYO7avkfKMOGjt0NMHxF/X14yFKpnaUilEIEVaK/ZJP2izTdExJ27TdT3mzp3F3Z8Eo8OTohC263zbnXyoJSUuNg5pm2iXnBegBhP8r0wkog74jh/2AMjyHFmWAVmG"
    "0dIyRjS2R5sQrf7VvSfjQixYKSwvLeNnb/tvmJUlppMlKMN47R+/HeOigMmAX7/zD2GYsa0rjPIRfvSvfgO6tvjqc9/91oD9yUmBV/3JvwAEYb5d4qm/810QWYYmA17whz+MRmmMsIIjs7P4jg++A3tHq9hUc9SsMJ0uO3NBBL8rraxffpZlqCqFrVkdRNFJedxJQw7i"
    "YjexDvVtfHhFn74QEqrReOzMnZBZA6mXoJSdDCtSWJ8/iqNbD+C2Ix/C6255G/7Nd/wx/tX//R0o5RkIyu3U1RvkagZpiRPn5vjx1/8s8nGJX3jfD+CCPbthaqAWDYxmFIVEnjvimclQ6hkKsQtvf90HcMPBZ9qJuMjQNV6IW1mOCoHYCCRLdIiJpiu6bTsGYX5zaaPw"
    "rc/6F1BG4X2f/xmsTfaB2UAp+xBHkwybGwpaGRdWALBkFGNCObeHAAmXeKUtEFhtS3zzLa/DZx55L+469DlcsGcPBBO00iHJBQbY3NrGa296B27a/0xsV1vIsyyZlPnJGxJzNDfVk5lb6Pa9eaV+0n51sCNyNz8gk/1IUfZeglmhtTtH7KAZXmSUuBtrp0yURtNxzkjW"
    "IsdsFfezmBPdXfD1DphVK0dqD2fRhuTGuj3mqHW1bhMU5E7O8ybmBREWVlFpDL1pL0VuBb2IqgZXmoe/bojb2Fx3OkopbUvtt6gb7yvvLlGbgBcpAsaTMaCMI/9KGMEQmXAHEmFZTsG1tfyhzH7GLCQEt/mXRtkKfSILNFAAGUiRoWGrrYM2yElgJJawUZaQWYapzC1R"
    "lTKgIMgig9EGTW07kHnVYHO7svI2jwe6cFtOcRqkIWrthmaHXRJRhx1OUKbBnsnFeOMt78QffP7/QJZVAOdQrFErDegcEzlCLjX+x2d+FQ9edg/e8KwfxO//3a9hMrXTwKYxEMv2+505V+F5N70Qz7/5xfiJP3oVVqZT1KUBpOVZrqzkKAq71wkCBhWAKf7Vt/wJbjj4"
    "DGij2sNqyN1/gOfAUceUDUK6sUKdaJipSgTBEtoofNtz3o55VeEDn/95rE73gQ3QKMueHY0ENiuFprGJyFrbktKfDyKzZn/EEuV2gxuuuBGPbf9vnDj3MC7YtQ9KNZZtWwhIx7va3DyLF13xT/HCy78N65snMZlMwCxd2ehHvRy1K1GHJwSkYxf7EFQIEQSusS9PkrEV"
    "a5ioKzvvmDxG7U6oGJIAzXbhCY7sFmEP9CAe7ti0JcUVtYRL7rSH1Dnb2q6PO9q+gewHSpV9iOLnPVuKyGkII50bR9hZqMSS9sQ3wWnLGdsAxTFVcAxzgzQROFaKcecyYFgnEBhAGgGhCSTta2FffoauXoQUZHhir+licNEGIoCcn4wha90cgHETB7Jah85MiOAs4W4T"
    "0EhCZnZQJKWEUhrnNv1hZUmvIsZEo1Qvih8Ap5dK+0nFwuL2wtmuzuLmS1+M75j9Jv74rh/HaGxju4TWaGpt21QA+5f24rZH/xIXLT+EfUsX4uTWYWS5hNaELLNwQF0Cb3zpD+HdH/s5aK7AehU1a0AR1nbl9uuUneAzGZRlg5947R/hpoPPgNIqkMuT6429mJsGnSfi"
    "BZr5HjFtVzjko4UKQIg4Xz08RQF7aL35RT8DcI4//vTPYTJaBlQOVrU9bMYCWxsuPDUMlYTjbjG0IWjdYG2yH9nSOk5vHsN0vIKysn9/MvGkywzb9Tpu3f8GvOTKf4SzW8cwnS5b73TStqR2tAFvCOdfZ2vMj0CFUFrj3HwDIssjSxPRVgwe6DSR86PjfbFLePYHGnWe"
    "mt+EUghMigLSkegCGznBlETaxnEKSQRv8PjPCT0MjGKrEs8hi0B0oj7GFNubtIcd9aktwie0aJDMQFKAWQdKhInTT9tTMamyOHhbULCzRvi9rsi+rQzjC9fjct6mpi3WfPISIEliThq6ECAWrTkNAZDxoS2c2Nq9XUHJ8g4QpXB6GCntQRxLvxxB2Ek9wvtmET5WK4Jm"
    "AS5rlGWJfE8BTQJb89pNSDmE5Wqjw1QwMWkNt5C/0CjFCV2lK2L/MDdFJCac2z6Bmy95Mbbqn8cH7/8pjOUKwBLZiKEroJ4ZEDVYHu3G6fIhmGkGvV6AhQI39ntubDW44eIn49Dxh3HbvZ/C/guXUakGRhNWd1mL8roGcpcIdG5rEz/68nfj2de83LWBeY+hzjivcqfP"
    "w+oLmqljW0r9QMxoIwlIGKPx5hf/JPYuHcR//ti/RNVsYlKs2AQNEEbjDFvnVPsJCIKqGNwAujEABPZelGGzPAUpC1SlglGEyVRY3ofIsa3O4fLJs/GyJ70Vs/ocJpNpZCRnEm/s0At3cCNA2Bh0ACtFgX/++m/G2q41F/tESQ/tcYOYPGljk4TjZJELu7Dthwm2Ma2L"
    "xX2PHsLH7rgP52qFXIqWvNlBm7uHlegQfykGqONW1N+uwe/LkvlEVAWG6V6SXdf2vtxbRH2XWf/9jbDOCEJmMEJZjRvaEXual8cdIX6nuuKWK8Qdq0Vmk3w/f4mwq2os6M+u7bcnTi4FNuZzjMer+N6nfjN+/nN/AMYIrEzqtxRjiiZ1XLAPrpNx6aaXbQXG4e8a5d6P"
    "iCAFB3UwnMtfw0CtsStbwatvfAk+dPsRGGXTwuESxdOavV1/7EbNflKtjYZxHnQejI5/GY5tZ9oGUpDdW8848Cqsbx/DRx78dSzlu6FrASKDopCYzwwM1zA6g8wNdu0eYf2csoe8EKga4MoDN+LT9/wvCAmoyuoPJysSBkBVGRSywKys0XCNH/vm/4hXPO1Nrg3MFzvs"
    "ddpY0KIpIZCxYRfDnmIp4Rbq+Fp3rSDaw0FC6QavfOZ348oLb8I7P/xjuOfwJzGdrgE6A5sGUgpUVQOZCVDO0HMbud5sGezetwSRz6AaA9XYhI6lZQnVALnMMTcb2COvwSuv+nFo0zhaAiLhZxykQcnvhXLdTd2EFJgrxjOuvARv+8ff5tIThp5SN5yRF/y56SxwtwFk"
    "hk9/8Us4cuIs/v5rj2FS5MEet40fbtNuDXcsYYMOjxM9nsfXRLhF48GoSGQfiaVObM+YsIkpAT8FWr1joHU67EgQORpIu7AM4uTnCKLzmFhYiNy3U+483li+1Ma0+TxxH4Daujr4cNtQyYgM/+5vPodffOU/wRue9EJs1nMbYBGVK8GvnVLfrgQvROorzt3JAsctqUlN"
    "CSM3TR+UqpoG111yFR44MseffvF/Y3X3Hovdyda0jgPaZy8/w76GNm30V2T1DaTTQmNsyrk9yGIKhKMQyRxb5Wl8wxXfjTMbp/DJQ+/C6mivPbSEgcyB+YZx2JfC6uoysmYVx7Yfh24II0gsLS3hvqP3YjLNUZYaeWFXoW7sYGRrvoFcLuNtr383Xv6Ub4sE0JxcRmKA"
    "QkQdl+PBCoto2DImlOs8zDoFp6WzrYgzKK1w/WVPwTt/6KN479++E+/9xK9jY+sMpqNdVu7B1mSNctjEZ8PQM8JkLNHoBkYB5VxjuixR1waFzLHZnMXF4xvx+mt+ArnIYWBQCAlBAsKJPkUUWc8uLYdgEi1V3OL4JJb5bI7SWdq01RGlIQou/KCNOqfIiCxK5OFWsc8M"
    "ZELi7MyxppsGOpfWpD3mt4kYr4oz/Fo+Uhrg18p0yKcXdY/WhAPlWMpao5UxUO8i63HE0E6MmeP4c5F6tIeqrVsjpElFAV+jVFTv4yLZ+E2JJEourg79dNpoAyNEO730W9cwpnmOu0+dwRvf/WHceuBiaGVTrMkzuBOhNQe7Yx+w25bRXrdn+nQQisAwNsjyHDLPwFo7"
    "HagIk1bj8LE8z/GBL96B//3goxgvLVvsdIik5s0l4yvYjwUpnoZGSCPH4cFIau+2cBTWsEBIzKqzeMW1P4Cq1vjfR38fS8Uu6EpCKWOF8NsanBFm9SZGxcXg4xnKzQaFWcOp8giafAPUjOydLAmmsSaYp2Yn8eQDz8VPfvvv4boDN0NphUxk6fkSVCAxSZBa0utOMYPg"
    "yA+rQ4fnrviwa7RFXSW1Y7nLDMYYjIsxvu8VP4UX3vBa/PJ7fgy3ffXjWNuzClkIVKW1s82crlgKCco0mtKgmtuTnmHzDE+cPoNbLnwhXn3dj6CQOQwrjOQUmbRCThminihJeY6Rdh7AZVpSHUEKt8jg04zTKAQCIXcgqiABQ3aoEAOyHIh7MrSQmRTO10nBKA3dNKAM"
    "gemcvFKOfib7qqpnuJ8w7StVY1bWbYUc3e7kOGfG4Y9L4zEyQUhooL7K6iTUJMk1iRTC+bS4nWBNBymKn0+tjBk8WEjFyTHJdDCegEUgG0dyKWaL35jo0CTR5g42SmH/7jWcYMaH738YSmlnoWySAQHCZJEjGVekr/S3PVtybOzpRM7wz2iDXEosry47PaD3qqJQXWpl"
    "048NCyijsba8ilFRIC9GICFC5Ri0dfFz8A617CpM8hUmJ8+ud6L6ENYoG1EIWxnLLEOmJGb1Jr7l+h/E2vgi/NWDvwNVV8jMBMY0gLAwjRYGqjkBKGnXMBQeWf8CRC7Q1IwiFyAjsbm1iSJfwlu+8V/j+175UxgXYyg3DeyzXWjQDy1U/AOHlPeKJ5DzwxogjvYYqLSg"
    "8RxQ5HuZiNIK1152I9719o/g3773p/Df/+E3sbp7ClEJ1KXGeCzAgpFNASNrzDYZRgvkowyzegZUI7zlhT+HK6dPxXx7CzoTGOUTZFmGvBjZIAJnCwNB0QTJGg+1erXoIzUm8gSPfLLcWN9wpHV2i1mzxr/4u9/HY/VZKGHwxoPPxPfe/CpsVzP7syOGut3T1tvIVz9K"
    "KeimAcY5BHPI0QtQUhLrTpFQdSj0wy7ZqmlwwyUX4htuucESBB3nRpCAds++qSpobXVcH73zfpyuamTuNTowqG/vEen+AqM+EmTDkCP8cZhsSbdBYlDfA85p9RdhdxRRNshZLHuQODqkPHVBRm2tcdpIe8mk0hbhyJX71laxNCpQVnU4rFquUlr9xZhRQk2JBPStrtQd"
    "5MyQgrC6vGwfSwhPjS4AYysmZRjzyrowEhGyIg+0DEQDhFaMLnoHfcq/S0eknDhzptWLf5YgshWWlMiyHKOCMSs38byDr8Lu7BL86e3/Ho+dewDT8QiUCbAiNHMDwSVIArIQMHmDBjX0zAIFgiROn9vA9Zc+HT/9pt/Gs258flh7MmkD0Zf6RVN3js8c5lZ576v92MBv"
    "EQV+Z6x+GDijyMtbCIFCWIfFvMjwju/9DeRFgf/6d7+CpWyCstbQuQELIF8yMADqkjAqJDY25rjmwM14x/f/Lp553fPwZx9+H7RuIMhO2/K8gMwyu0Hd1I44VrXTgHsqeh5N4TaP+EeIbnvlDOS01rjt7IN4iM9h1tR4yvIlADMUa2SQrh/vGNIxhYkkG0tkNJpR6RrC"
    "ZB25jmc9G9c2RxYb4XCz7VAmCKMsw9bWNr7zBc/AP3n1N3VuDIO6rlGWFbbLEue2ZphkGe4/dBKHHj6EtXGBWquokvFsS0rOEXBcbbTtZys1EqFVM/Fm9+C8MYMVONDlkaHXvngtZiL+9s4RzvzO8490NHmND3nDDJEXGGd5OozhNq7eTjhFYInFWsjU47kD7xoDSYTV"
    "5WnQ66GTIegpNnWjUZUNRkvjJB+xC3mmrAWOh7t9cm+XksKtqy6jP1DxmC4LhpQZstxAa4NM5tjYOoOLli/Dm5/6M7jj2CfxycffD4U5CBlMY4AcyJYAygn5yMpz6jlhMpHYLLfwqmd9N37th/4AucwcLCRs1R0P7rpFUOfA6U7DExyz4+6RoUsp6jIUkz4zxa268LDV"
    "DdkNduTIERw7fhzb21vY2trG9mwTl+IWHKCbcbS+G0IUYGhoBmRBUBUASDSosN9ci1cc+Kc49sg5/N2pv8PK0hp2Le+yt1WjrGo/Ak79phedlpDj90MxkcnhUR2hsondD5gxzQrXBgKr0yVMVQ0BwlIxgsgz7MISmIHtukzBcW5H9cIBY4YNMlY4uHsvRCbCpkc0eKJI"
    "D8aBVEoR8dngxOaWbUcjs7pZOQ+ODEorlFVjD626xnZZoZEKdW3jyGoBrI5GIUkZzv/LA/mmhbRdodTSMEqtsd00ECJz1I4O2z0arxMo5dvHLrZJSowJc0xOHkaf2mHDSNC2SJzifjH47Z0LgNYrJ9GXBiNBJELteFUzx1aArf0zSYHVpWk7VYZMDnY/dFBKY1abQGkx"
    "UQpOekjFnvX+55hQoRHHFA8Ddj+Po8QhH2KbHgpt32wLF8tBVEQoxmMsLa9ACLL7dL6FZ1/6LZBqFR95+D9DGwUwQSsFMRLQDUFKhpoDZDI0mOPy0VPwnL1vwEc/9jEsT6fYs2s39uzbh/379kFK6aLYug6osft6GxgTdxBeID9Ub2QYIA22G4Wj+Cb0bmB4KwtBqOsa"
    "Wmnce99X8N4/+kOcPHUSTdNgPB4hkxJVNUNdN1gzl+L06v2oVhSgCaoEuAIUEVAo5LNl7C+vxUf+4i9R1RWWl1awd99+LE2neMYzn4Fn3Po0nD27Dq0V8jxrGe3eoSBWrLMJlgsJ8Ge8VIcTuQMFQqad0/zkP/w+Htk+g8lkjMNmG8TAeDTCX525F4/+9TtxrtrEi/Zf"
    "jx99ymux3ZR2czMnWA4AZFmOrXmFH33FC/G2f/Kd2JyVkLLNOOKOwBgRiGyc3YrSGivTMX7nQx/Huz/2SRAETpxZx7nNTczqBoW02FmjGlRVDaUUGqVgtEbVNGjqGlubW/jGG5+E3/nxt6Ku69YoTxtoo60Xkxuda2M3TdMoVHUN1hof/8Jd+J2PfhL5mosHs946Difm"
    "KFfCO4kadCii0Xv1LgTDkzfAFn3aHZYUCcvjaLBEwcIIfCZQ6wkVpozxMIJiX4CUoMuhQgJay0+H1wlgeTKGlCKSUMV24k5zqRmbpTV49OuMQH0SUUTrMlFYCkcDnTi9OmBX0a8Y9xK9b83JHiAhsHv3PmxubeO9f/gePPbYo5iXJYTIwNCYFFMc2H46HpSfAeUEXQuI"
    "DFAlAGWVBGKikJfLWN2+FO9//3+HIuvgIYXEysoaLr74Ynzra1+HgwcOYN++fRiNRr12MHaB6ZpLBvpNl53HPJSag4QLQUOwFSP5oLTWmM1mmEynOHjgAF764pfg8NEjOHH8OB575Ks48fiD2DpzChtnz4IbA3HtBObiGWZnNIQwqLcIshCYjMZYOnERTuqjkCOJyXgZ"
    "u1ZXcdUVV+DqJ12D66+7Dnv27MH29gybm+sYj8euUojSnomcx3ds3G8xJmvnYQIwndxSItXYKaPxqRP348HZKeRLY2RZDqntonxMncND507gTLUFAcI/i4Baz7NqHSFdxWIMlqYjIJfQgp21MUMyBd8p7f2LYga4cCp5EMQoQ5YLlLMSu1am+Pcf+jgO7NuHG644gMoF"
    "fFZVjUbVqOoGZV0jI+CTt9+Hz3z1cUwmU1ywtoL9e9Yw295yC9/YJBRjsS+wgdECtbZKhZkxYAkoYyB0jaas0IxLGKV8n9ha+FI7LU1vttRtoJXZOFKuP5hd1Wsi22QDD51ZIXlMCfGBncRI7VYiNns4gGAiJwtqD71Y0N6Sw3pcIH+pLU8mdjIW3GRTC2jvUrI5r9vL"
    "nlv+WCLMD15nrsI0ZMNZo1mLXwttCK0NArZPIzVhjMM8KBYORxbho/EUu3bvQzGa4NZbn4bJeIJTp09j49w5HD/8KI6e+wrKjQrFrv2oLjuDZq6hGmNlSxrIRhJFncMcW8Fjs4dQTEcYjaZY3bUHlx44iGuvvR5XXnkVLr3kEsxnMzz00EO44YYbOnQpSt5b3Ey3hRAn"
    "UkD/NdkwmyFliQ/SUuP0VgB1XYFZY2VlCa/+lm8JX1aWJcqyQjmfYXNzE8bYmCxNGrVqLEAnbWD9ZDTF0niKYjJCnufW10gImyJdNzh95gy+8pX7sL29BaNqFMUIWSYhWUbYRwQYc4iRBFgk2FBCZGSOOLL+9BIwmQRPcsueV2yJfu71GBIgZYmDiX8YKIrxcnieG2/n"
    "YKzlOUQxCtIO4douXxlwhIEYL+3I7WtdGY0hWUOrGmUpcd2BC/HK5z8du5aXUKsGTWOrKh/bvjWboaobMAv81b2P4MS8RObi5nWx0o7AbeoCpN9QxkAqBdM0YLMNbWoIOcZ4aRkQwqYfK5XqEqkNE/UGhMNUGepNamOnhqCBZMBE7ZPmiDhqLJPcJATw1mm11UOa1Ik1"
    "+pwTdkUguFIbkoFUr2mMCZUVs04TqcNk176mc9sVlBP9my4bsNO2cZwmGs/GCM5lJG2nBKU4bIsNUe9JJ0YiPmRba2xvb6LIc7z2Nd+K177mWy1eqxTm8xnqukJZVmjqBtvNFrRW1iZGa5AgFHkOiRyjbIQsz1AUI4hMIssk8ixHXdeYbW/jxInjOHPmDFZXVlswvQvF"
    "DZn0Rdgtg9OalGPH0Rj/SUIMqe+cjDQ+mohCYmw5L1FVdmNkeQ4pM6ysLGPX2gouuvji4J7oGerGuLEzM5Rq0DQWfzm7sYHZfIbtrS3M56WzX7aUAyEktssKs+2ZfYDScbKEl1v4D8zEdg0Bs6GoOE+zjinEO0mSeMWlt+JQvQ4B4FOHvoIZN1CScXCyGzdML8Hm+Cye"
    "u/9amETUFH9HV3URoRiP8OmHH0Nz26ehm8r6XRt7CHrsx0tWAkPf0RKYANUoMDG+8PDXMBqPsVXV+McvewH27d6Fsm4gZIYMAkJm0MYg1xpCSpzZ2MQt11yBWy67AP/r/sdx/5FjuPdv/gdkswVt7MTNB3Nq56PfNNqFhWrMqxJzpTESBkcfLKFkYcFcFw7rsgqiANWo"
    "QGGkFs4d/MZb1njSo8+YZE9FdWBQHJpKbOPaDVtw16d6E/kNwC3LnuLJKhL1QgqriBY6E84Ym61mkF1rvDQahbRm7tgAGG6hlM2ZjUCj4EzLSCzyKZZ6OQOZjiNDYifNaSKUzYAU7e9zmyMwZA3FUQtp+WhWG1c3Nc6un0aW5cjzHEJYUujK8kqkaLGpP77I8C4aSinU"
    "TW0Pt2qG8myJ+bx0xckcSinILIMx1pI8vswTWyZaQEGI8MDFGNZAoGF6MrbMaEqMxRCIm5byIyAC4CbAbJydhg0Y9ZwYYxQaZWxGoNGWp6TtL6UUlPtvISWKUWHBVmPV9DaGqkajFOqqQuHGxMY4oav7YNmY0K7ERGXmtAIwTjBLERZhYPCLz/wuewA0NV785z+DB9VZ"
    "lKrGy3bfhF997j/BrNqyXkaqasmWccXgcvMarTGRGT5+ah1/dvRrQNMA3n5Dmza3yRM7WSFkxBNsMsf2DMgEcPQIDo6XMDPb2DWdAGAUrBwGYiOomBiKDaQwqAQgYVBI+54PHf0aVu/9eayNlLUZqRmk7I9U2oa91I19iUYDVQPUANQcGJ26Alq+GhZZSvMgYxCorXZM"
    "W4lzPMmLp7m2vfKHvmmNooLGLrG9jjafV2HEfx6LgruxfZyUHpGFCxknwGXXQrWDAmMMlooMozyz7T1RgnPFtkubsxpKm5CCE6o68hO7tEPuUmsM20SknnUZpfZEsdbQ0m5MdKjRItYltHJBl+5SzLLcTdsdW10r63bhqD9aK0u81RrGaPv/tYFSjdXvaruGlLKHGQlC"
    "HnSz1ktrNCoWmie0nDEKtKCYosGDUfULKA09e5IB6nzrv0PhcErWQcdpk0PCsv2KTBKEFz9HNANhBOAmgWGcbdoNwC5dxGjbAillH6Ql9LVFuHHYgZc4BP908ub/CIp6n37D7MURAufKbXumKIWKDEqpUW9XmM1nKOsZtpoSuZRhgcYAsA28FDbWXmtUSuNpu3fjaZdf"
    "j2a+DRoVlq3tnCU8hKaNpUswOVI8CKaqoMsaYprjS18zePzsKRRC4s5Nxv5Nwrm5QG3sh6mNQa2AjVpicy4x25AYyRyHqwx6awuX79vAgctXoMUahDBgZOCz62g2tpCzhDJA1hhoJWEMIa8sj2iWlVg6q0FlHTAmj8/EkqHE4TVG0qPAAe7A3BzPQkIVZFw2H7X0CTi3"
    "BJeq5JOCAm5DqSNndFYMHBStYkBE7HAT4W9sDCZFjiKX7rASoVrzJnxwguPNWYla+cqqpXOa6PtTBEMYpHkJHHl2hBo9qhI5MOddnoC74LyWlQ33zuF2uNF6jJHbV+hoPL0FMTl9JnsVhejywFTUWjueovPRj8Xqnvic5/mgZjBuweNqiyLWOwYM/bJBuU08RkkIKK1l"
    "C0XgJ0WAK3UYT95VkDttUzjMeMgTlSKmdPShOta2t5BtKzJXjQkRbFd9dFJoz4x2tiWi9VyKYgsT4DJYFFt8Kc9HuGXXZci3RmimJa5Y2WsPXO/PHnCO1GrYH7SCGbP5DM/du4Zfuf4pWN/cxu7JyI7FqY3KgsvW88WWIEADWK8abFU1pqMc/3bfYfzuXYexrBt8aYuB"
    "TcDMCaedRrVUhM0K2Kwltssc9aYEscTxbYbUFfR8A7x1EiZnqFIAYgycPgldWo2uduGtcNUW10A2si3TrLa4FkQ2IAPkYJds2EB6UmcP+2SkcjDncU5I7J0H2YBBf9yyv0UEUFB04HE8reWO/CMQQj0loDUojC/jUS4xHVn/KriEZg6XaOuOsDmrUTYK0lv+eJqIT7CO"
    "NZqR9pOJI7cOnbpdJFy1yOzHf0+fLsQc7JSRyjCTtW1cSAUcB0/EOC9bETaFizYOJE5dPhJRPKdVr+UKuvfh5ElZlvcmfV2OJMUtIndNH7u5hIHBkFIYFkOmnLaE7llKmVncIzmDaLE0uxeQ4DVjprWG7cSQ+xNGaWUfrGv7bPlqIKXNVvP6vMSp0ZfwwuoPY0jXT5ZE"
    "x0Cslawwfus534vGuvADRNhuKgjR5RRFG9iwQ9QtlwV1hUobnNYKx8oSv3n4BCjLMJYShRDI3AHnqQXGSTwMCbxybYxCK2xUBhvlHKhLGFXBqBo5A0vCIMusHfWMGVnGEJqRC4U6s8m8kjWgStDyNeCnvBy1ljDzBqbcRHORBeq1UoBn6BsDXTOaWoMf/gs0Zx9NXCEY"
    "bBvDKPSV0WVgp5rARJQYHWDCfSbkI4lsTHF0G0ctnsvvM8JVXQJJJY7oQEu46x50hkkthD1jjqIW1zCKLMPSOAf7C5Dbit22sZZzuDVvMK8bSNHGzCOR/rSYb3hF0fdDYAB6/mmnJUwwLAptahxe0XrqU+LH32osTZice7NEb9xo20vRBoUw9dUhQ/bakU1xQrGI/5w5"
    "rbCYEp4jOm1fKpkdjrXP4iqKkjZvYCKYmNd1pheC0gOGY2Jmv4wLiSFdEh15rx+O7EioBdHJuo/6r1eOQGl7bJdTyCJJGjHe2A++dZCBL9MYjUYrCFgWNwlKRNS6Sctz3yZnQjpdW3RbRwvMOB937ylvQ1UFMimRS4G5MtjQBoUADGnkTrzduNZgwkDFBpkrwCRsewRm"
    "kFYuDSUiyBq7kZWxJnY6cuAsrfQfxBrF6mWgJ/8roLaC6K15idphhgYESVbEzh5/pALz996HunzUeoAJa8/jJ58tJEG9AEyKtHmUuC+0o+pA5ExInC3h0XjvsA5/KVASOBqOcyus0f7cS6aEsdtFNCSI2ODaGBRSYGmU28qq49XREmAFZlWDsmnC2idQmhEZB4RwywWz"
    "S78dzhB3kp4T7wuTdDHtgWchhxBgC+4H5kbxX16nqI22lAziCDPj4GsWuz+0esU0DSq2ZPYVta/MTCQ1YwCjoojNzFqtahy0ggEgnhYZ+CFV0Kdmmmk72E4PTY+GKiLWdvCm7HistzQDtNPCKN7clpTtQvTlquGUOuCFx4EUqC0gKKWAYWk/BNNnXyORURDG2Qh7sjWM"
    "1NxOGoWwdAOHX2htfa+FoABMCudYarkwHJFP/cjdtnSN1pjmI2QsglcSaY1lAppRhp+56mI7NFBWXiKEzSnU7tDcL10MGQNzZszYIM8I0uvunHA7Y0alGKcrRm0MKm3/v40YN21fIBgk8yAL0abBfLaB7bPrToZkOe5aCJAsQFJC5mMYaqDmG/bjl+7CcnihzCUiW8Fg"
    "CcXxxKtDlowntOiIkONTjiOJjE/R9qz4loZPgSzqp3XouBwY+IRsShnWXSWEa4dyIbAyHlmjwkgUzg5mMLBYVtUolFXt2kDTcvtjK2pKlSI+7MRvehMLSk3b6iEE6cby8yHaQieEImqOu2lR3tBSh71StK/Dy6gifht3DOW9Awp3OHUxh45jEN2dK7k7sLoHE2PAzbiT"
    "IzCMYSXjRV4wYqSI7MV9bpbTzCGKz+6mCgOx95DplZIhDcS1eIbdKNVEYlj3MLVSrejYg5hR2QuYlrAZYWbGGHBTgbXCtFjGUbmB3zr+Pqg5IBwIn4kMoyJHJjIYbW9S4aagUghIklDcWGDcAMza3loAhBv3l9wgY4FJNsKfn/sM7tLHMJku4yQb/MWZCuVMIc/tQVw7"
    "rpAixvWjAmtOsnPEAJWWONtorDcalTYYGYNZXiAfjSBqDZHl2CZCgwKlBIxgaLKbqmENLQElaggIyPEYNF0Gmg3gnvfDVAojrbAftgrTWkXnBcPoBk1ZoSxLFFvHUUwEJjMJntkDQKsGnBfWZdPHUkWpncG5NSJhUscTMhbqsjHJpQb3eRnTMQjkuN2xtokBq0lg1wgH"
    "jYmsjEgK1IZjGGM1fiuTouVveRO8SM8JsvmZs7JEbGXtL0VGe3ImVvpRSDFHpEHu9NKEPrAb9o27oAPo3UmGTk030z3ox6lenJwjj6RKUZ4AUl4iR7hWUn3FtjYxNkgUfQai0xLGXmGcnjhx6G6XlxUdS9lC6wf3xSbxO+Ie9cH/pxCtCaAHvoXXm0Wghi+o4sUX3xjG"
    "LRKtbYXjwcJQXhuDpmmQZSL1b0rsOSgh5LGz9hVSAlrhyJc+hT1XPRtfPvowPvGZPwdqaef4SgHKIB+PMRpNwCysmyrDTqukcIZsjQX+Q4iCQkBWiW2dxAwoQM4kdh29BLLM8MWjx3D/HXfDlDUmhYQkoBZAyQYNGM+QBZaNgHCTmi0CjimDM1WNpmlA0xGweQZZPUdV"
    "zzA78TjOHDqMemsbNQloJtSKULtRc1PWaMoSmSjQbJ1EU82w/vjtePiP34nN+RymsaG2JNvWSft0HgbKEtieA9mogCbC9uYMavM0tupNrF5EWNq9F6ceO4fc2+gkrgHY0V2yH8cW8YrIDzE02HlqhzY72K2kAC07gIsD96rbOiJU2EEsHekaiQjTUR5VX5xYDfuvaZTG"
    "bF6lE0nvAjJIwE4HVsmQJ07DjrkZyZ9FFWjYNyYdRxnuXQjkKr/Oaeb8xHRbmbpioXWOjXGpVOfYHnAIRQV3qr2YqZ5JiaIoFi6FHm0hGozEdj4hbBVA5pN50RE0I7qpEgwrZnRHnljCtRoc+aAbahNS4tOZIxlGzK0KFZaL5PKjWDY6+E56PkhejAfDF/yCT1T0DsAW"
    "eYZLn34LoCsUu05g13iMA3c9yWautagnyIjgj8bCPngTQMM2WIJDUrYjpArfFjhKtmZrUngJgMskBD0O/uR/sYcBrLeUcG3dmIG7ACi3CDJBwR6Haw3U2oqoc8LBp0owT7F+/K/xpQ99wm1Ci2Fph19Btw6Ussixsqpw3fWMkzzCm7e/GUwSVHh8ux1UMJvgpSUKgNcs"
    "DlerGs0VjIMXA0JNsLJ/F449cKzdlILCOL+tBFIuclK/u5iv1vaLAhZCaBeuiTZxIpZO+FcL7I+71vJRdmOyrhlYGhUuLJRD9R4aI2PbwMZobM7KVu5FqVdXUkFQ6jThTSATUD32aPdNIhuwVvZgiN9SNBG0CWhthL3xPvCBJ9l2LN2WnMFQTRMqJjKWykA25ibquFtI"
    "IdZxevVF63Lq9muwKrdsfDYGeVGgGBVRlZfSGvoBN9yLqe+S11M/rCGGATqy6UH2u5302LbLCz7JPVhPX9CByWxYu0MJSeJvePDGV1eOCW9a1rifotmsQ91hnKSBUhfv32fbldaDA7UQmOzaB8oITU1oqjA7ijYTgyQFP22HLAXNWqJDozaeiIKtDIVQAzvR0cGfS3Pr"
    "FBGzlYSQbSVqGIkPLBOgDIyy1A0xsm4Jm9rqD9MgiZZKEkTDztYY7pmelcJeMH7TUfdmp6AVFA6nMiwt2A7ANAYnv/wojAHkOAeIoCSwf98+5ELahe6CPmIb5l6pH8Jk21bJgF2SECVYSiv+NWCtQVImB0Xv0PJTP47gDI4A96i6Xx4XgadHiSSNIj9/g415FWyEHBur"
    "PVRdy9eDf+MpWMQNQ8RVTEB6Y8BKAToSNlMqEWKIPpPdcOIW6w9i539rp6vuhzaqCVWSAMCCHCWnbTmNSf8dV1B+WOIPKOMOqzhhSmuD5dEIUsgkus4HFhNFCZ8R7NRj6xMtII4uJMnSgNSwZbwntrEJL0PbD1JHinn2LgmOJMm6ZdW6g8kYO9o33go3SroVIIuduJ9n"
    "jDWRa/GPdgQ8K+d4zlNuxcr7J6gkYeK6NFYGmyfP9iNNiSMtGaU6puSW62wOtHwyjiapnmfGbgAQxrnUGqol+A7F3ukd61yKcisSiYFwxoWdSaU/MA0n07rwuYnIJcK9TkI80eukP3uM0pnngY31IpMANwqQEqos8U3PfC7Kam43AskEu4z90lIxNDuTwegzpE7EWTQ5"
    "EoVNfBaZhIldlzhi0HNrcNOHMCLDOGasTMYoMmkPaIeHxQG2nuu0Na+BrLBDj7hi49YDH9yqJSj6GYhUATF9KKF9OGfarBhDyrznuko9R9eI+0gi6WRS5492PXkLo6qqrNuGw68scbrr1tx2PcaYHj6tA4FX2wLDSXisKZbtQCbTaQc4547we7BPTE3iBpnuOI9fX/wB"
    "dXEuv7kJkFmGqiyRkQOs2bgEkbaP928yHErM0JqhFbuDK+JWRaUnM2CEwWw+tw5EzmuntayVLhnaTizLssQNN96Ad3znW/BT7/+/wXt2Y+wmliKTad/cYeejk34dJj8mcsum+LZMhxYkvHOndVuIr9UuMTINcqcEiG1fU7TAE2tcCqGbxKlERvhNHLcrIq5sWna9o+W0"
    "vPOoF+HIzaDVwju80jCU1jjz2KN48ze9Bq97yTfh5KnjyLLMcdRkLy/A293a72IgyQpytdJhYwAikcAEuZOUmJ05htn6cTTc2CrOm/ZxeunY6si0OrvE1NHiO6NMYrYtsW0MhOCgI01sqaXAdlmjcrmacRXsLw3u0X/SpCOfixjzxVIXB/fnRoNFhq0zRyDHY/DWLBF2"
    "I5b8oMXEiGyFLqXvcjgqWBgs2pZPyAx1VQfKRjfxyTvO+k7HH1ymM0zzv++xZj8ttGvP/vfK8kpSUYc2NLIGoiFPhY4BZyzTyfrshY6aPGImU+eDYY71d0CWZZhzG3sliCPnydTfKfhsG2NbRKNtG6hN0BFaX6Z2ekQMzLa3UVVzqGYEQUBVOQKn8LpFhUxJCClx6sw6"
    "vuf1r8fSeIz/9L8+iMPbGxAiiwzvoxy++EDu4hPUBiUgoYBwasfDsb9yRwDsLw+RZgUadFQDIQHaJNNx37pxJJDjCLOJk2oQVXMUDjOO7unImZIpkU2BPCObAtWAIjmNDcWwelHWGlMNfM8r3oB3/PA/xbFjR1DVVaCBkCcnerKm8833uFCjlM3Rdi2E0cZVL84bPdLI"
    "sVEQozFycwz1I3+FSmunXbX4mU95b51344fOyX/6gdAM7DabD291lYlpuYXtRqPWhcYTQju8riRtp8PW98/fxLFxnsrgMFpiRtM0mO6eYnMzh1aNpZKwjLhm3HqluRQoozVm21totAoSORNhxUpbQwGltbUSaqx+17drhpxjB7mW32NTYVrvoRkdYBqtVfh9HX0tATDG"
    "HpwrKyspwM59yhR32AiDwc3RBDVDx32B0AHfKfW49lqpsFHIx/YI5HkRMuM8GY4SYo4JImZbAnMICfBVlXJSG+XbQfcgtdaYFCN8/JOfw5fv+xr279mNfFSAhESe5yjywpr75wWyPEOeFxBCoNEaa8sreNm1L8D6bAsyz2yuoHNphAuWCMWJSFNdYvmOdgtLkkitXwUl"
    "ujqfKmz8IhCWSayNTkfTiMmW6elm3NfG5ok+B7HdeKmNsccR08mOCeRB50NgCZJRC5bcc+TeHyGRsXj8MR45GcNYGU+wb7IHv/zb/9VOMp3HvpDOejgCZX2mo7/Z61ohz3N8/o47Mcqk5dfZkyJpDwle+8mYaUJ5YiM+fQJWllSEHdfZOHRU+LafkOJ/EZm032D51yLS"
    "9huUhNAmxNRo5B/vLcMRy547QLQQMOtnUZcVpMNRWXBLPjUGxrX0RlvL7McOn8A73/0B1M680T2wyJzROixUVWkPLKXwcz/5z3Dw4KWoq8qnyFqYxdkxsd+nofUzMAauorLwjZfG+U6pZd5rZHmGpaWlDjVhIGqr4y5BAzg6R0qBLOnxGb246Lh3FvHvxVogt2CyzBHn"
    "tT9kTNhEvmrwQswWVDfhoXpLE19x2dNbB3C4Kivc9+Cj2NiagylDURTIsiyozkdFgTzLIDILFHuj/8NHT0JKgcloBNNoqEis3C0/hYjkD5E5XLw4KcK5eirIQAWhcPi1ljwI5MFAEBRx/mCHcxMFVggvHDbReMABlyLZoB0XyijaKm6hux5R4VB0BFbT+V7G6QQJ7eEN"
    "AuZbcxw+eiq8vvYwiCdViGyshXPWMGic6v/IkSPg5THMeBJVMUh+tq8Sm1npDrSuc2fHuTUOq6WU5RTjltwds3M6ZqeOkV5qjMlpXBWod9N1HVXjyeCiDD7ni9hKcMIh6KkdWRgQsDbY2trG8dNnUVY1tudzN22LVATuAmzqBlobnDp9Gl954EFcecVlmOvWj15QKkI0"
    "zhXDBHzZ71cOHDnliKjW8sdil6pRWFlZxmhUODxT2PXAHWxqgP7Cgzqajvg5Md9fwB+NRcH9E40cxCAhRIamriznKXxvEXADOL2cNhraLVhtWgGzUib8dzi9DZDnGY6fOImjx44DUmJzY8MdVHbiJUPkFzmyp9WmeYtajtqbbvlOEe5BiGx2LUAUAbCIjePRjYVh7kRn"
    "RTqvRGMHjloHii6AuMdI/YPaUXk8AUKSGN3e5imLPLZzoYhN3FI5vL+uSH6uiVjZLX6X+juGC84h0aK7hKJRPwV8R4aYLNZ2GqIa22IIKQJ7ntlORik6eMhNHw3HmF88kWg/qzSoDX0ssZtiHpFAYz8qoq6FcnugCUawxknXGPccP9OM4nSqR5Tu1oSSwAasOfIbi2ge"
    "hpHnBY4dO4Yz66cDtiREPH00yZTv7NnTuOuee/HKl70IWisnVQNYtFM7ZtO2em4fauc8orRynZAKGJZ2LTpL67W1trqWkndjuypqhz7UnQ523GC6vNBImsPogVRDKuoBSkPQBQmBYlRgNp8h95m1hkBkEuKB9dSxgltlfAuonA95E0BY7bhESmuMJwUeeuQxbM1K7N6z"
    "Kyx6ISQyKd2/M+fkSa2YNlqAke12OKCFoOTeTRNL0iQWfysTUUKwC35PQVLi3T8i0Wui++XULZIW3PCIQ2Cpl+gcDw1FxF0C8+AHHnzMOdKy9dofSsbbvkJrw63TaLBOwDxS3J6jqWk7DfMYkiABcu28ErYKEFK2bXSWtQ9NSnuYOS98EdTMnPCd0sTreCqFxChxcDAe"
    "GQGmilJKxypxBgAjcQVl7kiHOXIxCe4m6VMTQ/1QhL0JIQApIDIJITOQQUvohrBJOFkGkgJkEMKFwxzWUKiQiIDJdIp77/8qtre2nT2MneqTiTlXnrrgigvdVlT+8FLKCuZVo6Aj6hEzsHv37uEJYOx5tdOksINnBYtkjjbvkLlW16+m/99pKzkaje2BI0RgFcceNx6X"
    "0lq3eFWjrCmY1hZ0VwqNO8Ri2v7dX/lqtPE48fEWYBjWTmQsbR9uKMgHg52Ney02yxCJ6R9Fxm2Ilqk3bovbq3Z0PiBPCIOkVPVOkU4r0EI8xhJy7Lh3oFG08UhEKUVhjiagqRWcJ7EbMXDODMPU4yEBccXFKdgiWhfWkNJMsaOnaDNvIi1akKeEFo8CS1qQJcgaGOQy"
    "h4JBrRmiriGNQa4l5lub4EceBVaW7ffKpZ0KCkocGFJHgRBz3F/LfgLZqVSTW8ykdJUooLJv+hc72Xa7EgY6Opzosuc0cWFoOu/b/mBnSsD6BqAVGq1QKYauKwgiKAYyDTTObC+xbBIUYBh24DkAFMUIjz5+BEeOHseFF10QqiMiPxjw0jZrTa3cBFe5SqpRLoXJBZ34"
    "Q8wekhp5noUDiwbODeow23uFEA1HfLXE0aE2MFFODxxW0QgUkXHbeDy2rOC6cczvNDfOW8FobUJZqVy6S+NOa9sS2r7Yf7hbW9u474GHMBqPk0ilVnLgzPxdLBJza/0r4oOIopEytxs5sU7jjkafoh2dMLZbADyxRu4mngAdhRglXuitcjq2wuUWD3Nf48MqmDoVIZnW"
    "ojhhmJtkRsXcSVU2zqU0stIhjqaD3FYwoUOOSjtPnkRsRRzp2Fp+VzslZmJUtYIUhOl0gjwrcMkFF6FiBZkVzhAPWLnuRrDStqoSEixaV9tEBB3Lb6KW16sQwoUiPHeDetSsbuoMU+vFxIk/VKcuoiFMi1M5kK9YKcIh0fd9avFJP6lsVSJGKeCCVYiLL8dkvIJaaZis"
    "sAMOmSHnDDAadVUhz7P2kNCRHpJbw4FcCqyvn8M9X7kfBw5eirIs3SAqclT1bWGQyNmup24a1HWDprFyMdW4bogNpBRQlcZFF12EyWQSYAJEaUCDBdFQx7bgnywe4VPcCtECEXSX3EVpDLyUEqPxGGfPriPPsojY1mYXhiCKRjk7ZHdQ+apL2xLUTxLH0zHuu/9rOHby"
    "NJZWV9rSPTogfD/vZiO2LHbvykRWukGw6g3jwkyaE1sbHwRg/ygmPFKYlBKj4x8UNZQmBV1NXPJz2lYmMpCoJktSfyhhakWtQ+rlFNutBGcNUDjUODpoKTG6MyBYHywWLY5CHRE7h6g36ngPd8S3FMVlRfIZ5YTrz37GszBdmljHVmF/bu3G7QAg8xyZbNt9azUDcMQA"
    "54if1uYwUH8YFTnm9tQcnZvfuGxD3xl4MqS/PJgjsjDaw094cb3hHgYT6+Liir0XpBpRHlrg2w04HIVDO6zPgJFJASEkjGGUVYnda8u46+57MVlabn2w0h/QymuY8ZnbvoiXfeOLoJQCC4sFh/3sAHePJYfKqrKHVV3XqOsGRqvAlzTEqJoGF190cdLGUddVcMBSJiYX"
    "LzrMgh9WjNu0eqSOFXI3mILTCO/4z5aXl3HyxPFQRgvpNoNr47xPtDI6cENUaAVtEIVx/XOjFZazDLd/6R40Wnd86zl8yMTWHkXC3sLaexwhIvhFmJTxZv+hzHIBB75i8cUDRbc1R4Gbvo3kbgqPiWQhHKY7PtIqnsZ6R4O4NehiUIE0R1arR4KSGzO4q0bjde6RfLnj"
    "FukE6NGhZn+ObrOzvNg2InpxD8wWHQuUeALGvVgtErbyfs4zno7VtTU0TRVEzgYASQEphUu/tr+vYCCMChWcSeK5ItxPUMs4R0xyjTmEnEa7RZVg6pMQH0pohwCJ7XMXFtkZP4yNMVtsqeMvTW216CsjNhy8vUg7xQEJyNDN+qgwwoHLroBWCvfe9wAmyyv2oEuvEqsl"
    "VBrFaITbvvglHDt2AktLEzSNrXrJHVqBe8UM7SAarRSUqu0erRuopok4WNYJIpMSF110Ya+7i9EjxJmPiStDvMZSjfMw031BOdbzy4rlH52ROTNjeWUZQkrUdQ0hJcgICDLBf7oF7VQwulfaJ+Y0th1000QpJLa2tvGlu7+C0XgEo22iTazqD86ObvwNYZm/nqxoV69J"
    "8QUXa8LR/+c2/iQCBCksiFY7yAkUQVFUeyjBu6PyTg6eJg5J0QzTphQnfmEez2iTUcjEqnY306Q0gIF7gH1UjUc3Wmw/YsDtJg8tXHtgUZzcHLaBDuTUeMYTos4C/GXfXzWb4YqDl+LZT78Vp9fXwRhF5n8CBOGeieUY2Ylv21alDgrGVcT9CsqTX+0Z4EyUXdXYCneR"
    "Thgda76dqCGYPMY0kkDVoBbcbieglOCbbVAspVbaHFkyJ1kAFOLJPPHTaAOWjtvmhO0MchQEChdhUTdQWuPWpz8Tx46fwPHT65g4+CROD/Jk7SwTOHziBD572xfwipe/BLPZDFmWwWt0jJseawfZ2F8adaNR1w3qpoZSOqx3EgLzqsFlBy/F8vKSsyynDjGKBqPoqWOu"
    "A4p4n0Ebaf9/tkjLw7TA3rjrUDpgGZHJDHv27MXjjz2G0Xgc7FY4kud4KoNSttRsage0KxWqK2U0lqZT3HX3fThy/BRWVlYcEVJY4JfYHlJCwBgnCSBbzdl/I8gAEMkl4jxFCmZpkXNA8r5My1vqOSTGCcJIHBkptsuIN1ogH/ruyTWxHW4Xd3zwyTtTxpFgkfYtPkHj"
    "n8/UmRSitR0J398d1PZfIoSOmkjMGrpN0874Ce30kDp3OXn7aNOaMDZ1jVoZfOqzX8C5jQ2LkSgdKkjhN34S6pEYaCUgrumSMmOSc6QFjHP7Yi0jUzowiblzSKrb1KnE32v+0GjNE9L23mgTOW61sW0J/utzDyjKc+z4TMHZDVn9LUdTxugQd5dDnhfYmM0xn23ZQ04I"
    "Wzl5SZJpnUazYoy//MjH8KIXPBfK2ZsnAenGuOpKhYScplYWu3JFh++aMmHzGp909dWDvKrUwz0ltzF1QHharDHM0MFEaEgx3T2aYvuQaNrlX7zSCvv378eRo8dQVVUyIfPWrJ5r1ShbYTVNg0Y1YeJgnExBjww+/nefCryu2F3Rq/G9v7b3p3Y9oft5OmTNBVA1SvWg"
    "6PYzQ+AqpVVLEHjGYC+oF8gprN9LwrBGJ6yc0XJR2ETZejGrxHDivphagJhEotNikWn4AnVNGikOzOgYLEK3cpiE/BhtsPCeaNDlg5y9SBiGwLYVvqo+s34W27PtIEsBt9QHclpM6tA22ksyro45HoglSXXtUwi5Tm0OJXcGIVG73LV65rhqjHqbpKLljpDQS2ei9OLg"
    "OJIsrlYxEToUIPFxb2VU1LuQ4tyCNtC4QVNV0FqjrkrkRQGCi9zzgme3vyajMb7wpXtw55fvxs0334Stzc3grAs4vqSyBG6lNJrG5RE2Lv7LGxSAUFYz7N+3D/v37cNsNrOuIoETSQlNITljKE525g5E3oq9PUUoCx8McTpm77WHHU6E9y7XOoxMA2CulMOyplhfX0eW"
    "FTBKBW2plQrYPrhRKrGRsetSQgrGZDLB7bffjs/fcSfW9uyDUqrFcJQtQ0lY4FGwgWCCFNJ6OUXOCPbhRbl3FBNHU4wi0BH8VKfHIkc6cUSac+gXvY5vDO/oGDXlgrrBDO3NK6ib98shN09Q39F1oWA92gQERC4CnWTjxO0hTZgJ2IdJb/bg0BHP0TklS3JHY6G0gqpr"
    "yGWncfQuEJGlLkVypwTfSy6HGDeinrMuxZyzyLo4tNBMqYtDJ8YudRSg9GfF4xUTdSKEzkXBLVeMGYJaG23idjPGzP5YbMKRswWhbzrBySHeUnQsCbdqHRSqEpzn7eZntCx5NtCG8Id/8iH85q23YFQUDj+OigrfDmpt28BaB+M+QQKQdr0q1WBlZQWHDh2CkAKjooDM"
    "pAtUzpDJDDITbhrp9qygQWZCN1Mi/kzIGMPo3hA9JD9dLN7cS4eJnu9vFZq6xrwssT3bxqlTp3HffQ8gk4TV1RWMRzaCHuGBqDCJUEqhqRtUjdVDlfM5zm2ew1/+r4/i4UePYDyd2OgoIULwonAHFgX5D4dxs28F/QIQghKulbcG4RjojMiRni1MEO04uqeDijRkibNq"
    "64xgNLdlPyyw7ePr41s1dmH1EpaQrqJ1wEn8a9Em8q+KD7+eSR7cAmmrHQ6qetEzoevq3mKU3gwAyeRu5GAhZDi1v3VSHAYwn23jgv0XYPfe/WgaHT4T4exRKCIVcgeLiqtq/z6QkNtjVUB8qLqNHCpoTtnvrQ6oxWW7qEo8cElsciK5CVJBM8edS1ei4w/7Dn7cv38o"
    "bbORvq9Yw2iAIG87dewQZrMtFKNJwHmlEM6OJwp0gYVv5vM5Xvr8Z+H5z3sudu9aw/LSErI8C2ExxoWw2ulgExQodV1jVs6xsbkNpTUuP3gQF+7fj917dmNlZQWTyQSjvMBoXCDP8/BLuqDl1HFFpBmm3eQqn6BtjOE+8W1g9JjgKx3wPADnVq80L0vMtmdYP3cOjzzy"
    "OA4fPoSyrLA9m9mY67oK+kGGrc78+F1pjdJZAsssw67du5FJ662UZxnyPA/4iPQVlnMPQKesZDCMMkG604qUUztlzxdDDPA6sDguRRjoWTD40XFgb0cHqMXFKGxMe7vp1v8qwgFbbVbjihz7517bKGLiavyZcDsp5TCCdzYuwe5GtJvSb55Y59ch44UhipCRBjLNiSSn"
    "7Ec0xSRYkTobJ7FxJoFaK9R1jaqscPT4cZw8eTo8H+NIkuzEvP65+xg3b0kTdJl+XO8eqA8PCZSU3o3tyK3BWaRt0fxnBrKiXusmI5IJllIqfK0Vb8sACgshnd27XVNN04SwXgL1W59YsQAfbBK159x2iibxXrM/lyIeGUfOur799Kzc3bvWnJZvjLyw1c2oKCCkgBBZ"
    "IF2DAHbk7eOnTqGcz7E8mSAvMmitXcaBtNyucAFJyEwiz+w+lFJiMplg37692L93D/bu3YuVlRVMp1NMJhOMRyOMRgXy3O7dPMshcwnpKiwvlg+DCd7Z6ipUWDGvKS7JEpoDpwZcreWx5YUY3R5i/t9+8zeNstOFurbgq/twdfBGR5AC+Ew+H7uE2KXTS2O4UxbHtiy+"
    "HYyiuXx8V0fLnxjwDfQTiTlgb2rqZ3yMzm1NiQxECGr5OaElEAnz1W/YmA3Nkeg5SVhIm6OI2kEp3hH5MCGqrNjp8NLQTIqmipGOMfLo5lCFciJ9IQyX9X7K58f3PhcvBqy7wmVG6gvuHQza9l0EK5NY2hRPZiNB3oBUCq1ZHVMUPswBLhAefGdYMNqY3uFu0VIRLhRQ"
    "imcR0tRzD7JLYePaRCC5msQ7PQEXIm2jcFUIogDixOvOmxO4SyJYwXCL9doDiyBFm9zt7b7t5SgTvI3cQSkEQZJwf9/6bgkhIQUhy3PkeQZBApm7pGwrKJFlGaS0kjnppFWCrLxKRJVVOwSh4bMq5sqFCmsR87SDXmFBZmEKQiOSqvjkk+iW7hiBdauEkILTC5Fkd8C1"
    "o+Mu/6U7sUxmV9w1rucOS2UAFERU0nN3wthluUSmhp1UEBPK945hYHe6Fq3AGLCP1W8UgfAxl6ctn9FGmcfJvAPC3tY3mJMqgELbENM1DHpKuA4GGGQ4XgdHlFje+CrX89dI0KBbJIES80AEn6z+MJyjz4coPbB60EYsFQrTIO6pbLzCJ+FgdeN5nLmgob6RYyr+Tl9P"
    "PBVtSbwUqjXqHNzJmqDIrNFPfBdgmNG4JBKep+0odcjf5DSeofrxv4JQP77g2jwH//dCRkBM+YhpUC1ek3A6d9Qrx15uyYG1EL3tIn59q9PBcm7gr6YGgNzTtHFMWIyDQsHJJDLmtHTnsUnyR8Qh6t3AnelnwoRe8D1jGxiixe4WMSDOibiWBnCKYbJh166knQaiF3yA"
    "BE6nJC25r75KMa+YohL7eg0/d0pkcYmbRHewjIV5mK0fVfqAIv7T8HPqTmYpwd/iarmb6Ee9RZlkI6JzmcRGgAOytTT/nNAJOkw3GXXlXtSTEg5N0OI1RtTfSIu7pwHCka96KSXEMrVVpp80J6/FS9s6JE8aSNhaxE4f3PdI8Soa1Cq33D9feZKJM7SQyhR4gSSHIp7W"
    "+TbuwkNrSJo4MCI/3z8xONeT80YBpwmEyemZxbHTZ9cZsTMZjatHou4Cp4QIiI7Cf8Gop/eeOenqhhfBsHqq/yzChx2+YZoJl4iju+xi5oUylkV7xK8Niq1cYitpWrSOUzJud+wNDIHST+CfITlZt/0cGDTEayL+OwusxiNgnnqtck92Eh/a6KTtDJx/FOOK5DqFSFzd"
    "/0gSncriziFMRqmXyP11/cOdaqhzNqRFDS/UEnKnRiXur5d+hbVwUUbhBAtOw7QIG07Xoe4C6i1iGmgLBq4V3uH63unjW/C6Yt5N9xAdIscO3XgLP0s3FeSBU6dn+9ahFIQJZCTUpgiHSigoMWkVAwlIjNQ0xWfXoWvG2F/UO1Eohp8nBRwk2fwDN+2iTRJXfd33iB6r"
    "LbKwQSeNZcEhTBHOGbex8QNM3nuiVex3FnE1nxCHE6Cc+mZhvWUcsymHTToHP6hFe3eni6Znw7PYoPL8RUjENYwuCO4oLAg4/+sJwQQp97OlNVCX3dt3DGq9nzBw2ERWtTuUg4sOjU6Mw3lP+e6H//XeDGkV057q7XRt5w+2w+AbPHwT1k70bBNC4qIFvMBNtjcBY+qf"
    "17TD8xo6MIk6f5XS6oOeyPPkHhO990x2ulh4sGs7/9d2qxXs8PvhYOkMFXZ6HwOvLbbvid8v97hDInwlQUSHY+rTRehDN7wIhN7xoh7I7KOdDoX2B6cXIg2wgc+zD4eYBtEUuYdVReL/3rNGXwb29VdYvPibfF1lI5232178wHdY8AurgPNUX8yps+fOX89JtUDdjY12"
    "gplsjGjzxOzn+PBnGnzgC6vd9rDsHFg7PK/harFLLUsZ2+eLUyKmgSzLHS6qaDCQumx2SKLnS3GiJ/b5dzin/5/WKmKGeXT5UCdAdiCBovdN4ult2rqiFziKgQ39RC8RGrQ8H6j0k5SfJ9Q2tNXTAoB8cZGxwGevC3wO/CMCdsvnwQgIiw+rBQr1brZeMotdgFdRF35I"
    "wGte+BeTn83dn9BJ/Om2M3T+myTxNsIA3kURCZXSCguRZ1bQg3o+EJAC4AlhYtFroeAwAYqsVSh5y+jPQdvfpIGBDA+BOYueBaehnYOZTZ1vkT5r7p+ahJ6WjBOjPE5i0mK8g4dwKR56TwvWTPc1dz/DzgwzoVQEGg16hxXF/sqRBrP9zKiD4/DXdVDvhCd1K2fqvu+e"
    "rjH2LOTBbRy3xkh0jei4pUaV4qIzodviEg+oAKl/YLVvqO8KuLBq6azwwBnaqc8emC7EgQlD/78/iXgCpVmvNaUkRXfHc6kXLNC/9QLHBzzo/w1eXE7z4M6PJB2dBJF0gMARxsGJ/mrwgqAeItoSBmnArZMHeFWdMr393uwzhRMQnzvcgO5F0puGJTYjUfBqMpGK3hZz"
    "j35AEYE25j8NTj+if9MTwSDjyzhaQ7Sw8u02LKY/FYs/ix3WOHX30AJRcLwmexX2wH4arEZjKk38NZHbQ29NR0aYMVwUFxqJ3Mofzl1j0F7l1v79WLsb7KS73jQxWEzJoh6qmoaHP7QALexukjYqPSnlIsyMerhNrFAfnAoi0vgNgpPYUYtHgwdip0WLyaqdTdvbUckD"
    "SYMEYzB2x3Y74jMhEpPSwKJMvdcplsN3WtT4dqPEMyocDqmnUEo05Y7OC32TPOpsOB74LNBD0BZUNUxpGEdv2rXwWz6B6hkLqhxOq8OIoNy9JGhoWsP9C5oHsMP0r0XPq3cwxZKc+HnRQIEQVXAdbSjFv7/wQKSYUR4lEXW2P6UTVUbXjqojGWNeWHFR8Ace6uoYYrAy"
    "6VZFoRPpNrj9hZUsSGq9dHdcTPwEJxsh+mrB3UitMj91J4jU4syDreiOI/Eou26nsjrpy2kI/6J06jHYEmDw2Sc3brcajG6ucPF1uDRB4Ezne7/Ui3pD181g4KDjzmVGT3QAMnDTLXyNtPNYZRAs7v6YoSokdjVEa8rYuzDjo3TQCoUHT8I2qDb6Lr3hROcw6f7RAD8q"
    "Ptj6634AzkjuzqGKmgeXf2In1Pu2cZJWR8FN6VHFGJguJFPYOLyYBj9HscgZMf7G3H1jwYfc9LEi6p6pFI18uZ0wUmzulVZr3TfCzMOHSG9pcA8zGfw4qHMrIC1hd2xJB6oTvwC6Ni7BifU8PexOeP9gRxOFTQxXsP2DlaPX2jtsdxqjohvE0C/hOYITaGhRBoP7gdaf"
    "+5uc4ooe6NWEHK/B+L36/xUD3XD0vJIV0cHNUr8+GsBkMBBxF4dUUO+QBUecIu8Ewljs/dStGgcOhe6EjYfwrygpKMU3uXNRtg6zNHSIJhPfgYO2s2fOO63vQh9DF82CtSn6Q2DEkcKdw4qSk7lfbdHCzUhIfNgiKIT7v3e+W7hrxubeCHkvrJ0eEqWNW0KOjdNRhiYr"
    "Qx9SVOXQEHIbxTrFZfhQCy06H35ysHRwpqSii14fpSVh+D1KyI8DExoeAMHjUNcY2+QBvAQ0sOY4SWhODluinlqid3PTMK4pkmqTkqSiEEnGff8pM0CYjT9LHqwWOL08iSOf6CiDctFG7kl7utXJkITs/PyqxCGEMXC4x8NeTtvywSFDQLF7ldiglacQnXZywdrm7i8O"
    "P6+Po0XJTyQGi1ZBg9hVqozrlXOLyGm8AMCOP6BOT24GQHjuHXbD7PAEhEck/F1QErfvhQY3Z7d625F5H7djg8PJyHytU+XxQLvFAyVzEv5JAyBsMg7n/iJYkFDSLeXjg5s7z4M6Gq82+4IGhn0dq+QBb6OhNiB8jl76NHTpLIiBii9UJqRjOKIkSZuGIIZOpcw7VNiB"
    "FhlRMQYJwQN/M07dTrqU5HVRSlZd8Bz6cAQwRCtjTtqJlFqwqNSPDm7egePACzsSGpavdMD9+O8mFRzazy0xgndfI3olWDwFiUSbifizPzePPJniy4X6E7MdqA9Dk4v+7w1XX9xxK+wtNUqWXKhoaKefFYdBdEDToZHr0C1LA7ImGozo7lwRSYtBCSq0qDXtAQ9xVmL8"
    "dzoawhZOo0E5ylDKSb/144HF2znUqRNKyzvQH4AB+5t2upY+C+5KKnecTJ+vXUmqvwFQH5HMaZHwPq1qaPjio8VGAoNDmJ53PfWHLTt8+/jvdqwcB9biArbAQjiBu8thoNkYziCkxFtn4LKN/lsMvsvIAcEfPMTpLRAjo4R+/8/xhIAWPOydAi92bDQXT3pitj3zwDij"
    "U+mgu/kHhgpENiqsu1Fpp36bKAHpBxe0ra17VSQzD/OVdmrh+Dz4GA8Y/C14Dju11LzoZw74p/WVAEgnUjRM2krwmfjnLBLX+2XM/aEg7TBg6HH3Otq3Re3QjtPH7kHf+Zx40QGwEJfd+ULkHT63nbm3vmLpwyhD2Qa04LUkNKAgkh9oPZ2nW7cTY96ZCds9DQQtCEtt"
    "Acr2LE4Pm/T86gpre/NdokH8ILZq6cVFdSj8i/dS6uiYKtxbrGFHTtlQD0hI2pM4JizJEBxoUfpAP/Xvs05wQUqdoIGSoQ0I4e7PGzrMBj6PNoh1mBzGHeymi5ul6+U87dDAz6ek6KX+815UMfLi1dwC6jtcDAP/P8nAwwBv7wlXZovwq4ELvcViBmAE9Krg870OkUzn"
    "Oxw4nGeIuWAyHU+wPczChIXVUfD76kSsdfG0WA3AnYFJ7/l1hwshNao1Ut+xeHnCRfWQONr7+HTmPQbYWSs1ADimcgMOByrvAFBi+Ag973tdJDM4r0PFoj/opmn/v7IfWIC7nefDo96WJBhnmvuE/1n0modsNzqiVfAO+MkCdwxiaikBC774fMLsJ7qIF68JToY8O6o9"
    "EqrDkFa24+PfeV2JTGyBN9T/n/8s0pf2bcDp65I1kfh/v7TP9wGKJ/JQ+n3s4jEsuvFZzH3gfKf105Vl7FjyDlQtO/rx9P23upWF6MYRATu3rU+kZ1iEBT2Rg2nRwdG/nwbfT7eIia1VBs3+v87XM0ju7WCWwayv56E0UFnFz55cEvMOrQM/wZ0xLH+K9uTX2Vj1Nnun"
    "8hzabsMYTrqumAaGW+db0+d75eeh6dDA/k1B9B32+6BOMsV6+YlgOU+wihVfR8GbTjiGflbkQ53YbyxoPc5Xri727+lPECluk3orpSOUWvDe6OvYAJSe5DvTKb6erZAMfmjHgySJ6VqkkaQndkAyPzGvi/NiRAsGCju/V9pBZUU7Xh5PvDjcoX3t0sSYMbyY8PVXdl/n"
    "Xh086oba+idwQT9RcvSgIMM/9Y40Comx5mIeGQ0ciP9/PKf/B6SLFprsat0OAAAAAElFTkSuQmCC"
)


def _cargar_logo():
    """Decodifica el logo incrustado y lo entrega como imagen en memoria."""
    return BytesIO(base64.b64decode(_LOGO_SALUDPLUS_B64))

IMAGENES_MEDICAMENTOS = {
    "M001": "https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=300&h=300&fit=crop",
    "M002": "https://images.unsplash.com/photo-1550572017-edd951b55104?w=300&h=300&fit=crop",
    "M003": "https://images.unsplash.com/photo-1607619056574-7b8d3ee536b2?w=300&h=300&fit=crop",
    "M004": "https://images.unsplash.com/photo-1631549916768-4119b2e5f926?w=300&h=300&fit=crop",
    "M005": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=300&h=300&fit=crop",
    "M006": "https://images.unsplash.com/photo-1583324113626-70df0f4deaab?w=300&h=300&fit=crop",
    "M007": "https://images.unsplash.com/photo-1576602976047-174e57a47881?w=300&h=300&fit=crop",
    "M008": "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=300&h=300&fit=crop",
    "M009": "https://images.unsplash.com/photo-1644303898977-26e4e6b76f5a?w=300&h=300&fit=crop",
    "M010": "https://images.unsplash.com/photo-1626716498378-61471b5f2d43?w=300&h=300&fit=crop",
    "M011": "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=300&h=300&fit=crop",
    "M012": "https://images.unsplash.com/photo-1571772996211-2f02c9727629?w=300&h=300&fit=crop",
    "M013": "https://images.unsplash.com/photo-1559757175-5700dde675bc?w=300&h=300&fit=crop",
    "M014": "https://images.unsplash.com/photo-1559650656-5d1d361ad10e?w=300&h=300&fit=crop",
    "M015": "https://images.unsplash.com/photo-1584308972272-9e4e7685e80f?w=300&h=300&fit=crop",
    "M016": "https://images.unsplash.com/photo-1582719471384-894fbb16e074?w=300&h=300&fit=crop",
    "M017": "https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=300&h=300&fit=crop",
    "M018": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=300&h=300&fit=crop",
    "M019": "https://images.unsplash.com/photo-1556227702-d1e4e7b5c232?w=300&h=300&fit=crop",
    "M020": "https://images.unsplash.com/photo-1587854692749-7e22e121af4f?w=300&h=300&fit=crop",
}


# ========================= FUNCIONES AUXILIARES =========================
def verificar_vencimiento(fecha_str):
    try:
        fecha_venc = datetime.strptime(fecha_str, "%d/%m/%Y")
        hoy = hora_ecuador()
        dias_restantes = (fecha_venc - hoy).days
        if dias_restantes < 0:
            return "VENCIDO", dias_restantes
        elif dias_restantes <= 30:
            return "PROXIMO", dias_restantes
        return "OK", dias_restantes
    except Exception:
        return "OK", 999


def procesar_producto_vencido(codigo, fecha_original):
    """
    Deja 1 unidad como registro y ajusta la fecha de vencimiento a
    60 días ANTES de la fecha original.
    """
    conn = conectar_db()
    fecha_original_dt = datetime.strptime(fecha_original, "%d/%m/%Y")
    fecha_ajustada = (fecha_original_dt - timedelta(days=60)).strftime("%d/%m/%Y")
    conn.execute("UPDATE medicamentos SET stock=1, es_vencido=1, fecha_vencimiento=? WHERE codigo=?",
                 (fecha_ajustada, codigo))
    conn.commit()
    conn.close()
    return fecha_ajustada


def reducir_stock_seguro(codigo, cantidad):
    conn = conectar_db()
    med = conn.execute("SELECT * FROM medicamentos WHERE codigo=?", (codigo,)).fetchone()
    if not med:
        conn.close()
        return 0, "No encontrado"

    stock_actual = med['stock']
    if stock_actual <= 1:
        conn.close()
        return 0, "ÚLTIMA UNIDAD: no se puede vender, se mantiene como registro"

    max_vender = stock_actual - 1
    if cantidad > max_vender:
        vendida = max_vender
        mensaje = f"⚠️ Solo se venden {max_vender} unidades (se deja 1 como registro)"
    else:
        vendida = cantidad
        mensaje = "OK"

    nuevo_stock = stock_actual - vendida
    conn.execute("UPDATE medicamentos SET stock=? WHERE codigo=?", (nuevo_stock, codigo))
    conn.commit()
    conn.close()
    return vendida, mensaje


def agregar_stock(codigo, cantidad):
    """
    Suma cantidad al stock existente.
    - Si el producto ESTÁ VENCIDO: actualiza su fecha a 12 meses desde hoy.
    - Si el producto NO está vencido: mantiene su fecha original.
    """
    conn = conectar_db()
    med = conn.execute("SELECT * FROM medicamentos WHERE codigo=?", (codigo,)).fetchone()
    if not med:
        conn.close()
        return False, "Medicamento no encontrado", None
    if cantidad <= 0:
        conn.close()
        return False, "La cantidad debe ser mayor a cero", None

    stock_anterior = med['stock']
    nuevo_stock = stock_anterior + cantidad

    estado, _ = verificar_vencimiento(med['fecha_vencimiento'])
    esta_vencido = (estado == "VENCIDO") or (med['es_vencido'] == 1)

    if esta_vencido:
        nueva_fecha = (hora_ecuador() + timedelta(days=365)).strftime("%d/%m/%Y")
        conn.execute(
            "UPDATE medicamentos SET stock=?, es_vencido=0, fecha_vencimiento=? WHERE codigo=?",
            (nuevo_stock, nueva_fecha, codigo)
        )
        conn.commit()
        conn.close()
        return True, f"✅ Stock actualizado: {stock_anterior} → {nuevo_stock} unidades. Fecha renovada a {nueva_fecha} (producto estaba vencido)", nueva_fecha
    else:
        conn.execute(
            "UPDATE medicamentos SET stock=?, es_vencido=0 WHERE codigo=?",
            (nuevo_stock, codigo)
        )
        conn.commit()
        conn.close()
        return True, f"✅ Stock actualizado: {stock_anterior} → {nuevo_stock} unidades. Fecha se mantiene: {med['fecha_vencimiento']}", None


# ========================= LOGIN =========================
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario_actual = None


def mostrar_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        # ✅ Padding superior reducido (antes 30px) para bajar aún más el espacio en blanco
        st.markdown(
            """
            <div style="
                background:white;
                padding:15px 40px 30px 40px;
                border-radius:20px;
                box-shadow:0px 6px 20px rgba(0,0,0,0.15);
                text-align:center;
            ">
            """,
            unsafe_allow_html=True,
        )

        # ✅ Logo de SaludPlus (icono de farmacia) centrado, arriba del nombre
        col_logo1, col_logo2, col_logo3 = st.columns([1, 1, 1])
        with col_logo2:
            st.image(_cargar_logo(), width=160)

        # Título SaludPlus
        st.markdown(
           "<h1 style='color:#1976d2; margin-bottom:5px; margin-top:10px;'>SaludPlus</h1>",
            unsafe_allow_html=True,
        )
        # Eslogan
        st.markdown(
           "<p style='color:#0d47a1; margin-top:0; margin-bottom:5px; font-size:16px; font-weight:500;'>Gestión Rápida y Segura</p>",
            unsafe_allow_html=True,
        )
        # Dirección
        st.markdown(
           "<p style='color:#64748B; margin-top:0; font-size:14px;'>📍 Machala - El Oro</p>",
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            usuario = st.text_input("Usuario", placeholder="Ingrese su usuario")
            contrasena = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
            st.markdown("<br>", unsafe_allow_html=True)
            ingresar = st.form_submit_button("Iniciar sesión", use_container_width=True)

            if ingresar:
                if usuario == "sistema" and contrasena == "12341":
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = "Administrador"
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")

        st.markdown("</div>", unsafe_allow_html=True)

# ========================= PANEL PRINCIPAL =========================
def mostrar_panel_principal():
    # Título con hora actual (hora de Ecuador)
    hora_actual = hora_ecuador().strftime("%d/%m/%Y %H:%M:%S")

    col_titulo, col_hora = st.columns([3, 1])
    with col_titulo:
        st.title("💊 SaludPlus - Sistema de Gestión")
        st.write(f"👤 Bienvenido: **{st.session_state.usuario_actual}**")
    with col_hora:
        st.markdown(f"<p style='text-align:right; font-size:18px; font-weight:bold;'>🕐 {hora_actual}</p>", unsafe_allow_html=True)

    if st.button("🚪 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    # Botón para actualizar inventario (y refrescar la hora en pantalla)
    if st.button("🔄 Actualizar Inventario"):
        st.rerun()

    # Alertas generales
    conn = conectar_db()
    alertas = []
    for m in conn.execute("SELECT * FROM medicamentos").fetchall():
        est, d = verificar_vencimiento(m['fecha_vencimiento'])
        if est == "VENCIDO" and m['es_vencido'] == 0:
            alertas.append(("error", f"❌ VENCIDO: {m['nombre']}"))
        elif est == "PROXIMO":
            alertas.append(("warning", f"⚠️ Próximo a vencer: {m['nombre']} ({d} días)"))
        if m['stock'] == 1:
            alertas.append(("warning", f"🔴 ÚLTIMA UNIDAD: {m['nombre']} (registro)"))
        elif m['stock'] <= 5:
            alertas.append(("warning", f"⚠️ Stock bajo: {m['nombre']} ({m['stock']})"))
    conn.close()

    if alertas:
        st.subheader("⚠️ Alertas del Sistema")
        for t, txt in alertas:
            if t == "error":
                st.error(txt)
            else:
                st.warning(txt)

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["💊 Inventario", "👥 Usuarios", "🏢 Proveedores", "💸 Ventas"])

    # ==================== PESTAÑA 1: INVENTARIO ====================
    with tab1:
        st.header("💊 Inventario de Medicamentos")

        # ✅ NUEVO (restaurado): Agregar Nuevo Medicamento
        with st.expander("➕ Agregar Nuevo Medicamento", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                cod_add = st.text_input("Código:", placeholder="M021", key="cod_add_inv")
                nom_add = st.text_input("Nombre:", key="nom_add_inv")
                cat_add = st.selectbox("Categoría:",
                                        ["Analgésicos/Antiinflamatorios", "Antibióticos", "Gastrointestinales",
                                         "Aseo e Higiene", "Vitaminas y Antialérgicos", "Otro"],
                                        key="cat_add_inv")
            with col2:
                pre_add = st.number_input("Precio ($):", min_value=0.0, step=0.01, key="pre_add_inv")
                sto_add = st.number_input("Stock:", min_value=1, step=1, key="sto_add_inv")
                fec_add = st.text_input("Fecha de vencimiento (DD/MM/AAAA):", placeholder="10/12/2026", key="fec_add_inv")

            if st.button("Agregar Medicamento", key="btn_add_inv"):
                try:
                    if not cod_add or not nom_add:
                        raise ValueError("Código y nombre son obligatorios")
                    if not fec_add.strip():
                        raise ValueError("La fecha de vencimiento es obligatoria")
                    datetime.strptime(fec_add.strip(), "%d/%m/%Y")  # valida el formato
                    conn = conectar_db()
                    conn.execute("INSERT INTO medicamentos VALUES (?,?,?,?,?,?,0)",
                                 (cod_add.strip(), nom_add.strip(), pre_add, sto_add, fec_add.strip(), cat_add))
                    conn.commit()
                    conn.close()
                    st.success("✅ Medicamento agregado correctamente.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("❌ Ya existe un medicamento con ese código")
                except ValueError as e:
                    st.error(f"❌ Error: la fecha debe tener el formato DD/MM/AAAA. Detalle: {e}")

        # Mostrar inventario por categorías
        st.markdown("### 📋 Inventario por Categorías")
        conn = conectar_db()
        categorias = conn.execute("SELECT DISTINCT categoria FROM medicamentos").fetchall()
        for cat_row in categorias:
            cat = cat_row['categoria']
            with st.expander(f"📂 {cat}", expanded=True):
                meds = conn.execute("SELECT * FROM medicamentos WHERE categoria=?", (cat,)).fetchall()
                for m in meds:
                    col_img, col_info = st.columns([1, 4])
                    with col_img:
                        img = IMAGENES_MEDICAMENTOS.get(m['codigo'], "https://cdn-icons-png.flaticon.com/512/2972/2972183.png")
                        st.image(img, width=90)
                    with col_info:
                        st.markdown(f"**{m['nombre']}**")
                        st.code(f"{m['codigo']} | {m['nombre']} | ${m['precio']:.2f} | Stock: {m['stock']}")

                        # Etiquetas de estado
                        estado, dias = verificar_vencimiento(m['fecha_vencimiento'])

                        etiquetas_html = ""
                        if m['stock'] == 1:
                            etiquetas_html += '<span class="etiqueta etiqueta-ultima">🔴 ÚLTIMA UNIDAD</span>'
                        elif m['stock'] <= 5:
                            etiquetas_html += f'<span class="etiqueta etiqueta-stock-bajo">⚠️ STOCK BAJO: {m["stock"]} unid.</span>'

                        if estado == "VENCIDO":
                            etiquetas_html += f'<span class="etiqueta etiqueta-vencido">❌ VENCIDO hace {abs(dias)} días</span>'
                        elif estado == "PROXIMO":
                            etiquetas_html += f'<span class="etiqueta etiqueta-proximo">⏰ Vence en {dias} días</span>'
                        else:
                            etiquetas_html += f'<span class="etiqueta etiqueta-ok">✅ Vence en {dias} días</span>'

                        if etiquetas_html:
                            st.markdown(etiquetas_html, unsafe_allow_html=True)

                        st.write(f"📅 Vencimiento: {m['fecha_vencimiento']}")

                        if m['stock'] == 1:
                            st.warning("🔴 ÚLTIMA UNIDAD (no se vende, se mantiene como registro)")

                        if st.button("❌ Eliminar definitivamente", key=f"del_{m['codigo']}"):
                            conn.execute("DELETE FROM medicamentos WHERE codigo=?", (m['codigo'],))
                            conn.commit()
                            st.success(f"✅ Medicamento {m['codigo']} eliminado")
                            st.rerun()
                    st.markdown("---")
        conn.close()

    # ==================== PESTAÑA 2: USUARIOS ====================
    with tab2:
        st.header("👥 Gestión de Usuarios")
        col1, col2 = st.columns(2)

        with col1:
            with st.expander("➕ Agregar Usuario", expanded=True):
                rol = st.selectbox("Rol:", ['Administrador', 'Empleado'], key="rol_user")
                nombre_u = st.text_input("Nombre:", key="nom_user")
                correo_u = st.text_input("Correo:", key="cor_user")
                pass_u = st.text_input("Contraseña:", type="password", key="pass_user")
                sueldo_preview = 1500 if rol == "Administrador" else 500
                st.info(f"💰 Sueldo asignado: ${sueldo_preview}")

                if st.button("Agregar Usuario", key="btn_add_user"):
                    try:
                        if not nombre_u or not correo_u or not pass_u:
                            raise ValueError("Todos los campos son obligatorios")
                        if "@" not in correo_u:
                            raise ValueError("Ingresa un correo válido")
                        conn = conectar_db()
                        conn.execute(
                            "INSERT INTO usuarios (nombre, correo, contrasena, rol, sueldo) VALUES (?,?,?,?,?)",
                            (nombre_u.strip(), correo_u.strip(), pass_u, rol, sueldo_preview))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Usuario {nombre_u} agregado como {rol}")
                    except ValueError as e:
                        st.error(f"❌ Error: {e}")

        with col2:
            with st.expander("🗑️ Eliminar Usuario", expanded=True):
                conn = conectar_db()
                usuarios = conn.execute("SELECT * FROM usuarios").fetchall()
                conn.close()
                if usuarios:
                    usuario_eliminar = st.selectbox(
                        "Seleccionar usuario:",
                        [f"{u['id_usuario']} - {u['nombre']} ({u['rol']})" for u in usuarios],
                        key="user_delete")
                    if st.button("Eliminar Usuario", key="btn_del_user"):
                        id_eliminar = int(usuario_eliminar.split(" - ")[0])
                        conn = conectar_db()
                        conn.execute("DELETE FROM usuarios WHERE id_usuario=?", (id_eliminar,))
                        conn.commit()
                        conn.close()
                        st.success("✅ Usuario eliminado correctamente")
                        st.rerun()
                else:
                    st.info("📭 No hay usuarios registrados")

        st.markdown("### 📋 Lista de Usuarios y Comprobantes de Pago")
        conn = conectar_db()
        usuarios = conn.execute("SELECT * FROM usuarios").fetchall()
        conn.close()
        if usuarios:
            for u in usuarios:
                with st.expander(f"👤 {u['nombre']} - {u['rol']}"):
                    st.code(f"Nombre: {u['nombre']}\nID: {u['id_usuario']}\nCorreo: {u['correo']}\nRol: {u['rol']}\nSueldo: ${u['sueldo']}")
                    if st.button("💰 Generar Comprobante", key=f"pago_{u['id_usuario']}"):
                        comprobante = f"""
========================================
COMPROBANTE DE PAGO - SALUDPLUS
========================================
Empleado    : {u['nombre']}
ID          : {u['id_usuario']}
Rol         : {u['rol']}
Sueldo base : ${u['sueldo']:.2f}
----------------------------------------
Total a pagar: ${u['sueldo']:.2f}
========================================
Fecha: {hora_ecuador().strftime('%d/%m/%Y %H:%M')}
========================================"""
                        st.markdown('<div class="factura">', unsafe_allow_html=True)
                        st.text(comprobante)
                        st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("📭 No hay usuarios registrados. Agrega uno arriba.")

    # ==================== PESTAÑA 3: PROVEEDORES ====================
    with tab3:
        st.header("🏢 Gestión de Proveedores")
        col1, col2 = st.columns(2)

        with col1:
            with st.expander("➕ Agregar Proveedor", expanded=True):
                nom_p = st.text_input("Nombre:", key="nom_prov")
                dir_p = st.text_input("Dirección:", key="dir_prov")
                tel_p = st.text_input("Teléfono:", key="tel_prov")
                emp_p = st.text_input("Empresa:", key="emp_prov")

                if st.button("Agregar Proveedor", key="btn_add_prov"):
                    try:
                        if not nom_p or not emp_p:
                            raise ValueError("Nombre y empresa son obligatorios")
                        conn = conectar_db()
                        conn.execute("INSERT INTO proveedores VALUES (NULL,?,?,?,?)",
                                     (nom_p.strip(), dir_p.strip(), tel_p.strip(), emp_p.strip()))
                        conn.commit()
                        conn.close()
                        st.success("✅ Proveedor agregado correctamente")
                    except ValueError as e:
                        st.error(f"❌ Error: {e}")

        with col2:
            with st.expander("🗑️ Eliminar Proveedor", expanded=True):
                conn = conectar_db()
                proveedores = conn.execute("SELECT * FROM proveedores").fetchall()
                conn.close()
                if proveedores:
                    prov_eliminar = st.selectbox(
                        "Seleccionar proveedor:",
                        [f"{p['id_proveedor']} - {p['nombre']} ({p['empresa']})" for p in proveedores],
                        key="prov_delete")
                    if st.button("Eliminar Proveedor", key="btn_del_prov"):
                        id_eliminar = int(prov_eliminar.split(" - ")[0])
                        conn = conectar_db()
                        conn.execute("DELETE FROM proveedores WHERE id_proveedor=?", (id_eliminar,))
                        conn.commit()
                        conn.close()
                        st.success("✅ Proveedor eliminado correctamente")
                        st.rerun()
                else:
                    st.info("📭 No hay proveedores registrados")

        # ===== RECIBIR MERCANCÍA =====
        st.markdown("### 📥 Recibir Mercancía de Proveedor")
        st.info("Esta opción genera la factura de pago Y actualiza automáticamente el stock. **Si el producto está vencido, su fecha se renovará automáticamente.**")
        conn = conectar_db()
        proveedores = conn.execute("SELECT * FROM proveedores").fetchall()
        meds = conn.execute("SELECT codigo, nombre, stock, fecha_vencimiento, es_vencido FROM medicamentos ORDER BY nombre").fetchall()
        conn.close()

        if proveedores and meds:
            col_a, col_b = st.columns(2)
            with col_a:
                prov_compra = st.selectbox(
                    "Proveedor:",
                    [f"{p['id_proveedor']} - {p['nombre']} ({p['empresa']})" for p in proveedores],
                    key="prov_compra")

                opciones_meds = []
                for m in meds:
                    estado, _ = verificar_vencimiento(m['fecha_vencimiento'])
                    vencido = " (VENCIDO)" if (estado == "VENCIDO" or m['es_vencido'] == 1) else ""
                    opciones_meds.append(f"{m['codigo']} - {m['nombre']} | Stock: {m['stock']} | Vence: {m['fecha_vencimiento']}{vencido}")

                med_compra = st.selectbox(
                    "Medicamento recibido:",
                    opciones_meds,
                    key="med_compra")
            with col_b:
                cant_compra = st.number_input("Cantidad recibida:", min_value=1, step=1, key="cant_compra")
                val_compra = st.number_input("Valor unitario de compra ($):", min_value=0.0, step=0.01, key="val_compra")

            if st.button("📥 Registrar Compra y Actualizar Stock", type="primary", key="btn_compra"):
                id_prov = int(prov_compra.split(" - ")[0])
                cod_med = med_compra.split(" - ")[0]
                total_compra = cant_compra * val_compra

                exito, msg_stock, nueva_fecha = agregar_stock(cod_med, cant_compra)
                if exito:
                    conn = conectar_db()
                    conn.execute("""INSERT INTO compras_proveedores
                        (id_proveedor, codigo_medicamento, cantidad, valor_unitario, total, fecha)
                        VALUES (?,?,?,?,?,?)""",
                                 (id_prov, cod_med, cant_compra, val_compra, total_compra,
                                  hora_ecuador().strftime('%d/%m/%Y %H:%M')))
                    conn.commit()

                    p = conn.execute("SELECT * FROM proveedores WHERE id_proveedor=?", (id_prov,)).fetchone()
                    m = conn.execute("SELECT nombre, fecha_vencimiento FROM medicamentos WHERE codigo=?", (cod_med,)).fetchone()
                    conn.close()

                    st.success(f"✅ Compra registrada! {msg_stock}")

                    info_fecha = f"Fecha vencimiento: {m['fecha_vencimiento']}"
                    if nueva_fecha:
                        info_fecha += f" 🔄 (RENOVADA, estaba vencido)"

                    factura = f"""
========================================
FACTURA DE COMPRA - SALUDPLUS
========================================
Proveedor  : {p['nombre']}
Empresa    : {p['empresa']}
Teléfono   : {p['telefono']}
----------------------------------------
Medicamento: {m['nombre']}
Cantidad   : {cant_compra} unidades
Valor unit.: ${val_compra:.2f}
{info_fecha}
----------------------------------------
TOTAL A PAGAR: ${total_compra:.2f}
========================================
Fecha: {hora_ecuador().strftime('%d/%m/%Y %H:%M')}
========================================"""
                    st.markdown('<div class="factura">', unsafe_allow_html=True)
                    st.text(factura)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error(f"❌ Error: {msg_stock}")
        else:
            st.warning("⚠️ Agrega primero proveedores y medicamentos")

        # Historial de compras
        conn = conectar_db()
        compras = conn.execute("""
            SELECT c.*, p.nombre as prov_nombre, m.nombre as med_nombre
            FROM compras_proveedores c
            JOIN proveedores p ON c.id_proveedor = p.id_proveedor
            JOIN medicamentos m ON c.codigo_medicamento = m.codigo
            ORDER BY c.id_compra DESC
        """).fetchall()
        conn.close()

        if compras:
            with st.expander("📜 Historial de Compras a Proveedores"):
                for c in compras:
                    st.code(f"ID: {c['id_compra']} | {c['prov_nombre']} | {c['med_nombre']} | Cant: {c['cantidad']} | Total: ${c['total']:.2f} | {c['fecha']}")

    # ==================== PESTAÑA 4: VENTAS ====================
    with tab4:
        st.header("💸 Realizar Venta")
        venta_codigo = st.text_input("Código del Medicamento:", key="cod_venta")
        venta_cantidad = st.number_input("Cantidad a vender:", min_value=1, step=1, key="cant_venta")

        if st.button("🛒 Realizar Venta", type="primary", key="btn_vender"):
            try:
                if not venta_codigo.strip():
                    raise ValueError("Ingresa el código del medicamento")
                conn = conectar_db()
                med = conn.execute("SELECT * FROM medicamentos WHERE codigo=?", (venta_codigo.strip(),)).fetchone()
                if not med:
                    raise ValueError("Medicamento no encontrado")

                est, _ = verificar_vencimiento(med['fecha_vencimiento'])
                if est == "VENCIDO":
                    st.error("❌ No se puede vender un medicamento vencido!")
                else:
                    vendida, mensaje = reducir_stock_seguro(med['codigo'], venta_cantidad)
                    if vendida == 0:
                        st.error(f"🔴 {mensaje}")
                    else:
                        total = vendida * med['precio']
                        conn.execute(
                            "INSERT INTO ventas (codigo_medicamento, cantidad, total, fecha) VALUES (?,?,?,?)",
                            (med['codigo'], vendida, total, hora_ecuador().strftime('%d/%m/%Y %H:%M')))
                        conn.commit()

                        if "⚠️" in mensaje:
                            st.warning(mensaje)
                        st.success(f"✅ Venta exitosa: {vendida} unidades")

                        factura = f"""
========================================
🧾 FACTURA DE VENTA - SALUDPLUS
========================================
Medicamento  : {med['nombre']}
Categoría    : {med['categoria']}
Cantidad     : {vendida}
Precio unit. : ${med['precio']:.2f}
----------------------------------------
Total a pagar: ${total:.2f}
========================================
Fecha: {hora_ecuador().strftime('%d/%m/%Y %H:%M')}
========================================"""
                        st.markdown('<div class="factura">', unsafe_allow_html=True)
                        st.text(factura)
                        st.markdown('</div>', unsafe_allow_html=True)
                conn.close()
            except ValueError as e:
                st.error(f"❌ Error: {e}")

        # Historial de ventas
        conn = conectar_db()
        ventas = conn.execute("SELECT * FROM ventas ORDER BY id_venta DESC").fetchall()
        conn.close()
        if ventas:
            with st.expander("📜 Historial de Ventas"):
                total_ventas = sum(v['total'] for v in ventas)
                st.markdown(f"Total de ventas: {len(ventas)}")
                st.markdown(f"**Ingresos totales: ${total_ventas:.2f}**")
                st.markdown("---")
                for v in ventas:
                    st.text(f"ID: {v['id_venta']} | Código: {v['codigo_medicamento']} | Cantidad: {v['cantidad']} | Total: ${v['total']:.2f} | Fecha: {v['fecha']}")


# ========================= EJECUCIÓN PRINCIPAL =========================
if not st.session_state.autenticado:
    mostrar_login()
else:
    mostrar_panel_principal()
