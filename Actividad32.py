import numpy as np
import cv2
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class CombinadorCanalesRGB:
    def __init__(self, root):
        self.root = root
        self.root.title("Combinador de Canales RGB - Actividad 3.2")
        
        # Obtener dimensiones de la pantalla
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Establecer ventana al 90% del tamaño de la pantalla
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        
        # Centrar la ventana
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Permitir maximizar
        self.root.state('zoomed')  # Maximizar en Windows
        
        # Variables para las imágenes
        self.imagen1 = None
        self.imagen2 = None
        self.imagen1_rgb = None
        self.imagen2_rgb = None
        self.imagenes_resultantes = []
        
        # Variables para los porcentajes (3 combinaciones completas)
        self.porcentajes = {
            'comb1': {
                'rojo_img1': tk.DoubleVar(value=65), 'rojo_img2': tk.DoubleVar(value=35),
                'verde_img1': tk.DoubleVar(value=50), 'verde_img2': tk.DoubleVar(value=50),
                'azul_img1': tk.DoubleVar(value=30), 'azul_img2': tk.DoubleVar(value=70)
            },
            'comb2': {
                'rojo_img1': tk.DoubleVar(value=40), 'rojo_img2': tk.DoubleVar(value=60),
                'verde_img1': tk.DoubleVar(value=70), 'verde_img2': tk.DoubleVar(value=30),
                'azul_img1': tk.DoubleVar(value=55), 'azul_img2': tk.DoubleVar(value=45)
            },
            'comb3': {
                'rojo_img1': tk.DoubleVar(value=20), 'rojo_img2': tk.DoubleVar(value=80),
                'verde_img1': tk.DoubleVar(value=35), 'verde_img2': tk.DoubleVar(value=65),
                'azul_img1': tk.DoubleVar(value=75), 'azul_img2': tk.DoubleVar(value=25)
            }
        }
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Crear canvas y scrollbar
        canvas = tk.Canvas(self.root, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding="10")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Posicionar canvas y scrollbar
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind mousewheel para scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Frame principal con scroll
        main_frame = scrollable_frame
        
        # === SECCIÓN 1: Selección de imágenes ===
        seccion_imagenes = ttk.LabelFrame(main_frame, text="Selección de Imágenes", padding="10")
        seccion_imagenes.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Botón para Imagen 1
        ttk.Label(seccion_imagenes, text="Corte 1:").grid(row=0, column=0, padx=5, pady=5)
        self.btn_img1 = ttk.Button(seccion_imagenes, text="Seleccionar Imagen 1", 
                                    command=lambda: self.cargar_imagen(1))
        self.btn_img1.grid(row=0, column=1, padx=5, pady=5)
        self.label_img1 = ttk.Label(seccion_imagenes, text="No seleccionada", foreground="red")
        self.label_img1.grid(row=0, column=2, padx=5, pady=5)
        
        # Botón para Imagen 2
        ttk.Label(seccion_imagenes, text="Corte 2:").grid(row=1, column=0, padx=5, pady=5)
        self.btn_img2 = ttk.Button(seccion_imagenes, text="Seleccionar Imagen 2", 
                                    command=lambda: self.cargar_imagen(2))
        self.btn_img2.grid(row=1, column=1, padx=5, pady=5)
        self.label_img2 = ttk.Label(seccion_imagenes, text="No seleccionada", foreground="red")
        self.label_img2.grid(row=1, column=2, padx=5, pady=5)
        
        # === SECCIÓN 2: Control de Combinaciones ===
        seccion_controles = ttk.LabelFrame(main_frame, text="Configuración de Combinaciones", padding="10")
        seccion_controles.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Combinación 1
        self.crear_control_combinacion(seccion_controles, 0, 'comb1', 'Combinación 1')
        
        # Combinación 2
        self.crear_control_combinacion(seccion_controles, 1, 'comb2', 'Combinación 2')
        
        # Combinación 3
        self.crear_control_combinacion(seccion_controles, 2, 'comb3', 'Combinación 3')
        
        # === SECCIÓN 3: Botones de acción ===
        seccion_botones = ttk.Frame(main_frame, padding="10")
        seccion_botones.grid(row=2, column=0, columnspan=3, pady=10)
        
        # Configurar peso de columnas para distribución
        seccion_botones.columnconfigure(0, weight=1)
        seccion_botones.columnconfigure(1, weight=0)
        
        # Frame izquierdo para botones principales
        frame_botones_izq = ttk.Frame(seccion_botones)
        frame_botones_izq.grid(row=0, column=0, sticky=tk.W)
        
        self.btn_generar = ttk.Button(frame_botones_izq, text="Generar Combinaciones", 
                                       command=self.generar_combinaciones, style='Accent.TButton')
        self.btn_generar.grid(row=0, column=0, padx=5)
        
        self.btn_guardar = ttk.Button(frame_botones_izq, text="Guardar Resultados", 
                                       command=self.guardar_resultados, state='disabled')
        self.btn_guardar.grid(row=0, column=1, padx=5)
        
        self.btn_limpiar = ttk.Button(frame_botones_izq, text="Limpiar Todo", 
                                       command=self.limpiar_todo)
        self.btn_limpiar.grid(row=0, column=2, padx=5)
        
        # Frame derecho para botones de visualización
        frame_botones_der = ttk.Frame(seccion_botones)
        frame_botones_der.grid(row=0, column=1, sticky=tk.E, padx=(20, 0))
        
        self.btn_ver_originales = ttk.Button(frame_botones_der, text="Ver Imágenes Originales", 
                                             command=self.mostrar_ventana_originales, state='disabled')
        self.btn_ver_originales.grid(row=0, column=0, padx=5)
        
        self.btn_ver_resultados = ttk.Button(frame_botones_der, text="Ver Imágenes Resultantes", 
                                             command=self.mostrar_ventana_resultados, state='disabled')
        self.btn_ver_resultados.grid(row=0, column=1, padx=5)
        
        # === SECCIÓN 4: Previsualización ===
        seccion_preview = ttk.LabelFrame(main_frame, text="Imágenes Originales", padding="10")
        seccion_preview.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.preview_frame = ttk.Frame(seccion_preview)
        self.preview_frame.grid(row=0, column=0)
        
        # Canvas para preview de imágenes originales
        self.canvas_img1 = tk.Canvas(self.preview_frame, width=250, height=250, bg='gray')
        self.canvas_img1.grid(row=0, column=0, padx=10, pady=5)
        ttk.Label(self.preview_frame, text="Imagen 1").grid(row=1, column=0)
        
        self.canvas_img2 = tk.Canvas(self.preview_frame, width=250, height=250, bg='gray')
        self.canvas_img2.grid(row=0, column=1, padx=10, pady=5)
        ttk.Label(self.preview_frame, text="Imagen 2").grid(row=1, column=1)
        
        # === SECCIÓN 5: Resultados ===
        seccion_resultados = ttk.LabelFrame(main_frame, text="Imágenes Resultantes", padding="10")
        seccion_resultados.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.resultados_frame = ttk.Frame(seccion_resultados)
        self.resultados_frame.grid(row=0, column=0)
        
        # Canvas para las 3 imágenes resultantes
        self.canvas_results = []
        for i in range(3):
            canvas = tk.Canvas(self.resultados_frame, width=250, height=250, bg='gray')
            canvas.grid(row=0, column=i, padx=10, pady=5)
            self.canvas_results.append(canvas)
            ttl = ttk.Label(self.resultados_frame, text=f"Combinación {i+1}")
            ttl.grid(row=1, column=i)
    
    def crear_control_combinacion(self, parent, row, comb_id, titulo):
        """Crea los controles para una combinación completa RGB"""
        frame = ttk.LabelFrame(parent, text=titulo, padding="10")
        frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Almacenar labels para actualizar
        self.porcentajes[comb_id]['labels'] = {}
        
        # Crear controles para cada canal (Rojo, Verde, Azul)
        canales = [
            ('Rojo', 'rojo', '#FF6B6B'),
            ('Verde', 'verde', '#51CF66'),
            ('Azul', 'azul', '#4DABF7')
        ]
        
        for idx, (nombre_canal, key_canal, color) in enumerate(canales):
            # Frame para cada canal
            canal_frame = ttk.Frame(frame)
            canal_frame.grid(row=idx, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=5)
            
            # Etiqueta del canal con color
            label_canal = ttk.Label(canal_frame, text=f"{nombre_canal}:", 
                                   font=('Arial', 9, 'bold'), foreground=color, width=8)
            label_canal.grid(row=0, column=0, padx=5)
            
            # Imagen 1
            ttk.Label(canal_frame, text="Img1:").grid(row=0, column=1, padx=2)
            scale1 = ttk.Scale(canal_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=150,
                              variable=self.porcentajes[comb_id][f'{key_canal}_img1'],
                              command=lambda v, c=comb_id, k=key_canal: self.actualizar_labels(c, k))
            scale1.grid(row=0, column=2, padx=5)
            
            label1 = ttk.Label(canal_frame, 
                              text=f"{self.porcentajes[comb_id][f'{key_canal}_img1'].get():.0f}%",
                              width=5)
            label1.grid(row=0, column=3, padx=2)
            self.porcentajes[comb_id]['labels'][f'{key_canal}_img1'] = label1
            
            # Imagen 2
            ttk.Label(canal_frame, text="Img2:").grid(row=0, column=4, padx=2)
            scale2 = ttk.Scale(canal_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=150,
                              variable=self.porcentajes[comb_id][f'{key_canal}_img2'],
                              command=lambda v, c=comb_id, k=key_canal: self.actualizar_labels(c, k))
            scale2.grid(row=0, column=5, padx=5)
            
            label2 = ttk.Label(canal_frame, 
                              text=f"{self.porcentajes[comb_id][f'{key_canal}_img2'].get():.0f}%",
                              width=5)
            label2.grid(row=0, column=6, padx=2)
            self.porcentajes[comb_id]['labels'][f'{key_canal}_img2'] = label2
    
    def actualizar_labels(self, comb_id, canal):
        """Actualiza los labels de porcentaje para un canal específico"""
        val1 = self.porcentajes[comb_id][f'{canal}_img1'].get()
        val2 = self.porcentajes[comb_id][f'{canal}_img2'].get()
        
        self.porcentajes[comb_id]['labels'][f'{canal}_img1'].config(text=f"{val1:.0f}%")
        self.porcentajes[comb_id]['labels'][f'{canal}_img2'].config(text=f"{val2:.0f}%")
    
    def cargar_imagen(self, num_imagen):
        """Carga una imagen desde el disco"""
        filename = filedialog.askopenfilename(
            title=f"Seleccionar Imagen {num_imagen}",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tiff"), ("Todos los archivos", "*.*")]
        )
        
        if filename:
            # Leer imagen con OpenCV (BGR)
            img = cv2.imread(filename)
            
            if img is None:
                messagebox.showerror("Error", f"No se pudo cargar la imagen {num_imagen}")
                return
            
            # Convertir a RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            if num_imagen == 1:
                self.imagen1 = img
                self.imagen1_rgb = img_rgb
                self.label_img1.config(text=filename.split('/')[-1], foreground="green")
                self.mostrar_preview(img_rgb, self.canvas_img1)
            else:
                self.imagen2 = img
                self.imagen2_rgb = img_rgb
                self.label_img2.config(text=filename.split('/')[-1], foreground="green")
                self.mostrar_preview(img_rgb, self.canvas_img2)
            
            # Abrir ventana de originales automáticamente si ambas imágenes están cargadas
            if self.imagen1_rgb is not None and self.imagen2_rgb is not None:
                self.btn_ver_originales.config(state='normal')
                self.mostrar_ventana_originales()
    
    def mostrar_preview(self, img_rgb, canvas):
        """Muestra una vista previa de la imagen en el canvas"""
        # Redimensionar para preview
        h, w = img_rgb.shape[:2]
        max_size = 250
        
        if h > w:
            new_h = max_size
            new_w = int(w * (max_size / h))
        else:
            new_w = max_size
            new_h = int(h * (max_size / w))
        
        img_resized = cv2.resize(img_rgb, (new_w, new_h))
        
        # Convertir a ImageTk
        img_pil = Image.fromarray(img_resized)
        img_tk = ImageTk.PhotoImage(img_pil)
        
        # Mostrar en canvas
        canvas.delete("all")
        canvas.create_image(125, 125, image=img_tk)
        canvas.image = img_tk  # Mantener referencia
    
    def generar_combinaciones(self):
        """Genera las tres imágenes combinadas con todos los canales RGB"""
        # Verificar que ambas imágenes estén cargadas
        if self.imagen1_rgb is None or self.imagen2_rgb is None:
            messagebox.showwarning("Advertencia", "Debe seleccionar ambas imágenes primero")
            return
        
        # Verificar que las imágenes tengan el mismo tamaño
        if self.imagen1_rgb.shape != self.imagen2_rgb.shape:
            messagebox.showwarning("Advertencia", 
                                   "Las imágenes deben tener el mismo tamaño.\n" +
                                   f"Imagen 1: {self.imagen1_rgb.shape}\n" +
                                   f"Imagen 2: {self.imagen2_rgb.shape}\n\n" +
                                   "Redimensionando a la más pequeña...")
            # Redimensionar a la más pequeña
            h1, w1 = self.imagen1_rgb.shape[:2]
            h2, w2 = self.imagen2_rgb.shape[:2]
            h_min = min(h1, h2)
            w_min = min(w1, w2)
            
            self.imagen1_rgb = cv2.resize(self.imagen1_rgb, (w_min, h_min))
            self.imagen2_rgb = cv2.resize(self.imagen2_rgb, (w_min, h_min))
        
        # Separar canales de ambas imágenes
        r1, g1, b1 = cv2.split(self.imagen1_rgb)
        r2, g2, b2 = cv2.split(self.imagen2_rgb)
        
        self.imagenes_resultantes = []
        
        # Generar las 3 combinaciones completas
        for i, comb_id in enumerate(['comb1', 'comb2', 'comb3']):
            # Obtener porcentajes para cada canal
            p_rojo_img1 = self.porcentajes[comb_id]['rojo_img1'].get() / 100.0
            p_rojo_img2 = self.porcentajes[comb_id]['rojo_img2'].get() / 100.0
            
            p_verde_img1 = self.porcentajes[comb_id]['verde_img1'].get() / 100.0
            p_verde_img2 = self.porcentajes[comb_id]['verde_img2'].get() / 100.0
            
            p_azul_img1 = self.porcentajes[comb_id]['azul_img1'].get() / 100.0
            p_azul_img2 = self.porcentajes[comb_id]['azul_img2'].get() / 100.0
            
            # Combinar cada canal independientemente
            canal_rojo = (r1 * p_rojo_img1 + r2 * p_rojo_img2).astype(np.uint8)
            canal_verde = (g1 * p_verde_img1 + g2 * p_verde_img2).astype(np.uint8)
            canal_azul = (b1 * p_azul_img1 + b2 * p_azul_img2).astype(np.uint8)
            
            # Crear imagen RGB combinada
            img_resultado = cv2.merge([canal_rojo, canal_verde, canal_azul])
            
            self.imagenes_resultantes.append(img_resultado)
            
            # Mostrar resultado
            self.mostrar_preview(img_resultado, self.canvas_results[i])
        
        # Habilitar botones
        self.btn_guardar.config(state='normal')
        self.btn_ver_resultados.config(state='normal')
        
        messagebox.showinfo("Éxito", "¡Combinaciones generadas exitosamente!")
        
        # Abrir ventana de resultados automáticamente
        self.mostrar_ventana_resultados()
    
    def guardar_resultados(self):
        """Guarda las imágenes resultantes"""
        if not self.imagenes_resultantes:
            messagebox.showwarning("Advertencia", "No hay imágenes para guardar")
            return
        
        directorio = filedialog.askdirectory(title="Seleccionar carpeta para guardar")
        
        if directorio:
            for i, img_rgb in enumerate(self.imagenes_resultantes):
                comb_id = f'comb{i+1}'
                
                # Obtener porcentajes de cada canal
                r1 = self.porcentajes[comb_id]['rojo_img1'].get()
                r2 = self.porcentajes[comb_id]['rojo_img2'].get()
                g1 = self.porcentajes[comb_id]['verde_img1'].get()
                g2 = self.porcentajes[comb_id]['verde_img2'].get()
                b1 = self.porcentajes[comb_id]['azul_img1'].get()
                b2 = self.porcentajes[comb_id]['azul_img2'].get()
                
                filename = f"{directorio}/combinacion_{i+1}_R{r1:.0f}-{r2:.0f}_G{g1:.0f}-{g2:.0f}_B{b1:.0f}-{b2:.0f}.jpg"
                
                # Convertir RGB a BGR para guardar con OpenCV
                img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
                cv2.imwrite(filename, img_bgr)
            
            messagebox.showinfo("Éxito", f"Se guardaron {len(self.imagenes_resultantes)} imágenes en:\n{directorio}")
    
    def limpiar_todo(self):
        """Limpia todas las imágenes y reinicia la interfaz"""
        self.imagen1 = None
        self.imagen2 = None
        self.imagen1_rgb = None
        self.imagen2_rgb = None
        self.imagenes_resultantes = []
        
        self.label_img1.config(text="No seleccionada", foreground="red")
        self.label_img2.config(text="No seleccionada", foreground="red")
        
        self.canvas_img1.delete("all")
        self.canvas_img2.delete("all")
        
        for canvas in self.canvas_results:
            canvas.delete("all")
        
        self.btn_guardar.config(state='disabled')
        self.btn_ver_originales.config(state='disabled')
        self.btn_ver_resultados.config(state='disabled')
    
    def mostrar_ventana_originales(self):
        """Muestra las imágenes originales en una ventana nueva"""
        if self.imagen1_rgb is None or self.imagen2_rgb is None:
            messagebox.showwarning("Advertencia", "Debe cargar ambas imágenes primero")
            return
        
        # Crear ventana nueva
        ventana = tk.Toplevel(self.root)
        ventana.title("Imágenes Originales")
        ventana.geometry("1000x500")
        
        # Crear figura de matplotlib
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle('Imágenes Originales', fontsize=16, fontweight='bold')
        
        # Mostrar Imagen 1
        axes[0].imshow(self.imagen1_rgb)
        axes[0].set_title('Corte 1', fontsize=12, fontweight='bold')
        axes[0].axis('off')
        
        # Mostrar Imagen 2
        axes[1].imshow(self.imagen2_rgb)
        axes[1].set_title('Corte 2', fontsize=12, fontweight='bold')
        axes[1].axis('off')
        
        plt.tight_layout()
        
        # Incrustar figura en la ventana de tkinter
        canvas = FigureCanvasTkAgg(fig, master=ventana)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Botón para cerrar
        btn_cerrar = ttk.Button(ventana, text="Cerrar", command=ventana.destroy)
        btn_cerrar.pack(pady=10)
    
    def mostrar_ventana_resultados(self):
        """Muestra las imágenes resultantes en una ventana nueva"""
        if not self.imagenes_resultantes:
            messagebox.showwarning("Advertencia", "Debe generar las combinaciones primero")
            return
        
        # Crear ventana nueva
        ventana = tk.Toplevel(self.root)
        ventana.title("Imágenes Resultantes")
        ventana.geometry("1400x500")
        
        # Crear figura de matplotlib
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle('Imágenes Resultantes - Combinaciones RGB', fontsize=16, fontweight='bold')
        
        # Mostrar las 3 combinaciones
        for i, img_rgb in enumerate(self.imagenes_resultantes):
            comb_id = f'comb{i+1}'
            
            # Obtener porcentajes para el título
            r1 = self.porcentajes[comb_id]['rojo_img1'].get()
            r2 = self.porcentajes[comb_id]['rojo_img2'].get()
            g1 = self.porcentajes[comb_id]['verde_img1'].get()
            g2 = self.porcentajes[comb_id]['verde_img2'].get()
            b1 = self.porcentajes[comb_id]['azul_img1'].get()
            b2 = self.porcentajes[comb_id]['azul_img2'].get()
            
            axes[i].imshow(img_rgb)
            titulo = f'Combinación {i+1}\nR:{r1:.0f}-{r2:.0f}% G:{g1:.0f}-{g2:.0f}% B:{b1:.0f}-{b2:.0f}%'
            axes[i].set_title(titulo, fontsize=10, fontweight='bold')
            axes[i].axis('off')
        
        plt.tight_layout()
        
        # Incrustar figura en la ventana de tkinter
        canvas = FigureCanvasTkAgg(fig, master=ventana)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Botón para cerrar
        btn_cerrar = ttk.Button(ventana, text="Cerrar", command=ventana.destroy)
        btn_cerrar.pack(pady=10)


def main():
    root = tk.Tk()
    app = CombinadorCanalesRGB(root)
    root.mainloop()


if __name__ == "__main__":
    main()

