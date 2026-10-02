# MarkItDown GUI · by Tinkama

Aplicación de escritorio para Windows que convierte documentos a Markdown (`.md`) o texto plano (`.txt`) con el motor MarkItDown de Microsoft. Su principal función es para ahorrar tokens en su ia preferida.

# Modo de uso
Puedes descargar directamente el archivo `markitdowngui.exe` que está en funcionamiento directo sin necesidad de realizar los pasos para generar el ejecutable. No es necesario ejecutar como administrador. Funciona como una GUI para usuarios no experimentados.
## Disclaimer
Microsoft Defender SmartScreen puede advertir sobre este ejecutable porque es una compilación reciente, sin firma digital, el mismo archivo generado existe en el repositorio `markitdown_by_tinkama.py` por si desean comprobarlo.
`SHA-256`: 778CB20F662FEBC5D0BFC1F645E41DCB45C6F9D6A73E0B3E5990AF0668A686D2

# Pasos para generar el ejecutable
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
- Indicador de progreso.
- Aviso para archivos mayores de 5 MB, confirmación adicional sobre 50 MB y límite preventivo de +800 páginas para PDFs locales.
- Aviso cuando MarkItDown no extrae contenido, sin guardar un archivo vacío.
- Acceso al conversor online para archivos pesados.
- Su principal función es ahorrar tokens en su IA preferida.

## Contributing
Es un complemento totalmente atribuido y basado en la herramienta de MarkItDown de Microsoft https://github.com/microsoft/markitdown 

# MarkItDown GUI · by Tinkama

A Windows desktop application that converts documents to Markdown (`.md`) or plain text (`.txt`) using Microsoft's MarkItDown engine. Its main function is to save tokens on your preferred AI.

# Usage
You can directly download the `markitdowngui.exe` file, which is ready to run without needing to perform the steps to generate the executable yourself. Running as administrator is not required. It serves as a GUI for non-technical users.
## Disclaimer
Microsoft Defender SmartScreen may flag this executable because it is a recent, unsigned build; the same generated file exists in the `markitdown_by_tinkama.py` repository, should you wish to verify it.
`SHA-256`: 778CB20F662FEBC5D0BFC1F645E41DCB45C6F9D6A73E0B3E5990AF0668A686D2

# Steps to generate the executable
## Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## Generate the executable

From the project folder:

```powershell
python -m PyInstaller --noconfirm --clean --onefile --windowed --name markitdowngui --distpath . --workpath build --icon="icon.ico" --add-data "icon.ico;." --add-data "icon.png;." --collect-all customtkinter --collect-all magika --collect-all markitdown markitdown_by_tinkama.py
```

The resulting file will be `markitdowngui.exe` in the main folder. The icon is bundled inside the executable.

You can also compile using the configuration file to output the executable to the main folder:

```powershell
python -m PyInstaller --noconfirm --clean --distpath . --workpath build app.spec
```

## Features

- Local conversion to Markdown or plain text, with location selection via "Save As".
- File attachment using Windows Explorer.
- Progress indicator that does not block the interface.
- Warning for files larger than 5 MB, additional confirmation for files over 50 MB, and a preventive limit of +800 pages for local PDFs.
- Notification when MarkItDown fails to extract content, without saving an empty file.
- Access to the online converter for large files. 
- Main function is to save tokens on your preferred AI.

## Contributing
This is a plugin fully based on—and attributed to—Microsoft's MarkItDown tool (https://github.com/microsoft/markitdown).