import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
import base_datos

# Configuración visual de la ventana
ctk.set_appearance_mode("Light")  # Se puede cambiar a "Dark"
ctk.set_default_color_theme("blue")

class SalsamentariaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Gestión - Salsamentaria")
        self.geometry("1100x700")
        self.minsize(900, 600)

        # Configurar grid principal (1 fila, 2 columnas)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- PANEL LATERAL (MENÚ) ---
        self.frame_menu = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.frame_menu.grid(row=0, column=0, sticky="nsew")
        self.frame_menu.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.frame_menu, text="SALSAMENTARIA", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        self.btn_ventas = ctk.CTkButton(self.frame_menu, text="Punto de Venta", height=40, command=self.mostrar_ventas)
        self.btn_ventas.grid(row=1, column=0, padx=20, pady=10)

        self.btn_inventario = ctk.CTkButton(self.frame_menu, text="Inventario / Compras", height=40, command=self.mostrar_inventario)
        self.btn_inventario.grid(row=2, column=0, padx=20, pady=10)

        # --- ÁREA DE TRABAJO ---
        self.frame_principal = ctk.CTkFrame(self, corner_radius=10)
        self.frame_principal.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.frame_principal.grid_rowconfigure(0, weight=1)
        self.frame_principal.grid_columnconfigure(0, weight=1)

        # Inicializar vistas
        self.vista_inventario = self.crear_vista_inventario()
        self.vista_ventas = self.crear_vista_ventas()
        
        # Mostrar inventario por defecto para poder crear productos
        self.mostrar_inventario()

    # ==========================================
    # LÓGICA DE CAMBIO DE PANTALLAS
    # ==========================================
    def mostrar_inventario(self):
        self.vista_ventas.grid_forget()
        self.vista_inventario.grid(row=0, column=0, sticky="nsew")
        self.cargar_tabla_inventario()

    def mostrar_ventas(self):
        self.vista_inventario.grid_forget()
        self.vista_ventas.grid(row=0, column=0, sticky="nsew")

    # ==========================================
    # PANTALLA DE INVENTARIO / COMPRAS
    # ==========================================
    def crear_vista_inventario(self):
        frame = ctk.CTkFrame(self.frame_principal, fg_color="transparent")
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure((0, 1), weight=1)

        # -- SECCIÓN: CREAR PRODUCTO / INGRESAR COMPRA --
        lbl_titulo = ctk.CTkLabel(frame, text="Gestión de Inventario y Compras", font=ctk.CTkFont(size=24, weight="bold"))
        lbl_titulo.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        # Formulario de Ingreso
        form_frame = ctk.CTkFrame(frame)
        form_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))

        # Fila 1 del formulario
        ctk.CTkLabel(form_frame, text="Nombre Producto:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.ent_nombre_prod = ctk.CTkEntry(form_frame, width=200)
        self.ent_nombre_prod.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(form_frame, text="Unidad:").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.cbx_unidad = ctk.CTkComboBox(form_frame, values=["Kg", "Gramos", "Libra", "Unidad"], width=100)
        self.cbx_unidad.grid(row=0, column=3, padx=10, pady=10)

        # Fila 2 del formulario (Datos de la compra)
        ctk.CTkLabel(form_frame, text="Cantidad comprada:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.ent_cantidad_compra = ctk.CTkEntry(form_frame, width=200)
        self.ent_cantidad_compra.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkLabel(form_frame, text="Costo TOTAL ($):").grid(row=1, column=2, padx=10, pady=10, sticky="w")
        self.ent_costo_total = ctk.CTkEntry(form_frame, width=150)
        self.ent_costo_total.grid(row=1, column=3, padx=10, pady=10)

        # Botón de guardado
        btn_guardar_compra = ctk.CTkButton(form_frame, text="Registrar Compra e Inventario", height=40, font=ctk.CTkFont(weight="bold"), command=self.guardar_compra)
        btn_guardar_compra.grid(row=2, column=0, columnspan=4, pady=20)

        # -- SECCIÓN: TABLA DE INVENTARIO ACTUAL --
        # Usamos ttk.Treeview para la tabla porque CTk no tiene tabla nativa
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", rowheight=30, font=('Arial', 11))
        style.configure("Treeview.Heading", font=('Arial', 12, 'bold'))

        columnas = ("ID", "Producto", "Unidad", "Stock", "Costo Unit.", "Precio Sugerido (+15%)")
        self.tabla_inventario = ttk.Treeview(frame, columns=columnas, show="headings")
        
        # Configurar cabeceras y anchos
        anchos = [40, 250, 80, 80, 100, 150]
        for col, ancho in zip(columnas, anchos):
            self.tabla_inventario.heading(col, text=col)
            self.tabla_inventario.column(col, width=ancho, anchor="center")

        self.tabla_inventario.grid(row=2, column=0, columnspan=2, sticky="nsew")

        return frame

    # ==========================================
    # LÓGICA DE BASE DE DATOS - INVENTARIO
    # ==========================================
    def guardar_compra(self):
        nombre = self.ent_nombre_prod.get().strip().upper()
        unidad = self.cbx_unidad.get()
        
        try:
            cantidad = float(self.ent_cantidad_compra.get())
            costo_total = float(self.ent_costo_total.get())
        except ValueError:
            messagebox.showerror("Error", "La cantidad y el costo deben ser números válidos.")
            return

        if not nombre or cantidad <= 0 or costo_total < 0:
            messagebox.showerror("Error", "Llene todos los campos correctamente.")
            return

        costo_unitario = costo_total / cantidad
        precio_sugerido = costo_unitario * 1.15 # Margen del 15%

        conexion = base_datos.obtener_conexion()
        cursor = conexion.cursor()

        try:
            # Verificar si el producto ya existe
            cursor.execute("SELECT id_producto, stock_actual FROM productos WHERE nombre = ?", (nombre,))
            producto = cursor.fetchone()

            if producto:
                # Actualizar producto existente (nuevo costo, nuevo precio, sumar stock)
                id_prod = producto[0]
                nuevo_stock = producto[1] + cantidad
                cursor.execute("""
                    UPDATE productos 
                    SET costo_actual = ?, precio_sugerido = ?, stock_actual = ? 
                    WHERE id_producto = ?
                """, (costo_unitario, precio_sugerido, nuevo_stock, id_prod))
            else:
                # Crear producto nuevo
                cursor.execute("""
                    INSERT INTO productos (nombre, unidad_medida, costo_actual, precio_sugerido, stock_actual)
                    VALUES (?, ?, ?, ?, ?)
                """, (nombre, unidad, costo_unitario, precio_sugerido, cantidad))
                id_prod = cursor.lastrowid

            # Registrar la transacción de compra
            cursor.execute("""
                INSERT INTO compras (id_producto, cantidad_comprada, costo_total_compra)
                VALUES (?, ?, ?)
            """, (id_prod, cantidad, costo_total))

            conexion.commit()
            messagebox.showinfo("Éxito", f"Compra registrada.\nCosto Unitario: ${costo_unitario:,.2f}\nPrecio Sugerido: ${precio_sugerido:,.2f}")
            
            # Limpiar campos
            self.ent_nombre_prod.delete(0, 'end')
            self.ent_cantidad_compra.delete(0, 'end')
            self.ent_costo_total.delete(0, 'end')
            
            self.cargar_tabla_inventario()

        except Exception as e:
            messagebox.showerror("Error BD", str(e))
        finally:
            conexion.close()

    def cargar_tabla_inventario(self):
        # Limpiar tabla
        for item in self.tabla_inventario.get_children():
            self.tabla_inventario.delete(item)

        conexion = base_datos.obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_producto, nombre, unidad_medida, stock_actual, costo_actual, precio_sugerido FROM productos")
        
        for fila in cursor.fetchall():
            # Formatear a moneda para que se vea claro
            fila_formateada = (
                fila[0], fila[1], fila[2], round(fila[3], 2), 
                f"${fila[4]:,.0f}", f"${fila[5]:,.0f}"
            )
            self.tabla_inventario.insert("", "end", values=fila_formateada)
            
        conexion.close()

    # ==========================================
    # PANTALLA DE VENTAS (MOCKUP PARA EL SIGUIENTE PASO)
    # ==========================================
    def crear_vista_ventas(self):
        frame = ctk.CTkFrame(self.frame_principal, fg_color="transparent")
        lbl_titulo = ctk.CTkLabel(frame, text="Punto de Venta (Próximo paso)", font=ctk.CTkFont(size=24, weight="bold"))
        lbl_titulo.pack(pady=50)
        return frame

if __name__ == "__main__":
    app = SalsamentariaApp()
    app.mainloop()