import streamlit as st
from datetime import datetime

# ========================= CONFIGURACIÓN DE PÁGINA =========================
st.set_page_config(page_title="Sistema de Farmacia", page_icon="🧪", layout="wide")

# ========================= ESTILOS PERSONALIZADOS =========================
def agregar_estilos():
    st.markdown("""
    <style>
    /* Fondo naranja suave */
    .stApp {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 50%, #ffcc80 100%);
        background-attachment: fixed;
    }

    /* Contenedores blancos semi-transparentes para legibilidad */
    .stExpander, .stCode, .stAlert, .stTextInput > div, .stNumberInput > div, 
    .stSelectbox > div, [data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 12px;
    }

    /* Todas las letras en color azul oscuro para contraste */
    .stApp, p, span, label, h1, h2, h3, h4, h5, h6, .stMarkdown, .stCode {
        color: #0d47a1 !important;
    }

    /* Títulos con sombra suave */
    h1, h2, h3 {
        text-shadow: 1px 1px 2px rgba(255,255,255,0.9);
        font-weight: bold !important;
    }

    /* Botones */
    .stButton > button {
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
        background-color: #1976d2 !important;
        color: white !important;
        border: none;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(25, 118, 210, 0.4);
        background-color: #0d47a1 !important;
    }

    /* Tarjetas de categorías */
    .categoria-card {
        background: rgba(255,255,255,0.9);
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #ff9800;
        margin: 10px 0;
    }

    /* Facturas y comprobantes */
    .factura {
        background: white;
        padding: 20px;
        border-radius: 10px;
        border: 2px dashed #1976d2;
        font-family: monospace;
    }
    </style>
    """, unsafe_allow_html=True)

agregar_estilos()

# ========================= DICCIONARIO DE IMÁGENES =========================
IMAGENES_MEDICAMENTOS = {
    # Analgésicos y Antiinflamatorios
    "M001": "https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=300&h=300&fit=crop",  # Paracetamol
    "M002": "https://images.unsplash.com/photo-1550572017-edd951b55104?w=300&h=300&fit=crop",  # Ibuprofeno
    "M003": "https://images.unsplash.com/photo-1607619056574-7b8d3ee536b2?w=300&h=300&fit=crop",  # Aspirina
    "M004": "https://images.unsplash.com/photo-1631549916768-4119b2e5f926?w=300&h=300&fit=crop",  # Naproxeno
    "M005": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=300&h=300&fit=crop",  # Diclofenaco
    
    # Antibióticos
    "M006": "https://images.unsplash.com/photo-1583324113626-70df0f4deaab?w=300&h=300&fit=crop",  # Amoxicilina
    "M007": "https://images.unsplash.com/photo-1576602976047-174e57a47881?w=300&h=300&fit=crop",  # Azitromicina
    "M008": "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=300&h=300&fit=crop",  # Ciprofloxacino
    "M009": "https://images.unsplash.com/photo-1644303898977-26e4e6b76f5a?w=300&h=300&fit=crop",  # Metronidazol
    
    # Gastrointestinales
    "M010": "https://images.unsplash.com/photo-1626716498378-61471b5f2d43?w=300&h=300&fit=crop", # Omeprazol
    "M011": "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=300&h=300&fit=crop", # Ranitidina
    "M012": "https://images.unsplash.com/photo-1571772996211-2f02c9727629?w=300&h=300&fit=crop", # Loperamida
    "M013": "https://images.unsplash.com/photo-1559757175-5700dde675bc?w=300&h=300&fit=crop", # Simeticona
    
    # Aseo e Higiene
    "M014": "https://images.unsplash.com/photo-1559650656-5d1d361ad10e?w=300&h=300&fit=crop", # Pasta dental
    "M015": "https://images.unsplash.com/photo-1584308972272-9e4e7685e80f?w=300&h=300&fit=crop", # Jabón antibacterial
    "M016": "https://images.unsplash.com/photo-1582719471384-894fbb16e074?w=300&h=300&fit=crop", # Papel higiénico
    "M017": "https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=300&h=300&fit=crop", # Alcohol en gel
    "M018": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=300&h=300&fit=crop", # Enjuague bucal
    
    # Vitaminas y Antialérgicos
    "M019": "https://images.unsplash.com/photo-1556227702-d1e4e7b5c232?w=300&h=300&fit=crop", # Vitamina C
    "M020": "https://images.unsplash.com/photo-1587854692749-7e22e121af4f?w=300&h=300&fit=crop"  # Loratadina
}

# ========================= CLASES =========================

class Usuario:
    def __init__(self, id_usuario, nombre, correo, contrasena, rol):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.correo = correo
        self.__contrasena = contrasena
        self.rol = rol
        self.sueldo = 1500 if rol == "Administrador" else 500

    def get_contrasena(self):
        return self.__contrasena

    def mostrar_info(self):
        return f"Nombre: {self.nombre}\nID: {self.id_usuario}\nCorreo: {self.correo}\nRol: {self.rol}\nSueldo: ${self.sueldo}"

    def generar_comprobante_pago(self):
        return f"""
========================================
      COMPROBANTE DE PAGO
========================================
Empleado : {self.nombre}
ID       : {self.id_usuario}
Rol      : {self.rol}
Cargo    : {self.rol}
----------------------------------------
Sueldo base: ${self.sueldo:.2f}
Total a pagar: ${self.sueldo:.2f}
========================================
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
========================================
"""

class Administrador(Usuario):
    def __init__(self, id_usuario, nombre, correo, contrasena):
        super().__init__(id_usuario, nombre, correo, contrasena, "Administrador")

class Empleado(Usuario):
    def __init__(self, id_usuario, nombre, correo, contrasena):
        super().__init__(id_usuario, nombre, correo, contrasena, "Empleado")

class Medicamento:
    def __init__(self, codigo, nombre, precio, stock, fecha_vencimiento, categoria):
        if not codigo or not nombre:
            raise ValueError("Código y nombre no pueden estar vacíos")
        if precio < 0:
            raise ValueError("El precio no puede ser negativo")
        if stock < 0:
            raise ValueError("El stock no puede ser negativo")
            
        self.__codigo = codigo
        self.__nombre = nombre
        self.__precio = precio
        self.__stock = stock
        self.__fecha_vencimiento = fecha_vencimiento
        self.categoria = categoria

    def get_codigo(self): return self.__codigo
    def get_nombre(self): return self.__nombre
    def get_precio(self): return self.__precio
    def get_stock(self): return self.__stock
    def get_fecha_vencimiento(self): return self.__fecha_vencimiento

    def reducir_stock(self, cantidad):
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero")
        if cantidad <= self.__stock:
            self.__stock -= cantidad
            return cantidad
        else:
            disponible = self.__stock
            self.__stock = 0
            return disponible

    def verificar_stock(self):
        if self.__stock <= 5:
            return f"⚠️ ALERTA: Stock MUY bajo de {self.__nombre} (quedan {self.__stock} unidades)"
        return ""

    def verificar_vencimiento(self):
        try:
            fecha_venc = datetime.strptime(self.__fecha_vencimiento, "%d/%m/%Y")
            hoy = datetime.now()
            dias_restantes = (fecha_venc - hoy).days
            
            if dias_restantes < 0:
                return f"❌ VENCIDO: {self.__nombre} venció el {self.__fecha_vencimiento}"
            elif dias_restantes <= 30:
                return f"⚠️ PRÓXIMO A VENCER: {self.__nombre} vence en {dias_restantes} días ({self.__fecha_vencimiento})"
            return ""
        except:
            return ""

    def __str__(self):
        return f"{self.__codigo} - {self.__nombre} | ${self.__precio:.2f} | Stock: {self.__stock} | Categoría: {self.categoria}"

class Inventario:
    def __init__(self):
        self.lista_medicamentos = []

    def agregar_medicamento(self, med):
        if self.buscar_medicamento(med.get_codigo()):
            raise ValueError(f"Ya existe un medicamento con el código {med.get_codigo()}")
        self.lista_medicamentos.append(med)

    def buscar_medicamento(self, codigo):
        for m in self.lista_medicamentos:
            if m.get_codigo() == codigo:
                return m
        return None

    def eliminar_medicamento(self, codigo):
        med = self.buscar_medicamento(codigo)
        if med:
            self.lista_medicamentos.remove(med)
            return True
        return False

    def obtener_por_categoria(self):
        categorias = {}
        for m in self.lista_medicamentos:
            if m.categoria not in categorias:
                categorias[m.categoria] = []
            categorias[m.categoria].append(m)
        return categorias

    def obtener_alertas(self):
        alertas = []
        for m in self.lista_medicamentos:
            alerta_stock = m.verificar_stock()
            alerta_venc = m.verificar_vencimiento()
            if alerta_stock:
                alertas.append(alerta_stock)
            if alerta_venc:
                alertas.append(alerta_venc)
        return alertas

class Proveedor:
    def __init__(self, id_proveedor, nombre, direccion, telefono, empresa):
        if not nombre or not empresa:
            raise ValueError("Nombre y empresa son obligatorios")
        self.id_proveedor = id_proveedor
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.empresa = empresa

    def generar_factura(self, medicamento, cantidad, valor_unitario):
        total = cantidad * valor_unitario
        return f"""
========================================
          FACTURA DE PROVEEDOR
========================================
Proveedor: {self.nombre}
Empresa  : {self.empresa}
Teléfono : {self.telefono}
Dirección: {self.direccion}
----------------------------------------
Medicamento: {medicamento}
Cantidad   : {cantidad} unidades
Valor unit.: ${valor_unitario:.2f}
----------------------------------------
TOTAL A PAGAR: ${total:.2f}
========================================
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
========================================
"""

    def __str__(self):
        return f"ID: {self.id_proveedor} | {self.nombre} - {self.empresa} | Tel: {self.telefono}"

class Venta:
    def __init__(self, numero_venta, medicamento, cantidad_solicitada):
        if cantidad_solicitada <= 0:
            raise ValueError("Cantidad inválida para la venta")
        
        self.numero_venta = numero_venta
        self.medicamento = medicamento
        self.cantidad_solicitada = cantidad_solicitada
        self.cantidad_vendida = medicamento.reducir_stock(cantidad_solicitada)
        self.total = medicamento.get_precio() * self.cantidad_vendida
        self.hubo_stock_insuficiente = self.cantidad_vendida < cantidad_solicitada

    def generar_factura(self):
        factura = f"""
========================================
           🧾 FACTURA DE VENTA
========================================
N° Venta     : {self.numero_venta}
Medicamento  : {self.medicamento.get_nombre()}
Categoría    : {self.medicamento.categoria}
"""
        if self.hubo_stock_insuficiente:
            factura += f"\n⚠️ ATENCIÓN: Stock insuficiente!"
            factura += f"\nSolicitado: {self.cantidad_solicitada} | Vendido: {self.cantidad_vendida}"
        
        factura += f"""
Cantidad     : {self.cantidad_vendida}
Precio unit. : ${self.medicamento.get_precio():.2f}
----------------------------------------
Total a pagar: ${self.total:.2f}
========================================
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
========================================
"""
        return factura

# ========================= INICIALIZAR DATOS =========================
def inicializar_datos():
    if 'inventario' not in st.session_state:
        st.session_state.inventario = Inventario()
        st.session_state.proveedores = []
        st.session_state.ventas = []
        st.session_state.usuarios = []
        st.session_state.autenticado = False
        st.session_state.usuario_actual = None
        
        # Cargar 20 medicamentos iniciales por categorías
        medicamentos_iniciales = [
            # Analgésicos y Antiinflamatorios
            ("M001", "Paracetamol 500mg", 3.50, 150, "10/12/2026", "Analgésicos/Antiinflamatorios"),
            ("M002", "Ibuprofeno 400mg", 5.00, 130, "15/08/2026", "Analgésicos/Antiinflamatorios"),
            ("M003", "Aspirina 100mg", 2.50, 4, "01/11/2025", "Analgésicos/Antiinflamatorios"),
            ("M004", "Naproxeno 250mg", 6.80, 80, "20/01/2027", "Analgésicos/Antiinflamatorios"),
            ("M005", "Diclofenaco 50mg", 7.20, 3, "05/09/2025", "Analgésicos/Antiinflamatorios"),
            
            # Antibióticos
            ("M006", "Amoxicilina 500mg", 15.30, 130, "20/08/2026", "Antibióticos"),
            ("M007", "Azitromicina 250mg", 22.50, 60, "15/03/2027", "Antibióticos"),
            ("M008", "Ciprofloxacino 500mg", 18.90, 45, "10/10/2026", "Antibióticos"),
            ("M009", "Metronidazol 250mg", 12.40, 2, "28/02/2026", "Antibióticos"),
            
            # Gastrointestinales
            ("M010", "Omeprazol 20mg", 12.00, 50, "10/12/2024", "Gastrointestinales"),
            ("M011", "Ranitidina 150mg", 8.50, 70, "05/06/2026", "Gastrointestinales"),
            ("M012", "Loperamida 2mg", 6.30, 90, "18/09/2026", "Gastrointestinales"),
            ("M013", "Simeticona 125mg", 9.80, 55, "22/11/2026", "Gastrointestinales"),
            
            # Aseo e Higiene
            ("M014", "Pasta Dental Colgate", 4.20, 200, "01/01/2028", "Aseo e Higiene"),
            ("M015", "Jabón Antibacterial", 3.80, 180, "15/06/2027", "Aseo e Higiene"),
            ("M016", "Papel Higiénico (4u)", 5.50, 160, "01/01/2029", "Aseo e Higiene"),
            ("M017", "Alcohol en Gel 500ml", 7.90, 120, "30/04/2027", "Aseo e Higiene"),
            ("M018", "Enjuague Bucal 500ml", 11.20, 75, "15/08/2027", "Aseo e Higiene"),
            
            # Vitaminas y Antialérgicos
            ("M019", "Vitamina C 1000mg", 14.50, 100, "20/12/2026", "Vitaminas y Antialérgicos"),
            ("M020", "Loratadina 10mg", 10.80, 85, "10/05/2027", "Vitaminas y Antialérgicos"),
        ]
        
        for med_data in medicamentos_iniciales:
            med = Medicamento(*med_data)
            st.session_state.inventario.agregar_medicamento(med)
        
        # Agregar proveedores iniciales
        st.session_state.proveedores = [
            Proveedor(1, "Juan Ruiz", "Av. Principal 123", "0991234567", "Farmacéutica del Sur"),
            Proveedor(2, "María Torres", "Calle Central 456", "0987654321", "Laboratorios Andinos")
        ]

inicializar_datos()

# ========================= SISTEMA DE LOGIN =========================
def mostrar_login():
    st.markdown("<h1 style='text-align:center; margin-top:100px;'>🧪 SISTEMA DE FARMACIA</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Iniciar Sesión</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            usuario = st.text_input("👤 Usuario:")
            contrasena = st.text_input("🔒 Contraseña:", type="password")
            submit = st.form_submit_button("✅ Iniciar Sesión")
            
            if submit:
                if usuario == "sistema" and contrasena == "12341":
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = "sistema"
                    st.success("✅ Inicio de sesión exitoso!")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos. Inténtalo de nuevo.")

# ========================= PANEL PRINCIPAL =========================
def mostrar_panel_principal():
    st.title("🧪 Sistema de Gestión de Farmacia")
    st.write(f"👤 Bienvenido: **{st.session_state.usuario_actual}**")
    
    # Botón de cerrar sesión
    if st.button("🚪 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.usuario_actual = None
        st.rerun()
    
    # Mostrar alertas generales
    alertas = st.session_state.inventario.obtener_alertas()
    if alertas:
        st.markdown("### ⚠️ Alertas del Sistema")
        for alerta in alertas:
            if "VENCIDO" in alerta:
                st.error(alerta)
            elif "PRÓXIMO A VENCER" in alerta or "MUY bajo" in alerta:
                st.warning(alerta)
    
    st.markdown("---")
    
    # Pestañas
    tab1, tab2, tab3, tab4 = st.tabs(["💊 Inventario", "👥 Usuarios", "🏢 Proveedores", "💸 Ventas"])

    # ==================== PESTAÑA 1: INVENTARIO ====================
    with tab1:
        st.header("💊 Inventario de Medicamentos")
        
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
                sto_add = st.number_input("Stock:", min_value=0, step=1)
                fec_add = st.text_input("Fecha de vencimiento (DD/MM/AAAA):", placeholder="10/12/2026")
            
            if st.button("Agregar Medicamento", key="btn_add_inv"):
                try:
                    med = Medicamento(cod_add.strip(), nom_add.strip(), pre_add, sto_add, fec_add.strip(), cat_add)
                    st.session_state.inventario.agregar_medicamento(med)
                    st.success("✅ Medicamento agregado correctamente.")
                except ValueError as e:
                    st.error(f"❌ Error: {e}")
        
        # Mostrar inventario por categorías
        st.markdown("### 📋 Inventario por Categorías")
        categorias = st.session_state.inventario.obtener_por_categoria()
        
        for cat, medicamentos in categorias.items():
            with st.expander(f"📂 {cat} ({len(medicamentos)} productos)", expanded=True):
                for m in medicamentos:
                    col_img, col_info = st.columns([1, 4])
                    with col_img:
                        if m.get_codigo() in IMAGENES_MEDICAMENTOS:
                            st.image(IMAGENES_MEDICAMENTOS[m.get_codigo()], width=100)
                        else:
                            st.image("https://cdn-icons-png.flaticon.com/512/2972/2972183.png", width=100)
                    with col_info:
                        st.markdown(f"**{m.get_nombre()}**")
                        st.code(str(m))
                        st.write(f"📅 Vencimiento: {m.get_fecha_vencimiento()}")
                        
                        # Verificar alertas
                        alerta_stock = m.verificar_stock()
                        alerta_venc = m.verificar_vencimiento()
                        if alerta_stock:
                            if "MUY bajo" in alerta_stock:
                                st.error(alerta_stock)
                            else:
                                st.warning(alerta_stock)
                        if alerta_venc:
                            if "VENCIDO" in alerta_venc:
                                st.error(alerta_venc)
                            else:
                                st.warning(alerta_venc)
                    st.markdown("---")

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
                        if not nombre_u.strip() or not correo_u.strip() or not pass_u:
                            raise ValueError("Todos los campos son obligatorios")
                        if "@" not in correo_u:
                            raise ValueError("Ingresa un correo válido")
                        
                        if rol == "Administrador":
                            user = Administrador(len(st.session_state.usuarios)+1, nombre_u.strip(), 
                                                correo_u.strip(), pass_u)
                        else:
                            user = Empleado(len(st.session_state.usuarios)+1, nombre_u.strip(), 
                                           correo_u.strip(), pass_u)
                        st.session_state.usuarios.append(user)
                        st.success(f"✅ Usuario {nombre_u} agregado como {rol}")
                    except ValueError as e:
                        st.error(f"❌ Error: {e}")
        
        with col2:
            with st.expander("🗑️ Eliminar Usuario", expanded=True):
                if st.session_state.usuarios:
                    usuario_eliminar = st.selectbox("Seleccionar usuario:", 
                        [f"{u.id_usuario} - {u.nombre} ({u.rol})" for u in st.session_state.usuarios],
                        key="user_delete")
                    
                    if st.button("Eliminar Usuario", key="btn_del_user"):
                        id_eliminar = int(usuario_eliminar.split(" - ")[0])
                        st.session_state.usuarios = [u for u in st.session_state.usuarios if u.id_usuario != id_eliminar]
                        st.success("✅ Usuario eliminado correctamente")
                        st.rerun()
                else:
                    st.info("📭 No hay usuarios registrados")
        
        # Lista de usuarios y comprobantes
        st.markdown("### 📋 Lista de Usuarios y Comprobantes de Pago")
        if st.session_state.usuarios:
            for u in st.session_state.usuarios:
                with st.expander(f"👤 {u.nombre} - {u.rol}"):
                    st.code(u.mostrar_info())
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        if st.button(f"💰 Generar Comprobante", key=f"pago_{u.id_usuario}"):
                            st.session_state[f"comprobante_{u.id_usuario}"] = True
                    
                    if st.session_state.get(f"comprobante_{u.id_usuario}", False):
                        st.markdown('<div class="factura">', unsafe_allow_html=True)
                        st.text(u.generar_comprobante_pago())
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
                        if not nom_p.strip() or not emp_p.strip():
                            raise ValueError("Nombre y empresa son obligatorios")
                        prov = Proveedor(len(st.session_state.proveedores)+1, nom_p.strip(), 
                                       dir_p.strip(), tel_p.strip(), emp_p.strip())
                        st.session_state.proveedores.append(prov)
                        st.success("✅ Proveedor agregado correctamente")
                    except ValueError as e:
                        st.error(f"❌ Error: {e}")
        
        with col2:
            with st.expander("🗑️ Eliminar Proveedor", expanded=True):
                if st.session_state.proveedores:
                    prov_eliminar = st.selectbox("Seleccionar proveedor:",
                        [f"{p.id_proveedor} - {p.nombre} ({p.empresa})" for p in st.session_state.proveedores],
                        key="prov_delete")
                    
                    if st.button("Eliminar Proveedor", key="btn_del_prov"):
                        id_eliminar = int(prov_eliminar.split(" - ")[0])
                        st.session_state.proveedores = [p for p in st.session_state.proveedores if p.id_proveedor != id_eliminar]
                        st.success("✅ Proveedor eliminado correctamente")
                        st.rerun()
                else:
                    st.info("📭 No hay proveedores registrados")
        
        # Generar factura a proveedor
        st.markdown("### 🧾 Generar Factura de Pago a Proveedor")
        if st.session_state.proveedores:
            prov_seleccionado = st.selectbox("Seleccionar proveedor:",
                [f"{p.id_proveedor} - {p.nombre} ({p.empresa})" for p in st.session_state.proveedores],
                key="prov_factura")
            
            med_codigo = st.text_input("Código del medicamento suministrado:", key="med_prov")
            cantidad_prov = st.number_input("Cantidad suministrada:", min_value=1, step=1, key="cant_prov")
            valor_unit = st.number_input("Valor unitario ($):", min_value=0.0, step=0.01, key="val_unit")
            
            if st.button("📄 Generar Factura", key="btn_gen_factura"):
                id_prov = int(prov_seleccionado.split(" - ")[0])
                prov = next((p for p in st.session_state.proveedores if p.id_proveedor == id_prov), None)
                med = st.session_state.inventario.buscar_medicamento(med_codigo.strip())
                nombre_med = med.get_nombre() if med else med_codigo.strip()
                
                if prov:
                    st.markdown('<div class="factura">', unsafe_allow_html=True)
                    st.text(prov.generar_factura(nombre_med, cantidad_prov, valor_unit))
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("📭 Agrega un proveedor primero")
        
        # Lista de proveedores
        st.markdown("### 📋 Lista de Proveedores")
        if st.session_state.proveedores:
            for p in st.session_state.proveedores:
                st.code(str(p))
        else:
            st.info("📭 No hay proveedores registrados")

    # ==================== PESTAÑA 4: VENTAS ====================
    with tab4:
        st.header("💸 Realizar Venta")
        
        venta_codigo = st.text_input("Código del Medicamento:", key="cod_venta")
        venta_cantidad = st.number_input("Cantidad a vender:", min_value=1, step=1, key="cant_venta")
        
        if st.button("🛒 Realizar Venta", type="primary", key="btn_vender"):
            try:
                if not venta_codigo.strip():
                    raise ValueError("Ingresa el código del medicamento")
                
                med = st.session_state.inventario.buscar_medicamento(venta_codigo.strip())
                if med:
                    if med.verificar_vencimiento() and "VENCIDO" in med.verificar_vencimiento():
                        st.error("❌ No se puede vender un medicamento vencido!")
                    else:
                        venta = Venta(len(st.session_state.ventas)+1000, med, venta_cantidad)
                        st.session_state.ventas.append(venta)
                        
                        if venta.hubo_stock_insuficiente:
                            st.warning(f"⚠️ Stock insuficiente! Solicitaste {venta.cantidad_solicitada} pero solo hay {venta.cantidad_vendida} unidades. Se vendió solo lo disponible.")
                        
                        st.success("✅ Venta realizada correctamente")
                        st.markdown('<div class="factura">', unsafe_allow_html=True)
                        st.text(venta.generar_factura())
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Verificar alerta de stock
                        alerta = med.verificar_stock()
                        if alerta:
                            st.warning(alerta)
                else:
                    raise ValueError("Medicamento no encontrado")
            except ValueError as e:
                st.error(f"❌ Error: {e}")
        
        # Historial de ventas
        if st.session_state.ventas:
            with st.expander("📜 Historial de Ventas"):
                total_ventas = sum(v.total for v in st.session_state.ventas)
                st.markdown(f"**Total de ventas realizadas: {len(st.session_state.ventas)}**")
                st.markdown(f"**Ingresos totales: ${total_ventas:.2f}**")
                st.markdown("---")
                for v in reversed(st.session_state.ventas):
                    st.text(v.generar_factura())
                    st.markdown("---")

# ========================= EJECUCIÓN PRINCIPAL =========================
if not st.session_state.autenticado:
    mostrar_login()
else:
    mostrar_panel_principal()
