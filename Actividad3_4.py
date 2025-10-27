import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from scipy import ndimage
from scipy.signal import wiener
from skimage import feature
from skimage.filters import gaussian
import os

class FiltrosImagenes:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicador de Filtros de Imagen")
        self.root.geometry("800x600")
        
        # Variables
        self.imagen_original = None
        self.imagen_filtrada = None
        self.ruta_imagen = None
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Selección de imagen
        ttk.Label(main_frame, text="Seleccionar Imagen:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.btn_seleccionar = ttk.Button(main_frame, text="Buscar Imagen", command=self.seleccionar_imagen)
        self.btn_seleccionar.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Ruta de imagen
        self.label_ruta = ttk.Label(main_frame, text="Ninguna imagen seleccionada")
        self.label_ruta.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Separador
        ttk.Separator(main_frame, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Selección de filtro
        ttk.Label(main_frame, text="Seleccionar Filtro:").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        self.filtro_var = tk.StringVar(value="wiener")
        filtros_frame = ttk.Frame(main_frame)
        filtros_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        filtros = [
            ("Wiener", "wiener"),
            ("Scharr", "scharr"),
            ("Prewitt", "prewitt"),
            ("Local Binary Patterns", "lbp"),
            ("Gaussiano (Frecuencia)", "gaussiano_freq"),
            ("Personalizado", "personalizado")
        ]
        
        for i, (text, value) in enumerate(filtros):
            ttk.Radiobutton(filtros_frame, text=text, variable=self.filtro_var, 
                           value=value, command=self.actualizar_parametros).grid(
                row=i//2, column=i%2, sticky=tk.W, padx=5, pady=2)
        
        # Frame de parámetros
        self.frame_parametros = ttk.LabelFrame(main_frame, text="Parámetros del Filtro", padding="10")
        self.frame_parametros.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Aplicar Filtro", command=self.aplicar_filtro).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Guardar Imagen", command=self.guardar_imagen).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Mostrar Resultado", command=self.mostrar_resultado).pack(side=tk.LEFT, padx=5)
        
        # Inicializar parámetros
        self.actualizar_parametros()
    
    def seleccionar_imagen(self):
        tipos_archivo = [
            ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
            ("Todos los archivos", "*.*")
        ]
        
        ruta = filedialog.askopenfilename(
            title="Seleccionar Imagen",
            filetypes=tipos_archivo
        )
        
        if ruta:
            self.ruta_imagen = ruta
            self.imagen_original = cv2.imread(ruta)
            if self.imagen_original is not None:
                self.imagen_original = cv2.cvtColor(self.imagen_original, cv2.COLOR_BGR2RGB)
                self.label_ruta.config(text=f"Imagen: {os.path.basename(ruta)}")
                messagebox.showinfo("Éxito", "Imagen cargada correctamente")
            else:
                messagebox.showerror("Error", "No se pudo cargar la imagen")
    
    def actualizar_parametros(self):
        # Limpiar frame de parámetros
        for widget in self.frame_parametros.winfo_children():
            widget.destroy()
        
        filtro = self.filtro_var.get()
        
        if filtro == "wiener":
            ttk.Label(self.frame_parametros, text="Tamaño del kernel:").grid(row=0, column=0, sticky=tk.W)
            self.param1 = tk.IntVar(value=3)
            ttk.Spinbox(self.frame_parametros, from_=3, to=15, textvariable=self.param1, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)
            
        elif filtro == "scharr":
            ttk.Label(self.frame_parametros, text="Dirección (0=X, 1=Y):").grid(row=0, column=0, sticky=tk.W)
            self.param1 = tk.IntVar(value=0)
            ttk.Spinbox(self.frame_parametros, from_=0, to=1, textvariable=self.param1, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)
            
        elif filtro == "prewitt":
            ttk.Label(self.frame_parametros, text="Dirección (0=X, 1=Y):").grid(row=0, column=0, sticky=tk.W)
            self.param1 = tk.IntVar(value=0)
            ttk.Spinbox(self.frame_parametros, from_=0, to=1, textvariable=self.param1, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)
            
        elif filtro == "lbp":
            ttk.Label(self.frame_parametros, text="Puntos (8 o 16):").grid(row=0, column=0, sticky=tk.W)
            self.param1 = tk.IntVar(value=8)
            ttk.Spinbox(self.frame_parametros, from_=8, to=16, textvariable=self.param1, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)
            
            ttk.Label(self.frame_parametros, text="Radio:").grid(row=1, column=0, sticky=tk.W)
            self.param2 = tk.DoubleVar(value=1.0)
            ttk.Spinbox(self.frame_parametros, from_=1.0, to=5.0, increment=0.5, textvariable=self.param2, width=10).grid(row=1, column=1, sticky=tk.W, padx=5)
            
        elif filtro == "gaussiano_freq":
            ttk.Label(self.frame_parametros, text="Sigma:").grid(row=0, column=0, sticky=tk.W)
            self.param1 = tk.DoubleVar(value=1.0)
            ttk.Spinbox(self.frame_parametros, from_=0.1, to=5.0, increment=0.1, textvariable=self.param1, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)
            
        elif filtro == "personalizado":
            ttk.Label(self.frame_parametros, text="Intensidad (0-2):").grid(row=0, column=0, sticky=tk.W)
            self.param1 = tk.DoubleVar(value=1.0)
            ttk.Spinbox(self.frame_parametros, from_=0.1, to=2.0, increment=0.1, textvariable=self.param1, width=10).grid(row=0, column=1, sticky=tk.W, padx=5)
            
            ttk.Label(self.frame_parametros, text="Tipo (1=Sharpen, 2=Emboss, 3=Edge):").grid(row=1, column=0, sticky=tk.W)
            self.param2 = tk.IntVar(value=1)
            ttk.Spinbox(self.frame_parametros, from_=1, to=3, textvariable=self.param2, width=10).grid(row=1, column=1, sticky=tk.W, padx=5)
    
    def aplicar_filtro(self):
        if self.imagen_original is None:
            messagebox.showerror("Error", "Primero selecciona una imagen")
            return
        
        try:
            filtro = self.filtro_var.get()
            imagen_gris = cv2.cvtColor(self.imagen_original, cv2.COLOR_RGB2GRAY)
            
            if filtro == "wiener":
                kernel_size = self.param1.get()
                self.imagen_filtrada = self.filtro_wiener(imagen_gris, kernel_size)
                
            elif filtro == "scharr":
                direccion = self.param1.get()
                self.imagen_filtrada = self.filtro_scharr(imagen_gris, direccion)
                
            elif filtro == "prewitt":
                direccion = self.param1.get()
                self.imagen_filtrada = self.filtro_prewitt(imagen_gris, direccion)
                
            elif filtro == "lbp":
                puntos = self.param1.get()
                radio = self.param2.get()
                self.imagen_filtrada = self.filtro_lbp(imagen_gris, puntos, radio)
                
            elif filtro == "gaussiano_freq":
                sigma = self.param1.get()
                self.imagen_filtrada = self.filtro_gaussiano_freq(imagen_gris, sigma)
                
            elif filtro == "personalizado":
                intensidad = self.param1.get()
                tipo = self.param2.get()
                self.imagen_filtrada = self.filtro_personalizado(imagen_gris, intensidad, tipo)
            
            messagebox.showinfo("Éxito", "Filtro aplicado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar el filtro: {str(e)}")
    
    def filtro_wiener(self, imagen, kernel_size):
        """Filtro de Wiener para reducción de ruido"""
        try:
            # Aplicar filtro de Wiener
            resultado = wiener(imagen, (kernel_size, kernel_size))
            # Normalizar a rango 0-255
            resultado = np.clip(resultado, 0, 255)
            return resultado.astype(np.uint8)
        except:
            # Fallback: filtro gaussiano simple
            return cv2.GaussianBlur(imagen, (kernel_size, kernel_size), 0)
    
    def filtro_scharr(self, imagen, direccion):
        """Filtro de Scharr para detección de bordes"""
        if direccion == 0:  # X
            resultado = cv2.Scharr(imagen, cv2.CV_64F, 1, 0)
        else:  # Y
            resultado = cv2.Scharr(imagen, cv2.CV_64F, 0, 1)
        
        # Normalizar y convertir a uint8
        resultado = np.abs(resultado)
        resultado = np.clip(resultado, 0, 255)
        return resultado.astype(np.uint8)
    
    def filtro_prewitt(self, imagen, direccion):
        """Filtro de Prewitt para detección de bordes"""
        if direccion == 0:  # X
            kernel = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
        else:  # Y
            kernel = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]])
        
        resultado = cv2.filter2D(imagen, -1, kernel)
        # Normalizar y convertir a uint8
        resultado = np.abs(resultado)
        resultado = np.clip(resultado, 0, 255)
        return resultado.astype(np.uint8)
    
    def filtro_lbp(self, imagen, puntos, radio):
        """Local Binary Patterns"""
        try:
            lbp = feature.local_binary_pattern(imagen, puntos, radio, method='uniform')
            # Normalizar LBP a rango 0-255
            lbp_normalized = ((lbp - lbp.min()) / (lbp.max() - lbp.min()) * 255).astype(np.uint8)
            return lbp_normalized
        except:
            # Fallback: retornar imagen original si hay error
            return imagen
    
    def filtro_gaussiano_freq(self, imagen, sigma):
        """Filtro Gaussiano en el dominio de la frecuencia"""
        # Transformada de Fourier
        f_transform = np.fft.fft2(imagen)
        f_shift = np.fft.fftshift(f_transform)
        
        # Crear filtro gaussiano
        rows, cols = imagen.shape
        crow, ccol = rows // 2, cols // 2
        
        # Crear máscara gaussiana
        y, x = np.ogrid[:rows, :cols]
        mask = np.exp(-((x - ccol)**2 + (y - crow)**2) / (2 * sigma**2))
        
        # Aplicar filtro
        f_shift_filtered = f_shift * mask
        
        # Transformada inversa
        f_ishift = np.fft.ifftshift(f_shift_filtered)
        img_filtered = np.fft.ifft2(f_ishift)
        img_filtered = np.real(img_filtered)
        
        return np.clip(img_filtered, 0, 255).astype(np.uint8)
    
    def filtro_personalizado(self, imagen, intensidad, tipo):
        """Filtro personalizado con diferentes efectos"""
        if tipo == 1:  # Sharpen
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]) * intensidad
        elif tipo == 2:  # Emboss
            kernel = np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]]) * intensidad
        else:  # Edge detection
            kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]]) * intensidad
        
        resultado = cv2.filter2D(imagen, -1, kernel)
        return np.clip(resultado, 0, 255).astype(np.uint8)
    
    def mostrar_resultado(self):
        if self.imagen_filtrada is None:
            messagebox.showerror("Error", "Primero aplica un filtro")
            return
        
        # Crear nueva ventana
        ventana_resultado = tk.Toplevel(self.root)
        ventana_resultado.title("Resultado del Filtro")
        ventana_resultado.geometry("800x600")
        
        # Crear frame con scrollbars
        canvas = tk.Canvas(ventana_resultado)
        scrollbar_v = ttk.Scrollbar(ventana_resultado, orient="vertical", command=canvas.yview)
        scrollbar_h = ttk.Scrollbar(ventana_resultado, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # Mostrar imagen original
        ttk.Label(scrollable_frame, text="Imagen Original", font=("Arial", 12, "bold")).pack(pady=10)
        img_original_pil = Image.fromarray(self.imagen_original)
        img_original_tk = ImageTk.PhotoImage(img_original_pil)
        label_original = ttk.Label(scrollable_frame, image=img_original_tk)
        label_original.image = img_original_tk
        label_original.pack(pady=5)
        
        # Mostrar imagen filtrada
        ttk.Label(scrollable_frame, text="Imagen Filtrada", font=("Arial", 12, "bold")).pack(pady=10)
        img_filtrada_pil = Image.fromarray(self.imagen_filtrada)
        img_filtrada_tk = ImageTk.PhotoImage(img_filtrada_pil)
        label_filtrada = ttk.Label(scrollable_frame, image=img_filtrada_tk)
        label_filtrada.image = img_filtrada_tk
        label_filtrada.pack(pady=5)
        
        # Configurar scrollbars
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_v.pack(side="right", fill="y")
        scrollbar_h.pack(side="bottom", fill="x")
    
    def guardar_imagen(self):
        if self.imagen_filtrada is None:
            messagebox.showerror("Error", "Primero aplica un filtro")
            return
        
        tipos_archivo = [
            ("PNG", "*.png"),
            ("JPEG", "*.jpg"),
            ("BMP", "*.bmp"),
            ("TIFF", "*.tiff")
        ]
        
        ruta = filedialog.asksaveasfilename(
            title="Guardar Imagen Filtrada",
            defaultextension=".png",
            filetypes=tipos_archivo
        )
        
        if ruta:
            try:
                cv2.imwrite(ruta, self.imagen_filtrada)
                messagebox.showinfo("Éxito", f"Imagen guardada en: {ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

def main():
    root = tk.Tk()
    app = FiltrosImagenes(root)
    root.mainloop()

if __name__ == "__main__":
    main()
