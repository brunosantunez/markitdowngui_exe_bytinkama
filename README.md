# MarkItDown GUI · By Tinkama

Aplicación de escritorio para Windows que convierte documentos a Markdown (`.md`) o texto plano (`.txt`) con el motor MarkItDown de Microsoft.

## Instalar dependencias

```powershell
python -m pip install -r requirements.txt
```

## Generar el ejecutable

Desde la carpeta del proyecto:

```powershell
python -m PyInstaller --noconfirm --clean --onefile --windowed --name markitdowngui --distpath . --workpath build --icon="icon.ico" --add-data "icon.ico;." --add-data "icon.png;." --collect-all customtkinter --collect-all magika --collect-all markitdown markitdown_by_tinkama.py
```

El archivo resultante será `markitdowngui.exe` en la carpeta principal. El icono se empaqueta dentro del ejecutable.

También se puede compilar con el archivo de configuración para escribir el ejecutable en la carpeta principal:

```powershell
python -m PyInstaller --noconfirm --clean --distpath . --workpath build app.spec
```

## Funciones

- Conversión local a Markdown o texto plano, con selección de ubicación mediante «Guardar como».
- Adjuntar archivos con el explorador de Windows.
- Indicador de progreso sin bloquear la interfaz.
- Aviso para archivos mayores de 50 MB y límite preventivo de 800 páginas para PDFs locales.
- Acceso al conversor online para archivos pesados.
