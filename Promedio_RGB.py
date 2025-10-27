import cv2
import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog
import tkinter as tk

def cargar_imagen():
    """Función para cargar una imagen usando un diálogo de archivo"""
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal de tkinter
    archivo = filedialog.askopenfilename(
        title="Seleccionar imagen",
        filetypes=[("Archivos de imagen", "*.jpg *.jpeg *.png *.bmp *.tiff")]
    )
    root.destroy()
    return archivo

def convertir_a_escala_grises_promedio(imagen):
    """
    Convierte una imagen a escala de grises usando el promedio de los valores RGB
    """
    # Obtener las dimensiones de la imagen
    alto, ancho, canales = imagen.shape
    
    # Crear una matriz para la imagen en escala de grises
    imagen_gris = np.zeros((alto, ancho), dtype=np.uint8)
    
    # Calcular el promedio de RGB para cada píxel
    for i in range(alto):
        for j in range(ancho):
            # Obtener los valores R, G, B del píxel
            r, g, b = imagen[i, j]
            # Calcular el promedio
            promedio = (int(r) + int(g) + int(b)) // 3
            imagen_gris[i, j] = promedio
    
    return imagen_gris

def mostrar_imagenes(imagenes_originales, imagenes_grises, titulos):
    """
    Muestra las imágenes originales y en escala de grises en una cuadrícula
    """
    num_imagenes = len(imagenes_originales)
    
    # Crear una figura con subplots
    fig, axes = plt.subplots(2, num_imagenes, figsize=(15, 8))
    
    # Si solo hay una imagen, ajustar la forma de axes
    if num_imagenes == 1:
        axes = axes.reshape(2, 1)
    
    for i in range(num_imagenes):
        # Mostrar imagen original
        axes[0, i].imshow(cv2.cvtColor(imagenes_originales[i], cv2.COLOR_BGR2RGB))
        axes[0, i].set_title(f'{titulos[i]} - Original')
        axes[0, i].axis('off')
        
        # Mostrar imagen en escala de grises
        axes[1, i].imshow(imagenes_grises[i], cmap='gray')
        axes[1, i].set_title(f'{titulos[i]} - Escala de Grises (Promedio RGB)')
        axes[1, i].axis('off')
    
    plt.tight_layout()
    plt.show()

def main():
    """
    Función principal que ejecuta el programa
    """
    print("=== Convertidor de Imágenes a Escala de Grises ===")
    print("Este programa convierte imágenes a escala de grises usando el promedio de los valores RGB")
    print()
    
    imagenes_originales = []
    imagenes_grises = []
    titulos = []
    
    # Cargar tres imágenes
    for i in range(3):
        print(f"Cargando imagen {i+1}...")
        ruta_imagen = cargar_imagen()
        
        if not ruta_imagen:
            print(f"No se seleccionó imagen {i+1}. Saliendo...")
            return
        
        # Leer la imagen
        imagen = cv2.imread(ruta_imagen)
        if imagen is None:
            print(f"Error al cargar la imagen {i+1}. Verifica que el archivo sea válido.")
            continue
        
        # Obtener el nombre del archivo para el título
        nombre_archivo = ruta_imagen.split('/')[-1].split('\\')[-1]
        titulos.append(nombre_archivo)
        
        # Convertir a escala de grises usando el promedio RGB
        imagen_gris = convertir_a_escala_grises_promedio(imagen)
        
        # Guardar las imágenes
        imagenes_originales.append(imagen)
        imagenes_grises.append(imagen_gris)
        
        print(f"Imagen {i+1} cargada exitosamente: {nombre_archivo}")
    
    if not imagenes_originales:
        print("No se cargaron imágenes válidas.")
        return
    
    print(f"\nSe cargaron {len(imagenes_originales)} imágenes exitosamente.")
    print("Mostrando resultados...")
    
    # Mostrar las imágenes
    mostrar_imagenes(imagenes_originales, imagenes_grises, titulos)
    
    # Opción para guardar las imágenes en escala de grises
    respuesta = input("\n¿Deseas guardar las imágenes en escala de grises? (s/n): ").lower()
    if respuesta == 's':
        for i, (imagen_gris, titulo) in enumerate(zip(imagenes_grises, titulos)):
            nombre_sin_extension = titulo.split('.')[0]
            nombre_guardado = f"{nombre_sin_extension}_escala_grises_promedio.jpg"
            cv2.imwrite(nombre_guardado, imagen_gris)
            print(f"Imagen guardada: {nombre_guardado}")

if __name__ == "__main__":
    main()
