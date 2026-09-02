import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog, filedialog
import sqlite3
import base_datos
import impresion
import exportar_excel
from datetime import datetime
import backup

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
        self.frame_menu.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.frame_menu, text="SALSAMENTARIA", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        self.btn_ventas = ctk.CTkButton(self.frame_menu, text="Punto de Venta", height=40, command=self.mostrar_ventas)
        self.btn_ventas.grid(row=1, column=0, padx=20, pady=10)

        self.btn_inventario = ctk.CTkButton(self.frame_menu, text="Inventario / Compras", height=40, command=self.mostrar_inventario)
        self.btn_inventario.grid(row=2, column=0, padx=20, pady=10)
        
        self.btn_reportes = ctk.CTkButton(self.frame_menu, text="Cierre de Caja", height=40, command=self.mostrar_reportes)
        self.btn_reportes.grid(row=3, column=0, padx=20, pady=10)

        # --- ÁREA PRINCIPAL ---
        self.frame_principal = ctk.CTkFrame(self, corner_radius=10)
        self.frame_principal.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.frame_principal.grid_rowconfigure(0, weight=1)
        self.frame_principal.grid_columnconfigure(0, weight=1)

        self.carrito = []
        self.total_venta = 0.0
        self.total_dia_actual = 0.0
        self.cantidad_facturas_actual = 0

        # Inicializar vistas
        self.vista_inventario = self.crear_vista_inventario()
        self.vista_ventas = self.crear_vista_ventas()
        self.vista_reportes = self.crear_vista_reportes()
        
        # --- EJECUTAR BACKUP AUTOMÁTICO AL ARRANCAR ---
        backup.realizar_backup_automatico(base_datos.DB_NAME)

        self.mostrar_ventas()

    def mostrar_inventario(self):
        self.vista_ventas.grid_forget()
        self.vista_reportes.grid_forget()
        self.vista_inventario.grid(row=0, column=0, sticky="nsew")
        self.cargar_tabla_inventario()

    def mostrar_ventas(self):
        self.vista_inventario.grid_forget()
        self.vista_reportes.grid_forget()
        self.vista_ventas.grid(row=0, column=0, sticky="nsew")
        self.filtrar_productos_venta()

    def mostrar_reportes(self):
        self.vista_inventario.grid_forget()
        self.vista_ventas.grid_forget()
        self.vista_reportes.grid(row=0, column=0, sticky="nsew")
        self.cargar_datos_cierre()

    # ==========================================
    # 1. INVENTARIO
    # ==========================================
    def crear_vista_inventario(self):
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

        ctk.CTkButton(form_frame, text="Registrar Compra", height=40, font=ctk.CTkFont(weight="bold"), command=self.guardar_compra).grid(row=2, column=0, columnspan=4, pady=20)

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

        # NUEVO BOTÓN EXPORTAR INVENTARIO
        btn_exportar_inv = ctk.CTkButton(frame, text="Exportar a Excel", height=35, fg_color="#217346", hover_color="#1e6b40", font=ctk.CTkFont(weight="bold"), command=self.exportar_inv_excel)
        btn_exportar_inv.grid(row=3, column=1, pady=10, sticky="e")

        return frame

    def guardar_compra(self):
        nombre = self.ent_nombre_prod.get().strip().upper()
        unidad = self.cbx_unidad.get()
        try:
            cantidad = float(self.ent_cantidad_compra.get())
            costo_total = float(self.ent_costo_total.get())
        except ValueError:
            return messagebox.showerror("Error", "Cantidad y costo deben ser números.")

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
                producto = (cursor.lastrowid,)
            
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

    def exportar_inv_excel(self):
        ruta_guardado = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Archivos de Excel", "*.xlsx")], title="Guardar Inventario", initialfile="Inventario_Salsamentaria.xlsx")
        if ruta_guardado:
            exportar_excel.exportar_inventario(base_datos.DB_NAME, ruta_guardado)

    # ==========================================
    # 2. PUNTO DE VENTA
    # ==========================================
    def crear_vista_ventas(self):
        frame = ctk.CTkFrame(self.frame_principal, fg_color="transparent")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        panel_izq = ctk.CTkFrame(frame)
        panel_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        panel_izq.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(panel_izq, text="Buscador de Productos", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=10)
        self.ent_buscador = ctk.CTkEntry(panel_izq, placeholder_text="Escriba el nombre...", width=300)
        self.ent_buscador.grid(row=1, column=0, pady=5, padx=10, sticky="ew")
        self.ent_buscador.bind("<KeyRelease>", self.filtrar_productos_venta)

        cols_busqueda = ("ID", "Producto", "Precio", "Unidad", "Stock")
        self.tabla_busqueda = ttk.Treeview(panel_izq, columns=cols_busqueda, show="headings")
        for col in cols_busqueda: self.tabla_busqueda.heading(col, text=col)
        self.tabla_busqueda.column("ID", width=30)
        self.tabla_busqueda.column("Producto", width=220)
        self.tabla_busqueda.column("Precio", width=80)
        self.tabla_busqueda.column("Unidad", width=60)
        self.tabla_busqueda.column("Stock", width=60)
        self.tabla_busqueda.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.tabla_busqueda.bind("<Double-1>", self.agregar_al_carrito)

        panel_der = ctk.CTkFrame(frame)
        panel_der.grid(row=0, column=1, sticky="nsew")
        panel_der.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(panel_der, text="Factura Actual", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=10)

        cols_carrito = ("Producto", "Cantidad", "Subtotal")
        self.tabla_carrito = ttk.Treeview(panel_der, columns=cols_carrito, show="headings")
        for col in cols_carrito: self.tabla_carrito.heading(col, text=col)
        self.tabla_carrito.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.lbl_total = ctk.CTkLabel(panel_der, text="TOTAL: $0", font=ctk.CTkFont(size=35, weight="bold"), text_color="#2A9D8F")
        self.lbl_total.grid(row=2, column=0, pady=10)

        frame_pagos = ctk.CTkFrame(panel_der, fg_color="transparent")
        frame_pagos.grid(row=3, column=0, pady=10)
        ctk.CTkLabel(frame_pagos, text="Dinero Recibido $:").grid(row=0, column=0, padx=10)
        self.ent_recibido = ctk.CTkEntry(frame_pagos, width=150)
        self.ent_recibido.grid(row=0, column=1)
        self.ent_recibido.bind("<KeyRelease>", self.calcular_vueltas)

        self.lbl_vueltas = ctk.CTkLabel(panel_der, text="VUELTAS: $0", font=ctk.CTkFont(size=28, weight="bold"), text_color="#E76F51")
        self.lbl_vueltas.grid(row=4, column=0, pady=10)

        self.btn_cobrar = ctk.CTkButton(panel_der, text="COBRAR E IMPRIMIR", height=60, font=ctk.CTkFont(weight="bold"), command=self.procesar_venta)
        self.btn_cobrar.grid(row=5, column=0, sticky="ew", padx=20, pady=20)

        return frame

    def filtrar_productos_venta(self, event=None):
        termino = self.ent_buscador.get().strip().upper()
        for item in self.tabla_busqueda.get_children(): self.tabla_busqueda.delete(item)
        conexion = base_datos.obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_producto, nombre, precio_sugerido, unidad_medida, stock_actual FROM productos WHERE nombre LIKE ?", (f'%{termino}%',))
        for fila in cursor.fetchall():
            self.tabla_busqueda.insert("", "end", values=(fila[0], fila[1], fila[2], fila[3], round(fila[4], 2)))
        conexion.close()

    def agregar_al_carrito(self, event):
        seleccion = self.tabla_busqueda.selection()
        if not seleccion: return
        item = self.tabla_busqueda.item(seleccion[0])
        id_prod, nombre, precio, unidad, stock = item['values']
        stock_total = float(stock)
        
        cantidad_en_carrito = sum(item["cantidad"] for item in self.carrito if str(item["id_producto"]) == str(id_prod))
        stock_disponible = stock_total - cantidad_en_carrito

        if stock_disponible <= 0:
            return messagebox.showwarning("Agotado", f"No hay stock disponible de {nombre}.")
        
        cantidad = simpledialog.askfloat("Cantidad", f"Stock disponible: {stock_disponible} {unidad}\nIngrese cantidad:", parent=self, minvalue=0.01)
        if cantidad:
            if cantidad > stock_disponible:
                return messagebox.showerror("Error", f"Solo puedes vender hasta {stock_disponible}.")
            subtotal = float(precio) * cantidad
            self.carrito.append({"id_producto": id_prod, "nombre": nombre, "cantidad": cantidad, "precio_unitario": precio, "subtotal": subtotal})
            self.tabla_carrito.insert("", "end", values=(nombre, f"{cantidad} {unidad}", f"${subtotal:,.0f}"))
            self.actualizar_total()

    def actualizar_total(self):
        self.total_venta = sum(item["subtotal"] for item in self.carrito)
        self.lbl_total.configure(text=f"TOTAL: ${self.total_venta:,.0f}")
        self.calcular_vueltas()

    def calcular_vueltas(self, event=None):
        try:
            recibido = float(self.ent_recibido.get())
            vueltas = recibido - self.total_venta
            self.lbl_vueltas.configure(text=f"VUELTAS: ${vueltas:,.0f}" if vueltas >= 0 else "Falta dinero")
        except ValueError:
            self.lbl_vueltas.configure(text="VUELTAS: $0")

    def procesar_venta(self):
        if not self.carrito: return
        try:
            recibido = float(self.ent_recibido.get())
            vueltas = recibido - self.total_venta
            if vueltas < 0: return messagebox.showerror("Error", "Dinero insuficiente.")
        except: return messagebox.showerror("Error", "Ingrese valor válido.")

        conexion = base_datos.obtener_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("INSERT INTO ventas (total_venta, valor_recibido, vueltas) VALUES (?, ?, ?)", (self.total_venta, recibido, vueltas))
            numero_factura = cursor.lastrowid
            for item in self.carrito:
                cursor.execute("INSERT INTO detalle_venta (numero_factura, id_producto, cantidad_o_peso, subtotal) VALUES (?, ?, ?, ?)",
                               (numero_factura, item["id_producto"], item["cantidad"], item["subtotal"]))
                cursor.execute("UPDATE productos SET stock_actual = stock_actual - ? WHERE id_producto = ?", (item["cantidad"], item["id_producto"]))
            conexion.commit()
            impresion.generar_y_imprimir_factura(numero_factura, self.carrito, self.total_venta, recibido, vueltas)
            messagebox.showinfo("Éxito", f"Factura #{numero_factura} impresa.")
            
            self.carrito.clear()
            for item in self.tabla_carrito.get_children(): self.tabla_carrito.delete(item)
            self.total_venta = 0.0
            self.actualizar_total()
            self.ent_recibido.delete(0, 'end')
            self.filtrar_productos_venta()
        finally:
            conexion.close()

    # ==========================================
    # 3. CIERRE DE CAJA Y RESPALDOS
    # ==========================================
    def exportar_copia_seguridad(self):
        backup.realizar_backup_manual(base_datos.DB_NAME)

    def crear_vista_reportes(self):
        frame = ctk.CTkFrame(self.frame_principal, fg_color="transparent")
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text="Cierre de Caja y Respaldos", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, pady=(0, 10), sticky="w")
        
        panel_metricas = ctk.CTkFrame(frame)
        panel_metricas.grid(row=1, column=0, sticky="ew", pady=10)
        panel_metricas.grid_columnconfigure((0, 1), weight=1)
        
        self.lbl_total_cierre = ctk.CTkLabel(panel_metricas, text="Total Ingresos: $0", font=ctk.CTkFont(size=28, weight="bold"), text_color="#2A9D8F")
        self.lbl_total_cierre.grid(row=0, column=0, pady=20)
        
        self.lbl_cantidad_facturas = ctk.CTkLabel(panel_metricas, text="Facturas Emitidas: 0", font=ctk.CTkFont(size=24, weight="bold"))
        self.lbl_cantidad_facturas.grid(row=0, column=1, pady=20)

        ctk.CTkLabel(frame, text="Detalle de Facturas de Hoy", font=ctk.CTkFont(size=16)).grid(row=2, column=0, sticky="w", pady=(10, 5))
        
        cols_cierre = ("No. Factura", "Hora de Venta", "Total")
        self.tabla_cierre = ttk.Treeview(frame, columns=cols_cierre, show="headings")
        for col in cols_cierre: self.tabla_cierre.heading(col, text=col)
        self.tabla_cierre.column("No. Factura", width=100, anchor="center")
        self.tabla_cierre.column("Hora de Venta", width=250, anchor="center")
        self.tabla_cierre.column("Total", width=150, anchor="e")
        self.tabla_cierre.grid(row=3, column=0, sticky="nsew")

        # BOTONES DE ACCIÓN (Imprimir, Excel y Copia de Seguridad)
        frame_botones = ctk.CTkFrame(frame, fg_color="transparent")
        frame_botones.grid(row=4, column=0, pady=20)

        btn_imprimir_cierre = ctk.CTkButton(frame_botones, text="IMPRIMIR CORTE Z (PDF)", height=50, font=ctk.CTkFont(weight="bold"), command=self.imprimir_cierre)
        btn_imprimir_cierre.grid(row=0, column=0, padx=5)

        btn_exportar_cierre = ctk.CTkButton(frame_botones, text="EXPORTAR A EXCEL", height=50, font=ctk.CTkFont(weight="bold"), fg_color="#217346", hover_color="#1e6b40", command=self.exportar_cierre_excel)
        btn_exportar_cierre.grid(row=0, column=1, padx=5)

        # NUEVO BOTÓN PARA COPIA DE SEGURIDAD MANUAL
        btn_backup = ctk.CTkButton(frame_botones, text="CREAR COPIA DE SEGURIDAD", height=50, font=ctk.CTkFont(weight="bold"), fg_color="#457B9D", hover_color="#1D3557", command=self.exportar_copia_seguridad)
        btn_backup.grid(row=0, column=2, padx=5)

        return frame

    def cargar_datos_cierre(self):
        for item in self.tabla_cierre.get_children(): self.tabla_cierre.delete(item)
        conexion = base_datos.obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT numero_factura, datetime(fecha_venta, 'localtime'), total_venta FROM ventas WHERE date(fecha_venta, 'localtime') = date('now', 'localtime')")
        ventas_hoy = cursor.fetchall()
        conexion.close()
        
        total_dia = 0
        for fila in ventas_hoy:
            self.tabla_cierre.insert("", "end", values=(fila[0], fila[1], f"${fila[2]:,.0f}"))
            total_dia += fila[2]
            
        self.total_dia_actual = total_dia
        self.cantidad_facturas_actual = len(ventas_hoy)
        self.lbl_total_cierre.configure(text=f"Total Ingresos: ${total_dia:,.0f}")
        self.lbl_cantidad_facturas.configure(text=f"Facturas Emitidas: {self.cantidad_facturas_actual}")

    def imprimir_cierre(self):
        if self.cantidad_facturas_actual == 0: return messagebox.showinfo("Aviso", "No hay ventas hoy.")
        fecha_cierre = datetime.now().strftime('%d/%m/%Y')
        impresion.generar_imprimir_cierre(self.total_dia_actual, self.cantidad_facturas_actual, fecha_cierre)
        messagebox.showinfo("Cierre Exitoso", "Reporte enviado a la impresora.")

    def exportar_cierre_excel(self):
        if self.cantidad_facturas_actual == 0:
            return messagebox.showinfo("Aviso", "No hay ventas para exportar hoy.")
        fecha_str = datetime.now().strftime('%d-%m-%Y')
        ruta_guardado = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Archivos de Excel", "*.xlsx")], title="Guardar Cierre", initialfile=f"Ventas_Dia_{fecha_str}.xlsx")
        if ruta_guardado:
            exportar_excel.exportar_ventas_dia(base_datos.DB_NAME, ruta_guardado)

if __name__ == "__main__":
    # Esto garantiza que al abrir el .exe en un PC nuevo, se creen las tablas automáticamente
    base_datos.inicializar_base_datos() 
    app = SalsamentariaApp()
    app.mainloop()