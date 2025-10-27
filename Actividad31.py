import numpy as np
import cv2

def AjusteRangoDinamico(I, min_entrada=None, max_entrada=None):
    # Verificar si la imagen es a color
    if len(I.shape) > 2 and I.shape[2] > 1:
        print('La imagen debe ser escala de grises')
        return None
    
    # Convertir a tipo float
    I = I.astype(float)
    
    # Obtener dimensiones
    m, n = I.shape[:2]
    
    # Determinar los valores mínimo y máximo
    if min_entrada is None:
        minI = np.min(I)
    else:
        minI = min_entrada
        
    if max_entrada is None:
        maxI = np.max(I)
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
    O = Pendiente * I + b
    
    # Asegurar que los valores estén en el rango [0, 255]
    O = np.clip(O, 0, 255)
    
    # Convertir a uint8
    O = O.astype(np.uint8)
    
    return O

# Cargar imagen
imagen = cv2.imread('eye.jpg', cv2.IMREAD_GRAYSCALE)

# Ingresar valores de min_entrada y max_entrada
min_entrada = int(input("Ingrese el valor de min_entrada: "))
max_entrada = int(input("Ingrese el valor de max_entrada: "))

# Especificando rango personalizado
imagen_ajustada2 = AjusteRangoDinamico(imagen, min_entrada=min_entrada, max_entrada=max_entrada)