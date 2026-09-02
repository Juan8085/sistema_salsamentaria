import os
import shutil
from datetime import datetime
from tkinter import messagebox

CARPETA_BACKUP = "backups_salsamentaria"

def realizar_backup_automatico(ruta_db):
    """Crea una copia de la base de datos al abrir el sistema."""
    if not os.path.exists(ruta_db):
        return

    if not os.path.exists(CARPETA_BACKUP):
        os.makedirs(CARPETA_BACKUP)

    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    nombre_backup = f"backup_{fecha_hoy}.db"
    ruta_destino = os.path.join(CARPETA_BACKUP, nombre_backup)

    # Si ya se hizo un backup hoy, no duplicar
    if not os.path.exists(ruta_destino):
        try:
            shutil.copy(ruta_db, ruta_destino)
            print(f"Backup automático creado: {nombre_backup}")
            _limpiar_backups_antiguos(dias_retencion=15) # Mantiene solo los últimos 15 días
        except Exception as e:
            print(f"Error al crear backup automático: {e}")

def realizar_backup_manual(ruta_db):
    """Permite guardar una copia en una ubicación elegida por el usuario (ej: USB)."""
    if not os.path.exists(ruta_db):
        messagebox.showerror("Error", "No se encontró la base de datos.")
        return

    from tkinter import filedialog
    fecha_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
    ruta_destino = filedialog.asksaveasfilename(
        defaultextension=".db",
        filetypes=[("Base de datos SQLite", "*.db")],
        title="Guardar Copia de Seguridad",
        initialfile=f"copia_seguridad_salsamentaria_{fecha_str}.db"
    )

    if ruta_destino:
        try:
            shutil.copy(ruta_db, ruta_destino)
            messagebox.showinfo("Éxito", "Copia de seguridad guardada correctamente en la ubicación seleccionada.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la copia: {e}")

def _limpiar_backups_antiguos(dias_retencion=15):
    """Elimina respaldos automáticos con más de X días para ahorrar espacio."""
    try:
        ahora = datetime.now().timestamp()
        limite_segundos = dias_retencion * 24 * 60 * 60
        for archivo in os.listdir(CARPETA_BACKUP):
            ruta_archivo = os.path.join(CARPETA_BACKUP, archivo)
            if os.path.isfile(ruta_archivo) and archivo.startswith("backup_"):
                tiempo_archivo = os.path.getmtime(ruta_archivo)
                if (ahora - tiempo_archivo) > limite_segundos:
                    os.remove(ruta_archivo)
    except Exception as e:
        print(f"Error limpiando backups antiguos: {e}")