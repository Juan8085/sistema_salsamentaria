import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from datetime import datetime

# Tamaño Media Carta (140 mm ancho x 216 mm alto aprox)
MEDIA_CARTA = (140 * mm, 216 * mm)

def generar_y_imprimir_factura(numero_factura, carrito, total, recibido, vueltas):
    # Crear la carpeta de facturas si no existe
    if not os.path.exists("facturas_pdf"):
        os.makedirs("facturas_pdf")

    # Ruta del archivo
    ruta_pdf = os.path.abspath(f"facturas_pdf/factura_{numero_factura}.pdf")
    
    # Iniciar el "lienzo" del PDF
    c = canvas.Canvas(ruta_pdf, pagesize=MEDIA_CARTA)
    ancho, alto = MEDIA_CARTA
    
    # ==========================
    # ENCABEZADO DE LA FACTURA
    # ==========================
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(ancho / 2, alto - 20 * mm, "SALSAMENTARIA")
    
    c.setFont("Helvetica", 10)
    c.drawCentredString(ancho / 2, alto - 26 * mm, "Régimen No Responsable de IVA") # Término legal para pequeñas empresas en Colombia
    c.drawCentredString(ancho / 2, alto - 32 * mm, f"Fecha: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(ancho / 2, alto - 40 * mm, f"Factura de Venta No. {numero_factura}")
    
    # Línea separadora
    c.line(10 * mm, alto - 45 * mm, ancho - 10 * mm, alto - 45 * mm)
    
    # ==========================
    # CABECERAS DE PRODUCTOS
    # ==========================
    c.setFont("Helvetica-Bold", 10)
    y = alto - 52 * mm
    c.drawString(10 * mm, y, "Cant.")
    c.drawString(30 * mm, y, "Producto")
    c.drawRightString(ancho - 10 * mm, y, "Subtotal")
    
    c.line(10 * mm, y - 3 * mm, ancho - 10 * mm, y - 3 * mm)
    
    # ==========================
    # DETALLE DE PRODUCTOS
    # ==========================
    c.setFont("Helvetica", 10)
    y -= 10 * mm
    for item in carrito:
        c.drawString(10 * mm, y, f"{item['cantidad']}")
        
        # Acortamos el nombre si es muy largo para que no se superponga
        nombre_prod = item['nombre'][:25]
        c.drawString(30 * mm, y, nombre_prod)
        
        c.drawRightString(ancho - 10 * mm, y, f"${item['subtotal']:,.0f}")
        y -= 6 * mm  # Bajar a la siguiente línea
        
        # Si la factura es muy larga, crear nueva página (prevención)
        if y < 40 * mm:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = alto - 20 * mm
    
    c.line(10 * mm, y, ancho - 10 * mm, y)
    
    # ==========================
    # TOTALES
    # ==========================
    y -= 8 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40 * mm, y, "TOTAL A PAGAR:")
    c.drawRightString(ancho - 10 * mm, y, f"${total:,.0f}")
    
    y -= 6 * mm
    c.setFont("Helvetica", 10)
    c.drawString(40 * mm, y, "Efectivo Recibido:")
    c.drawRightString(ancho - 10 * mm, y, f"${recibido:,.0f}")
    
    y -= 6 * mm
    c.drawString(40 * mm, y, "Cambio (Vueltas):")
    c.drawRightString(ancho - 10 * mm, y, f"${vueltas:,.0f}")
    
    # ==========================
    # PIE DE PÁGINA
    # ==========================
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(ancho / 2, 15 * mm, "¡Gracias por su compra, vuelva pronto!")
    
    # Guardar el PDF
    c.save()
    
    # ==========================
    # IMPRESIÓN AUTOMÁTICA
    # ==========================
    try:
        # En Windows, esto envía el PDF a la impresora configurada por defecto
        os.startfile(ruta_pdf, "print")
    except Exception as e:
        print(f"Error al enviar a la impresora: {e}")