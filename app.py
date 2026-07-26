import streamlit as st
import sqlite3
from datetime import datetime, timedelta, timezone

st.set_page_config(page_title="SaludPlus - Sistema de Farmacia", page_icon="💊", layout="wide")

def hora_ecuador():
    return (datetime.now(timezone.utc) - timedelta(hours=5)).replace(tzinfo=None)

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

def agregar_estilos():
    st.markdown("""
    <style>
    header[data-testid="stHeader"] {
        height: 0rem;
        visibility: hidden;
    }
    .stApp {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 50%, #ffcc80 100%);
        background-attachment: fixed;
    }
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 2rem;
    }
    .stApp, p, span, label, .stMarkdown, .stCode, li, div {
        color: #0d47a1 !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #0d47a1 !important;
        font-weight: 700 !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.9);
    }
    .stExpander, .stAlert, [data-testid="stForm"],
    .stTextInput > div, .stNumberInput > div, .stSelectbox > div {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 12px;
    }
    .stTextInput input, .stNumberInput input, .stSelectbox input {
        color: #0d47a1 !important;
        border-radius: 10px;
    }
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
    .factura {
        background: white;
        padding: 20px;
        border-radius: 10px;
        border: 2px dashed #1976d2;
        font-family: monospace;
    }
    .stAlert p, .stAlert div {
        color: #0d47a1 !important;
    }
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

LOGO_SALUDPLUS = "logo_farmacia.png"

IMAGENES_MEDICAMENTOS = {
    "M001": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSh1OFLcF_t6DezMx2BrqHwS7K2v4isNqrB-K_fYeyfPHRT0iNNfnS4QVE&s=10&w=300&h=300&fit=crop",
    "M002": "https://farmaenlace.vtexassets.com/arquivos/ids/180844/08642-1.jpg?v=638973636616370000&w=300&h=300&fit=crop",
    "M003": "https://farmaenlace.vtexassets.com/arquivos/ids/172034/06218-1.jpg?v=638386895440700000&w=300&h=300&fit=crop",
    "M004": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRLJNpiIrllCsLYbYrFh906IXSSlXuUKHJaKPZ5iYRZPw&s=10&w=300&h=300&fit=crop",
    "M005": "https://colsubsidio.vtexassets.com/arquivos/ids/203306/7703763280612.jpg.jpg?v=638760227716130000&w=300&h=300&fit=crop",
    "M006": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSTr4V9v3s-oSTvk52xDXzgWxfJ-fhdIBZQfPziTu9lT_QcdFSZZaxwudEk&s=10&w=300&h=300&fit=crop",
    "M007": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTiTtwGAqgMngllNN744iZwm26T7brULFN_TsFghh_G-g&s=10&w=300&h=300&fit=crop",
    "M008": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQrdG-317Q8aAc0_10bO59sjq3WODg0Qs4GzalPWBDtdUTnczubuL5TwUA&s=10&w=300&h=300&fit=crop",
    "M009": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRXc7zIV5MUROJwokhByL9EFoR42VggAC-9fMvqAbbomA&s=10&w=300&h=300&fit=crop",
    "M010": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSFaz3Z5b0d-ZewFZQXSlxbpO9E73g-DR0LZtpeHOxwkg&s=10%w=300&h=300&fit=crop",
    "M011": "https://farmaciarex.uy/cdn/shop/products/D_948345-MLU49524040312_032022-B.jpg?v=1648664848&w=300&h=300&fit=crop",
    "M012": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSE9NDhjHAP1Os_qqZKYeumZ7khvn7MfavuzZdS3QnifSfG8hF02WjX-CPQ&s=10&w=300&h=300&fit=crop",
    "M013": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTT92-K0oVB7YqbQz_BkS2oHym7bq0IeRea3ony_pMkrQ&s=10&w=300&h=300&fit=crop",
    "M014": "https://unimarc.vtexassets.com/arquivos/ids/234258/000000000000647890-UN-01.jpg?v=638785956451000000&w=300&h=300&fit=crop",
    "M015": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQov5Ok8JRQfvKWGipzI-SVoLd4u9R-ANFpSjNJ_y8gZpjrj7_b9kTONov5&s=10&w=300&h=300&fit=crop",
    "M016": "https://pharmacys.vtexassets.com/arquivos/ids/169550-800-800?v=639011483227830000&width=800&height=800&aspect=true&w=300&h=300&fit=crop",
    "M017": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRHt8iwNuaI1boZ6xXHuF6fhWi6xA_B0yPOsyckyXC9koWAQlaQ_7uDdu-Z&s=10&w=300&h=300&fit=crop",
    "M018": "https://pharmacys.vtexassets.com/arquivos/ids/184268/72472.jpg?v=639189719630200000&w=300&h=300&fit=crop",
    "M019": "https://http2.mlstatic.com/D_NQ_NP_669036-MLA99514782260_112025-O.webp&w=300&h=300&fit=crop",
    "M020": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQfwb9EntwpbE-nPSkDnEArcO1cXBtrSvZkvm0_a7QPM9cyzdLuW90mhLVH&s=10&w=300&h=300&fit=crop",
}

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

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario_actual = None

def mostrar_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
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

        col_logo1, col_logo2, col_logo3 = st.columns([1, 1, 1])
        with col_logo2:
            st.image(LOGO_SALUDPLUS, width=160)

        st.markdown(
           "<h1 style='color:#1976d2; margin-bottom:5px; margin-top:10px;'>SaludPlus</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
           "<p style='color:#0d47a1; margin-top:0; margin-bottom:5px; font-size:16px; font-weight:500;'>Gestión Rápida y Segura</p>",
            unsafe_allow_html=True,
        )
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

def mostrar_panel_principal():
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

    if st.button("🔄 Actualizar Inventario"):
        st.rerun()

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

    with tab1:
        st.header("💊 Inventario de Medicamentos")

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
                    datetime.strptime(fec_add.strip(), "%d/%m/%Y")
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
                        st.image(img, width=140)
                    with col_info:
                        st.markdown(f"**{m['nombre']}**")
                        st.code(f"{m['codigo']} | {m['nombre']} | ${m['precio']:.2f} | Stock: {m['stock']}")

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

if not st.session_state.autenticado:
    mostrar_login()
else:
    mostrar_panel_principal()
