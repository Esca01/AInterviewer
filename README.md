# Entrevistador Virtual Inteligente

Este proyecto implementa un sistema de entrevista virtual que utiliza reconocimiento de voz, procesamiento de lenguaje natural y modelos LLM para mantener conversaciones fluidas con candidatos.

## Requisitos de instalación

```bash
# Clonar el repositorio
git clone https://github.com/usuario/entrevistador-virtual.git
cd entrevistador-virtual

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## Configuración

1. Asegúrate de tener las claves API necesarias como variables de entorno:

   ```bash
   export ANTHROPIC_API_KEY=tu_clave_aqui
   export OPENAI_API_KEY=tu_clave_aqui
   ```

2. Crea la carpeta `data` y configura el archivo `prompt_base.txt` con las instrucciones del entrevistador.

## Uso

Para iniciar el entrevistador:

```bash
python main.py
```

Con opciones:

```bash
# Usar síntesis de voz para las preguntas
python main.py --tts

# Utilizar un modelo específico de LLM
python main.py --modelo gpt  # Opciones: claude, gpt
```

## Estructura del proyecto

```
entrevistador_terminal/
├── main.py                  # Orquestador principal
├── modules/
│   ├── whisper_stt.py       # Transcripción de voz con Whisper
│   ├── coqui_tts.py         # Síntesis de voz (opcional)
│   ├── llm_conversacion.py  # Integración con modelos LLM
│   └── entrevista_logger.py # Registro de conversaciones
├── data/
│   └── prompt_base.txt      # Instrucciones para el entrevistador
└── transcripts/             # Transcripciones guardadas
```

## Requisitos

Este proyecto requiere Python 3.11 o superior y las siguientes librerías:

- openai-whisper
- coqui-tts
- sounddevice
- soundfile
- scipy
- anthropic
- openai
- termcolor

## Licencia

Este proyecto está bajo la licencia MIT.
