import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.naive_bayes import GaussianNB
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import threading

class ImageSegmenterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Segmentador de Imágenes - Actividad 5.2")
        self.root.geometry("1000x700")
        
        # Variables de estado
        self.image = None
        self.image_rgb = None
        self.image_display = None
        self.positive_mask = None
        self.negative_mask = None
        self.original_image = None
        self.result_image = None
        
        # Variables para selección de rectángulos
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.current_selection_mode = None  # 'positive' o 'negative'
        self.selection_rectangles = {'positive': [], 'negative': []}
        
        # Configurar interfaz
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Panel de controles
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botón cargar imagen
        btn_load = ttk.Button(control_frame, text="Cargar Imagen", command=self.load_image)
        btn_load.grid(row=0, column=0, padx=5)
        
        # Botones de selección
        btn_positive = ttk.Button(control_frame, text="Seleccionar Región Positiva", 
                                  command=lambda: self.set_selection_mode('positive'))
        btn_positive.grid(row=0, column=1, padx=5)
        
        btn_negative = ttk.Button(control_frame, text="Seleccionar Región Negativa", 
                                  command=lambda: self.set_selection_mode('negative'))
        btn_negative.grid(row=0, column=2, padx=5)
        
        # Botón limpiar selecciones
        btn_clear = ttk.Button(control_frame, text="Limpiar Selecciones", 
                               command=self.clear_selections)
        btn_clear.grid(row=0, column=3, padx=5)
        
        # Botón procesar
        btn_process = ttk.Button(control_frame, text="Procesar y Mostrar Resultado", 
                                command=self.process_image)
        btn_process.grid(row=0, column=4, padx=5)
        
        # Label de estado
        self.status_label = ttk.Label(control_frame, text="Carga una imagen para comenzar", 
                                      foreground="blue")
        self.status_label.grid(row=1, column=0, columnspan=5, pady=5)
        
        # Canvas para mostrar imagen
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        # Canvas con scrollbars
        self.canvas = tk.Canvas(canvas_frame, bg="gray", cursor="cross")
        
        # Función para actualizar vista con restauración de selecciones
        def on_scroll(*args):
            self.canvas.xview(*args)
            self.restore_selection_rectangles()
        
        def on_vscroll(*args):
            self.canvas.yview(*args)
            self.restore_selection_rectangles()
        
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=on_scroll)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=on_vscroll)
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind eventos del canvas
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        # Mantener selecciones visibles al hacer scroll
        self.canvas.bind("<Configure>", lambda e: self.restore_selection_rectangles())
        
        # Panel de información
        info_frame = ttk.LabelFrame(main_frame, text="Información", padding="10")
        info_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.info_label = ttk.Label(info_frame, 
                                    text="1. Carga una imagen\n"
                                         "2. Selecciona región positiva (zona de interés)\n"
                                         "3. Selecciona región negativa (zona NO de interés)\n"
                                         "4. Procesa para ver el resultado")
        self.info_label.grid(row=0, column=0)
        
    def load_image(self):
        """Carga una imagen desde un archivo"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Imagen",
            filetypes=[
                ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            # Leer imagen
            self.original_image = cv2.imread(file_path)
            if self.original_image is None:
                messagebox.showerror("Error", "No se pudo cargar la imagen")
                return
            
            # Redimensionar si es muy grande
            height, width = self.original_image.shape[:2]
            max_size = 800
            if height > max_size or width > max_size:
                scale = max_size / max(height, width)
                new_width = int(width * scale)
                new_height = int(height * scale)
                self.original_image = cv2.resize(self.original_image, (new_width, new_height))
            
            self.image = self.original_image.copy()
            self.image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            
            # Inicializar máscaras
            self.positive_mask = np.zeros((self.image.shape[0], self.image.shape[1]), dtype=np.uint8)
            self.negative_mask = np.zeros((self.image.shape[0], self.image.shape[1]), dtype=np.uint8)
            
            # Limpiar selecciones anteriores
            self.clear_selections()
            
            # Mostrar imagen
            self.display_image()
            self.update_status("Imagen cargada. Selecciona las regiones positiva y negativa.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar la imagen: {str(e)}")
    
    def display_image(self):
        """Muestra la imagen en el canvas"""
        if self.image_rgb is None:
            return
        
        # Convertir a PIL Image
        pil_image = Image.fromarray(self.image_rgb)
        self.image_display = ImageTk.PhotoImage(pil_image)
        
        # Actualizar canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_display)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Restaurar rectángulos de selección
        self.restore_selection_rectangles()
    
    def set_selection_mode(self, mode):
        """Establece el modo de selección (positive o negative)"""
        if self.image_rgb is None:
            messagebox.showwarning("Advertencia", "Primero carga una imagen")
            return
        
        self.current_selection_mode = mode
        color = "green" if mode == 'positive' else "red"
        mode_text = "Positiva" if mode == 'positive' else "Negativa"
        
        # Asegurar que las selecciones existentes se mantengan visibles
        # Eliminar solo el rectángulo temporal si existe
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
        
        # Restaurar todas las selecciones para asegurar que estén visibles
        self.restore_selection_rectangles()
        
        # Mostrar información actualizada
        count_pos = len(self.selection_rectangles['positive'])
        count_neg = len(self.selection_rectangles['negative'])
        self.update_status(f"Modo: Selección {mode_text} (color {color}). Arrastra para seleccionar. "
                          f"Positivas: {count_pos}, Negativas: {count_neg}")
        
    def on_button_press(self, event):
        """Inicia la selección de rectángulo"""
        if self.current_selection_mode is None:
            return
        
        # Obtener coordenadas del canvas
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        self.start_x = canvas_x
        self.start_y = canvas_y
        
        # Eliminar solo el rectángulo temporal anterior si existe
        # NO borrar las selecciones existentes
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
    
    def on_move_press(self, event):
        """Actualiza el rectángulo mientras se arrastra"""
        if self.start_x is None or self.start_y is None or self.current_selection_mode is None:
            return
        
        # Obtener coordenadas actuales
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        
        # Eliminar solo el rectángulo temporal anterior
        # NO borrar las selecciones existentes (que tienen tag "selection")
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        
        # Determinar color
        color = "green" if self.current_selection_mode == 'positive' else "red"
        
        # Dibujar nuevo rectángulo temporal con tag diferente
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, cur_x, cur_y,
            outline=color, width=2, tags="temp_rect"
        )
    
    def on_button_release(self, event):
        """Finaliza la selección de rectángulo"""
        if self.start_x is None or self.start_y is None or self.current_selection_mode is None:
            return
        
        # Obtener coordenadas finales
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        
        # Asegurar que start < end
        x1, x2 = int(min(self.start_x, end_x)), int(max(self.start_x, end_x))
        y1, y2 = int(min(self.start_y, end_y)), int(max(self.start_y, end_y))
        
        # Verificar que el rectángulo tenga un tamaño mínimo
        if abs(x2 - x1) < 5 or abs(y2 - y1) < 5:
            # Rectángulo demasiado pequeño, ignorar
            if self.rect_id:
                self.canvas.delete(self.rect_id)
                self.rect_id = None
            self.start_x = None
            self.start_y = None
            return
        
        # Convertir coordenadas del canvas a coordenadas de la imagen
        # La imagen está en (0,0) del canvas, así que solo necesitamos ajustar por el scroll
        canvas_x0 = self.canvas.canvasx(0)
        canvas_y0 = self.canvas.canvasy(0)
        
        # Ajustar coordenadas restando el desplazamiento del scroll
        img_x1 = max(0, int(x1 - canvas_x0))
        img_y1 = max(0, int(y1 - canvas_y0))
        img_x2 = min(self.image_rgb.shape[1], int(x2 - canvas_x0))
        img_y2 = min(self.image_rgb.shape[0], int(y2 - canvas_y0))
        
        # Verificar que el área del rectángulo sea válida
        width = img_x2 - img_x1
        height = img_y2 - img_y1
        
        if width <= 0 or height <= 0:
            # Área inválida, ignorar
            if self.rect_id:
                self.canvas.delete(self.rect_id)
                self.rect_id = None
            self.start_x = None
            self.start_y = None
            return
        
        # Guardar rectángulo
        rect = (img_x1, img_y1, width, height)
        self.selection_rectangles[self.current_selection_mode].append(rect)
        
        # Aplicar a máscara (asegurar que no se sobreescriba)
        mask = self.positive_mask if self.current_selection_mode == 'positive' else self.negative_mask
        mask[img_y1:img_y2, img_x1:img_x2] = 1
        
        # Actualizar la referencia de la máscara en el objeto
        if self.current_selection_mode == 'positive':
            self.positive_mask = mask
        else:
            self.negative_mask = mask
        
        # Eliminar rectángulo temporal si existe
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
        
        # Resetear variables de arrastre
        self.start_x = None
        self.start_y = None
        
        # Actualizar visualización restaurando TODAS las selecciones (positivas y negativas)
        self.restore_selection_rectangles()
        
        # Mostrar información
        count_pos = len(self.selection_rectangles['positive'])
        count_neg = len(self.selection_rectangles['negative'])
        mode_text = "Positiva" if self.current_selection_mode == 'positive' else "Negativa"
        self.update_status(f"Región {mode_text} agregada. Total: Positivas={count_pos}, Negativas={count_neg}")
    
    def restore_selection_rectangles(self):
        """Restaura los rectángulos de selección en el canvas"""
        # Eliminar solo las selecciones existentes, no los temporales durante arrastre
        self.canvas.delete("selection")
        
        # Obtener posición del scroll
        canvas_x0 = self.canvas.canvasx(0)
        canvas_y0 = self.canvas.canvasy(0)
        
        # Dibujar rectángulos positivos
        for x, y, w, h in self.selection_rectangles['positive']:
            self.canvas.create_rectangle(
                canvas_x0 + x, canvas_y0 + y,
                canvas_x0 + x + w, canvas_y0 + y + h,
                outline="green", width=2, tags="selection"
            )
        
        # Dibujar rectángulos negativos
        for x, y, w, h in self.selection_rectangles['negative']:
            self.canvas.create_rectangle(
                canvas_x0 + x, canvas_y0 + y,
                canvas_x0 + x + w, canvas_y0 + y + h,
                outline="red", width=2, tags="selection"
            )
    
    def clear_selections(self):
        """Limpia todas las selecciones"""
        if self.image_rgb is None:
            return
        
        self.positive_mask = np.zeros((self.image.shape[0], self.image.shape[1]), dtype=np.uint8)
        self.negative_mask = np.zeros((self.image.shape[0], self.image.shape[1]), dtype=np.uint8)
        self.selection_rectangles = {'positive': [], 'negative': []}
        self.current_selection_mode = None
        self.display_image()
        self.update_status("Selecciones limpiadas")
    
    def rebuild_masks_from_rectangles(self):
        """Reconstruye las máscaras desde los rectángulos guardados"""
        if self.image_rgb is None:
            return
        
        # Reinicializar máscaras
        self.positive_mask = np.zeros((self.image.shape[0], self.image.shape[1]), dtype=np.uint8)
        self.negative_mask = np.zeros((self.image.shape[0], self.image.shape[1]), dtype=np.uint8)
        
        # Reconstruir máscara positiva desde rectángulos guardados
        for x, y, w, h in self.selection_rectangles['positive']:
            # Asegurar que las coordenadas estén dentro de los límites de la imagen
            x_end = min(self.image.shape[1], x + w)
            y_end = min(self.image.shape[0], y + h)
            x_start = max(0, x)
            y_start = max(0, y)
            
            if x_end > x_start and y_end > y_start:
                self.positive_mask[y_start:y_end, x_start:x_end] = 1
        
        # Reconstruir máscara negativa desde rectángulos guardados
        for x, y, w, h in self.selection_rectangles['negative']:
            # Asegurar que las coordenadas estén dentro de los límites de la imagen
            x_end = min(self.image.shape[1], x + w)
            y_end = min(self.image.shape[0], y + h)
            x_start = max(0, x)
            y_start = max(0, y)
            
            if x_end > x_start and y_end > y_start:
                self.negative_mask[y_start:y_end, x_start:x_end] = 1
    
    def process_image(self):
        """Procesa la imagen con el clasificador Naive Bayes"""
        if self.image_rgb is None:
            messagebox.showwarning("Advertencia", "Primero carga una imagen")
            return
        
        # Verificar que las máscaras existan
        if self.positive_mask is None or self.negative_mask is None:
            messagebox.showwarning("Advertencia", 
                                 "No se han inicializado las máscaras. Carga una imagen primero.")
            return
        
        # Reconstruir máscaras desde rectángulos para asegurar sincronización
        self.rebuild_masks_from_rectangles()
        
        positive_sum = np.sum(self.positive_mask)
        negative_sum = np.sum(self.negative_mask)
        
        # Debug: mostrar información de las máscaras
        count_pos_rects = len(self.selection_rectangles['positive'])
        count_neg_rects = len(self.selection_rectangles['negative'])
        
        if positive_sum == 0 or negative_sum == 0:
            msg = (f"Debes seleccionar al menos una región positiva y una negativa.\n"
                   f"Regiones positivas seleccionadas: {count_pos_rects} (píxeles: {positive_sum})\n"
                   f"Regiones negativas seleccionadas: {count_neg_rects} (píxeles: {negative_sum})")
            messagebox.showwarning("Advertencia", msg)
            return
        
        try:
            self.update_status("Procesando...")
            self.root.update()
            
            # Extraer canales RGB
            R = self.image_rgb[:, :, 0]
            G = self.image_rgb[:, :, 1]
            B = self.image_rgb[:, :, 2]
            
            # Extraer características de las regiones
            PositiveExamplesR = R[self.positive_mask == 1]
            NegativeExamplesR = R[self.negative_mask == 1]
            
            PositiveExamplesG = G[self.positive_mask == 1]
            NegativeExamplesG = G[self.negative_mask == 1]
            
            PositiveExamplesB = B[self.positive_mask == 1]
            NegativeExamplesB = B[self.negative_mask == 1]
            
            # Crear matrices de características
            PositiveFeatures = np.column_stack((PositiveExamplesR, PositiveExamplesG, PositiveExamplesB))
            NegativeFeatures = np.column_stack((NegativeExamplesR, NegativeExamplesG, NegativeExamplesB))
            
            # Preparar datos de entrenamiento
            training = np.vstack((PositiveFeatures, NegativeFeatures))
            Classes = np.hstack((np.ones(PositiveFeatures.shape[0]), np.zeros(NegativeFeatures.shape[0])))
            
            # Entrenar clasificador Naive Bayes
            nb = GaussianNB()
            nb.fit(training, Classes)
            
            # Preparar datos de prueba (todos los píxeles)
            test = np.column_stack((R.flatten(), G.flatten(), B.flatten()))
            
            # Predecir
            predictions = nb.predict(test)
            
            # Remodelar predicción a dimensiones originales
            result = predictions.reshape((self.image.shape[0], self.image.shape[1]))
            
            self.result_image = result
            
            # Mostrar resultados en ventana separada
            self.show_results()
            
            self.update_status("Procesamiento completado. Resultado mostrado en ventana separada.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar: {str(e)}")
            self.update_status("Error en el procesamiento")
    
    def show_results(self):
        """Muestra los resultados en una ventana separada con matplotlib"""
        if self.image_rgb is None or self.result_image is None:
            return
        
        # Crear figura con dos subplots
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Imagen original
        axes[0].imshow(self.image_rgb)
        axes[0].set_title('Imagen Original', fontsize=14, fontweight='bold')
        axes[0].axis('off')
        
        # Imagen resultado
        result_display = self.result_image.astype(float)
        im = axes[1].imshow(result_display, cmap='viridis', vmin=0, vmax=1)
        axes[1].set_title('Resultado de la Clasificación', fontsize=14, fontweight='bold')
        axes[1].axis('off')
        
        # Agregar colorbar
        plt.colorbar(im, ax=axes[1], fraction=0.046, pad=0.04)
        
        plt.tight_layout()
        plt.show()
    
    def update_status(self, message):
        """Actualiza el mensaje de estado"""
        self.status_label.config(text=message)
        self.root.update_idletasks()


def main():
    root = tk.Tk()
    app = ImageSegmenterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

