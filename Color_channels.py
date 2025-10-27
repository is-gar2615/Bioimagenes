import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

class VisualizadorImagenes:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Visualizador de Imágenes")
        self.root.geometry("400x200")
        
        # Lista para almacenar las ventanas de imágenes
        self.ventanas_imagenes = []
        
        # Crear la interfaz principal
        self.crear_interfaz()
        
    def crear_interfaz(self):
        # Título
        titulo = tk.Label(self.root, text="Visualizador de Imágenes", 
                         font=("Arial", 16, "bold"))
        titulo.pack(pady=10)
        
        # Instrucciones
        instrucciones = tk.Label(self.root, 
                               text="Selecciona tres imágenes para visualizar",
                               font=("Arial", 10))
        instrucciones.pack(pady=5)
        
        # Botón para seleccionar imágenes
        btn_seleccionar = tk.Button(self.root, 
                                  text="Seleccionar 3 Imágenes", 
                                  command=self.seleccionar_imagenes,
                                  font=("Arial", 12),
                                  bg="#4CAF50",
                                  fg="white",
                                  padx=20,
                                  pady=10)
        btn_seleccionar.pack(pady=20)
        
        # Botón para cerrar todas las ventanas
        btn_cerrar = tk.Button(self.root, 
                             text="Cerrar Todas las Ventanas", 
                             command=self.cerrar_todas_ventanas,
                             font=("Arial", 10),
                             bg="#f44336",
                             fg="white",
                             padx=15,
                             pady=5)
        btn_cerrar.pack(pady=5)
        
    def seleccionar_imagenes(self):
        # Tipos de archivos soportados
        tipos_archivo = [
            ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
            ("JPEG", "*.jpg *.jpeg"),
            ("PNG", "*.png"),
            ("Todos los archivos", "*.*")
        ]
        
        # Abrir diálogo para seleccionar múltiples archivos
        archivos = filedialog.askopenfilenames(
            title="Selecciona hasta 3 imágenes",
            filetypes=tipos_archivo
        )
        
        if not archivos:
            return
            
        # Limitar a 3 imágenes
        if len(archivos) > 3:
            messagebox.showwarning("Advertencia", 
                                 "Solo se pueden seleccionar hasta 3 imágenes. "
                                 "Se tomarán las primeras 3.")
            archivos = archivos[:3]
        
        # Cerrar ventanas existentes
        self.cerrar_todas_ventanas()
        
        # Mostrar cada imagen en una ventana separada
        for i, archivo in enumerate(archivos):
            self.mostrar_imagen(archivo, i + 1)
    
    def mostrar_imagen(self, ruta_archivo, numero_ventana):
        try:
            # Abrir la imagen
            imagen = Image.open(ruta_archivo)
            
            # Crear una nueva ventana
            ventana = tk.Toplevel(self.root)
            ventana.title(f"Imagen {numero_ventana}: {os.path.basename(ruta_archivo)}")
            
            # Obtener el tamaño de la imagen
            ancho, alto = imagen.size
            
            # Calcular el tamaño máximo para la ventana (máximo 800x600)
            max_ancho, max_alto = 800, 600
            
            if ancho > max_ancho or alto > max_alto:
                # Calcular factor de escala
                factor_escala = min(max_ancho/ancho, max_alto/alto)
                nuevo_ancho = int(ancho * factor_escala)
                nuevo_alto = int(alto * factor_escala)
                imagen = imagen.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
            
            # Convertir imagen para tkinter
            imagen_tk = ImageTk.PhotoImage(imagen)
            
            # Crear label para mostrar la imagen
            label_imagen = tk.Label(ventana, image=imagen_tk)
            label_imagen.image = imagen_tk  # Mantener referencia
            label_imagen.pack(padx=10, pady=10)
            
            # Información de la imagen
            info_texto = f"Archivo: {os.path.basename(ruta_archivo)}\n"
            info_texto += f"Tamaño original: {ancho}x{alto}\n"
            info_texto += f"Tamaño mostrado: {imagen.width}x{imagen.height}"
            
            label_info = tk.Label(ventana, text=info_texto, 
                                font=("Arial", 9), 
                                justify=tk.LEFT)
            label_info.pack(pady=(0, 10))
            
            # Agregar la ventana a la lista
            self.ventanas_imagenes.append(ventana)
            
            # Configurar el cierre de la ventana
            ventana.protocol("WM_DELETE_WINDOW", 
                           lambda: self.cerrar_ventana(ventana))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir la imagen:\n{str(e)}")
    
    def cerrar_ventana(self, ventana):
        """Cerrar una ventana específica y removerla de la lista"""
        if ventana in self.ventanas_imagenes:
            self.ventanas_imagenes.remove(ventana)
        ventana.destroy()
    
    def cerrar_todas_ventanas(self):
        """Cerrar todas las ventanas de imágenes"""
        for ventana in self.ventanas_imagenes[:]:
            ventana.destroy()
        self.ventanas_imagenes.clear()
    
    def ejecutar(self):
        """Iniciar la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    # Verificar que PIL esté instalado
    try:
        from PIL import Image, ImageTk
    except ImportError:
        print("Error: Necesitas instalar Pillow (PIL)")
        print("Ejecuta: pip install Pillow")
        exit(1)
    
    # Crear y ejecutar la aplicación
    app = VisualizadorImagenes()
    app.ejecutar()
