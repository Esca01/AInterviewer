#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Entrevistador Virtual Inteligente (Versión Terminal)
Archivo principal que orquesta el flujo de la entrevista.
"""

import os
import argparse
import time
from termcolor import colored
from modules.whisper_stt import grabar_y_transcribir
from modules.coqui_tts import texto_a_voz
from modules.llm_conversacion import generar_pregunta
from modules.entrevista_logger import EntrevistaLogger

def limpiar_pantalla():
    """Limpia la pantalla de la terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_banner():
    """Muestra el banner de la aplicación."""
    banner = """
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║           ENTREVISTADOR VIRTUAL INTELIGENTE                ║
    ║                   (Versión Terminal)                       ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    """
    print(colored(banner, 'cyan', attrs=['bold']))

def mostrar_instrucciones():
    """Muestra las instrucciones para el usuario."""
    print(colored("\n[INFO] Instrucciones:", 'yellow'))
    print("- Presiona ENTER para comenzar a hablar")
    print("- Habla claramente durante tu respuesta")
    print("- Presiona CTRL+C en cualquier momento para finalizar la entrevista")
    print(colored("\n[INFO] La entrevista comenzará en breve...", 'yellow'))
    time.sleep(3)

def ejecutar_entrevista(usar_tts=False, modelo_llm='claude'):
    """
    Ejecuta el flujo principal de la entrevista.
    
    Args:
        usar_tts (bool): Si es True, utiliza síntesis de voz para las preguntas.
        modelo_llm (str): Modelo LLM a utilizar ('claude', 'gpt', etc.)
    """
    limpiar_pantalla()
    mostrar_banner()
    
    # Crear carpeta de transcripciones si no existe
    os.makedirs('transcripts', exist_ok=True)
    
    # Inicializar el logger de la entrevista
    logger = EntrevistaLogger()
    
    # Cargar el prompt base
    with open('data/prompt_base.txt', 'r', encoding='utf-8') as f:
        prompt_base = f.read()
    
    # Iniciar entrevista con pregunta de presentación
    conversacion = []
    pregunta_inicial = "Hola, bienvenido a esta entrevista. ¿Podrías presentarte brevemente y contarme sobre tu experiencia profesional?"
    
    print(colored(f"\n[Entrevistador]: {pregunta_inicial}", 'green'))
    
    if usar_tts:
        texto_a_voz(pregunta_inicial)
    
    # Añadir pregunta inicial a la conversación
    conversacion.append({
        "rol": "entrevistador",
        "texto": pregunta_inicial
    })
    
    try:
        while True:
            # Esperar a que el usuario presione ENTER para hablar
            input(colored("\n[Presiona ENTER para responder...]", 'yellow'))
            
            # Grabar y transcribir la respuesta del candidato
            print(colored("\n[Grabando tu respuesta...]", 'yellow'))
            respuesta = grabar_y_transcribir()
            
            if not respuesta.strip():
                print(colored("\n[No se detectó ninguna respuesta. Intenta de nuevo.]", 'red'))
                continue
            
            # Mostrar la respuesta transcrita
            print(colored(f"\n[Tú]: {respuesta}", 'blue'))
            
            # Añadir respuesta a la conversación
            conversacion.append({
                "rol": "candidato",
                "texto": respuesta
            })
            
            # Guardar la conversación hasta el momento
            logger.guardar_conversacion(conversacion)
            
            # Generar nueva pregunta basada en la conversación
            nueva_pregunta = generar_pregunta(conversacion, prompt_base, modelo_llm)
            
            # Revisar si la entrevista debe terminar
            if "gracias por tu tiempo" in nueva_pregunta.lower() or "finalizar" in nueva_pregunta.lower():
                print(colored(f"\n[Entrevistador]: {nueva_pregunta}", 'green'))
                if usar_tts:
                    texto_a_voz(nueva_pregunta)
                conversacion.append({
                    "rol": "entrevistador",
                    "texto": nueva_pregunta
                })
                logger.guardar_conversacion(conversacion)
                print(colored("\n[INFO] La entrevista ha finalizado.", 'yellow'))
                break
            
            # Mostrar la nueva pregunta
            print(colored(f"\n[Entrevistador]: {nueva_pregunta}", 'green'))
            
            if usar_tts:
                texto_a_voz(nueva_pregunta)
            
            # Añadir pregunta a la conversación
            conversacion.append({
                "rol": "entrevistador",
                "texto": nueva_pregunta
            })
            
    except KeyboardInterrupt:
        # Capturar Ctrl+C para finalizar graciosamente
        print(colored("\n\n[INFO] Entrevista finalizada por el usuario.", 'yellow'))
        
        # Guardar la conversación final
        logger.guardar_conversacion(conversacion)
        print(colored(f"\n[INFO] Transcripción guardada en: {logger.archivo_salida}", 'yellow'))

def main():
    """Punto de entrada principal del programa."""
    parser = argparse.ArgumentParser(description='Entrevistador Virtual Inteligente')
    parser.add_argument('--tts', action='store_true', help='Utilizar síntesis de voz (TTS)')
    parser.add_argument('--modelo', type=str, default='meta-llama', choices=['claude', 'gpt'], 
                        help='Modelo LLM a utilizar (meta-llama,claude, gpt)')
    
    args = parser.parse_args()
    
    mostrar_instrucciones()
    ejecutar_entrevista(usar_tts=args.tts, modelo_llm=args.modelo)

if __name__ == "__main__":
    main()