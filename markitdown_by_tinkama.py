import ctypes
import os
import queue
import sys
import threading
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from markitdown import MarkItDown
from PIL import Image
from pypdf import PdfReader


LIMITE_PESO_BYTES = 50 * 1024 * 1024
LIMITE_PAGINAS_PDF = 800
URL_CONVERSOR_ONLINE = "https://convertio.co/es/pdf-txt/"

COLOR_FONDO = "#0b1220"
COLOR_PANEL = "#111c2e"
COLOR_PANEL_SECUNDARIO = "#17243a"
COLOR_TEXTO = "#e8f0f7"
COLOR_TEXTO_SECUNDARIO = "#9aabc0"
COLOR_ACENTO = "#19c7b3"
COLOR_ACENTO_HOVER = "#13a895"


def ruta_recurso(nombre: str) -> str:
    """Devuelve la ruta de un recurso tanto en desarrollo como en PyInstaller."""
    carpeta_base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(carpeta_base, nombre)


class ConvertidorApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("MarkItDown · By Tinkama")
        self.geometry("1020x700")
        self.minsize(900, 640)
        self.configure(fg_color=COLOR_FONDO)

        self.archivo_seleccionado: str | None = None
        self.resultados_conversion: queue.Queue[tuple[str, str]] = queue.Queue()
        self.icono_ventana: ctk.CTkImage | None = None

        self._configurar_icono()
        self._configurar_id_aplicacion()
        self._crear_interfaz()

    def _configurar_icono(self) -> None:
        ruta_ico = ruta_recurso("icon.ico")
        ruta_png = ruta_recurso("icon.png")

        if os.path.exists(ruta_ico):
            self.iconbitmap(ruta_ico)

        if os.path.exists(ruta_png):
            with Image.open(ruta_png) as imagen:
                self.icono_ventana = ctk.CTkImage(
                    light_image=imagen.copy(),
                    dark_image=imagen.copy(),
                    size=(170, 170),
                )

    @staticmethod
    def _configurar_id_aplicacion() -> None:
        if os.name == "nt":
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "Tinkama.MarkItDown.Converter"
            )

    def _crear_interfaz(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._crear_barra_lateral()
        self._crear_panel_principal()

    def _crear_barra_lateral(self) -> None:
        barra = ctk.CTkFrame(self, width=270, corner_radius=0, fg_color=COLOR_PANEL)
        barra.grid(row=0, column=0, sticky="nsew")
        barra.grid_propagate(False)
        barra.grid_columnconfigure(0, weight=1)
        barra.grid_rowconfigure(3, weight=1)

        if self.icono_ventana:
            ctk.CTkLabel(barra, image=self.icono_ventana, text="").grid(
                row=0, column=0, padx=34, pady=(46, 12)
            )

        ctk.CTkLabel(
            barra,
            text="MARKITDOWN",
            font=ctk.CTkFont(family="Segoe UI", size=21, weight="bold"),
            text_color=COLOR_TEXTO,
        ).grid(row=1, column=0, padx=24, pady=(0, 4))
        ctk.CTkLabel(
            barra,
            text="CONVERTIDOR · TINKAMA",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=COLOR_ACENTO,
        ).grid(row=2, column=0, padx=24, pady=(0, 24))

        ctk.CTkFrame(barra, height=1, fg_color="#25344a").grid(
            row=3, column=0, sticky="new", padx=24, pady=(12, 0)
        )

        ctk.CTkLabel(
            barra,
            text="CONVERSIÓN LOCAL",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLOR_TEXTO_SECUNDARIO,
        ).grid(row=4, column=0, sticky="sw", padx=24, pady=(18, 8))
        ctk.CTkLabel(
            barra,
            text="Tus documentos se procesan en este equipo. Elige Markdown para conservar estructura o TXT para texto plano.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLOR_TEXTO_SECUNDARIO,
            wraplength=215,
            justify="left",
        ).grid(row=5, column=0, sticky="nw", padx=24, pady=(0, 20))

        self.btn_online = ctk.CTkButton(
            barra,
            text="Convertir Online ↗",
            command=self.abrir_convertio,
            height=42,
            corner_radius=10,
            fg_color=COLOR_PANEL_SECUNDARIO,
            hover_color="#243650",
            text_color=COLOR_TEXTO,
            border_width=1,
            border_color="#334862",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        )
        self.btn_online.grid(row=6, column=0, sticky="sew", padx=20, pady=(0, 22))

    def _crear_panel_principal(self) -> None:
        panel = ctk.CTkFrame(self, fg_color="transparent")
        panel.grid(row=0, column=1, sticky="nsew", padx=48, pady=38)
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel,
            text="Convierte tus documentos",
            font=ctk.CTkFont(family="Segoe UI", size=29, weight="bold"),
            text_color=COLOR_TEXTO,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", pady=(4, 6))
        ctk.CTkLabel(
            panel,
            text="Pasa PDF, Word, Excel, PowerPoint y más a un formato sencillo de reutilizar.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLOR_TEXTO_SECUNDARIO,
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", pady=(0, 26))

        self.zona_archivo = ctk.CTkFrame(
            panel,
            height=220,
            fg_color=COLOR_PANEL,
            corner_radius=18,
            border_width=1,
            border_color="#2c4059",
        )
        self.zona_archivo.grid(row=2, column=0, sticky="ew", pady=(0, 18))
        self.zona_archivo.grid_propagate(False)
        self.zona_archivo.grid_columnconfigure(0, weight=1)

        self.lbl_archivo = ctk.CTkLabel(
            self.zona_archivo,
            text="Selecciona el archivo que quieres convertir",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLOR_TEXTO,
        )
        self.lbl_archivo.grid(row=0, column=0, padx=20, pady=(38, 6))
        self.lbl_detalle_archivo = ctk.CTkLabel(
            self.zona_archivo,
            text="PDF, Word, Excel, PowerPoint y más",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLOR_TEXTO_SECUNDARIO,
        )
        self.lbl_detalle_archivo.grid(row=1, column=0, padx=20, pady=(0, 18))

        self.btn_adjuntar = ctk.CTkButton(
            self.zona_archivo,
            text="Adjuntar archivo",
            command=self.seleccionar_archivo,
            height=40,
            width=170,
            corner_radius=10,
            fg_color=COLOR_PANEL_SECUNDARIO,
            hover_color="#243650",
            text_color=COLOR_TEXTO,
            border_width=1,
            border_color="#334862",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        )
        self.btn_adjuntar.grid(row=2, column=0, pady=(0, 20))

        opciones = ctk.CTkFrame(panel, fg_color="transparent")
        opciones.grid(row=3, column=0, sticky="ew", pady=(2, 18))
        opciones.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            opciones,
            text="Formato de salida",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLOR_TEXTO_SECUNDARIO,
        ).grid(row=0, column=0, sticky="w", padx=(0, 14))

        self.combo_formato = ctk.CTkComboBox(
            opciones,
            values=[".md", ".txt"],
            width=115,
            height=38,
            corner_radius=9,
            fg_color=COLOR_PANEL,
            border_color="#334862",
            button_color=COLOR_PANEL_SECUNDARIO,
            button_hover_color="#243650",
            text_color=COLOR_TEXTO,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            state="readonly",
        )
        self.combo_formato.set(".md")
        self.combo_formato.grid(row=0, column=1, sticky="w")

        self.btn_convertir = ctk.CTkButton(
            panel,
            text="Convertir y guardar…",
            command=self.convertir_archivo,
            height=48,
            corner_radius=11,
            fg_color=COLOR_ACENTO,
            hover_color=COLOR_ACENTO_HOVER,
            text_color="#06201f",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
        )
        self.btn_convertir.grid(row=4, column=0, sticky="ew", pady=(2, 10))

        self.barra_progreso = ctk.CTkProgressBar(
            panel,
            mode="indeterminate",
            height=5,
            corner_radius=3,
            progress_color=COLOR_ACENTO,
            fg_color=COLOR_PANEL_SECUNDARIO,
        )
        self.lbl_estado = ctk.CTkLabel(
            panel,
            text="Listo para convertir",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLOR_TEXTO_SECUNDARIO,
        )
        self.lbl_estado.grid(row=5, column=0, sticky="w", pady=(4, 0))

    def seleccionar_archivo(self) -> None:
        ruta_archivo = filedialog.askopenfilename(
            title="Adjunta un archivo para convertir",
            filetypes=[("Todos los archivos", "*.*")],
        )
        if ruta_archivo:
            self._seleccionar_ruta(ruta_archivo)

    def _seleccionar_ruta(self, ruta_archivo: str) -> None:
        if not os.path.isfile(ruta_archivo):
            messagebox.showerror(
                "Archivo no válido",
                "No se encontró el archivo seleccionado.",
                parent=self,
            )
            return

        self.archivo_seleccionado = ruta_archivo
        nombre = os.path.basename(ruta_archivo)
        peso_bytes = os.path.getsize(ruta_archivo)
        peso_mb = peso_bytes / (1024 * 1024)
        detalle = f"{nombre} · {peso_mb:.1f} MB" if peso_bytes >= 1024 * 1024 else nombre

        self.lbl_archivo.configure(text=nombre, text_color=COLOR_TEXTO)
        self.lbl_detalle_archivo.configure(text=detalle, text_color=COLOR_TEXTO_SECUNDARIO)
        self.lbl_estado.configure(text="Archivo listo. Elige el formato y convierte.")

        if peso_bytes > LIMITE_PESO_BYTES:
            messagebox.showwarning(
                "Archivo de más de 50 MB",
                "Este archivo puede tardar bastante o consumir mucha memoria. "
                "Te recomendamos usar «Convertir Online» antes de procesarlo localmente.",
                parent=self,
            )

    def convertir_archivo(self) -> None:
        if not self.archivo_seleccionado:
            messagebox.showwarning(
                "Falta un archivo",
                "Adjunta un archivo antes de convertirlo.",
                parent=self,
            )
            return

        ruta_entrada = self.archivo_seleccionado
        peso_bytes = os.path.getsize(ruta_entrada)
        if peso_bytes > LIMITE_PESO_BYTES:
            confirmacion = messagebox.askyesno(
                "Confirmar conversión local",
                "El archivo supera los 50 MB. Para evitar esperas largas, se recomienda «Convertir Online».\n\n"
                "¿Quieres intentar la conversión local de todos modos?",
                parent=self,
            )
            if not confirmacion:
                return

        extension = self.combo_formato.get()
        nombre_base = Path(ruta_entrada).stem
        ruta_salida = filedialog.asksaveasfilename(
            title="Guardar archivo convertido",
            initialfile=f"{nombre_base}{extension}",
            defaultextension=extension,
            filetypes=[(f"Archivo {extension}", f"*{extension}"), ("Todos los archivos", "*.*")],
        )
        if not ruta_salida:
            return

        salida = Path(ruta_salida)
        if salida.suffix.lower() != extension:
            salida = salida.with_suffix(extension)
            ruta_salida = str(salida)
            if os.path.exists(ruta_salida) and not messagebox.askyesno(
                "Confirmar reemplazo",
                f"Ya existe un archivo en esta ubicación:\n{ruta_salida}\n\n¿Quieres reemplazarlo?",
                parent=self,
            ):
                return

        ruta_entrada_normalizada = os.path.normcase(os.path.abspath(ruta_entrada))
        ruta_salida_normalizada = os.path.normcase(os.path.abspath(ruta_salida))
        if ruta_entrada_normalizada == ruta_salida_normalizada:
            messagebox.showwarning(
                "Elige otra ubicación",
                "El archivo convertido no puede reemplazar al archivo original.",
                parent=self,
            )
            return

        self._iniciar_conversion(ruta_entrada, ruta_salida)

    def _iniciar_conversion(self, ruta_entrada: str, ruta_salida: str) -> None:
        self.btn_convertir.configure(state="disabled", text="Convirtiendo…")
        self.btn_adjuntar.configure(state="disabled")
        self.combo_formato.configure(state="disabled")
        self.lbl_estado.configure(text="Procesando el archivo. Puedes seguir usando Windows…")
        self.barra_progreso.grid(row=6, column=0, sticky="ew", pady=(11, 0))
        self.barra_progreso.start()

        hilo = threading.Thread(
            target=self._convertir_en_segundo_plano,
            args=(ruta_entrada, ruta_salida),
            daemon=True,
        )
        hilo.start()
        self.after(150, self._revisar_resultado)

    def _convertir_en_segundo_plano(self, ruta_entrada: str, ruta_salida: str) -> None:
        try:
            if Path(ruta_entrada).suffix.lower() == ".pdf":
                cantidad_paginas = len(PdfReader(ruta_entrada).pages)
                if cantidad_paginas > LIMITE_PAGINAS_PDF:
                    self.resultados_conversion.put(
                        (
                            "pdf_extenso",
                            f"El PDF tiene {cantidad_paginas} páginas. El límite preventivo para la conversión local es "
                            f"{LIMITE_PAGINAS_PDF} páginas.",
                        )
                    )
                    return

            resultado = MarkItDown().convert(ruta_entrada)
            with open(ruta_salida, "w", encoding="utf-8") as archivo_salida:
                archivo_salida.write(resultado.text_content)
            self.resultados_conversion.put(("exito", ruta_salida))
        except Exception as error:
            self.resultados_conversion.put(("error", str(error)))

    def _revisar_resultado(self) -> None:
        try:
            estado, detalle = self.resultados_conversion.get_nowait()
        except queue.Empty:
            self.after(150, self._revisar_resultado)
            return

        self.barra_progreso.stop()
        self.barra_progreso.grid_remove()
        self.btn_convertir.configure(state="normal", text="Convertir y guardar…")
        self.btn_adjuntar.configure(state="normal")
        self.combo_formato.configure(state="readonly")

        if estado == "exito":
            self.lbl_estado.configure(text="Conversión terminada correctamente.")
            messagebox.showinfo(
                "Conversión completada",
                f"El archivo se guardó en:\n{detalle}",
                parent=self,
            )
        elif estado == "pdf_extenso":
            self.lbl_estado.configure(text="El PDF supera el límite preventivo de páginas.")
            messagebox.showwarning(
                "PDF demasiado extenso",
                f"{detalle}\n\nUsa «Convertir Online» para este documento.",
                parent=self,
            )
        else:
            self.lbl_estado.configure(text="No se pudo completar la conversión.")
            messagebox.showerror(
                "Error de conversión",
                f"No se pudo convertir el archivo.\n\nDetalle: {detalle}",
                parent=self,
            )

    @staticmethod
    def abrir_convertio() -> None:
        webbrowser.open(URL_CONVERSOR_ONLINE)


if __name__ == "__main__":
    app = ConvertidorApp()
    app.mainloop()
