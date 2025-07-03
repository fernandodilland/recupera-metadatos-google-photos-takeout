# Recupera Metadatos desde respaldo de Google Fotos usando Google Takeout

Este script te ayuda a asociar y procesar los archivos multimedia (fotos y videos) exportados desde Google Fotos mediante Google Takeout, recuperando sus metadatos originales desde los archivos `.json` generados por Google.

## ¿Qué hace este programa?
- Permite seleccionar un archivo `.zip` de Google Takeout (o varios, si está dividido en partes) **o** una carpeta `Takeout` ya descomprimida.
- Descomprime automáticamente los archivos `.zip` si es necesario.
- Busca la carpeta de fotos dentro de `Takeout` (puede llamarse `Google Fotos` o `Google Photos`).
- Recorre todas las subcarpetas (álbumes incluidos) y asocia cada archivo multimedia con su archivo de metadatos `.json` correspondiente, aunque el nombre esté truncado o modificado.
- Valida que el `.json` realmente contenga metadatos de Google Takeout.
- (Opcional) Puedes agregar tu lógica para escribir los metadatos en la foto/video y el script eliminará el `.json` tras procesarlo.

## Ejemplo de archivos soportados

```
Takeout/
└── Google Fotos/
    ├── IMG_20250627_225251_820.jpg
    ├── IMG_20250627_225251_820.jpg.supplemental-metadata.json
    ├── Screenshot_2025-06-26-22-27-29-757_com.instagra.jpg
    ├── Screenshot_2025-06-26-22-27-29-757_com.instagr.json
    └── AlbumVacaciones/
        ├── IMG_1234.JPG
        ├── IMG_1234.JPG.supplemental-metad.json
        └── ...
```

## ¿Cómo usarlo?
1. Ejecuta el script con Python 3:
   ```
   python main.py
   ```
2. Selecciona el archivo `.zip` de Takeout (por ejemplo, `takeout-2025-07-03.zip`) **o** la carpeta `Takeout` ya descomprimida.
3. El script buscará automáticamente la carpeta de fotos y asociará cada archivo multimedia con su metadato `.json`.
4. Verás en consola el progreso y un resumen de la asociación.
5. (Opcional) Puedes modificar el script para procesar los metadatos y luego se eliminarán los `.json` usados.

## Notas
- El script funciona en Windows y usa una ventana gráfica para seleccionar archivos/carpetas.
- Soporta archivos `.zip` divididos en varias partes (`takeout-2025-07-03.zip`, `takeout-2025-07-03(1).zip`, etc.).
- Asocia metadatos aunque el nombre esté truncado, cortado o tenga sufijos especiales.
- Si tienes dudas o necesitas adaptar el procesamiento de metadatos, puedes modificar la función `asociar_archivos_y_metadatos`.

---

**Ejemplo de asociación:**

- `IMG_20250627_225251_820.jpg` → `IMG_20250627_225251_820.jpg.supplemental-metadata.json`
- `Screenshot_2025-06-26-22-27-29-757_com.instagra.jpg` → `Screenshot_2025-06-26-22-27-29-757_com.instagr.json`
- `AlbumVacaciones/IMG_1234.JPG` → `AlbumVacaciones/IMG_1234.JPG.supplemental-metad.json`
- `foto_sin_metadata.jpg` → Sin metadata

---

¡Listo para recuperar tus recuerdos con sus metadatos originales!