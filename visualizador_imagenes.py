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
                               text="Selecciona hasta 3 imágenes para visualizar con sus canales RGB",
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
            
            # Convertir a RGB si no lo está
            if imagen.mode != 'RGB':
                imagen = imagen.convert('RGB')
            
            # Crear una nueva ventana
            ventana = tk.Toplevel(self.root)
            ventana.title(f"Imagen {numero_ventana}: {os.path.basename(ruta_archivo)} - Canales RGB")
            
            # Obtener el tamaño de la imagen
            ancho_original, alto_original = imagen.size
            
            # Calcular el tamaño para cada canal (máximo 200x200 por canal)
            max_ancho_canal, max_alto_canal = 200, 200
            
            if ancho_original > max_ancho_canal or alto_original > max_alto_canal:
                factor_escala = min(max_ancho_canal/ancho_original, max_alto_canal/alto_original)
                nuevo_ancho = int(ancho_original * factor_escala)
                nuevo_alto = int(alto_original * factor_escala)
                imagen_redimensionada = imagen.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
            else:
                imagen_redimensionada = imagen
                nuevo_ancho, nuevo_alto = ancho_original, alto_original
            
            # Separar los canales RGB
            canales = imagen_redimensionada.split()
            canal_r = canales[0]
            canal_g = canales[1] 
            canal_b = canales[2]
            
            # Crear un frame principal para organizar las imágenes
            frame_principal = tk.Frame(ventana)
            frame_principal.pack(padx=10, pady=10)
            
            # Frame para la imagen original
            frame_original = tk.Frame(frame_principal)
            frame_original.grid(row=0, column=0, columnspan=3, pady=(0, 10))
            
            # Mostrar imagen original
            imagen_tk = ImageTk.PhotoImage(imagen_redimensionada)
            label_original = tk.Label(frame_original, image=imagen_tk)
            label_original.image = imagen_tk  # Mantener referencia
            label_original.pack()
            
            label_titulo_original = tk.Label(frame_original, text="Imagen Original", 
                                           font=("Arial", 12, "bold"))
            label_titulo_original.pack(pady=(5, 0))
            
            # Frame para los canales RGB
            frame_canales = tk.Frame(frame_principal)
            frame_canales.grid(row=1, column=0, columnspan=3)
            
            # Canal Rojo
            canal_r_tk = ImageTk.PhotoImage(canal_r)
            label_r = tk.Label(frame_canales, image=canal_r_tk)
            label_r.image = canal_r_tk
            label_r.grid(row=0, column=0, padx=5)
            
            label_r_titulo = tk.Label(frame_canales, text="Canal Rojo (R)", 
                                    font=("Arial", 10, "bold"), fg="red")
            label_r_titulo.grid(row=1, column=0, pady=(5, 0))
            
            # Canal Verde
            canal_g_tk = ImageTk.PhotoImage(canal_g)
            label_g = tk.Label(frame_canales, image=canal_g_tk)
            label_g.image = canal_g_tk
            label_g.grid(row=0, column=1, padx=5)
            
            label_g_titulo = tk.Label(frame_canales, text="Canal Verde (G)", 
                                    font=("Arial", 10, "bold"), fg="green")
            label_g_titulo.grid(row=1, column=1, pady=(5, 0))
            
            # Canal Azul
            canal_b_tk = ImageTk.PhotoImage(canal_b)
            label_b = tk.Label(frame_canales, image=canal_b_tk)
            label_b.image = canal_b_tk
            label_b.grid(row=0, column=2, padx=5)
            
            label_b_titulo = tk.Label(frame_canales, text="Canal Azul (B)", 
                                    font=("Arial", 10, "bold"), fg="blue")
            label_b_titulo.grid(row=1, column=2, pady=(5, 0))
            
            # Información de la imagen
            info_texto = f"Archivo: {os.path.basename(ruta_archivo)}\n"
            info_texto += f"Tamaño original: {ancho_original}x{alto_original}\n"
            info_texto += f"Tamaño mostrado: {nuevo_ancho}x{nuevo_alto}"
            
            label_info = tk.Label(frame_principal, text=info_texto, 
                                font=("Arial", 9), 
                                justify=tk.LEFT)
            label_info.grid(row=2, column=0, columnspan=3, pady=(10, 0))
            
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
