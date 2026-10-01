import os
import webbrowser  # <- NUEVA IMPORTACIÓN para abrir enlaces web
import customtkinter as ctk
from tkinter import filedialog, messagebox
from markitdown import MarkItDown

# Configuración básica de la apariencia de la ventana
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class ConvertidorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal (Aumentamos un poco la altura)
        self.title("Convertidor Markitdown - By Tinkama")
        self.geometry("800x600") 
        self.resizable(True, True)

        self.archivo_seleccionado = None

        # --- INTERFAZ GRÁFICA ---

        self.lbl_titulo = ctk.CTkLabel(self, text="MarkItDown Converter - By Tinkama", font=ctk.CTkFont(size=20, weight="bold"))
        self.lbl_titulo.pack(pady=(20, 5))

        self.lbl_subtitulo = ctk.CTkLabel(self, text="Convierte PDFs, Word, Excel, PowerPoint, etc.", text_color="white")
        self.lbl_subtitulo.pack(pady=(0, 20))

        self.btn_adjuntar = ctk.CTkButton(self, text="Adjuntar Archivo", command=self.seleccionar_archivo)
        self.btn_adjuntar.pack(pady=10)

        self.lbl_archivo = ctk.CTkLabel(self, text="Ningún archivo seleccionado", text_color="gray")
        self.lbl_archivo.pack(pady=(0, 15))

        self.frame_opciones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_opciones.pack(pady=5)

        self.lbl_formato = ctk.CTkLabel(self.frame_opciones, text="Formato de salida:")
        self.lbl_formato.grid(row=0, column=0, padx=10)

        self.combo_formato = ctk.CTkComboBox(self.frame_opciones, values=[".md", ".txt"], width=80)
        self.combo_formato.grid(row=0, column=1)

        self.btn_convertir = ctk.CTkButton(self, text="Convertir", fg_color="#28a745", hover_color="#218838", command=self.convertir_archivo)
        self.btn_convertir.pack(pady=(20, 10))

        # --- NUEVO BOTÓN PARA CONVERTIO ---
        # Usamos un color transparente y bordes para que parezca un botón secundario
        self.btn_online = ctk.CTkButton(
            self, 
            text="¿Archivo muy grande? Convertir Online", 
            fg_color="transparent", 
            border_width=1, 
            text_color=("gray10", "gray90"), # Se adapta al modo claro/oscuro
            command=self.abrir_convertio
        )
        self.btn_online.pack(pady=(5, 10))

    # --- LÓGICA DE LA APLICACIÓN ---

    def seleccionar_archivo(self):
        ruta_archivo = filedialog.askopenfilename(
            title="Selecciona un archivo",
            filetypes=[("Todos los archivos", "*.*")]
        )
        
        if ruta_archivo:
            self.archivo_seleccionado = ruta_archivo
            nombre_archivo = os.path.basename(ruta_archivo)
            self.lbl_archivo.configure(text=f"Seleccionado: {nombre_archivo}", text_color=("black", "white"))

    def convertir_archivo(self):
        if not self.archivo_seleccionado:
            messagebox.showwarning("Atención", "Por favor, adjunta un archivo primero.")
            return

        self.btn_convertir.configure(state="disabled", text="Convirtiendo...")
        self.update()

        try:
            extension_salida = self.combo_formato.get()
            directorio_base = os.path.dirname(self.archivo_seleccionado)
            nombre_sin_ext = os.path.splitext(os.path.basename(self.archivo_seleccionado))[0]
            ruta_salida = os.path.join(directorio_base, f"{nombre_sin_ext}{extension_salida}")

            md = MarkItDown()
            resultado = md.convert(self.archivo_seleccionado)

            with open(ruta_salida, "w", encoding="utf-8") as archivo_salida:
                archivo_salida.write(resultado.text_content)

            messagebox.showinfo("¡Éxito!", f"Archivo convertido correctamente.\nGuardado en:\n{ruta_salida}")

        except Exception as e:
            messagebox.showerror("Error de conversión", f"No se pudo convertir el archivo.\nDetalle del error:\n{str(e)}")

        finally:
            self.btn_convertir.configure(state="normal", text="Convertir")

    # --- NUEVA FUNCIÓN PARA ABRIR LA WEB ---
    def abrir_convertio(self):
        webbrowser.open("https://convertio.co/es/pdf-txt/")

if __name__ == "__main__":
    app = ConvertidorApp()
    app.mainloop()