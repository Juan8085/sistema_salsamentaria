import sqlite3
import os

DB_NAME = "salsamentaria.db"

def obtener_conexion():
    """Retorna una conexión a la base de datos SQLite."""
    conexion = sqlite3.connect(DB_NAME)
    conexion.execute("PRAGMA foreign_keys = ON;") # Activa la integridad referencial
    return conexion

def inicializar_base_datos():
    """Crea las tablas necesarias si no existen."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # 1. Tabla de Productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            unidad_medida TEXT NOT NULL,
            costo_actual REAL NOT NULL DEFAULT 0.0,
            precio_sugerido REAL NOT NULL DEFAULT 0.0,
            stock_actual REAL NOT NULL DEFAULT 0.0
        )
    """)

    # 2. Tabla de Compras (Ingreso de inventario)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compras (
            id_compra INTEGER PRIMARY KEY AUTOINCREMENT,
            id_producto INTEGER NOT NULL,
            cantidad_comprada REAL NOT NULL,
            costo_total_compra REAL NOT NULL,
            fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
        )
    """)

    # 3. Tabla de Ventas (Cabecera de Factura)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            numero_factura INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_venta REAL NOT NULL,
            valor_recibido REAL NOT NULL,
            vueltas REAL NOT NULL
        )
    """)

    # 4. Tabla de Detalle de Ventas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_venta (
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_factura INTEGER NOT NULL,
            id_producto INTEGER NOT NULL,
            cantidad_o_peso REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (numero_factura) REFERENCES ventas(numero_factura),
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
        )
    """)

    conexion.commit()
    conexion.close()
    print("Base de datos inicializada correctamente.")

if __name__ == "__main__":
    inicializar_base_datos()