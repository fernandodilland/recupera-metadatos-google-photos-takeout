import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import glob
import json

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
    base = os.path.basename(zip_path)
    dir_ = os.path.dirname(zip_path)
    prefix = base.split(".zip")[0]
    partes = sorted(glob.glob(os.path.join(dir_, prefix + "*.zip")))
    if len(partes) > 1:
        print(f"Descomprimiendo varias partes: {', '.join([os.path.basename(p) for p in partes])}")
        temp_zip = os.path.join(dir_, "_takeout_temp.zip")
        with open(temp_zip, "wb") as wfd:
            for p in partes:
                with open(p, "rb") as fd:
                    shutil.copyfileobj(fd, wfd)
        zip_path = temp_zip
    else:
        print(f"Descomprimiendo: {base}")
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
    # Indexar los .json por carpeta para acelerar la búsqueda
    jsons_por_carpeta = {}
    for root, dirs, files in os.walk(carpeta_fotos):
        jsons_por_carpeta[root] = [f for f in files if f.lower().endswith('.json')]

    for idx, archivo in enumerate(archivos):
        if idx % 100 == 0:
            print(f"Procesando archivo {idx+1} de {len(archivos)}...")
        carpeta = os.path.dirname(archivo)
        base_nombre = os.path.splitext(os.path.basename(archivo))[0]
        # Buscar todos los .json en la carpeta que empiecen igual (truncados o no)
        candidatos = [f for f in jsons_por_carpeta.get(carpeta, []) if f.startswith(base_nombre[:30])]
        metadatas = []
        for candidato in candidatos:
            ruta_json = os.path.join(carpeta, candidato)
            try:
                with open(ruta_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Validar que sea metadata de Google Takeout
                if any(k in data for k in ['photoTakenTime', 'creationTime', 'title', 'creation_time', 'creationTimestamp']):
                    metadatas.append(ruta_json)
            except Exception:
                continue
        # También buscar los patrones fijos por si acaso
        patrones = [
            archivo + '.json',
            os.path.splitext(archivo)[0] + '.json',
            # Caso especial: foo(1).jpg <-> foo.jpg(1).json
            None,
            archivo + '.supplemental-metadata.json',
            archivo + '.supplement-metad.json',
            archivo + '.supplement.json'
        ]
        import re
        filename, extension = os.path.splitext(archivo)
        parts = re.split(r'(\(\d+\))$', filename, maxsplit=1)
        if len(parts) == 3:
            patrones[2] = f'{parts[0]}{extension}{parts[1]}.json'
        for p in patrones:
            if p and os.path.isfile(p) and p not in metadatas:
                try:
                    with open(p, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if any(k in data for k in ['photoTakenTime', 'creationTime', 'title', 'creation_time', 'creationTimestamp']):
                        metadatas.append(p)
                except Exception:
                    continue
        archivos_con_metadata[archivo] = metadatas if metadatas else None

    print(f"Asociación de archivos y metadatos completada. Ejemplo:")
    for i, (k, v) in enumerate(archivos_con_metadata.items()):
        if v:
            print(f"{os.path.basename(k)} -> {[os.path.basename(x) for x in v]}")
        else:
            print(f"{os.path.basename(k)} -> Sin metadata")
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
    
    archivos_borrados = set()
    for archivo, metadatas in archivos_con_metadata.items():
        if metadatas:
            for metadata in metadatas:
                # Aquí iría tu lógica para procesar la metadata y agregarla a la foto/video
                # Por ejemplo: escribir EXIF, copiar, renombrar, etc.
                # Una vez procesado, borra el archivo de metadatos solo si no se ha borrado antes:
                if metadata not in archivos_borrados:
                    try:
                        os.remove(metadata)
                        archivos_borrados.add(metadata)
                        print(f"Borrado metadatos: {os.path.basename(metadata)}")
                    except Exception as e:
                        print(f"No se pudo borrar {metadata}: {e}")

if __name__ == "__main__":
    main()
