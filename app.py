import streamlit as st

# ========================= CLASES =========================

class Usuario:
    def __init__(self, id_usuario, nombre, correo, contrasena, rol):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.correo = correo
        self.__contrasena = contrasena
        self.rol = rol

    def mostrar_info(self):
        return f"Nombre: {self.nombre}\nID: {self.id_usuario}\nCorreo: {self.correo}\nRol: {self.rol}\nContraseña: {'*' * len(self.__contrasena)}"


class Administrador(Usuario):
    def mostrar_info(self):
        return "===== ADMINISTRADOR =====\n" + super().mostrar_info()


class Empleado(Usuario):
    def mostrar_info(self):
        return "===== EMPLEADO =====\n" + super().mostrar_info()


class Medicamento:
    def __init__(self, codigo, nombre, precio, stock, fecha_vencimiento):
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
            return True
        return False

    def verificar_stock(self):
        if self.__stock <= 5:
            return f"⚠️ ALERTA: Stock bajo de {self.__nombre} ({self.__stock})"
        return ""

    def __str__(self):
        return f"{self.__codigo} - {self.__nombre} | ${self.__precio} | Stock: {self.__stock}"


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


class Proveedor:
    def __init__(self, nombre, direccion, telefono, empresa):
        if not nombre or not empresa:
            raise ValueError("Nombre y empresa son obligatorios")
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.empresa = empresa

    def __str__(self):
        return f"{self.nombre} - {self.empresa} | {self.telefono}"


class Venta:
    def __init__(self, numero_venta, medicamento, cantidad):
        if cantidad <= 0:
            raise ValueError("Cantidad inválida para la venta")
        self.numero_venta = numero_venta
        self.medicamento = medicamento
        self.cantidad = cantidad
        self.total = medicamento.get_precio() * cantidad

    def registrar_venta(self):
        return self.medicamento.reducir_stock(self.cantidad)


# ========================= INICIALIZAR DATOS =========================
if 'inventario' not in st.session_state:
    st.session_state.inventario = Inventario()
    st.session_state.proveedores = []
    st.session_state.ventas = []
    st.session_state.usuarios = []
    
    # Cargar medicamentos iniciales
    for med in [
        Medicamento("M001", "Paracetamol", 3.50, 150, "10/12/2026"),
        Medicamento("M002", "Ibuprofeno", 5.00, 130, "15/08/2026"),
        Medicamento("M003", "Amoxicilina", 15.30, 130, "20/08/2026"),
        Medicamento("M004", "Omeprazol", 12.00, 50, "10/12/2024")
    ]:
        st.session_state.inventario.agregar_medicamento(med)

# ========================= INTERFAZ STREAMLIT =========================
st.title("🧪 Sistema de Farmacia")

# Pestañas
tab1, tab2, tab3, tab4 = st.tabs(["Inventario", "Usuarios", "Proveedores", "Ventas"])

# ==================== PESTAÑA 1: INVENTARIO ====================
with tab1:
    st.header("📦 Inventario")
    
    # Agregar medicamento
    with st.expander("➕ Agregar Medicamento", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            cod_add = st.text_input("Código:", placeholder="M005", key="cod_add")
            nom_add = st.text_input("Nombre:", key="nom_add")
        with col2:
            pre_add = st.number_input("Precio:", min_value=0.0, step=0.01, key="pre_add")
            sto_add = st.number_input("Stock:", min_value=0, step=1, key="sto_add")
        fec_add = st.text_input("Fecha de vencimiento:", key="fec_add")
        
        if st.button("Agregar Medicamento", type="primary", key="btn_add_inv"):
            try:
                med = Medicamento(cod_add.strip(), nom_add.strip(), pre_add, sto_add, fec_add.strip())
                st.session_state.inventario.agregar_medicamento(med)
                st.success("✅ Medicamento agregado correctamente.")
            except ValueError as e:
                st.error(f"❌ Error: {e}")
    
    # Buscar o Eliminar
    with st.expander("🔍 Buscar o Eliminar"):
        cod_buscar = st.text_input("Código para buscar o eliminar:", key="cod_buscar")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Buscar", key="btn_buscar"):
                if not cod_buscar.strip():
                    st.warning("Ingresa un código para buscar")
                else:
                    med = st.session_state.inventario.buscar_medicamento(cod_buscar.strip())
                    if med:
                        st.success("✅ Encontrado:")
                        st.code(str(med))
                        alerta = med.verificar_stock()
                        if alerta:
                            st.warning(alerta)
                    else:
                        st.error("❌ Medicamento no encontrado.")
        with col2:
            if st.button("Eliminar por Código", key="btn_eliminar"):
                if not cod_buscar.strip():
                    st.warning("Ingresa un código para eliminar")
                else:
                    if st.session_state.inventario.eliminar_medicamento(cod_buscar.strip()):
                        st.success(f"✅ Medicamento {cod_buscar} eliminado correctamente.")
                    else:
                        st.error(f"❌ No se encontró el medicamento {cod_buscar}")
    
    # Ver inventario completo
    if st.button("📋 Ver Inventario Completo", key="btn_ver_inv"):
        if not st.session_state.inventario.lista_medicamentos:
            st.info("📭 Inventario vacío")
        else:
            for m in st.session_state.inventario.lista_medicamentos:
                st.code(str(m))

# ==================== PESTAÑA 2: USUARIOS ====================
with tab2:
    st.header("👥 Usuarios")
    
    with st.expander("➕ Agregar Usuario", expanded=True):
        rol = st.selectbox("Rol:", ['Administrador', 'Empleado'], key="rol_user")
        col1, col2 = st.columns(2)
        with col1:
            nombre_u = st.text_input("Nombre:", key="nom_user")
            correo_u = st.text_input("Correo:", key="cor_user")
        with col2:
            pass_u = st.text_input("Contraseña:", type="password", key="pass_user")
        
        if st.button("Agregar Usuario", type="primary", key="btn_add_user"):
            try:
                if not nombre_u.strip() or not correo_u.strip() or not pass_u:
                    raise ValueError("Todos los campos son obligatorios")
                if "@" not in correo_u:
                    raise ValueError("Ingresa un correo válido")
                
                if rol == "Administrador":
                    user = Administrador(len(st.session_state.usuarios)+1, nombre_u.strip(), 
                                        correo_u.strip(), pass_u, rol)
                else:
                    user = Empleado(len(st.session_state.usuarios)+1, nombre_u.strip(), 
                                   correo_u.strip(), pass_u, rol)
                st.session_state.usuarios.append(user)
                st.success(f"✅ Usuario {nombre_u} agregado como {rol}")
            except ValueError as e:
                st.error(f"❌ Error: {e}")
    
    if st.button("📋 Ver Usuarios", key="btn_ver_user"):
        if not st.session_state.usuarios:
            st.info("📭 No hay usuarios registrados")
        else:
            for u in st.session_state.usuarios:
                st.code(u.mostrar_info())
                st.markdown("---")

# ==================== PESTAÑA 3: PROVEEDORES ====================
with tab3:
    st.header("🏢 Proveedores")
    
    with st.expander("➕ Agregar Proveedor", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            nom_p = st.text_input("Nombre:", key="nom_prov")
            dir_p = st.text_input("Dirección:", key="dir_prov")
        with col2:
            tel_p = st.text_input("Teléfono:", key="tel_prov")
            emp_p = st.text_input("Empresa:", key="emp_prov")
        
        if st.button("Agregar Proveedor", type="primary", key="btn_add_prov"):
            try:
                if not nom_p.strip() or not emp_p.strip():
                    raise ValueError("Nombre y empresa son obligatorios")
                prov = Proveedor(nom_p.strip(), dir_p.strip(), tel_p.strip(), emp_p.strip())
                st.session_state.proveedores.append(prov)
                st.success("✅ Proveedor agregado correctamente")
            except ValueError as e:
                st.error(f"❌ Error: {e}")
    
    if st.button("📋 Ver Proveedores", key="btn_ver_prov"):
        if not st.session_state.proveedores:
            st.info("📭 No hay proveedores registrados")
        else:
            for p in st.session_state.proveedores:
                st.code(str(p))

# ==================== PESTAÑA 4: VENTAS ====================
with tab4:
    st.header("💸 Ventas")
    
    venta_codigo = st.text_input("Código del Medicamento:", key="cod_venta")
    venta_cantidad = st.number_input("Cantidad:", min_value=1, step=1, key="cant_venta")
    
    if st.button("Realizar Venta", type="primary", key="btn_vender"):
        try:
            if not venta_codigo.strip():
                raise ValueError("Ingresa el código del medicamento")
            
            med = st.session_state.inventario.buscar_medicamento(venta_codigo.strip())
            if med:
                venta = Venta(len(st.session_state.ventas)+1000, med, venta_cantidad)
                if venta.registrar_venta():
                    st.session_state.ventas.append(venta)
                    # Mostrar factura
                    st.success("✅ Venta realizada correctamente")
                    st.markdown("### 🧾 Factura")
                    st.code(f"""========================================
           FACTURA
========================================
N° Venta     : {venta.numero_venta}
Medicamento  : {venta.medicamento.get_nombre()}
Cantidad     : {venta.cantidad}
Total a pagar: ${venta.total:.2f}
========================================""")
                    alerta = med.verificar_stock()
                    if alerta:
                        st.warning(alerta)
                else:
                    raise ValueError(f"Stock insuficiente. Disponible: {med.get_stock()}")
            else:
                raise ValueError("Medicamento no encontrado")
        except ValueError as e:
            st.error(f"❌ Error: {e}")
