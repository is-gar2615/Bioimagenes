import tkinter as tk
from tkinter import filedialog, messagebox
import pydicom
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os

class DICOMViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Archivos DICOM")
        self.root.geometry("1200x800")
        
        # Lista para almacenar los archivos DICOM
        self.dicom_files = []
        self.dicom_data = []
        
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
        
        # Botón para mostrar imágenes
        show_button = tk.Button(button_frame, text="Mostrar Imágenes", 
                               command=self.show_images, bg="#2196F3", fg="white",
                               font=("Arial", 12, "bold"))
        show_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón para mostrar metadatos
        metadata_button = tk.Button(button_frame, text="Ver Metadatos", 
                                   command=self.show_metadata, bg="#FF9800", fg="white",
                                   font=("Arial", 12, "bold"))
        metadata_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón para limpiar
        clear_button = tk.Button(button_frame, text="Limpiar", 
                                command=self.clear_all, bg="#f44336", fg="white",
                                font=("Arial", 12, "bold"))
        clear_button.pack(side=tk.LEFT)
        
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
            title="Seleccionar archivos DICOM",
            filetypes=file_types
        )
        
        if files:
            self.dicom_files = list(files)
            self.dicom_data = []
            
            # Actualizar la lista de archivos
            self.file_listbox.delete(0, tk.END)
            for file_path in self.dicom_files:
                filename = os.path.basename(file_path)
                self.file_listbox.insert(tk.END, filename)
            
            messagebox.showinfo("Éxito", f"Se cargaron {len(files)} archivo(s) DICOM")
    
    def show_images(self):
        """Mostrar las imágenes DICOM en subplots"""
        if not self.dicom_files:
            messagebox.showwarning("Advertencia", "Primero debe cargar archivos DICOM")
            return
        
        # Limpiar el frame de plots
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        
        try:
            # Crear figura de matplotlib
            fig = Figure(figsize=(12, 8), dpi=100)
            
            # Determinar el número de archivos a mostrar (máximo 3)
            num_files = min(len(self.dicom_files), 3)
            
            # Crear subplots
            if num_files == 1:
                axes = [fig.add_subplot(111)]
            elif num_files == 2:
                axes = [fig.add_subplot(121), fig.add_subplot(122)]
            else:
                axes = [fig.add_subplot(131), fig.add_subplot(132), fig.add_subplot(133)]
            
            # Procesar cada archivo DICOM
            for i in range(num_files):
                try:
                    # Leer archivo DICOM
                    dicom_data = pydicom.dcmread(self.dicom_files[i])
                    
                    # Obtener la imagen
                    image = dicom_data.pixel_array
                    
                    # Aplicar normalización para mejor visualización
                    if image.dtype != np.uint8:
                        image = ((image - image.min()) / (image.max() - image.min()) * 255).astype(np.uint8)
                    
                    # Mostrar la imagen
                    axes[i].imshow(image, cmap='gray')
                    axes[i].set_title(f'DICOM {i+1}: {os.path.basename(self.dicom_files[i])}', 
                                    fontsize=10, fontweight='bold')
                    axes[i].axis('off')
                    
                    # Agregar información del archivo
                    patient_name = getattr(dicom_data, 'PatientName', 'N/A')
                    study_date = getattr(dicom_data, 'StudyDate', 'N/A')
                    modality = getattr(dicom_data, 'Modality', 'N/A')
                    
                    info_text = f"Paciente: {patient_name}\nFecha: {study_date}\nModalidad: {modality}"
                    axes[i].text(0.02, 0.98, info_text, transform=axes[i].transAxes, 
                               fontsize=8, verticalalignment='top',
                               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                    
                except Exception as e:
                    axes[i].text(0.5, 0.5, f'Error al cargar\n{os.path.basename(self.dicom_files[i])}\n{str(e)}', 
                               transform=axes[i].transAxes, ha='center', va='center',
                               fontsize=10, color='red')
                    axes[i].set_title(f'Error en DICOM {i+1}', fontsize=10, color='red')
                    axes[i].axis('off')
            
            # Ajustar layout
            fig.tight_layout()
            
            # Crear canvas de matplotlib
            canvas = FigureCanvasTkAgg(fig, self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar las imágenes: {str(e)}")
    
    def show_metadata(self):
        """Mostrar metadatos de los archivos DICOM en una ventana separada"""
        if not self.dicom_files:
            messagebox.showwarning("Advertencia", "Primero debe cargar archivos DICOM")
            return
        
        # Crear ventana para metadatos
        metadata_window = tk.Toplevel(self.root)
        metadata_window.title("Metadatos de Archivos DICOM")
        metadata_window.geometry("800x600")
        
        # Frame principal con scrollbar
        main_frame = tk.Frame(metadata_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Crear notebook para pestañas (uno por archivo)
        from tkinter import ttk
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Procesar cada archivo DICOM
        for i, file_path in enumerate(self.dicom_files):
            try:
                # Leer archivo DICOM
                dicom_data = pydicom.dcmread(file_path)
                
                # Crear frame para este archivo
                frame = tk.Frame(notebook)
                notebook.add(frame, text=f"DICOM {i+1}: {os.path.basename(file_path)}")
                
                # Crear scrollbar y text widget
                scrollbar = tk.Scrollbar(frame)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                text_widget = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                                    font=("Consolas", 9), bg="#f8f9fa")
                text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.config(command=text_widget.yview)
                
                # Obtener metadatos
                metadata_text = self.get_metadata_text(dicom_data, file_path)
                text_widget.insert(tk.END, metadata_text)
                text_widget.config(state=tk.DISABLED)  # Hacer solo lectura
                
            except Exception as e:
                # Crear frame de error
                frame = tk.Frame(notebook)
                notebook.add(frame, text=f"Error DICOM {i+1}")
                
                error_label = tk.Label(frame, text=f"Error al leer {os.path.basename(file_path)}:\n{str(e)}",
                                     font=("Arial", 12), fg="red", justify=tk.LEFT)
                error_label.pack(pady=20)
        
        # Botón para cerrar
        close_button = tk.Button(metadata_window, text="Cerrar", 
                               command=metadata_window.destroy, bg="#6c757d", fg="white",
                               font=("Arial", 10, "bold"))
        close_button.pack(pady=10)
    
    def get_metadata_text(self, dicom_data, file_path):
        """Obtener texto formateado con los metadatos del archivo DICOM"""
        metadata_lines = []
        
        # Información del archivo
        metadata_lines.append("=" * 80)
        metadata_lines.append(f"INFORMACIÓN DEL ARCHIVO")
        metadata_lines.append("=" * 80)
        metadata_lines.append(f"Ruta del archivo: {file_path}")
        metadata_lines.append(f"Tamaño del archivo: {os.path.getsize(file_path)} bytes")
        metadata_lines.append("")
        
        # Información del paciente
        metadata_lines.append("=" * 80)
        metadata_lines.append(f"INFORMACIÓN DEL PACIENTE")
        metadata_lines.append("=" * 80)
        patient_fields = [
            ('PatientName', 'Nombre del Paciente'),
            ('PatientID', 'ID del Paciente'),
            ('PatientBirthDate', 'Fecha de Nacimiento'),
            ('PatientSex', 'Sexo'),
            ('PatientAge', 'Edad'),
            ('PatientWeight', 'Peso'),
            ('PatientSize', 'Altura')
        ]
        
        for field, description in patient_fields:
            value = getattr(dicom_data, field, 'N/A')
            if value != 'N/A':
                metadata_lines.append(f"{description}: {value}")
        
        metadata_lines.append("")
        
        # Información del estudio
        metadata_lines.append("=" * 80)
        metadata_lines.append(f"INFORMACIÓN DEL ESTUDIO")
        metadata_lines.append("=" * 80)
        study_fields = [
            ('StudyDate', 'Fecha del Estudio'),
            ('StudyTime', 'Hora del Estudio'),
            ('StudyDescription', 'Descripción del Estudio'),
            ('StudyID', 'ID del Estudio'),
            ('StudyInstanceUID', 'UID del Estudio'),
            ('AccessionNumber', 'Número de Acceso')
        ]
        
        for field, description in study_fields:
            value = getattr(dicom_data, field, 'N/A')
            if value != 'N/A':
                metadata_lines.append(f"{description}: {value}")
        
        metadata_lines.append("")
        
        # Información de la serie
        metadata_lines.append("=" * 80)
        metadata_lines.append(f"INFORMACIÓN DE LA SERIE")
        metadata_lines.append("=" * 80)
        series_fields = [
            ('SeriesDate', 'Fecha de la Serie'),
            ('SeriesTime', 'Hora de la Serie'),
            ('SeriesDescription', 'Descripción de la Serie'),
            ('SeriesNumber', 'Número de Serie'),
            ('SeriesInstanceUID', 'UID de la Serie'),
            ('Modality', 'Modalidad'),
            ('Manufacturer', 'Fabricante'),
            ('ManufacturerModelName', 'Modelo del Equipo')
        ]
        
        for field, description in series_fields:
            value = getattr(dicom_data, field, 'N/A')
            if value != 'N/A':
                metadata_lines.append(f"{description}: {value}")
        
        metadata_lines.append("")
        
        # Información de la imagen
        metadata_lines.append("=" * 80)
        metadata_lines.append(f"INFORMACIÓN DE LA IMAGEN")
        metadata_lines.append("=" * 80)
        image_fields = [
            ('InstanceNumber', 'Número de Instancia'),
            ('ImageType', 'Tipo de Imagen'),
            ('SOPClassUID', 'UID de la Clase SOP'),
            ('SOPInstanceUID', 'UID de la Instancia SOP'),
            ('Rows', 'Filas'),
            ('Columns', 'Columnas'),
            ('BitsAllocated', 'Bits Asignados'),
            ('BitsStored', 'Bits Almacenados'),
            ('HighBit', 'Bit Alto'),
            ('PixelRepresentation', 'Representación de Píxel'),
            ('SamplesPerPixel', 'Muestras por Píxel'),
            ('PhotometricInterpretation', 'Interpretación Fotométrica'),
            ('PixelSpacing', 'Espaciado de Píxeles'),
            ('SliceThickness', 'Grosor de Corte')
        ]
        
        for field, description in image_fields:
            value = getattr(dicom_data, field, 'N/A')
            if value != 'N/A':
                if isinstance(value, (list, tuple)) and len(value) > 1:
                    metadata_lines.append(f"{description}: {value}")
                else:
                    metadata_lines.append(f"{description}: {value}")
        
        metadata_lines.append("")
        
        # Parámetros de adquisición
        metadata_lines.append("=" * 80)
        metadata_lines.append(f"PARÁMETROS DE ADQUISICIÓN")
        metadata_lines.append("=" * 80)
        acquisition_fields = [
            ('KVP', 'Kilovoltaje del Tubo'),
            ('ExposureTime', 'Tiempo de Exposición'),
            ('XRayTubeCurrent', 'Corriente del Tubo de Rayos X'),
            ('Exposure', 'Exposición'),
            ('FilterMaterial', 'Material del Filtro'),
            ('BodyPartExamined', 'Parte del Cuerpo Examinada'),
            ('ViewPosition', 'Posición de Vista'),
            ('PatientPosition', 'Posición del Paciente')
        ]
        
        for field, description in acquisition_fields:
            value = getattr(dicom_data, field, 'N/A')
            if value != 'N/A':
                metadata_lines.append(f"{description}: {value}")
        
        metadata_lines.append("")
        
        # Todos los metadatos (opcional - comentado para evitar demasiada información)
        # metadata_lines.append("=" * 80)
        # metadata_lines.append(f"TODOS LOS METADATOS")
        # metadata_lines.append("=" * 80)
        # for elem in dicom_data:
        #     if elem.VR != 'SQ':  # Excluir secuencias
        #         metadata_lines.append(f"{elem.tag} {elem.name}: {elem.value}")
        
        return "\n".join(metadata_lines)
    
    def clear_all(self):
        """Limpiar todos los datos y la visualización"""
        self.dicom_files = []
        self.dicom_data = []
        self.file_listbox.delete(0, tk.END)
        
        # Limpiar el frame de plots
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        
        messagebox.showinfo("Información", "Datos limpiados correctamente")

def main():
    """Función principal"""
    root = tk.Tk()
    app = DICOMViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
