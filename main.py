import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import base_datos

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class SalsamentariaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Gestión - Salsamentaria")
        self.geometry("1100x700")
        self.minsize(900, 600)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- MENÚ LATERAL ---
        self.frame_menu = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.frame_menu.grid(row=0, column=0, sticky="nsew")
        self.frame_menu.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.frame_menu, text="SALSAMENTARIA", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        self.btn_ventas = ctk.CTkButton(self.frame_menu, text="Punto de Venta", height=40, command=self.mostrar_ventas)
        self.btn_ventas.grid(row=1, column=0, padx=20, pady=10)

        self.btn_inventario = ctk.CTkButton(self.frame_menu, text="Inventario / Compras", height=40, command=self.mostrar_inventario)
        self.btn_inventario.grid(row=2, column=0, padx=20, pady=10)

        # --- ÁREA PRINCIPAL ---
        self.frame_principal = ctk.CTkFrame(self, corner_radius=10)
        self.frame_principal.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.frame_principal.grid_rowconfigure(0, weight=1)
        self.frame_principal.grid_columnconfigure(0, weight=1)

        # Variables de estado para la venta
        self.carrito = [] # Lista de diccionarios
        self.total_venta = 0.0

        # Vistas
        self.vista_inventario = self.crear_vista_inventario()
        self.vista_ventas = self.crear_vista_ventas()
        
        # Iniciar en ventas (es lo que más se usa)
        self.mostrar_ventas()

    def mostrar_inventario(self):
        self.vista_ventas.grid_forget()
        self.vista_inventario.grid(row=0, column=0, sticky="nsew")
        self.cargar_tabla_inventario()

    def mostrar_ventas(self):
        self.vista_inventario.grid_forget()
        self.vista_ventas.grid(row=0, column=0, sticky="nsew")
        self.filtrar_productos_venta() # Cargar todos los productos al inicio

    # ==========================================
    # 1. MÓDULO DE INVENTARIO (YA LO TENÍAMOS)
    # ==========================================
    def crear_vista_inventario(self):
        # [El código de inventario se mantiene igual al paso anterior]
        frame = ctk.CTkFrame(self.frame_principal, fg_color="transparent")
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(frame, text="Gestión de Inventario y Compras", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        form_frame = ctk.CTkFrame(frame)
        form_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(form_frame, text="Nombre Producto:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.ent_nombre_prod = ctk.CTkEntry(form_frame, width=200)
        self.ent_nombre_prod.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(form_frame, text="Unidad:").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.cbx_unidad = ctk.CTkComboBox(form_frame, values=["Kg", "Gramos", "Libra", "Unidad"], width=100)
        self.cbx_unidad.grid(row=0, column=3, padx=10, pady=10)

        ctk.CTkLabel(form_frame, text="Cantidad comprada:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.ent_cantidad_compra = ctk.CTkEntry(form_frame, width=200)
        self.ent_cantidad_compra.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkLabel(form_frame, text="Costo TOTAL ($):").grid(row=1, column=2, padx=10, pady=10, sticky="w")
        self.ent_costo_total = ctk.CTkEntry(form_frame, width=150)
        self.ent_costo_total.grid(row=1, column=3, padx=10, pady=10)

        ctk.CTkButton(form_frame, text="Registrar Compra e Inventario", height=40, font=ctk.CTkFont(weight="bold"), command=self.guardar_compra).grid(row=2, column=0, columnspan=4, pady=20)

        style = ttk.Style()
        style.configure("Treeview", rowheight=30, font=('Arial', 11))
        style.configure("Treeview.Heading", font=('Arial', 12, 'bold'))

        columnas = ("ID", "Producto", "Unidad", "Stock", "Costo Unit.", "Precio Sugerido (+15%)")
        self.tabla_inventario = ttk.Treeview(frame, columns=columnas, show="headings")
        anchos = [40, 250, 80, 80, 100, 150]
        for col, ancho in zip(columnas, anchos):
            self.tabla_inventario.heading(col, text=col)
            self.tabla_inventario.column(col, width=ancho, anchor="center")
        self.tabla_inventario.grid(row=2, column=0, columnspan=2, sticky="nsew")

        return frame

    def guardar_compra(self):
        nombre = self.ent_nombre_prod.get().strip().upper()
        unidad = self.cbx_unidad.get()
        try:
            cantidad = float(self.ent_cantidad_compra.get())
            costo_total = float(self.ent_costo_total.get())
        except ValueError:
            messagebox.showerror("Error", "Cantidad y costo deben ser números.")
            return

        costo_unitario = costo_total / cantidad
        precio_sugerido = costo_unitario * 1.15
        conexion = base_datos.obtener_conexion()
        cursor = conexion.cursor()

        try:
            cursor.execute("SELECT id_producto, stock_actual FROM productos WHERE nombre = ?", (nombre,))
            producto = cursor.fetchone()
            if producto:
                cursor.execute("UPDATE productos SET costo_actual = ?, precio_sugerido = ?, stock_actual = stock_actual + ? WHERE id_producto = ?", (costo_unitario, precio_sugerido, cantidad, producto[0]))
            else:
                cursor.execute("INSERT INTO productos (nombre, unidad_medida, costo_actual, precio_sugerido, stock_actual) VALUES (?, ?, ?, ?, ?)", (nombre, unidad, costo_unitario, precio_sugerido, cantidad))
                id_prod = cursor.lastrowid
                producto = (id_prod,)
            
            cursor.execute("INSERT INTO compras (id_producto, cantidad_comprada, costo_total_compra) VALUES (?, ?, ?)", (producto[0], cantidad, costo_total))
            conexion.commit()
            messagebox.showinfo("Éxito", "Compra guardada.")
            self.ent_nombre_prod.delete(0, 'end')
            self.ent_cantidad_compra.delete(0, 'end')
            self.ent_costo_total.delete(0, 'end')
            self.cargar_tabla_inventario()
        finally:
            conexion.close()

    def cargar_tabla_inventario(self):
        for item in self.tabla_inventario.get_children(): self.tabla_inventario.delete(item)
        conexion = base_datos.obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_producto, nombre, unidad_medida, stock_actual, costo_actual, precio_sugerido FROM productos")
        for fila in cursor.fetchall():
            self.tabla_inventario.insert("", "end", values=(fila[0], fila[1], fila[2], round(fila[3], 2), f"${fila[4]:,.0f}", f"${fila[5]:,.0f}"))
        conexion.close()

    # ==========================================
    # 2. NUEVO MÓDULO: PUNTO DE VENTA
    # ==========================================
    def crear_vista_ventas(self):
        frame = ctk.CTkFrame(self.frame_principal, fg_color="transparent")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # -- PANEL IZQUIERDO: BÚSQUEDA --
        panel_izq = ctk.CTkFrame(frame)
        panel_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        panel_izq.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(panel_izq, text="Buscador de Productos", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=10)
        
        self.ent_buscador = ctk.CTkEntry(panel_izq, placeholder_text="Escriba el nombre para buscar...", width=300, font=ctk.CTkFont(size=14))
        self.ent_buscador.grid(row=1, column=0, pady=5, padx=10, sticky="ew")
        self.ent_buscador.bind("<KeyRelease>", self.filtrar_productos_venta)

        cols_busqueda = ("ID", "Producto", "Precio", "Unidad")
        self.tabla_busqueda = ttk.Treeview(panel_izq, columns=cols_busqueda, show="headings")
        self.tabla_busqueda.heading("ID", text="ID")
        self.tabla_busqueda.heading("Producto", text="Producto (Doble clic para agregar)")
        self.tabla_busqueda.heading("Precio", text="Precio/U")
        self.tabla_busqueda.heading("Unidad", text="Medida")
        
        self.tabla_busqueda.column("ID", width=40)
        self.tabla_busqueda.column("Producto", width=250)
        self.tabla_busqueda.column("Precio", width=90)
        self.tabla_busqueda.column("Unidad", width=70)
        
        self.tabla_busqueda.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.tabla_busqueda.bind("<Double-1>", self.agregar_al_carrito) # Evento de doble clic

        # -- PANEL DERECHO: CARRITO Y COBRO --
        panel_der = ctk.CTkFrame(frame)
        panel_der.grid(row=0, column=1, sticky="nsew")
        panel_der.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(panel_der, text="Factura Actual", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=10)

        cols_carrito = ("Producto", "Cantidad", "Subtotal")
        self.tabla_carrito = ttk.Treeview(panel_der, columns=cols_carrito, show="headings")
        self.tabla_carrito.heading("Producto", text="Producto")
        self.tabla_carrito.heading("Cantidad", text="Cant/Peso")
        self.tabla_carrito.heading("Subtotal", text="Subtotal")
        
        self.tabla_carrito.column("Producto", width=180)
        self.tabla_carrito.column("Cantidad", width=80, anchor="center")
        self.tabla_carrito.column("Subtotal", width=100, anchor="e")
        
        self.tabla_carrito.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Totales y Vueltas
        self.lbl_total = ctk.CTkLabel(panel_der, text="TOTAL: $0", font=ctk.CTkFont(size=35, weight="bold"), text_color="#2A9D8F")
        self.lbl_total.grid(row=2, column=0, pady=10)

        frame_pagos = ctk.CTkFrame(panel_der, fg_color="transparent")
        frame_pagos.grid(row=3, column=0, pady=10)

        ctk.CTkLabel(frame_pagos, text="Dinero Recibido $:", font=ctk.CTkFont(size=18)).grid(row=0, column=0, padx=10)
        self.ent_recibido = ctk.CTkEntry(frame_pagos, font=ctk.CTkFont(size=18), width=150)
        self.ent_recibido.grid(row=0, column=1)
        self.ent_recibido.bind("<KeyRelease>", self.calcular_vueltas)

        self.lbl_vueltas = ctk.CTkLabel(panel_der, text="VUELTAS: $0", font=ctk.CTkFont(size=28, weight="bold"), text_color="#E76F51")
        self.lbl_vueltas.grid(row=4, column=0, pady=10)

        self.btn_cobrar = ctk.CTkButton(panel_der, text="COBRAR E IMPRIMIR", height=60, font=ctk.CTkFont(size=18, weight="bold"), command=self.procesar_venta)
        self.btn_cobrar.grid(row=5, column=0, sticky="ew", padx=20, pady=20)

        return frame

    def filtrar_productos_venta(self, event=None):
        termino = self.ent_buscador.get().strip().upper()
        for item in self.tabla_busqueda.get_children():
            self.tabla_busqueda.delete(item)

        conexion = base_datos.obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_producto, nombre, precio_sugerido, unidad_medida FROM productos WHERE nombre LIKE ?", (f'%{termino}%',))
        
        for fila in cursor.fetchall():
            self.tabla_busqueda.insert("", "end", values=(fila[0], fila[1], fila[2], fila[3]))
        conexion.close()

    def agregar_al_carrito(self, event):
        seleccion = self.tabla_busqueda.selection()
        if not seleccion: return

        item = self.tabla_busqueda.item(seleccion[0])
        id_prod, nombre, precio, unidad = item['values']
        
        # Pedir cantidad / peso al usuario
        cantidad = simpledialog.askfloat("Cantidad", f"Ingrese la cantidad de {nombre} ({unidad}):", parent=self, minvalue=0.01)
        
        if cantidad:
            subtotal = float(precio) * cantidad
            # Guardamos en la variable para registrar en BD
            self.carrito.append({
                "id_producto": id_prod,
                "nombre": nombre,
                "cantidad": cantidad,
                "precio_unitario": precio,
                "subtotal": subtotal
            })
            
            # Mostramos en la tabla
            self.tabla_carrito.insert("", "end", values=(nombre, f"{cantidad} {unidad}", f"${subtotal:,.0f}"))
            self.actualizar_total()

    def actualizar_total(self):
        self.total_venta = sum(item["subtotal"] for item in self.carrito)
        self.lbl_total.configure(text=f"TOTAL: ${self.total_venta:,.0f}")
        self.calcular_vueltas() # Recalcular si ya habían escrito algo en "Recibido"

    def calcular_vueltas(self, event=None):
        try:
            recibido = float(self.ent_recibido.get())
            vueltas = recibido - self.total_venta
            if vueltas >= 0:
                self.lbl_vueltas.configure(text=f"VUELTAS: ${vueltas:,.0f}")
            else:
                self.lbl_vueltas.configure(text="Falta dinero")
        except ValueError:
            self.lbl_vueltas.configure(text="VUELTAS: $0")

    def procesar_venta(self):
        if not self.carrito:
            messagebox.showwarning("Atención", "El carrito está vacío.")
            return

        try:
            recibido = float(self.ent_recibido.get())
            vueltas = recibido - self.total_venta
            if vueltas < 0:
                messagebox.showerror("Error", "El valor recibido es menor al total.")
                return
        except ValueError:
            messagebox.showerror("Error", "Ingrese un valor recibido válido.")
            return

        # 1. Guardar en Base de Datos
        conexion = base_datos.obtener_conexion()
        cursor = conexion.cursor()
        
        try:
            # Cabecera de venta
            cursor.execute("INSERT INTO ventas (total_venta, valor_recibido, vueltas) VALUES (?, ?, ?)", (self.total_venta, recibido, vueltas))
            numero_factura = cursor.lastrowid

            # Detalles y descontar stock
            for item in self.carrito:
                cursor.execute("INSERT INTO detalle_venta (numero_factura, id_producto, cantidad_o_peso, subtotal) VALUES (?, ?, ?, ?)",
                               (numero_factura, item["id_producto"], item["cantidad"], item["subtotal"]))
                
                cursor.execute("UPDATE productos SET stock_actual = stock_actual - ? WHERE id_producto = ?", (item["cantidad"], item["id_producto"]))

            conexion.commit()
            messagebox.showinfo("Venta Exitosa", f"Se generó la factura #{numero_factura}")
            
            # --- AQUÍ LLAMAREMOS A LA FUNCIÓN DE IMPRIMIR PDF EN EL SIGUIENTE PASO ---
            
            # Limpiar pantalla
            self.carrito.clear()
            for item in self.tabla_carrito.get_children(): self.tabla_carrito.delete(item)
            self.total_venta = 0.0
            self.actualizar_total()
            self.ent_recibido.delete(0, 'end')
            self.ent_buscador.delete(0, 'end')
            self.filtrar_productos_venta()
            
        except Exception as e:
            messagebox.showerror("Error BD", str(e))
            conexion.rollback()
        finally:
            conexion.close()

if __name__ == "__main__":
    app = SalsamentariaApp()
    app.mainloop()