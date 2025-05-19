#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para la captura y transcripción de audio usando Whisper.
Permite grabar audio desde el micrófono y convertirlo a texto.
"""

import os
import tempfile
import numpy as np
import sounddevice as sd
import soundfile as sf
import whisper
from scipy.io.wavfile import write

class WhisperTranscriptor:
    """Clase para manejar la transcripción de audio con Whisper."""
    
    def __init__(self, modelo="base"):
        """
        Inicializa el transcriptor de Whisper.
        
        Args:
            modelo (str): Tamaño del modelo de Whisper ('tiny', 'base', 'small', 'medium', 'large')
        """
        self.modelo = whisper.load_model(modelo)
    
    def transcribir_archivo(self, ruta_archivo):
        """
        Transcribe un archivo de audio usando Whisper.
        
        Args:
            ruta_archivo (str): Ruta al archivo de audio a transcribir.
            
        Returns:
            str: Texto transcrito del archivo de audio.
        """
        resultado = self.modelo.transcribe(ruta_archivo, language="es")
        return resultado["text"]

def grabar_audio(duracion_max=30, fs=16000):
    """
    Graba audio desde el micrófono.
    
    Args:
        duracion_max (int): Duración máxima de la grabación en segundos.
        fs (int): Frecuencia de muestreo en Hz.
        
    Returns:
        numpy.ndarray: Array con los datos de audio grabados.
    """
    print("Grabando... (Habla ahora)")
    
    # Crear array para almacenar la grabación
    grabacion = sd.rec(int(duracion_max * fs), samplerate=fs, channels=1, dtype='float32')
    
    # Configurar detección de silencio para detener la grabación
    umbral_silencio = 0.02
    tiempo_silencio = 2.0  # segundos de silencio para terminar
    muestras_silencio = int(tiempo_silencio * fs)
    contador_silencio = 0
    
    # Monitorear el audio y detectar silencio
    for i in range(int(duracion_max * fs)):
        sd.wait()
        if i < len(grabacion) and abs(grabacion[i]) < umbral_silencio:
            contador_silencio += 1
        else:
            contador_silencio = 0
        
        if contador_silencio >= muestras_silencio:
            # Recortar la grabación hasta donde se detectó actividad
            grabacion = grabacion[:i - muestras_silencio]
            break
    
    print("Grabación finalizada.")
    return grabacion

def grabar_y_transcribir(modelo_whisper="base"):
    """
    Graba audio desde el micrófono y lo transcribe a texto.
    
    Args:
        modelo_whisper (str): Tamaño del modelo de Whisper a utilizar.
        
    Returns:
        str: Texto transcrito del audio grabado.
    """
    # Crear directorio temporal si no existe
    os.makedirs('temp', exist_ok=True)
    
    # Grabar audio
    fs = 16000  # Frecuencia de muestreo
    grabacion = grabar_audio(duracion_max=15, fs=fs)
    
    # Guardar la grabación en un archivo temporal
    archivo_temp = os.path.join('temp', 'grabacion_temp.wav')
    write(archivo_temp, fs, grabacion)
    
    # Transcribir el audio
    transcriptor = WhisperTranscriptor(modelo=modelo_whisper)
    texto = transcriptor.transcribir_archivo(archivo_temp)
    
    # Limpiar el archivo temporal
    try:
        os.remove(archivo_temp)
    except:
        pass
    
    return texto

if __name__ == "__main__":
    # Prueba del módulo
    print("Probando módulo de transcripción...")
    texto = grabar_y_transcribir()
    print(f"Texto transcrito: {texto}")