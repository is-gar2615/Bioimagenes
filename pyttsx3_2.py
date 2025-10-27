import pyttsx3

engine = pyttsx3.init()

# Configurar velocidad y volumen
engine.setProperty('rate', 160)   # velocidad de habla
engine.setProperty('volume', 1.0) # volumen máximo

# Seleccionar voz en español (ajusta el índice según tu lista)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Texto a voz
texto = "Hola, ¿cómo estás? Este texto se pronuncia completamente en español."
engine.say(texto)
engine.runAndWait()
