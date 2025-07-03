import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import glob

# --- Selección de archivo o carpeta ---
def seleccionar_zip_o_carpeta():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Selección", "Selecciona un archivo .zip de Takeout o una carpeta 'Takeout'.")
    file_path = filedialog.askopenfilename(title="Selecciona un archivo .zip de Takeout", filetypes=[("Archivos ZIP", "takeout-*.zip")])
    if file_path:
        return file_path, 'zip'
    dir_path = filedialog.askdirectory(title="O selecciona la carpeta 'Takeout'")
    if dir_path:
        return dir_path, 'carpeta'
    return None, None

# --- Descomprimir ZIP (incluyendo multipartes) ---
def descomprimir_zip(zip_path, destino):
    # Si es multipartes, buscar todos los takeout-*.zip en el mismo directorio
    base = os.path.basename(zip_path)
    dir_ = os.path.dirname(zip_path)
    prefix = base.split(".zip")[0]
    partes = sorted(glob.glob(os.path.join(dir_, prefix + "*.zip")))
    if len(partes) > 1:
        # Unir los zips en uno temporal
        temp_zip = os.path.join(dir_, "_takeout_temp.zip")
        with open(temp_zip, "wb") as wfd:
            for p in partes:
                with open(p, "rb") as fd:
                    shutil.copyfileobj(fd, wfd)
        zip_path = temp_zip
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(destino)
    if os.path.exists(os.path.join(dir_, "_takeout_temp.zip")):
        os.remove(os.path.join(dir_, "_takeout_temp.zip"))

# --- Buscar carpeta de fotos ---
def buscar_carpeta_fotos(takeout_dir):
    for nombre in os.listdir(takeout_dir):
        if nombre.lower().startswith("google fot") or nombre.lower().startswith("google pho"):
            return os.path.join(takeout_dir, nombre)
    return None

# --- Asociación de archivos multimedia y metadatos ---
def asociar_archivos_y_metadatos(carpeta_fotos):
    archivos = []
    for root, dirs, files in os.walk(carpeta_fotos):
        for f in files:
            if not f.lower().endswith('.json'):
                archivos.append(os.path.join(root, f))

    print(f"Se encontraron {len(archivos)} archivos multimedia.")
    archivos_con_metadata = {}
    for archivo in archivos:
        # 1. Buscar metadata con el mismo nombre + .json
        metadata_file = archivo + '.json'
        if os.path.isfile(metadata_file):
            archivos_con_metadata[archivo] = metadata_file
            continue
        # 2. Buscar metadata cambiando la extensión a .json
        base, _ = os.path.splitext(archivo)
        metadata_file2 = base + '.json'
        if os.path.isfile(metadata_file2):
            archivos_con_metadata[archivo] = metadata_file2
            continue
        # 3. Caso especial: foo(1).jpg <-> foo.jpg(1).json
        import re
        filename, extension = os.path.splitext(archivo)
        parts = re.split(r'(\(\d+\))$', filename, maxsplit=1)
        if len(parts) == 3:
            metadata_file3 = f'{parts[0]}{extension}{parts[1]}.json'
            if os.path.isfile(metadata_file3):
                archivos_con_metadata[archivo] = metadata_file3
                continue
        # 4. Buscar metadata supplemental-metadata
        metadata_file4 = archivo + '.supplemental-metadata.json'
        if os.path.isfile(metadata_file4):
            archivos_con_metadata[archivo] = metadata_file4
            continue
        # 5. Buscar metadata supplemental-metad.json (caso álbumes)
        metadata_file5 = archivo + '.supplemental-metad.json'
        if os.path.isfile(metadata_file5):
            archivos_con_metadata[archivo] = metadata_file5
            continue
        archivos_con_metadata[archivo] = None

    print(f"Asociación de archivos y metadatos completada. Ejemplo:")
    for i, (k, v) in enumerate(archivos_con_metadata.items()):
        print(f"{os.path.basename(k)} -> {os.path.basename(v) if v else 'Sin metadata'}")
        if i > 10:
            break
    return archivos_con_metadata

# --- Main ---
def main():
    seleccion, tipo = seleccionar_zip_o_carpeta()
    if not seleccion:
        print("No se seleccionó nada. Saliendo.")
        return
    if tipo == 'zip':
        destino = os.path.join(os.path.dirname(seleccion), "Takeout")
        descomprimir_zip(seleccion, os.path.dirname(seleccion))
        takeout_dir = destino
    else:
        takeout_dir = seleccion
    if not os.path.exists(takeout_dir):
        print(f"No se encontró la carpeta Takeout en {takeout_dir}")
        return
    carpeta_fotos = buscar_carpeta_fotos(takeout_dir)
    if not carpeta_fotos:
        print(f"No se encontró la carpeta de fotos dentro de {takeout_dir}")
        return
    print(f"Carpeta de fotos encontrada: {carpeta_fotos}")
    archivos_con_metadata = asociar_archivos_y_metadatos(carpeta_fotos)
    
    for archivo, metadata in archivos_con_metadata.items():
        if metadata:
            # Aquí iría tu lógica para procesar la metadata y agregarla a la foto/video
            # Por ejemplo: escribir EXIF, copiar, renombrar, etc.
            # Una vez procesado, borra el archivo de metadatos:
            try:
                os.remove(metadata)
                print(f"Borrado metadatos: {os.path.basename(metadata)}")
            except Exception as e:
                print(f"No se pudo borrar {metadata}: {e}")

if __name__ == "__main__":
    main()
