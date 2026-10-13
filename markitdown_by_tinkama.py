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


LIMITE_AVISO_BYTES = 5 * 1024 * 1024
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

        self.title("MarkItDown · by Tinkama")
        self.geometry("1020x700")
        self.minsize(900, 640)
        self.configure(fg_color=COLOR_FONDO)

        self.archivos_seleccionados: tuple[str, ...] = ()
        self.resultados_conversion: queue.Queue[tuple[str, str, str]] = queue.Queue()
        self.resultados_lote: list[tuple[str, str, str]] = []
        self.total_archivos_lote = 0
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
            text="Tinkama · Converter",
            font=ctk.CTkFont(family="Segoe UI", size=21, weight="bold"),
            text_color=COLOR_TEXTO,
        ).grid(row=1, column=0, padx=24, pady=(0, 4))
        ctk.CTkLabel(
            barra,
            text="MarkitDown Microsoft®",
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
            text="Adjunta los archivos que quieras convertir y elige el formato de salida, estos archivos se procesaran localmente. \n\nSi el archivo es muy grande o extenso, se recomienda usar la opción de conversión online. Herramienta brindada por Microsoft®.",
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
            text="Sube PDF, Word, Excel, PowerPoint, etc. y convertilo a texto plano sencillo para ahorrar tokens en tu ia.",
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
            text="Selecciona los archivos que quieres convertir",
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
            text="Adjuntar archivos",
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
        rutas_archivos = filedialog.askopenfilenames(
            title="Adjunta los archivos para convertir",
            filetypes=[("Todos los archivos", "*.*")],
        )
        if not rutas_archivos:
            return

        rutas_validas = tuple(ruta for ruta in rutas_archivos if os.path.isfile(ruta))
        if len(rutas_validas) != len(rutas_archivos):
            messagebox.showerror(
                "Archivo no válido",
                "Uno o más archivos seleccionados ya no están disponibles.",
                parent=self,
            )
            return

        self.archivos_seleccionados = rutas_validas
        nombres = [os.path.basename(ruta) for ruta in rutas_validas]
        detalle = " · ".join(nombres[:3])
        if len(nombres) > 3:
            detalle = f"{detalle} · y {len(nombres) - 3} más"
        self.lbl_archivo.configure(
            text=f"{len(rutas_validas)} archivo(s) seleccionado(s)",
            text_color=COLOR_TEXTO,
        )
        self.lbl_detalle_archivo.configure(text=detalle, text_color=COLOR_TEXTO_SECUNDARIO)
        self.lbl_estado.configure(text="Elige el formato y convierte la tanda.")

        archivos_grandes = [
            os.path.basename(ruta)
            for ruta in rutas_validas
            if os.path.getsize(ruta) > LIMITE_AVISO_BYTES
        ]
        if archivos_grandes:
            messagebox.showwarning(
                "Archivo de más de 5 MB",
                f"{len(archivos_grandes)} archivo(s) superan los 5 MB y podrían no convertirse correctamente. "
                "Se intentarán convertir localmente, pero se recomienda usar «Convertir Online» para esos archivos.",
                parent=self,
            )

    def convertir_archivo(self) -> None:
        if not self.archivos_seleccionados:
            messagebox.showwarning(
                "Falta un archivo",
                "Adjunta uno o más archivos antes de convertirlos.",
                parent=self,
            )
            return

        rutas_entrada = self.archivos_seleccionados
        archivos_mayores = [
            os.path.basename(ruta)
            for ruta in rutas_entrada
            if os.path.getsize(ruta) > LIMITE_PESO_BYTES
        ]
        if archivos_mayores:
            confirmacion = messagebox.askyesno(
                "Confirmar conversión local",
                f"{len(archivos_mayores)} archivo(s) superan los 50 MB. Para evitar esperas largas, "
                "se recomienda «Convertir Online». ¿Quieres continuar con la tanda local?",
                parent=self,
            )
            if not confirmacion:
                return

        extension = self.combo_formato.get()
        carpeta_salida = filedialog.askdirectory(
            title="Elige la carpeta para guardar los archivos convertidos",
            mustexist=True,
        )
        if not carpeta_salida:
            return

        rutas_salida = tuple(
            str(Path(carpeta_salida) / f"{Path(ruta).stem}{extension}")
            for ruta in rutas_entrada
        )
        rutas_salida_normalizadas = [
            os.path.normcase(os.path.abspath(ruta)) for ruta in rutas_salida
        ]
        if len(set(rutas_salida_normalizadas)) != len(rutas_salida_normalizadas):
            messagebox.showwarning(
                "Nombres de salida duplicados",
                "Varios archivos seleccionados generarían el mismo nombre de salida. "
                "Elige archivos con nombres distintos o conviértelos en tandas separadas.",
                parent=self,
            )
            return

        rutas_entrada_normalizadas = {
            os.path.normcase(os.path.abspath(ruta)) for ruta in rutas_entrada
        }
        if any(ruta in rutas_entrada_normalizadas for ruta in rutas_salida_normalizadas):
            messagebox.showwarning(
                "Elige otra carpeta",
                "Un archivo convertido coincidiría con uno de los archivos originales. "
                "Elige una carpeta distinta para proteger los archivos fuente.",
                parent=self,
            )
            return

        rutas_existentes = [ruta for ruta in rutas_salida if os.path.exists(ruta)]
        if rutas_existentes and not messagebox.askyesno(
            "Confirmar reemplazo",
            f"Ya existen {len(rutas_existentes)} archivo(s) en la carpeta elegida. "
            "¿Quieres reemplazar esos archivos?",
            parent=self,
        ):
            return

        tareas = tuple(zip(rutas_entrada, rutas_salida))
        self._iniciar_conversion(tareas)

    def _iniciar_conversion(self, tareas: tuple[tuple[str, str], ...]) -> None:
        self.resultados_lote = []
        self.total_archivos_lote = len(tareas)
        self.btn_convertir.configure(state="disabled", text="Convirtiendo…")
        self.btn_adjuntar.configure(state="disabled")
        self.combo_formato.configure(state="disabled")
        self.lbl_estado.configure(text=f"Procesando 1 de {self.total_archivos_lote}…")
        self.barra_progreso.grid(row=6, column=0, sticky="ew", pady=(11, 0))
        self.barra_progreso.start()

        hilo = threading.Thread(
            target=self._convertir_en_segundo_plano,
            args=(tareas,),
            daemon=True,
        )
        hilo.start()
        self.after(150, self._revisar_resultado)

    def _convertir_en_segundo_plano(
        self,
        tareas: tuple[tuple[str, str], ...],
    ) -> None:
        for ruta_entrada, ruta_salida in tareas:
            try:
                if Path(ruta_entrada).suffix.lower() == ".pdf":
                    cantidad_paginas = len(PdfReader(ruta_entrada).pages)
                    if cantidad_paginas > LIMITE_PAGINAS_PDF:
                        self.resultados_conversion.put(
                            (
                                ruta_entrada,
                                "pdf_extenso",
                                f"Tiene {cantidad_paginas} páginas; el límite local es {LIMITE_PAGINAS_PDF}.",
                            )
                        )
                        continue

                resultado = MarkItDown().convert(ruta_entrada)
                if not resultado.text_content or not resultado.text_content.strip():
                    self.resultados_conversion.put(
                        (ruta_entrada, "vacio", "MarkItDown no extrajo contenido.")
                    )
                    continue

                with open(ruta_salida, "w", encoding="utf-8") as archivo_salida:
                    archivo_salida.write(resultado.text_content)
                self.resultados_conversion.put((ruta_entrada, "exito", ruta_salida))
            except Exception as error:
                self.resultados_conversion.put((ruta_entrada, "error", str(error)))

        self.resultados_conversion.put(("", "finalizado", ""))

    def _revisar_resultado(self) -> None:
        try:
            ruta_archivo, estado, detalle = self.resultados_conversion.get_nowait()
        except queue.Empty:
            self.after(150, self._revisar_resultado)
            return

        if estado == "finalizado":
            self._finalizar_lote()
            return

        self.resultados_lote.append((ruta_archivo, estado, detalle))
        procesados = len(self.resultados_lote)
        self.lbl_estado.configure(
            text=f"Procesados {procesados} de {self.total_archivos_lote} archivos…"
        )
        self.after(150, self._revisar_resultado)

    def _finalizar_lote(self) -> None:
        self.barra_progreso.stop()
        self.barra_progreso.grid_remove()
        self.btn_convertir.configure(state="normal", text="Convertir y guardar…")
        self.btn_adjuntar.configure(state="normal")
        self.combo_formato.configure(state="readonly")

        exitos = [
            os.path.basename(ruta)
            for ruta, estado, _ in self.resultados_lote
            if estado == "exito"
        ]
        fallidos = [
            f"{os.path.basename(ruta)}: {detalle}"
            for ruta, estado, detalle in self.resultados_lote
            if estado != "exito"
        ]
        resumen = f"Archivos convertidos correctamente: {len(exitos)} de {self.total_archivos_lote}."
        if exitos:
            resumen += "\n\nConvertidos:\n" + "\n".join(exitos)
        if fallidos:
            resumen += "\n\nNo convertidos:\n" + "\n".join(fallidos)

        if fallidos:
            self.lbl_estado.configure(
                text=f"Tanda terminada: {len(exitos)} de {self.total_archivos_lote} convertidos."
            )
            messagebox.showwarning("Tanda de conversión finalizada", resumen, parent=self)
        else:
            self.lbl_estado.configure(text="Todos los archivos se convirtieron correctamente.")
            messagebox.showinfo("Tanda de conversión completada", resumen, parent=self)

    @staticmethod
    def abrir_convertio() -> None:
        webbrowser.open(URL_CONVERSOR_ONLINE)


if __name__ == "__main__":
    app = ConvertidorApp()
    app.mainloop()
