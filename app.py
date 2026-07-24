import streamlit as st
import sqlite3
from datetime import datetime

# ========================= CONFIGURACIÓN =========================
st.set_page_config(page_title="Sistema de Farmacia", page_icon="🧪", layout="wide")

# ========================= BASE DE DATOS =========================
def conectar_db():
    conn = sqlite3.connect('farmacia.db')
    conn.row_factory = sqlite3.Row
    return conn

def crear_tablas():
    conn = conectar_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS medicamentos (
        codigo TEXT PRIMARY KEY, nombre TEXT NOT NULL, precio REAL NOT NULL,
        stock INTEGER NOT NULL, fecha_vencimiento TEXT NOT NULL,
        categoria TEXT NOT NULL, es_vencido INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL,
        correo TEXT NOT NULL, contrasena TEXT NOT NULL, rol TEXT NOT NULL, sueldo REAL NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS proveedores (
        id_proveedor INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL,
        direccion TEXT, telefono TEXT, empresa TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS ventas (
        id_venta INTEGER PRIMARY KEY AUTOINCREMENT, codigo_medicamento TEXT NOT NULL,
        cantidad INTEGER NOT NULL, total REAL NOT NULL, fecha TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

def inicializar_datos():
    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM medicamentos")
    if c.fetchone()[0] == 0:
        medicamentos = [
            ("M001", "Paracetamol 500mg", 3.50, 150, "10/12/2026", "Analgésicos"),
            ("M002", "Ibuprofeno 400mg", 5.00, 130, "15/08/2026", "Analgésicos"),
            ("M003", "Aspirina 100mg", 2.50, 4, "01/11/2025", "Analgésicos"),
            ("M004", "Naproxeno 250mg", 6.80, 80, "20/01/2027", "Analgésicos"),
            ("M005", "Diclofenaco 50mg", 7.20, 3, "05/09/2025", "Analgésicos"),
            ("M006", "Amoxicilina 500mg", 15.30, 130, "20/08/2026", "Antibióticos"),
            ("M007", "Azitromicina 250mg", 22.50, 60, "15/03/2027", "Antibióticos"),
            ("M008", "Ciprofloxacino 500mg", 18.90, 45, "10/10/2026", "Antibióticos"),
            ("M009", "Metronidazol 250mg", 12.40, 2, "28/02/2026", "Antibióticos"),
            ("M010", "Omeprazol 20mg", 12.00, 50, "10/12/2024", "Gastrointestinales"),
            ("M011", "Ranitidina 150mg", 8.50, 70, "05/06/2026", "Gastrointestinales"),
            ("M012", "Loperamida 2mg", 6.30, 90, "18/09/2026", "Gastrointestinales"),
            ("M013", "Simeticona 125mg", 9.80, 55, "22/11/2026", "Gastrointestinales"),
            ("M014", "Pasta Dental", 4.20, 200, "01/01/2028", "Aseo e Higiene"),
            ("M015", "Jabón Antibacterial", 3.80, 180, "15/06/2027", "Aseo e Higiene"),
            ("M016", "Papel Higiénico", 5.50, 160, "01/01/2029", "Aseo e Higiene"),
            ("M017", "Alcohol en Gel", 7.90, 120, "30/04/2027", "Aseo e Higiene"),
            ("M018", "Enjuague Bucal", 11.20, 75, "15/08/2027", "Aseo e Higiene"),
            ("M019", "Vitamina C 1000mg", 14.50, 100, "20/12/2026", "Vitaminas"),
            ("M020", "Loratadina 10mg", 10.80, 85, "10/05/2027", "Vitaminas"),
        ]
        c.executemany("INSERT INTO medicamentos VALUES (?,?,?,?,?,?,0)", medicamentos)
    c.execute("SELECT COUNT(*) FROM proveedores")
    if c.fetchone()[0] == 0:
        proveedores = [("Juan Ruiz", "Av. Principal 123", "0991234567", "Farmacéutica del Sur"),
                       ("María Torres", "Calle Central 456", "0987654321", "Laboratorios Andinos")]
        c.executemany("INSERT INTO proveedores VALUES (NULL,?,?,?,?)", proveedores)
    conn.commit()
    conn.close()

crear_tablas()
inicializar_datos()

# ========================= FUNCIONES AUXILIARES =========================
def verificar_vencimiento(fecha_str):
    try:
        fecha_venc = datetime.strptime(fecha_str, "%d/%m/%Y")
        hoy = datetime.now()
        dias = (fecha_venc - hoy).days
        if dias < 0: return "VENCIDO", dias
        elif dias <= 30: return "PROXIMO", dias
        return "OK", dias
    except:
        return "OK", 999

# ========================= LOGIN =========================
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario_actual = None

def mostrar_login():
    st.markdown("<h1 style='text-align:center; margin-top:100px;'>🧪 SISTEMA DE FARMACIA</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Iniciar Sesión</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            usuario = st.text_input("👤 Usuario:")
            contrasena = st.text_input("🔒 Contraseña:", type="password")
            if st.form_submit_button("✅ Iniciar Sesión"):
                if usuario == "sistema" and contrasena == "12341":
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = "sistema"
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")

# ========================= PANEL PRINCIPAL =========================
def mostrar_panel():
    st.title("🧪 Gestión de Farmacia")
    st.write(f"👤 Bienvenido: **{st.session_state.usuario_actual}**")
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    # Alertas
    conn = conectar_db()
    alertas = []
    for m in conn.execute("SELECT * FROM medicamentos").fetchall():
        est, d = verificar_vencimiento(m['fecha_vencimiento'])
        if est == "VENCIDO" and m['es_vencido'] == 0:
            alertas.append(("error", f"❌ VENCIDO: {m['nombre']}"))
        elif est == "PROXIMO":
            alertas.append(("warning", f"⚠️ Próximo a vencer: {m['nombre']} ({d} días)"))
        if m['stock'] == 1:
            alertas.append(("warning", f"🔴 ÚLTIMA UNIDAD: {m['nombre']}"))
    conn.close()

    if alertas:
        st.subheader("⚠️ Alertas")
        for t, txt in alertas:
            if t == "error":
                st.error(txt)
            else:
                st.warning(txt)
    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(["💊 Inventario", "👥 Usuarios", "🏢 Proveedores", "💸 Ventas"])

    # --- INVENTARIO ---
    with tab1:
        st.subheader("Medicamentos")
        with st.expander("➕ Agregar"):
            c1, c2 = st.columns(2)
            with c1:
                cod = st.text_input("Código")
                nom = st.text_input("Nombre")
                cat = st.selectbox("Categoría", ["Analgésicos", "Antibióticos", "Gastrointestinales", "Aseo e Higiene", "Vitaminas"])
            with c2:
                pre = st.number_input("Precio", 0.0, step=0.01)
                sto = st.number_input("Stock", 1, step=1)
                fec = st.text_input("Vencimiento (DD/MM/AAAA)")
            if st.button("Guardar") and cod and nom:
                try:
                    conn = conectar_db()
                    conn.execute("INSERT INTO medicamentos VALUES (?,?,?,?,?,?,0)", (cod.strip(), nom.strip(), pre, sto, fec.strip(), cat))
                    conn.commit()
                    st.success("✅ Agregado")
                except sqlite3.IntegrityError:
                    st.error("❌ Código repetido")

        st.subheader("Por Categoría")
        conn = conectar_db()
        categorias = conn.execute("SELECT DISTINCT categoria FROM medicamentos").fetchall()
        for cat_row in categorias:
            cat = cat_row['categoria']
            with st.expander(f"📂 {cat}"):
                meds = conn.execute("SELECT * FROM medicamentos WHERE categoria=?", (cat,)).fetchall()
                for m in meds:
                    st.code(f"{m['codigo']} | {m['nombre']} | ${m['precio']:.2f} | Stock: {m['stock']} | Vence: {m['fecha_vencimiento']}")
                    est, _ = verificar_vencimiento(m['fecha_vencimiento'])
                    if est == "VENCIDO" and m['es_vencido'] == 0 and m['stock'] > 1:
                        if st.button("🗑️ Dejar 1 unidad", key=f"v{m['codigo']}"):
                            conn.execute("UPDATE medicamentos SET stock=1, es_vencido=1 WHERE codigo=?", (m['codigo'],))
                            conn.commit()
                            st.rerun()
                    if m['stock'] == 1:
                        st.warning("🔴 ÚLTIMA UNIDAD (no se vende)")
                    if st.button("❌ Eliminar todo", key=f"e{m['codigo']}"):
                        conn.execute("DELETE FROM medicamentos WHERE codigo=?", (m['codigo'],))
                        conn.commit()
                        st.rerun()
        conn.close()

    # --- USUARIOS ---
    with tab2:
        st.subheader("Gestión de Usuarios")
        ca, cb = st.columns(2)
        with ca:
            with st.expander("➕ Agregar"):
                rol = st.selectbox("Rol", ["Administrador", "Empleado"])
                nom = st.text_input("Nombre")
                cor = st.text_input("Correo")
                pas = st.text_input("Contraseña", type="password")
                sue = 1500 if rol == "Administrador" else 500
                st.info(f"💰 Sueldo: ${sue}")
                if st.button("Guardar") and nom and "@" in cor and pas:
                    conn = conectar_db()
                    conn.execute("INSERT INTO usuarios VALUES (NULL,?,?,?,?,?)", (nom.strip(), cor.strip(), pas, rol, sue))
                    conn.commit()
                    st.success("✅ Usuario agregado")
        with cb:
            with st.expander("🗑️ Eliminar"):
                conn = conectar_db()
                usu = conn.execute("SELECT * FROM usuarios").fetchall()
                conn.close()
                if usu:
                    sel = st.selectbox("Seleccionar", [f"{u['id_usuario']} - {u['nombre']} ({u['rol']})" for u in usu])
                    if st.button("Eliminar"):
                        id_eliminar = int(sel.split(" - ")[0])
                        conn = conectar_db()
                        conn.execute("DELETE FROM usuarios WHERE id_usuario=?", (id_eliminar,))
                        conn.commit()
                        st.rerun()
        st.subheader("Lista y Comprobantes")
        conn = conectar_db()
        usuarios = conn.execute("SELECT * FROM usuarios").fetchall()
        conn.close()
        for u in usuarios:
            with st.expander(f"👤 {u['nombre']}"):
                st.code(f"Nombre: {u['nombre']}\nRol: {u['rol']}\nSueldo: ${u['sueldo']}")
                if st.button("🧾 Comprobante", key=f"c{u['id_usuario']}"):
                    st.text(f"COMPROBANTE DE PAGO\nEmpleado: {u['nombre']}\nRol: {u['rol']}\nTotal: ${u['sueldo']:.2f}\nFecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # --- PROVEEDORES ---
    with tab3:
        st.subheader("Gestión de Proveedores")
        ca, cb = st.columns(2)
        with ca:
            with st.expander("➕ Agregar"):
                nom = st.text_input("Nombre")
                dirr = st.text_input("Dirección")
                tel = st.text_input("Teléfono")
                emp = st.text_input("Empresa")
                if st.button("Guardar Prov.") and nom and emp:
                    conn = conectar_db()
                    conn.execute("INSERT INTO proveedores VALUES (NULL,?,?,?,?)", (nom.strip(), dirr.strip(), tel.strip(), emp.strip()))
                    conn.commit()
                    st.success("✅ Proveedor agregado")
        with cb:
            with st.expander("🗑️ Eliminar"):
                conn = conectar_db()
                prov = conn.execute("SELECT * FROM proveedores").fetchall()
                conn.close()
                if prov:
                    sel = st.selectbox("Seleccionar Prov.", [f"{p['id_proveedor']} - {p['nombre']}" for p in prov])
                    if st.button("Eliminar Prov."):
                        id_eliminar = int(sel.split(" - ")[0])
                        conn = conectar_db()
                        conn.execute("DELETE FROM proveedores WHERE id_proveedor=?", (id_eliminar,))
                        conn.commit()
                        st.rerun()
        st.subheader("🧾 Factura de Pago")
        conn = conectar_db()
        prov = conn.execute("SELECT * FROM proveedores").fetchall()
        conn.close()
        if prov:
            sel_p = st.selectbox("Proveedor", [f"{p['id_proveedor']} - {p['nombre']} ({p['empresa']})" for p in prov])
            med_c = st.text_input("Código Medicamento")
            cant = st.number_input("Cantidad", 1, step=1)
            val_u = st.number_input("Valor Unitario", 0.0, step=0.01)
            if st.button("Generar Factura"):
                idp = int(sel_p.split(" - ")[0])
                conn = conectar_db()
                p = conn.execute("SELECT * FROM proveedores WHERE id_proveedor=?", (idp,)).fetchone()
                m = conn.execute("SELECT nombre FROM medicamentos WHERE codigo=?", (med_c.strip(),)).fetchone()
                conn.close()
                nom_m = m['nombre'] if m else med_c.strip()
                st.text(f"FACTURA PROVEEDOR\nProveedor: {p['nombre']} | {p['empresa']}\nMedicamento: {nom_m}\nCantidad: {cant} | Valor: ${val_u:.2f}\nTOTAL: ${cant*val_u:.2f}\nFecha: {datetime.now().strftime('%d/%m/%Y')}")

    # --- VENTAS ---
    with tab4:
        st.subheader("Realizar Venta")
        cod_v = st.text_input("Código Medicamento")
        cant_v = st.number_input("Cantidad a vender", 1, step=1)
        if st.button("🛒 Vender", type="primary"):
            conn = conectar_db()
            med = conn.execute("SELECT * FROM medicamentos WHERE codigo=?", (cod_v.strip(),)).fetchone()
            if not med:
                st.error("❌ No encontrado")
            elif med['stock'] == 1:
                st.error("🔴 No se puede vender la última unidad de registro")
            elif verificar_vencimiento(med['fecha_vencimiento'])[0] == "VENCIDO":
                st.error("❌ Producto vencido")
            else:
                # REGLA CLAVE: NUNCA MENOS DE 1
                max_vender = med['stock'] - 1
                if cant_v > max_vender:
                    st.warning(f"⚠️ Solo se venden {max_vender} unidades (se deja 1 como registro)")
                    vendida = max_vender
                else:
                    vendida = cant_v
                nuevo_stock = med['stock'] - vendida
                total = vendida * med['precio']
                conn.execute("UPDATE medicamentos SET stock=? WHERE codigo=?", (nuevo_stock, cod_v.strip()))
                conn.execute("INSERT INTO ventas VALUES (NULL,?,?,?,?)", (cod_v.strip(), vendida, total, datetime.now().strftime('%d/%m/%Y %H:%M')))
                conn.commit()
                st.success(f"✅ Venta exitosa: {vendida} unidades | Quedan {nuevo_stock}")
                st.text(f"FACTURA DE VENTA\nMedicamento: {med['nombre']}\nCantidad: {vendida}\nTotal: ${total:.2f}\nFecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            conn.close()

# ========================= EJECUCIÓN =========================
if not st.session_state.autenticado:
    mostrar_login()
else:
    mostrar_panel()
