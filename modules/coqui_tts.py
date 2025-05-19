#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para la síntesis de voz usando Coqui TTS.
Convierte texto a voz y reproduce el audio.
"""

import os
import numpy as np
import sounddevice as sd
import soundfile as sf
from scipy.io.wavfile import write
# Importaciones para la versión actual de Coqui TTS
try:
    # Intenta las importaciones para la versión más reciente
    from TTS.api import TTS
except ImportError:
    # Fallback para versiones anteriores
    try:
        from TTS.utils.manage import ModelManager
        from TTS.utils.synthesizer import Synthesizer
    except ImportError:
        print("No se pudo importar los módulos necesarios de Coqui TTS.")
        raise

class CoquiSintetizador:
    """Clase para manejar la síntesis de voz con Coqui TTS."""
    
    def __init__(self, modelo="tts_models/es/css10/vits", vocoder=None):
        """
        Inicializa el sintetizador de voz.
        
        Args:
            modelo (str): Identificador del modelo TTS a usar.
            vocoder (str, opcional): Identificador del vocoder.
        """
        # Crear directorio para modelos si no existe
        os.makedirs('models', exist_ok=True)
        
        try:
            print(f"Intentando inicializar TTS con modelo: {modelo}")
            
            # Intentar usar la API moderna de TTS primero
            try:
                # Enfoque para versiones más nuevas de TTS
                self.tts = TTS(model_name=modelo, progress_bar=True)
                self.use_new_api = True
                print("Usando la API moderna de TTS")
            except (NameError, AttributeError):
                # Fallback para versiones antiguas
                print("Fallback a la API antigua de TTS")
                self.use_new_api = False
                
                # Obtener la ruta correcta al archivo de modelos
                import importlib.util
                tts_spec = importlib.util.find_spec("TTS")
                tts_package_path = os.path.dirname(tts_spec.origin)
                models_file_path = os.path.join(tts_package_path, ".models.json")
                
                print(f"Usando archivo de modelos en: {models_file_path}")
                
                # Inicializar con la API antigua
                self.manager = ModelManager(models_file=models_file_path)
                self.model_path, self.config_path, self.model_item = self.manager.download_model(modelo)
                
                if vocoder is not None:
                    self.vocoder_path, self.vocoder_config_path, _ = self.manager.download_model(vocoder)
                else:
                    self.vocoder_path, self.vocoder_config_path = None, None
                
                # Crear un diccionario de configuración en lugar de pasar argumentos posicionales
                synth_config = {
                    "tts_checkpoint": self.model_path,
                    "tts_config_path": self.config_path,
                    "vocoder_checkpoint": self.vocoder_path,
                    "vocoder_config": self.vocoder_config_path,
                    "use_cuda": False
                }
                
                # Crear el sintetizador con la configuración como diccionario
                self.synthesizer = Synthesizer(**synth_config)
                
        except Exception as e:
            print(f"Error al inicializar el sintetizador: {str(e)}")
            raise
    
    def sintetizar(self, texto, archivo_salida=None):
        """
        Sintetiza el texto a voz.
        
        Args:
            texto (str): Texto a sintetizar.
            archivo_salida (str, opcional): Ruta para guardar el archivo de audio generado.
            
        Returns:
            numpy.ndarray: Array con los datos de audio sintetizados o la ruta del archivo guardado.
        """
        # Crear directorio temporal si no existe y no se especifica otro
        if archivo_salida is None:
            os.makedirs('temp', exist_ok=True)
            archivo_salida = os.path.join('temp', 'audio_temp.wav')
        
        try:
            if self.use_new_api:
                # Usando la API nueva
                self.tts.tts_to_file(text=texto, file_path=archivo_salida)
                # Cargar el archivo para devolver los datos de audio si es necesario
                data, _ = sf.read(archivo_salida)
                return data
            else:
                # API antigua
                wavs = self.synthesizer.tts(texto)
                # Guardar audio si se especifica archivo de salida
                if archivo_salida:
                    self.synthesizer.save_wav(wavs, archivo_salida)
                return wavs
        except Exception as e:
            print(f"Error durante la síntesis: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

def texto_a_voz(texto, reproducir=True):
    """
    Convierte texto a voz y opcionalmente lo reproduce.
    
    Args:
        texto (str): Texto a sintetizar.
        reproducir (bool): Si es True, reproduce el audio.
        
    Returns:
        str: Ruta al archivo de audio generado.
    """
    try:
        # Crear directorio temporal si no existe
        os.makedirs('temp', exist_ok=True)
        archivo_salida = os.path.join('temp', 'audio_salida.wav')
        
        # Inicializar sintetizador
        print("Inicializando sintetizador...")
        sintetizador = CoquiSintetizador()
        
        # Sintetizar texto
        print(f"Sintetizando texto: '{texto}'")
        sintetizador.sintetizar(texto, archivo_salida)
        
        print(f"Audio guardado en: {archivo_salida}")
        
        # Reproducir el audio si se solicita
        if reproducir:
            print("Reproduciendo audio...")
            try:
                data, fs = sf.read(archivo_salida)
                sd.play(data, fs)
                sd.wait()
            except Exception as e:
                print(f"Error al reproducir audio: {str(e)}")
        
        return archivo_salida
    
    except Exception as e:
        print(f"Error en la síntesis de voz: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def verificar_dependencias():
    """
    Verifica que todas las dependencias estén instaladas correctamente.
    """
    try:
        print("Verificando dependencias:")
        
        # Verificar TTS
        import TTS
        try:
            print(f"✓ TTS instalado (versión: {TTS.__version__})")
        except AttributeError:
            print("✓ TTS instalado (versión desconocida)")
            
        # Comprobar la estructura de la API de TTS
        print("\nComprobando la estructura de la API de TTS:")
        try:
            from TTS.api import TTS as NewTTS
            print("✓ API moderna de TTS disponible (TTS.api.TTS)")
            # Imprimir modelos disponibles
            print("\nModelos TTS disponibles:")
            try:
                print(NewTTS.list_models())
            except Exception as e:
                print(f"  No se pudieron listar los modelos: {str(e)}")
        except ImportError:
            print("✗ API moderna de TTS no disponible")
            
            try:
                from TTS.utils.manage import ModelManager
                from TTS.utils.synthesizer import Synthesizer
                print("✓ API antigua de TTS disponible (TTS.utils.synthesizer.Synthesizer)")
            except ImportError:
                print("✗ API antigua de TTS no disponible")
        
        # Verificar numpy
        import numpy
        print(f"✓ numpy instalado (versión: {numpy.__version__})")
        
        # Verificar sounddevice
        import sounddevice
        print(f"✓ sounddevice instalado (versión: {sounddevice.__version__})")
        
        # Verificar soundfile
        import soundfile
        print(f"✓ soundfile instalado")
        
        # Verificar scipy
        import scipy
        print(f"✓ scipy instalado (versión: {scipy.__version__})")
        
        print("\nTodas las dependencias están instaladas correctamente.")
        return True
    except ImportError as e:
        print(f"Falta instalar la dependencia: {str(e)}")
        print("\nSugerencia: Instala las dependencias con:")
        print("pip install TTS numpy sounddevice soundfile scipy")
        return False

if __name__ == "__main__":
    # Verificar dependencias antes de probar
    if verificar_dependencias():
        # Prueba del módulo
        print("\nProbando módulo de síntesis de voz...")
        texto_prueba = "Hola, soy el entrevistador virtual. ¿Cómo estás hoy?"
        
        try:
            archivo = texto_a_voz(texto_prueba)
            if archivo:
                print(f"¡Prueba exitosa! Audio guardado en: {archivo}")
            else:
                print("No se pudo generar el audio.")
        except Exception as e:
            print(f"Error durante la prueba: {str(e)}")
            import traceback
            traceback.print_exc()
            
            print("\n=========================================================")
            print("Sugerencia: Prueba reinstalar TTS con la siguiente versión:")
            print("pip uninstall -y TTS")
            print("pip install TTS==0.8.0")
            print("=========================================================")
            
            # Intentar con un enfoque alternativo usando Python TTS nativo
            print("\nProbando alternativa con pyttsx3...")
            try:
                import pyttsx3
                print("Usando pyttsx3 como alternativa...")
                
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)  # Velocidad de habla
                
                # Intentar configurar una voz en español si está disponible
                voices = engine.getProperty('voices')
                spanish_voice = None
                
                for voice in voices:
                    if "spanish" in voice.name.lower() or "español" in voice.name.lower():
                        spanish_voice = voice.id
                        break
                
                if spanish_voice:
                    engine.setProperty('voice', spanish_voice)
                    
                print(f"Sintetizando texto: '{texto_prueba}'")
                engine.say(texto_prueba)
                engine.runAndWait()
                print("Audio reproducido con pyttsx3")
            except Exception as e2:
                print(f"También falló pyttsx3: {str(e2)}")
                print("Sugerencia final: pip install pyttsx3")