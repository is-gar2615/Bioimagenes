import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import math

class TransformadorImagenes:
    def __init__(self, root):
        self.root = root
        self.root.title("Transformador de Imágenes Geométricas")
        self.root.geometry("1000x700")
        
        # Variables para la imagen
        self.imagen_original = None
        self.imagen_actual = None
        self.imagen_tk = None
        
        # Ventana para imagen original
        self.ventana_original = None
        self.canvas_original = None
        
        # Ventana para imagen transformada
        self.ventana_transformada = None
        self.canvas_transformada = None
        
        # Configurar la interfaz
        self.configurar_interfaz()
        
    def configurar_interfaz(self):
        # Frame principal
        frame_principal = ttk.Frame(self.root, padding="10")
        frame_principal.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        frame_principal.columnconfigure(1, weight=1)
        frame_principal.rowconfigure(1, weight=1)
        
        # Frame para controles
        frame_controles = ttk.LabelFrame(frame_principal, text="Controles de Transformación", padding="10")
        frame_controles.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botón para cargar imagen
        ttk.Button(frame_controles, text="Cargar Imagen", 
                  command=self.cargar_imagen).grid(row=0, column=0, padx=(0, 10))
        
        # Botón para resetear
        ttk.Button(frame_controles, text="Resetear", 
                  command=self.resetear_imagen).grid(row=0, column=1, padx=(0, 10))
        
        # Botón para mostrar ventanas de comparación
        ttk.Button(frame_controles, text="Mostrar Comparación", 
                  command=self.mostrar_comparacion).grid(row=0, column=2, padx=(0, 10))
        
        # Separador
        ttk.Separator(frame_controles, orient='vertical').grid(row=0, column=3, sticky=(tk.N, tk.S), padx=10)
        
        # Controles de escalado
        ttk.Label(frame_controles, text="Escalar:").grid(row=0, column=4, padx=(0, 5))
        self.escala_var = tk.DoubleVar(value=1.0)
        escala_spin = ttk.Spinbox(frame_controles, from_=0.1, to=5.0, increment=0.1, 
                                 textvariable=self.escala_var, width=8)
        escala_spin.grid(row=0, column=5, padx=(0, 5))
        ttk.Button(frame_controles, text="Aplicar Escala", 
                  command=self.aplicar_escala).grid(row=0, column=6, padx=(0, 10))
        
        # Controles de rotación
        ttk.Label(frame_controles, text="Rotar (grados):").grid(row=1, column=4, padx=(0, 5))
        self.rotacion_var = tk.DoubleVar(value=0.0)
        rotacion_spin = ttk.Spinbox(frame_controles, from_=-360, to=360, increment=15, 
                                   textvariable=self.rotacion_var, width=8)
        rotacion_spin.grid(row=1, column=5, padx=(0, 5))
        ttk.Button(frame_controles, text="Aplicar Rotación", 
                  command=self.aplicar_rotacion).grid(row=1, column=6, padx=(0, 10))
        
        # Controles de reflexión
        ttk.Label(frame_controles, text="Reflexión:").grid(row=2, column=4, padx=(0, 5))
        self.reflexion_var = tk.StringVar(value="ninguna")
        reflexion_combo = ttk.Combobox(frame_controles, textvariable=self.reflexion_var, 
                                      values=["ninguna", "eje X", "eje Y", "ambos"], 
                                      state="readonly", width=10)
        reflexion_combo.grid(row=2, column=5, padx=(0, 5))
        ttk.Button(frame_controles, text="Aplicar Reflexión", 
                  command=self.aplicar_reflexion).grid(row=2, column=6, padx=(0, 10))
        
        # Frame para mostrar imagen
        frame_imagen = ttk.LabelFrame(frame_principal, text="Vista de Imagen", padding="10")
        frame_imagen.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame_imagen.columnconfigure(0, weight=1)
        frame_imagen.rowconfigure(0, weight=1)
        
        # Canvas para mostrar la imagen
        self.canvas = tk.Canvas(frame_imagen, bg="white", width=800, height=500)
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars para el canvas
        scrollbar_v = ttk.Scrollbar(frame_imagen, orient="vertical", command=self.canvas.yview)
        scrollbar_h = ttk.Scrollbar(frame_imagen, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        scrollbar_v.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_h.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Frame de información
        frame_info = ttk.Frame(frame_principal)
        frame_info.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.info_label = ttk.Label(frame_info, text="Cargue una imagen para comenzar")
        self.info_label.pack()
        
    def cargar_imagen(self):
        """Cargar una imagen desde el sistema de archivos"""
        tipos_archivo = [
            ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
            ("JPEG", "*.jpg *.jpeg"),
            ("PNG", "*.png"),
            ("BMP", "*.bmp"),
            ("GIF", "*.gif"),
            ("TIFF", "*.tiff"),
            ("Todos los archivos", "*.*")
        ]
        
        archivo = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=tipos_archivo
        )
        
        if archivo:
            try:
                # Cargar imagen original
                self.imagen_original = Image.open(archivo)
                self.imagen_actual = self.imagen_original.copy()
                
                # Mostrar imagen
                self.mostrar_imagen()
                
                # Actualizar información
                info = f"Imagen cargada: {self.imagen_original.size[0]}x{self.imagen_original.size[1]} píxeles"
                self.info_label.config(text=info)
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen: {str(e)}")
    
    def mostrar_imagen(self):
        """Mostrar la imagen actual en el canvas principal"""
        if self.imagen_actual is None:
            return
            
        # Redimensionar imagen para que quepa en el canvas
        canvas_width = 800
        canvas_height = 500
        
        img_width, img_height = self.imagen_actual.size
        ratio = min(canvas_width/img_width, canvas_height/img_height)
        
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        
        # Crear copia redimensionada para mostrar
        img_mostrar = self.imagen_actual.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.imagen_tk = ImageTk.PhotoImage(img_mostrar)
        
        # Limpiar canvas y mostrar imagen
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width//2, canvas_height//2, 
                               image=self.imagen_tk, anchor="center")
        
        # Configurar scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Actualizar ventanas de comparación si están abiertas
        self.actualizar_ventanas_comparacion()
    
    def mostrar_comparacion(self):
        """Mostrar ventanas de comparación lado a lado"""
        if self.imagen_original is None:
            messagebox.showwarning("Advertencia", "Primero cargue una imagen")
            return
            
        # Crear ventana para imagen original
        self.crear_ventana_original()
        
        # Crear ventana para imagen transformada
        self.crear_ventana_transformada()
        
        # Mostrar ambas imágenes
        self.actualizar_ventanas_comparacion()
    
    def crear_ventana_original(self):
        """Crear ventana para mostrar imagen original"""
        if self.ventana_original is None or not self.ventana_original.winfo_exists():
            self.ventana_original = tk.Toplevel(self.root)
            self.ventana_original.title("Imagen Original")
            self.ventana_original.geometry("600x500")
            
            # Frame para la imagen original
            frame_original = ttk.Frame(self.ventana_original, padding="10")
            frame_original.pack(fill=tk.BOTH, expand=True)
            
            # Canvas para imagen original
            self.canvas_original = tk.Canvas(frame_original, bg="white", width=580, height=460)
            self.canvas_original.pack(fill=tk.BOTH, expand=True)
            
            # Scrollbars para canvas original
            scrollbar_v_orig = ttk.Scrollbar(frame_original, orient="vertical", command=self.canvas_original.yview)
            scrollbar_h_orig = ttk.Scrollbar(frame_original, orient="horizontal", command=self.canvas_original.xview)
            self.canvas_original.configure(yscrollcommand=scrollbar_v_orig.set, xscrollcommand=scrollbar_h_orig.set)
            
            scrollbar_v_orig.pack(side=tk.RIGHT, fill=tk.Y)
            scrollbar_h_orig.pack(side=tk.BOTTOM, fill=tk.X)
    
    def crear_ventana_transformada(self):
        """Crear ventana para mostrar imagen transformada"""
        if self.ventana_transformada is None or not self.ventana_transformada.winfo_exists():
            self.ventana_transformada = tk.Toplevel(self.root)
            self.ventana_transformada.title("Imagen Transformada")
            self.ventana_transformada.geometry("600x500")
            
            # Frame para la imagen transformada
            frame_transformada = ttk.Frame(self.ventana_transformada, padding="10")
            frame_transformada.pack(fill=tk.BOTH, expand=True)
            
            # Canvas para imagen transformada
            self.canvas_transformada = tk.Canvas(frame_transformada, bg="white", width=580, height=460)
            self.canvas_transformada.pack(fill=tk.BOTH, expand=True)
            
            # Scrollbars para canvas transformada
            scrollbar_v_trans = ttk.Scrollbar(frame_transformada, orient="vertical", command=self.canvas_transformada.yview)
            scrollbar_h_trans = ttk.Scrollbar(frame_transformada, orient="horizontal", command=self.canvas_transformada.xview)
            self.canvas_transformada.configure(yscrollcommand=scrollbar_v_trans.set, xscrollcommand=scrollbar_h_trans.set)
            
            scrollbar_v_trans.pack(side=tk.RIGHT, fill=tk.Y)
            scrollbar_h_trans.pack(side=tk.BOTTOM, fill=tk.X)
    
    def actualizar_ventanas_comparacion(self):
        """Actualizar las ventanas de comparación con las imágenes actuales"""
        if self.ventana_original and self.ventana_original.winfo_exists() and self.canvas_original:
            self.mostrar_imagen_en_canvas(self.imagen_original, self.canvas_original, "Original")
            
        if self.ventana_transformada and self.ventana_transformada.winfo_exists() and self.canvas_transformada:
            self.mostrar_imagen_en_canvas(self.imagen_actual, self.canvas_transformada, "Transformada")
    
    def mostrar_imagen_en_canvas(self, imagen, canvas, titulo):
        """Mostrar una imagen en un canvas específico"""
        if imagen is None:
            return
            
        # Obtener dimensiones del canvas
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Si el canvas no está inicializado, usar dimensiones por defecto
            canvas_width = 580
            canvas_height = 460
        
        # Redimensionar imagen para que quepa en el canvas
        img_width, img_height = imagen.size
        ratio = min(canvas_width/img_width, canvas_height/img_height, 1.0)  # No ampliar más del 100%
        
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        
        # Crear copia redimensionada para mostrar
        img_mostrar = imagen.resize((new_width, new_height), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_mostrar)
        
        # Limpiar canvas y mostrar imagen
        canvas.delete("all")
        canvas.create_image(canvas_width//2, canvas_height//2, 
                          image=img_tk, anchor="center")
        
        # Configurar scroll region
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Mantener referencia a la imagen para evitar garbage collection
        canvas.image = img_tk
    
    def resetear_imagen(self):
        """Resetear la imagen a su estado original"""
        if self.imagen_original is not None:
            self.imagen_actual = self.imagen_original.copy()
            self.mostrar_imagen()
            self.info_label.config(text="Imagen reseteada al estado original")
    
    def aplicar_escala(self):
        """Aplicar transformación de escala"""
        if self.imagen_actual is None:
            messagebox.showwarning("Advertencia", "Primero cargue una imagen")
            return
            
        escala = self.escala_var.get()
        if escala <= 0:
            messagebox.showerror("Error", "La escala debe ser mayor que 0")
            return
            
        try:
            # Aplicar escala desde el origen
            ancho_original, alto_original = self.imagen_actual.size
            nuevo_ancho = int(ancho_original * escala)
            nuevo_alto = int(alto_original * escala)
            
            # Redimensionar imagen
            self.imagen_actual = self.imagen_actual.resize((nuevo_ancho, nuevo_alto), 
                                                          Image.Resampling.LANCZOS)
            
            # Mostrar resultado
            self.mostrar_imagen()
            
            info = f"Escala aplicada: {escala:.2f}x - Nuevo tamaño: {nuevo_ancho}x{nuevo_alto}"
            self.info_label.config(text=info)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar escala: {str(e)}")
    
    def aplicar_rotacion(self):
        """Aplicar transformación de rotación"""
        if self.imagen_actual is None:
            messagebox.showwarning("Advertencia", "Primero cargue una imagen")
            return
            
        angulo = self.rotacion_var.get()
        
        try:
            # Rotar imagen desde el origen
            self.imagen_actual = self.imagen_actual.rotate(-angulo, expand=True)
            
            # Mostrar resultado
            self.mostrar_imagen()
            
            info = f"Rotación aplicada: {angulo}° - Nuevo tamaño: {self.imagen_actual.size[0]}x{self.imagen_actual.size[1]}"
            self.info_label.config(text=info)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar rotación: {str(e)}")
    
    def aplicar_reflexion(self):
        """Aplicar transformación de reflexión"""
        if self.imagen_actual is None:
            messagebox.showwarning("Advertencia", "Primero cargue una imagen")
            return
            
        tipo_reflexion = self.reflexion_var.get()
        
        try:
            if tipo_reflexion == "eje X":
                # Reflejar sobre el eje X (horizontal)
                self.imagen_actual = self.imagen_actual.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            elif tipo_reflexion == "eje Y":
                # Reflejar sobre el eje Y (vertical)
                self.imagen_actual = self.imagen_actual.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            elif tipo_reflexion == "ambos":
                # Reflejar sobre ambos ejes
                self.imagen_actual = self.imagen_actual.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                self.imagen_actual = self.imagen_actual.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            elif tipo_reflexion == "ninguna":
                messagebox.showinfo("Información", "No se aplicó ninguna reflexión")
                return
            
            # Mostrar resultado
            self.mostrar_imagen()
            
            info = f"Reflexión aplicada: {tipo_reflexion} - Tamaño: {self.imagen_actual.size[0]}x{self.imagen_actual.size[1]}"
            self.info_label.config(text=info)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar reflexión: {str(e)}")

def main():
    """Función principal"""
    root = tk.Tk()
    app = TransformadorImagenes(root)
    root.mainloop()

if __name__ == "__main__":
    main()
