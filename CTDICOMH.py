import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pydicom
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector
import os

class DICOMHistogramViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador DICOM con Histogramas y Ajuste de Rango Dinámico")
        self.root.geometry("1400x900")
        
        # Lista para almacenar los archivos DICOM
        self.dicom_files = []
        self.dicom_data = []
        self.current_image = None
        self.current_dicom = None
        self.roi_coords = None
        self.roi_selector = None
        
        # Crear la interfaz
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame para botones
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botón para cargar archivos DICOM
        load_button = tk.Button(button_frame, text="Cargar Archivos DICOM", 
                               command=self.load_dicom_files, bg="#4CAF50", fg="white",
                               font=("Arial", 12, "bold"))
        load_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón para mostrar histogramas
        histogram_button = tk.Button(button_frame, text="Mostrar Histogramas", 
                                   command=self.show_histograms, bg="#2196F3", fg="white",
                                   font=("Arial", 12, "bold"))
        histogram_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón para seleccionar ROI
        roi_button = tk.Button(button_frame, text="Seleccionar ROI", 
                              command=self.select_roi, bg="#FF9800", fg="white",
                              font=("Arial", 12, "bold"))
        roi_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón para ajustar rango dinámico
        adjust_button = tk.Button(button_frame, text="Ajustar Rango Dinámico", 
                                 command=self.adjust_dynamic_range, bg="#9C27B0", fg="white",
                                 font=("Arial", 12, "bold"))
        adjust_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón para limpiar
        clear_button = tk.Button(button_frame, text="Limpiar", 
                                command=self.clear_all, bg="#f44336", fg="white",
                                font=("Arial", 12, "bold"))
        clear_button.pack(side=tk.LEFT)
        
        # Frame para controles de rango dinámico
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Controles para rango dinámico
        tk.Label(control_frame, text="Rango Dinámico:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(control_frame, text="Min:").pack(side=tk.LEFT, padx=(0, 5))
        self.min_entry = tk.Entry(control_frame, width=10)
        self.min_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(control_frame, text="Max:").pack(side=tk.LEFT, padx=(0, 5))
        self.max_entry = tk.Entry(control_frame, width=10)
        self.max_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Checkbox para usar ROI
        self.use_roi_var = tk.BooleanVar()
        self.use_roi_check = tk.Checkbutton(control_frame, text="Usar ROI para ajuste", 
                                           variable=self.use_roi_var)
        self.use_roi_check.pack(side=tk.LEFT, padx=(20, 0))
        
        # Frame para mostrar información de archivos
        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Lista de archivos cargados
        tk.Label(info_frame, text="Archivos DICOM cargados:", 
                font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.file_listbox = tk.Listbox(info_frame, height=3, font=("Arial", 9))
        self.file_listbox.pack(fill=tk.X, pady=(5, 0))
        
        # Frame para matplotlib
        self.plot_frame = tk.Frame(main_frame)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)
        
    def load_dicom_files(self):
        """Cargar archivos DICOM usando un diálogo de archivos"""
        file_types = [
            ("Archivos DICOM", "*.dcm"),
            ("Todos los archivos", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Seleccionar archivos DICOM (máximo 3)",
            filetypes=file_types
        )
        
        if files:
            # Limitar a 3 archivos
            self.dicom_files = list(files)[:3]
            self.dicom_data = []
            
            # Actualizar la lista de archivos
            self.file_listbox.delete(0, tk.END)
            for file_path in self.dicom_files:
                filename = os.path.basename(file_path)
                self.file_listbox.insert(tk.END, filename)
            
            messagebox.showinfo("Éxito", f"Se cargaron {len(self.dicom_files)} archivo(s) DICOM")
    
    def ajuste_rango_dinamico(self, imagen, min_entrada=None, max_entrada=None):
        """
        Función adaptada de Actividad31.py para ajustar el rango dinámico de una imagen DICOM
        """
        # Convertir a tipo float
        imagen = imagen.astype(float)
        
        # Obtener dimensiones
        m, n = imagen.shape[:2]
        
        # Determinar los valores mínimo y máximo
        if min_entrada is None:
            minI = np.min(imagen)
        else:
            minI = min_entrada
            
        if max_entrada is None:
            maxI = np.max(imagen)
        else:
            maxI = max_entrada
        
        # Evitar división por cero
        if maxI == minI:
            print('Advertencia: Los valores mínimo y máximo son iguales')
            O = np.zeros((m, n), dtype=np.uint8)
            return O
        
        # Calcular pendiente y término independiente
        Pendiente = 255.0 / (maxI - minI)
        b = -Pendiente * minI
        
        # Aplicar transformación lineal usando operaciones vectorizadas
        O = Pendiente * imagen + b
        
        # Asegurar que los valores estén en el rango [0, 255]
        O = np.clip(O, 0, 255)
        
        # Convertir a uint8
        O = O.astype(np.uint8)
        
        return O
    
    def show_histograms(self):
        """Mostrar histogramas de los archivos DICOM"""
        if not self.dicom_files:
            messagebox.showwarning("Advertencia", "Primero debe cargar archivos DICOM")
            return
        
        # Limpiar el frame de plots
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        
        try:
            # Crear figura de matplotlib
            fig = Figure(figsize=(15, 10), dpi=100)
            
            # Determinar el número de archivos a mostrar (máximo 3)
            num_files = min(len(self.dicom_files), 3)
            
            # Crear subplots: 2 filas, 3 columnas (imagen + histograma por archivo)
            for i in range(num_files):
                try:
                    # Leer archivo DICOM
                    dicom_data = pydicom.dcmread(self.dicom_files[i])
                    image = dicom_data.pixel_array
                    
                    # Almacenar la primera imagen como imagen actual
                    if i == 0:
                        self.current_image = image
                        self.current_dicom = dicom_data
                    
                    # Subplot para la imagen
                    ax_img = fig.add_subplot(2, 3, i+1)
                    ax_img.imshow(image, cmap='gray')
                    ax_img.set_title(f'DICOM {i+1}: {os.path.basename(self.dicom_files[i])}', 
                                    fontsize=10, fontweight='bold')
                    ax_img.axis('off')
                    
                    # Subplot para el histograma
                    ax_hist = fig.add_subplot(2, 3, i+4)
                    hist, bins = np.histogram(image.flatten(), bins=256, range=(0, 256))
                    ax_hist.plot(bins[:-1], hist, 'b-', linewidth=1)
                    ax_hist.set_title(f'Histograma DICOM {i+1}', fontsize=10, fontweight='bold')
                    ax_hist.set_xlabel('Valor de píxel')
                    ax_hist.set_ylabel('Frecuencia')
                    ax_hist.grid(True, alpha=0.3)
                    
                    # Agregar estadísticas del histograma
                    mean_val = np.mean(image)
                    std_val = np.std(image)
                    min_val = np.min(image)
                    max_val = np.max(image)
                    
                    stats_text = f'Min: {min_val:.1f}\nMax: {max_val:.1f}\nMedia: {mean_val:.1f}\nStd: {std_val:.1f}'
                    ax_hist.text(0.02, 0.98, stats_text, transform=ax_hist.transAxes, 
                               fontsize=8, verticalalignment='top',
                               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                    
                except Exception as e:
                    # Mostrar error en ambos subplots
                    ax_img = fig.add_subplot(2, 3, i+1)
                    ax_img.text(0.5, 0.5, f'Error al cargar\n{os.path.basename(self.dicom_files[i])}\n{str(e)}', 
                               transform=ax_img.transAxes, ha='center', va='center',
                               fontsize=10, color='red')
                    ax_img.set_title(f'Error en DICOM {i+1}', fontsize=10, color='red')
                    ax_img.axis('off')
                    
                    ax_hist = fig.add_subplot(2, 3, i+4)
                    ax_hist.text(0.5, 0.5, f'Error al cargar\nhistograma', 
                               transform=ax_hist.transAxes, ha='center', va='center',
                               fontsize=10, color='red')
                    ax_hist.set_title(f'Error Histograma {i+1}', fontsize=10, color='red')
                    ax_hist.axis('off')
            
            # Ajustar layout
            fig.tight_layout()
            
            # Crear canvas de matplotlib
            canvas = FigureCanvasTkAgg(fig, self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar los histogramas: {str(e)}")
    
    def select_roi(self):
        """Permitir al usuario seleccionar una región de interés (ROI) en la imagen"""
        if self.current_image is None:
            messagebox.showwarning("Advertencia", "Primero debe mostrar los histogramas para seleccionar una imagen")
            return
        
        # Limpiar el frame de plots
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        
        try:
            # Crear figura para selección de ROI
            fig = Figure(figsize=(10, 8), dpi=100)
            ax = fig.add_subplot(111)
            ax.imshow(self.current_image, cmap='gray')
            ax.set_title('Seleccione una región de interés (ROI) arrastrando el mouse', 
                        fontsize=12, fontweight='bold')
            ax.axis('off')
            
            # Función para manejar la selección de ROI
            def onselect(eclick, erelease):
                self.roi_coords = (int(eclick.xdata), int(eclick.ydata), 
                                 int(erelease.xdata), int(erelease.ydata))
                print(f"ROI seleccionada: {self.roi_coords}")
                
                # Mostrar información de la ROI
                x1, y1, x2, y2 = self.roi_coords
                roi_image = self.current_image[y1:y2, x1:x2]
                
                # Actualizar los campos de entrada con los valores de la ROI
                self.min_entry.delete(0, tk.END)
                self.max_entry.delete(0, tk.END)
                self.min_entry.insert(0, str(int(np.min(roi_image))))
                self.max_entry.insert(0, str(int(np.max(roi_image))))
                
                messagebox.showinfo("ROI Seleccionada", 
                                  f"ROI seleccionada:\nMin: {np.min(roi_image):.1f}\nMax: {np.max(roi_image):.1f}\n"
                                  f"Media: {np.mean(roi_image):.1f}\nStd: {np.std(roi_image):.1f}")
            
            # Crear selector de rectángulo
            self.roi_selector = RectangleSelector(ax, onselect, useblit=True,
                                                button=[1], minspanx=5, minspany=5,
                                                spancoords='pixels', interactive=True)
            
            # Crear canvas de matplotlib
            canvas = FigureCanvasTkAgg(fig, self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al seleccionar ROI: {str(e)}")
    
    def adjust_dynamic_range(self):
        """Ajustar el rango dinámico de la imagen DICOM"""
        if self.current_image is None:
            messagebox.showwarning("Advertencia", "Primero debe mostrar los histogramas")
            return
        
        try:
            # Obtener valores de entrada
            min_val = self.min_entry.get()
            max_val = self.max_entry.get()
            
            if not min_val or not max_val:
                messagebox.showwarning("Advertencia", "Debe especificar valores mínimo y máximo")
                return
            
            min_val = float(min_val)
            max_val = float(max_val)
            
            # Si se seleccionó usar ROI, calcular estadísticas de la ROI
            if self.use_roi_var.get() and self.roi_coords is not None:
                x1, y1, x2, y2 = self.roi_coords
                roi_image = self.current_image[y1:y2, x1:x2]
                min_roi = np.min(roi_image)
                max_roi = np.max(roi_image)
                mean_roi = np.mean(roi_image)
                std_roi = np.std(roi_image)
                
                # Usar estadísticas de la ROI para el ajuste
                min_entrada = mean_roi - 2 * std_roi  # 2 desviaciones estándar
                max_entrada = mean_roi + 2 * std_roi
            else:
                min_entrada = min_val
                max_entrada = max_val
            
            # Aplicar ajuste de rango dinámico
            imagen_ajustada = self.ajuste_rango_dinamico(self.current_image, min_entrada, max_entrada)
            
            # Mostrar resultados
            self.show_adjustment_results(self.current_image, imagen_ajustada, min_entrada, max_entrada)
            
        except ValueError:
            messagebox.showerror("Error", "Los valores de entrada deben ser números válidos")
        except Exception as e:
            messagebox.showerror("Error", f"Error al ajustar el rango dinámico: {str(e)}")
    
    def show_adjustment_results(self, imagen_original, imagen_ajustada, min_val, max_val):
        """Mostrar los resultados del ajuste de rango dinámico"""
        # Limpiar el frame de plots
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        
        try:
            # Crear figura con 4 subplots
            fig = Figure(figsize=(15, 10), dpi=100)
            
            # Imagen original
            ax1 = fig.add_subplot(2, 3, 1)
            ax1.imshow(imagen_original, cmap='gray')
            ax1.set_title('Imagen Original', fontsize=12, fontweight='bold')
            ax1.axis('off')
            
            # Imagen ajustada
            ax2 = fig.add_subplot(2, 3, 2)
            ax2.imshow(imagen_ajustada, cmap='gray')
            ax2.set_title('Imagen Ajustada', fontsize=12, fontweight='bold')
            ax2.axis('off')
            
            # Diferencia
            ax3 = fig.add_subplot(2, 3, 3)
            diferencia = imagen_ajustada.astype(float) - imagen_original.astype(float)
            im_diff = ax3.imshow(diferencia, cmap='RdBu_r')
            ax3.set_title('Diferencia (Ajustada - Original)', fontsize=12, fontweight='bold')
            ax3.axis('off')
            fig.colorbar(im_diff, ax=ax3, fraction=0.046, pad=0.04)
            
            # Histograma original
            ax4 = fig.add_subplot(2, 3, 4)
            hist_orig, bins_orig = np.histogram(imagen_original.flatten(), bins=256, range=(0, 256))
            ax4.plot(bins_orig[:-1], hist_orig, 'b-', linewidth=1, label='Original')
            ax4.axvline(min_val, color='r', linestyle='--', label=f'Min: {min_val:.1f}')
            ax4.axvline(max_val, color='r', linestyle='--', label=f'Max: {max_val:.1f}')
            ax4.set_title('Histograma Original', fontsize=12, fontweight='bold')
            ax4.set_xlabel('Valor de píxel')
            ax4.set_ylabel('Frecuencia')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            
            # Histograma ajustado
            ax5 = fig.add_subplot(2, 3, 5)
            hist_adj, bins_adj = np.histogram(imagen_ajustada.flatten(), bins=256, range=(0, 256))
            ax5.plot(bins_adj[:-1], hist_adj, 'g-', linewidth=1, label='Ajustada')
            ax5.set_title('Histograma Ajustado', fontsize=12, fontweight='bold')
            ax5.set_xlabel('Valor de píxel')
            ax5.set_ylabel('Frecuencia')
            ax5.legend()
            ax5.grid(True, alpha=0.3)
            
            # Comparación de histogramas
            ax6 = fig.add_subplot(2, 3, 6)
            ax6.plot(bins_orig[:-1], hist_orig, 'b-', linewidth=1, label='Original', alpha=0.7)
            ax6.plot(bins_adj[:-1], hist_adj, 'g-', linewidth=1, label='Ajustada', alpha=0.7)
            ax6.axvline(min_val, color='r', linestyle='--', alpha=0.7, label=f'Rango: {min_val:.1f}-{max_val:.1f}')
            ax6.set_title('Comparación de Histogramas', fontsize=12, fontweight='bold')
            ax6.set_xlabel('Valor de píxel')
            ax6.set_ylabel('Frecuencia')
            ax6.legend()
            ax6.grid(True, alpha=0.3)
            
            # Ajustar layout
            fig.tight_layout()
            
            # Crear canvas de matplotlib
            canvas = FigureCanvasTkAgg(fig, self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Mostrar estadísticas
            stats_text = f"Estadísticas del Ajuste:\n"
            stats_text += f"Rango original: {np.min(imagen_original):.1f} - {np.max(imagen_original):.1f}\n"
            stats_text += f"Rango ajustado: {np.min(imagen_ajustada):.1f} - {np.max(imagen_ajustada):.1f}\n"
            stats_text += f"Rango de entrada: {min_val:.1f} - {max_val:.1f}\n"
            stats_text += f"Contraste mejorado: {np.std(imagen_ajustada)/np.std(imagen_original):.2f}x"
            
            messagebox.showinfo("Resultados del Ajuste", stats_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar los resultados: {str(e)}")
    
    def clear_all(self):
        """Limpiar todos los datos y la visualización"""
        self.dicom_files = []
        self.dicom_data = []
        self.current_image = None
        self.current_dicom = None
        self.roi_coords = None
        self.roi_selector = None
        self.file_listbox.delete(0, tk.END)
        self.min_entry.delete(0, tk.END)
        self.max_entry.delete(0, tk.END)
        self.use_roi_var.set(False)
        
        # Limpiar el frame de plots
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        
        messagebox.showinfo("Información", "Datos limpiados correctamente")

def main():
    """Función principal"""
    root = tk.Tk()
    app = DICOMHistogramViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
