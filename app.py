import streamlit as st
import sqlite3
from datetime import datetime, timedelta

# ========================= CONFIGURACIÓN DE PÁGINA =========================
st.set_page_config(page_title="Sistema de Farmacia", page_icon="🧪", layout="wide")

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


# ========================= ESTILOS MEJORADOS =========================
def agregar_estilos():
    st.markdown("""
    <style>
    /* FONDO NARANJA SUAVE */
    .stApp {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 50%, #ffcc80 100%);
        background-attachment: fixed;
    }

    .block-container {
        padding-top: 2rem;
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
    </style>
    """, unsafe_allow_html=True)


agregar_estilos()

# ========================= IMÁGENES =========================
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
        hoy = datetime.now()
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
    """Suma cantidad al stock existente"""
    conn = conectar_db()
    med = conn.execute("SELECT * FROM medicamentos WHERE codigo=?", (codigo,)).fetchone()
    if not med:
        conn.close()
        return False, "Medicamento no encontrado"
    if cantidad <= 0:
        conn.close()
        return False, "La cantidad debe ser mayor a cero"

    nuevo_stock = med['stock'] + cantidad
    conn.execute("UPDATE medicamentos SET stock=?, es_vencido=0 WHERE codigo=?", (nuevo_stock, codigo))
    conn.commit()
    conn.close()
    return True, f"✅ Stock actualizado: {med['stock']} → {nuevo_stock} unidades"


# ========================= LOGIN =========================
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
                padding:40px;
                border-radius:20px;
                box-shadow:0px 6px 20px rgba(0,0,0,0.15);
                text-align:center;
            ">
            """,
            unsafe_allow_html=True,
        )

        col_logo1, col_logo2, col_logo3 = st.columns([1, 1, 1])
        with col_logo2:
            st.image("https://cdn-icons-png.flaticon.com/512/4320/4320337.png", width=120)

        st.markdown(
           "<h2 style='color:#1976d2; margin-bottom:0;'>Sistema de Gestión Farmacéutica</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
           "<p style='color:#0d47a1; margin-top:5px;'>Control de inventario, ventas y proveedores</p>",
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)

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
    st.title("🧪 Sistema de Gestión de Farmacia")
    st.write(f"👤 Bienvenido: **{st.session_state.usuario_actual}**")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.autenticado = False
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

        # Actualizar stock manualmente
        with st.expander("✏️ Actualizar Stock Manualmente", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                conn = conectar_db()
                meds = conn.execute("SELECT codigo, nombre, stock FROM medicamentos ORDER BY nombre").fetchall()
                conn.close()
                med_seleccionado = st.selectbox(
                    "Seleccionar medicamento:",
                    [f"{m['codigo']} - {m['nombre']} (Stock actual: {m['stock']})" for m in meds],
                    key="stock_manual")
            with col2:
                cantidad_agregar = st.number_input("Cantidad a agregar:", min_value=1, step=1, key="cant_stock")

            if st.button("📈 Actualizar Stock", key="btn_stock_manual"):
                codigo = med_seleccionado.split(" - ")[0]
                exito, mensaje = agregar_stock(codigo, cantidad_agregar)
                if exito:
                    st.success(mensaje)
                    st.rerun()
                else:
                    st.error(mensaje)

        # Agregar medicamento
        with st.expander("➕ Agregar Nuevo Medicamento", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                cod_add = st.text_input("Código:", placeholder="M021")
                nom_add = st.text_input("Nombre:")
                cat_add = st.selectbox("Categoría:",
                                        ["Analgésicos/Antiinflamatorios", "Antibióticos", "Gastrointestinales",
                                         "Aseo e Higiene", "Vitaminas y Antialérgicos", "Otro"])
            with col2:
                pre_add = st.number_input("Precio ($):", min_value=0.0, step=0.01)
                sto_add = st.number_input("Stock:", min_value=1, step=1)
                fec_add = st.text_input("Fecha de vencimiento (DD/MM/AAAA):", placeholder="10/12/2026")

            if st.button("Agregar Medicamento", key="btn_add_inv"):
                try:
                    if not cod_add or not nom_add:
                        raise ValueError("Código y nombre son obligatorios")
                    conn = conectar_db()
                    conn.execute("INSERT INTO medicamentos VALUES (?,?,?,?,?,?,0)",
                                 (cod_add.strip(), nom_add.strip(), pre_add, sto_add, fec_add.strip(), cat_add))
                    conn.commit()
                    conn.close()
                    st.success("✅ Medicamento agregado correctamente.")
                except sqlite3.IntegrityError:
                    st.error("❌ Ya existe un medicamento con ese código")
                except ValueError as e:
                    st.error(f"❌ Error: {e}")

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
                        st.write(f"📅 Vencimiento: {m['fecha_vencimiento']}")

                        est, _ = verificar_vencimiento(m['fecha_vencimiento'])
                        if est == "VENCIDO" and m['es_vencido'] == 0:
                            st.error(f"❌ VENCIDO el {m['fecha_vencimiento']}")
                            if st.button("🗑️ Procesar vencido (dejar 1 unidad)", key=f"venc_{m['codigo']}"):
                                nueva_fecha = procesar_producto_vencido(m['codigo'], m['fecha_vencimiento'])
                                st.success(f"✅ Procesado: stock reducido a 1 unidad. Fecha ajustada a {nueva_fecha}")
                                st.rerun()
                        elif m['es_vencido'] == 1:
                            st.warning("⚠️ Producto vencido procesado (1 unidad de registro)")

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
COMPROBANTE DE PAGO
========================================
Empleado    : {u['nombre']}
ID          : {u['id_usuario']}
Rol         : {u['rol']}
Sueldo base : ${u['sueldo']:.2f}
----------------------------------------
Total a pagar: ${u['sueldo']:.2f}
========================================
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
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
        st.info("Esta opción genera la factura de pago Y actualiza automáticamente el stock del inventario.")
        conn = conectar_db()
        proveedores = conn.execute("SELECT * FROM proveedores").fetchall()
        meds = conn.execute("SELECT codigo, nombre, stock FROM medicamentos ORDER BY nombre").fetchall()
        conn.close()

        if proveedores and meds:
            col_a, col_b = st.columns(2)
            with col_a:
                prov_compra = st.selectbox(
                    "Proveedor:",
                    [f"{p['id_proveedor']} - {p['nombre']} ({p['empresa']})" for p in proveedores],
                    key="prov_compra")
                med_compra = st.selectbox(
                    "Medicamento recibido:",
                    [f"{m['codigo']} - {m['nombre']} (Stock actual: {m['stock']})" for m in meds],
                    key="med_compra")
            with col_b:
                cant_compra = st.number_input("Cantidad recibida:", min_value=1, step=1, key="cant_compra")
                val_compra = st.number_input("Valor unitario de compra ($):", min_value=0.0, step=0.01, key="val_compra")

            if st.button("📥 Registrar Compra y Actualizar Stock", type="primary", key="btn_compra"):
                id_prov = int(prov_compra.split(" - ")[0])
                cod_med = med_compra.split(" - ")[0]
                total_compra = cant_compra * val_compra

                exito, msg_stock = agregar_stock(cod_med, cant_compra)
                if exito:
                    conn = conectar_db()
                    conn.execute("""INSERT INTO compras_proveedores
                        (id_proveedor, codigo_medicamento, cantidad, valor_unitario, total, fecha)
                        VALUES (?,?,?,?,?,?)""",
                                 (id_prov, cod_med, cant_compra, val_compra, total_compra,
                                  datetime.now().strftime('%d/%m/%Y %H:%M')))
                    conn.commit()

                    p = conn.execute("SELECT * FROM proveedores WHERE id_proveedor=?", (id_prov,)).fetchone()
                    m = conn.execute("SELECT nombre FROM medicamentos WHERE codigo=?", (cod_med,)).fetchone()
                    conn.close()

                    st.success(f"✅ Compra registrada! {msg_stock}")
                    factura = f"""
========================================
FACTURA DE COMPRA A PROVEEDOR
========================================
Proveedor  : {p['nombre']}
Empresa    : {p['empresa']}
Teléfono   : {p['telefono']}
Medicamento: {m['nombre']}
Cantidad   : {cant_compra} unidades
Valor unit.: ${val_compra:.2f}
----------------------------------------
TOTAL A PAGAR: ${total_compra:.2f}
========================================
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
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
                            (med['codigo'], vendida, total, datetime.now().strftime('%d/%m/%Y %H:%M')))
                        conn.commit()

                        if "⚠️" in mensaje:
                            st.warning(mensaje)
                        st.success(f"✅ Venta exitosa: {vendida} unidades")

                        factura = f"""
========================================
🧾 FACTURA DE VENTA
========================================
Medicamento  : {med['nombre']}
Categoría    : {med['categoria']}
Cantidad     : {vendida}
Precio unit. : ${med['precio']:.2f}
----------------------------------------
Total a pagar: ${total:.2f}
========================================
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
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
