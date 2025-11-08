import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

def ver_histograma(imagen):
    """
    Calcula el histograma de una imagen por cada canal de color.
    Retorna tres histogramas: rojo, verde y azul.
    """
    # Obtener las dimensiones de la imagen
    alto, ancho, canales = imagen.shape
    
    # Crear matrices para los histogramas de cada canal
    histograma_rojo = np.zeros(256, dtype=np.int32)
    histograma_verde = np.zeros(256, dtype=np.int32)
    histograma_azul = np.zeros(256, dtype=np.int32)
    
    # Calcular el histograma para cada canal
    for i in range(alto):
        for j in range(ancho):
            # Obtener el valor del píxel (OpenCV usa BGR, no RGB)
            b, g, r = imagen[i, j]
            # Incrementar el valor del histograma para cada canal
            histograma_rojo[r] += 1
            histograma_verde[g] += 1
            histograma_azul[b] += 1

    return histograma_rojo, histograma_verde, histograma_azul

def binarizar_imagen_RGB(imagen, umbral_min_rojo, umbral_max_rojo, umbral_min_verde, umbral_max_verde, umbral_min_azul, umbral_max_azul):
    """
    Binariza una imagen RGB en escala de grises usando umbrales específicos para cada canal.
    """
    # Obtener las dimensiones de la imagen
    alto, ancho, canales = imagen.shape
    
    # Crear una matriz para la imagen binarizada
    imagen_binarizada = np.zeros((alto, ancho), dtype=np.uint8)
    
    # Binarizar cada canal
    for i in range(alto):
        for j in range(ancho):
            # Obtener los valores BGR del píxel (OpenCV usa BGR, no RGB)
            b, g, r = imagen[i, j]
            # Aplicar umbrales
            if r > umbral_min_rojo and r < umbral_max_rojo and g > umbral_min_verde and g < umbral_max_verde and b > umbral_min_azul and b < umbral_max_azul:
                imagen_binarizada[i, j] = 255
            else:
                imagen_binarizada[i, j] = 0
    return imagen_binarizada

class AplicacionBinarizacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Binarización de Imágenes RGB")
        self.root.geometry("1400x900")
        
        # Variables para almacenar la imagen
        self.imagen_original = None
        self.imagen_cv = None
        self.histograma_rojo = None
        self.histograma_verde = None
        self.histograma_azul = None
        
        # Variables para rastrear dimensiones de canvas (evitar redimensionamientos innecesarios)
        self.canvas_original_size = (0, 0)
        self.canvas_binarizada_size = (0, 0)
        
        # Variables para los umbrales
        self.umbral_min_rojo = tk.IntVar(value=0)
        self.umbral_max_rojo = tk.IntVar(value=255)
        self.umbral_min_verde = tk.IntVar(value=0)
        self.umbral_max_verde = tk.IntVar(value=255)
        self.umbral_min_azul = tk.IntVar(value=0)
        self.umbral_max_azul = tk.IntVar(value=255)
        
        # Crear interfaz
        self.crear_interfaz()
        
    def crear_interfaz(self):
        # Frame superior para botones
        frame_superior = tk.Frame(self.root)
        frame_superior.pack(pady=10)
        
        # Botón para cargar imagen
        btn_cargar = tk.Button(frame_superior, text="Cargar Imagen", command=self.cargar_imagen, 
                              bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), padx=20, pady=10)
        btn_cargar.pack(side=tk.LEFT, padx=10)
        
        # Botón para actualizar histogramas
        btn_actualizar_hist = tk.Button(frame_superior, text="Actualizar Histogramas", 
                                       command=self.actualizar_histogramas, 
                                       bg="#2196F3", fg="white", font=("Arial", 12, "bold"), padx=20, pady=10)
        btn_actualizar_hist.pack(side=tk.LEFT, padx=10)
        
        # Botón para aplicar binarización
        btn_binarizar = tk.Button(frame_superior, text="Aplicar Binarización", 
                                 command=self.aplicar_binarizacion, 
                                 bg="#FF9800", fg="white", font=("Arial", 12, "bold"), padx=20, pady=10)
        btn_binarizar.pack(side=tk.LEFT, padx=10)
        
        # Frame principal dividido en dos columnas
        frame_principal = tk.Frame(self.root)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Columna izquierda: Imágenes
        frame_imagenes = tk.Frame(frame_principal)
        frame_imagenes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame para imagen original
        frame_original = tk.LabelFrame(frame_imagenes, text="Imagen Original", font=("Arial", 10, "bold"))
        frame_original.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas para imagen original
        self.canvas_original = tk.Canvas(frame_original, bg="lightgray", highlightthickness=1, highlightbackground="gray")
        self.canvas_original.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.imagen_original_tk = None
        self.imagen_original_data = None  # Almacenar datos de la imagen original
        
        # Texto inicial
        self.canvas_original.create_text(200, 150, text="Cargue una imagen para comenzar", 
                                        fill="gray", font=("Arial", 12))
        
        # Bind para redimensionamiento (solo cuando cambia significativamente)
        self.canvas_original.bind("<Configure>", self.on_canvas_original_configure)
        
        # Frame para imagen binarizada
        frame_binarizada = tk.LabelFrame(frame_imagenes, text="Imagen Binarizada", font=("Arial", 10, "bold"))
        frame_binarizada.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas para imagen binarizada
        self.canvas_binarizada = tk.Canvas(frame_binarizada, bg="lightgray", highlightthickness=1, highlightbackground="gray")
        self.canvas_binarizada.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.imagen_binarizada_tk = None
        self.imagen_binarizada_data = None  # Almacenar datos de la imagen binarizada
        
        # Texto inicial
        self.canvas_binarizada.create_text(200, 150, text="Aplique binarización para ver resultado", 
                                          fill="gray", font=("Arial", 12))
        
        # Bind para redimensionamiento (solo cuando cambia significativamente)
        self.canvas_binarizada.bind("<Configure>", self.on_canvas_binarizada_configure)
        
        # Columna derecha: Controles y histogramas
        frame_derecha = tk.Frame(frame_principal)
        frame_derecha.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Frame para controles de umbrales
        frame_controles = tk.LabelFrame(frame_derecha, text="Controles de Umbrales", font=("Arial", 10, "bold"))
        frame_controles.pack(fill=tk.X, padx=5, pady=5)
        
        # Controles para canal Rojo
        self.crear_controles_canal(frame_controles, "Rojo", self.umbral_min_rojo, self.umbral_max_rojo, "red")
        
        # Controles para canal Verde
        self.crear_controles_canal(frame_controles, "Verde", self.umbral_min_verde, self.umbral_max_verde, "green")
        
        # Controles para canal Azul
        self.crear_controles_canal(frame_controles, "Azul", self.umbral_min_azul, self.umbral_max_azul, "blue")
        
        # Frame para histogramas
        frame_histogramas = tk.LabelFrame(frame_derecha, text="Histogramas por Canal", font=("Arial", 10, "bold"))
        frame_histogramas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Crear figura de matplotlib para histogramas
        self.fig_histogramas = Figure(figsize=(10, 4), dpi=100)
        self.canvas_histogramas = FigureCanvasTkAgg(self.fig_histogramas, frame_histogramas)
        self.canvas_histogramas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def crear_controles_canal(self, parent, nombre, var_min, var_max, color):
        frame_canal = tk.Frame(parent, bg=color, relief=tk.RAISED, bd=2)
        frame_canal.pack(fill=tk.X, padx=5, pady=5)
        
        label_canal = tk.Label(frame_canal, text=f"Canal {nombre}", 
                              font=("Arial", 9, "bold"), bg=color, fg="white")
        label_canal.pack(anchor=tk.W, padx=5, pady=2)
        
        # Umbral mínimo
        frame_min = tk.Frame(frame_canal, bg=color)
        frame_min.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(frame_min, text="Mín:", bg=color, fg="white", width=5).pack(side=tk.LEFT)
        scale_min = tk.Scale(frame_min, from_=0, to=255, orient=tk.HORIZONTAL, 
                            variable=var_min, length=200, bg=color, fg="white",
                            command=lambda v: self.actualizar_labels())
        scale_min.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Crear etiqueta para valor mínimo
        label_min = tk.Label(frame_min, text=str(var_min.get()), bg=color, fg="white", width=4)
        label_min.pack(side=tk.LEFT, padx=5)
        
        # Guardar referencia a la etiqueta
        if nombre == "Rojo":
            self.label_min_rojo = label_min
        elif nombre == "Verde":
            self.label_min_verde = label_min
        else:
            self.label_min_azul = label_min
        
        # Umbral máximo
        frame_max = tk.Frame(frame_canal, bg=color)
        frame_max.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(frame_max, text="Máx:", bg=color, fg="white", width=5).pack(side=tk.LEFT)
        scale_max = tk.Scale(frame_max, from_=0, to=255, orient=tk.HORIZONTAL, 
                            variable=var_max, length=200, bg=color, fg="white",
                            command=lambda v: self.actualizar_labels())
        scale_max.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Crear etiqueta para valor máximo
        label_max = tk.Label(frame_max, text=str(var_max.get()), bg=color, fg="white", width=4)
        label_max.pack(side=tk.LEFT, padx=5)
        
        # Guardar referencia a la etiqueta
        if nombre == "Rojo":
            self.label_max_rojo = label_max
        elif nombre == "Verde":
            self.label_max_verde = label_max
        else:
            self.label_max_azul = label_max
        
    def actualizar_labels(self):
        """Actualiza las etiquetas de los valores de umbrales"""
        try:
            if hasattr(self, 'label_min_rojo') and hasattr(self, 'label_max_rojo'):
                self.label_min_rojo.config(text=str(self.umbral_min_rojo.get()))
                self.label_max_rojo.config(text=str(self.umbral_max_rojo.get()))
            if hasattr(self, 'label_min_verde') and hasattr(self, 'label_max_verde'):
                self.label_min_verde.config(text=str(self.umbral_min_verde.get()))
                self.label_max_verde.config(text=str(self.umbral_max_verde.get()))
            if hasattr(self, 'label_min_azul') and hasattr(self, 'label_max_azul'):
                self.label_min_azul.config(text=str(self.umbral_min_azul.get()))
                self.label_max_azul.config(text=str(self.umbral_max_azul.get()))
        except:
            pass  # Ignorar errores si las etiquetas aún no están creadas
    
    def on_canvas_original_configure(self, event):
        """Maneja el evento de redimensionamiento del canvas original"""
        nuevo_ancho = event.width
        nuevo_alto = event.height
        # Solo redimensionar si el cambio es significativo (más de 10 píxeles)
        # y hay una imagen cargada
        if self.imagen_original_data is not None:
            if abs(nuevo_ancho - self.canvas_original_size[0]) > 10 or abs(nuevo_alto - self.canvas_original_size[1]) > 10:
                self.canvas_original_size = (nuevo_ancho, nuevo_alto)
                self.redimensionar_imagen("original")
        else:
            # Actualizar dimensiones incluso sin imagen
            self.canvas_original_size = (nuevo_ancho, nuevo_alto)
    
    def on_canvas_binarizada_configure(self, event):
        """Maneja el evento de redimensionamiento del canvas binarizada"""
        nuevo_ancho = event.width
        nuevo_alto = event.height
        # Solo redimensionar si el cambio es significativo (más de 10 píxeles)
        # y hay una imagen cargada
        if self.imagen_binarizada_data is not None:
            if abs(nuevo_ancho - self.canvas_binarizada_size[0]) > 10 or abs(nuevo_alto - self.canvas_binarizada_size[1]) > 10:
                self.canvas_binarizada_size = (nuevo_ancho, nuevo_alto)
                self.redimensionar_imagen("binarizada")
        else:
            # Actualizar dimensiones incluso sin imagen
            self.canvas_binarizada_size = (nuevo_ancho, nuevo_alto)
    
    def mostrar_imagen_en_canvas(self, imagen_rgb, canvas, tipo):
        """Muestra una imagen en un Canvas, escalándola y centrándola correctamente"""
        # Guardar datos de la imagen original para poder redimensionarla después
        if tipo == "original":
            self.imagen_original_data = imagen_rgb.copy()
            # Actualizar dimensiones del canvas si no están establecidas
            if self.canvas_original_size[0] == 0:
                self.canvas_original.update_idletasks()
                self.canvas_original_size = (max(self.canvas_original.winfo_width(), 400), 
                                             max(self.canvas_original.winfo_height(), 300))
        elif tipo == "binarizada":
            self.imagen_binarizada_data = imagen_rgb.copy()
            # Actualizar dimensiones del canvas si no están establecidas
            if self.canvas_binarizada_size[0] == 0:
                self.canvas_binarizada.update_idletasks()
                self.canvas_binarizada_size = (max(self.canvas_binarizada.winfo_width(), 400), 
                                               max(self.canvas_binarizada.winfo_height(), 300))
        
        # Redimensionar y mostrar
        self.redimensionar_imagen(tipo)
    
    def redimensionar_imagen(self, tipo):
        """Redimensiona y muestra la imagen según el tamaño actual del canvas"""
        # Determinar qué canvas e imagen usar
        if tipo == "original":
            canvas = self.canvas_original
            imagen_data = self.imagen_original_data
            # Usar dimensiones guardadas o obtener del canvas
            if self.canvas_original_size[0] > 0:
                canvas_ancho, canvas_alto = self.canvas_original_size
            else:
                canvas.update_idletasks()
                canvas_ancho = max(canvas.winfo_width() - 10, 100)
                canvas_alto = max(canvas.winfo_height() - 10, 100)
        elif tipo == "binarizada":
            canvas = self.canvas_binarizada
            imagen_data = self.imagen_binarizada_data
            # Usar dimensiones guardadas o obtener del canvas
            if self.canvas_binarizada_size[0] > 0:
                canvas_ancho, canvas_alto = self.canvas_binarizada_size
            else:
                canvas.update_idletasks()
                canvas_ancho = max(canvas.winfo_width() - 10, 100)
                canvas_alto = max(canvas.winfo_height() - 10, 100)
        else:
            return
        
        # Si no hay imagen cargada, no hacer nada
        if imagen_data is None:
            return
        
        # Limpiar canvas
        canvas.delete("all")
        
        # Ajustar dimensiones del canvas (con un pequeño margen para bordes)
        canvas_ancho = max(canvas_ancho - 20, 100)
        canvas_alto = max(canvas_alto - 20, 100)
        
        # Obtener dimensiones de la imagen
        alto_imagen, ancho_imagen = imagen_data.shape[:2]
        
        # Calcular factor de escala manteniendo aspect ratio
        factor_escala = min(canvas_ancho / ancho_imagen, canvas_alto / alto_imagen)
        
        # Redimensionar imagen
        nuevo_ancho = int(ancho_imagen * factor_escala)
        nuevo_alto = int(alto_imagen * factor_escala)
        
        if nuevo_ancho > 0 and nuevo_alto > 0:
            # Redimensionar con OpenCV
            imagen_redimensionada = cv2.resize(imagen_data, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_AREA)
            
            # Convertir a PIL Image
            imagen_pil = Image.fromarray(imagen_redimensionada)
            imagen_tk = ImageTk.PhotoImage(imagen_pil)
            
            # Calcular posición para centrar
            x = canvas_ancho // 2
            y = canvas_alto // 2
            
            # Mostrar imagen en el canvas (centrada)
            canvas.create_image(x, y, image=imagen_tk, anchor=tk.CENTER)
            
            # Guardar referencia a la imagen para evitar que sea recolectada por el garbage collector
            if tipo == "original":
                self.imagen_original_tk = imagen_tk
            elif tipo == "binarizada":
                self.imagen_binarizada_tk = imagen_tk
        
    def cargar_imagen(self):
        """Carga una imagen desde un archivo"""
        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"), ("Todos los archivos", "*.*")]
        )
        
        if ruta_archivo:
            try:
                # Cargar imagen con OpenCV
                self.imagen_cv = cv2.imread(ruta_archivo)
                
                if self.imagen_cv is None:
                    messagebox.showerror("Error", "No se pudo cargar la imagen")
                    return
                
                # Convertir BGR a RGB para mostrar
                imagen_rgb = cv2.cvtColor(self.imagen_cv, cv2.COLOR_BGR2RGB)
                
                # Guardar imagen original RGB para mostrar
                self.imagen_original_rgb = imagen_rgb.copy()
                
                # Mostrar imagen en canvas
                self.mostrar_imagen_en_canvas(imagen_rgb, None, "original")
                
                # Calcular histogramas
                self.actualizar_histogramas()
                
                messagebox.showinfo("Éxito", "Imagen cargada correctamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar la imagen: {str(e)}")
    
    def actualizar_histogramas(self):
        """Actualiza los histogramas de la imagen"""
        if self.imagen_cv is None:
            messagebox.showwarning("Advertencia", "Primero debe cargar una imagen")
            return
        
        # Calcular histogramas
        self.histograma_rojo, self.histograma_verde, self.histograma_azul = ver_histograma(self.imagen_cv)
        
        # Limpiar figura anterior
        self.fig_histogramas.clear()
        
        # Crear valores de intensidad (0-255)
        valores_intensidad = np.arange(256)
        
        # Histograma del canal Rojo
        ax1 = self.fig_histogramas.add_subplot(1, 3, 1)
        ax1.bar(valores_intensidad, self.histograma_rojo, color='red', alpha=0.7, linewidth=1)
        ax1.set_title('Canal Rojo', fontsize=10)
        ax1.set_xlabel('Valor de píxel')
        ax1.set_ylabel('Intensidad')
        ax1.grid(True, alpha=0.3)
        
        # Histograma del canal Verde
        ax2 = self.fig_histogramas.add_subplot(1, 3, 2)
        ax2.bar(valores_intensidad, self.histograma_verde, color='green', alpha=0.7, linewidth=1)
        ax2.set_title('Canal Verde', fontsize=10)
        ax2.set_xlabel('Valor de píxel')
        ax2.set_ylabel('Intensidad')
        ax2.grid(True, alpha=0.3)
        
        # Histograma del canal Azul
        ax3 = self.fig_histogramas.add_subplot(1, 3, 3)
        ax3.bar(valores_intensidad, self.histograma_azul, color='blue', alpha=0.7, linewidth=1)
        ax3.set_title('Canal Azul', fontsize=10)
        ax3.set_xlabel('Valor de píxel')
        ax3.set_ylabel('Intensidad')
        ax3.grid(True, alpha=0.3)
        
        self.fig_histogramas.tight_layout()
        self.canvas_histogramas.draw()
    
    def aplicar_binarizacion(self):
        """Aplica la binarización con los umbrales seleccionados"""
        if self.imagen_cv is None:
            messagebox.showwarning("Advertencia", "Primero debe cargar una imagen")
            return
        
        # Obtener valores de umbrales
        umbral_min_rojo = self.umbral_min_rojo.get()
        umbral_max_rojo = self.umbral_max_rojo.get()
        umbral_min_verde = self.umbral_min_verde.get()
        umbral_max_verde = self.umbral_max_verde.get()
        umbral_min_azul = self.umbral_min_azul.get()
        umbral_max_azul = self.umbral_max_azul.get()
        
        # Validar umbrales
        if umbral_min_rojo >= umbral_max_rojo:
            messagebox.showerror("Error", "El umbral mínimo de rojo debe ser menor al máximo")
            return
        if umbral_min_verde >= umbral_max_verde:
            messagebox.showerror("Error", "El umbral mínimo de verde debe ser menor al máximo")
            return
        if umbral_min_azul >= umbral_max_azul:
            messagebox.showerror("Error", "El umbral mínimo de azul debe ser menor al máximo")
            return
        
        # Aplicar binarización
        imagen_binarizada = binarizar_imagen_RGB(
            self.imagen_cv, umbral_min_rojo, umbral_max_rojo,
            umbral_min_verde, umbral_max_verde, umbral_min_azul, umbral_max_azul
        )
        
        # Convertir a RGB para mostrar (aunque es escala de grises)
        imagen_rgb = cv2.cvtColor(imagen_binarizada, cv2.COLOR_GRAY2RGB)
        
        # Mostrar imagen en canvas
        self.mostrar_imagen_en_canvas(imagen_rgb, None, "binarizada")

def main():
    root = tk.Tk()
    app = AplicacionBinarizacion(root)
    root.mainloop()

if __name__ == "__main__":
    main()
