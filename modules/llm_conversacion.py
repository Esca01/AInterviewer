#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo simplificado para la interacción con modelos de lenguaje (LLM) a través de OpenRouter
para generar preguntas durante entrevistas basándose en la conversación previa.
"""

import os
import requests
from typing import List, Dict, Optional

# Cargar clave API desde variables de entorno
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class OpenRouterConversacion:
    """Clase para manejar la interacción con modelos a través de OpenRouter."""
    
    def __init__(self, modelo="meta-llama/llama-3.3-8b-instruct:free"):
        """
        Inicializa la interacción con OpenRouter.
        
        Args:
            modelo (str): Modelo a utilizar a través de OpenRouter.
                Ejemplos comunes que suelen funcionar bien:
                - "openai/gpt-3.5-turbo" (predeterminado)
                - "google/gemini-pro"
                - "mistralai/mistral-7b-instruct"
                
                Para ver una lista actualizada de modelos disponibles:
                https://openrouter.ai/docs#models
        """
        if not OPENROUTER_API_KEY:
            raise ValueError("No se encontró la clave API de OpenRouter en las variables de entorno.")
        
        # Mapeo de nombres cortos a IDs completos en OpenRouter
        modelo_mapping = {
            "meta-llama":"meta-llama/llama-3.3-8b-instruct:free",
        }
        
        # Si se proporciona un nombre corto, convertirlo al ID completo
        if modelo in modelo_mapping:
            modelo = modelo_mapping[modelo]
            print(f"Usando modelo: {modelo}")
        
        self.api_key = OPENROUTER_API_KEY
        self.modelo = modelo
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://entrevistador-app.com",  # Cambiado a un dominio más específico
            "X-Title": "Entrevistador-LLM"       # Identificador de tu aplicación
        }
    
    def generar_pregunta(self, conversacion: List[Dict[str, str]], prompt_base: str) -> str:
        """
        Genera una nueva pregunta usando OpenRouter.
        
        Args:
            conversacion (List[Dict[str, str]]): Lista de diccionarios con la conversación.
            prompt_base (str): Prompt base con instrucciones para el modelo.
            
        Returns:
            str: La nueva pregunta generada.
        """
        # Formatear los mensajes en el formato de OpenRouter/ChatCompletion
        mensajes = [{"role": "system", "content": prompt_base}]
        
        for mensaje in conversacion:
            rol = mensaje["rol"]
            texto = mensaje["texto"]
            rol_api = "assistant" if rol == "entrevistador" else "user"
            mensajes.append({"role": rol_api, "content": texto})
        
        mensajes.append({
            "role": "user", 
            "content": "Genera la siguiente pregunta del entrevistador basada en la conversación anterior. Solo devuelve la pregunta sin explicaciones adicionales o prefijos."
        })
        
        payload = {
            "model": self.modelo,
            "messages": mensajes,
            "max_tokens": 250,
            "temperature": 0.7
        }
        
        try:
            # Realizar la solicitud a OpenRouter
            response = requests.post(self.url, headers=self.headers, json=payload)
            
            # Si hay error, intentar obtener el mensaje detallado de la API
            if not response.ok:
                error_detail = "Detalles no disponibles"
                try:
                    error_json = response.json()
                    if "error" in error_json:
                        if isinstance(error_json["error"], dict) and "message" in error_json["error"]:
                            error_detail = error_json["error"]["message"]
                        elif isinstance(error_json["error"], str):
                            error_detail = error_json["error"]
                except:
                    pass
                
                print(f"Error en la API de OpenRouter ({response.status_code}): {error_detail}")
                print(f"Modelo solicitado: {self.modelo}")
                response.raise_for_status()
            
            resultado = response.json()
            
            # Extraer la respuesta
            if "choices" in resultado and len(resultado["choices"]) > 0:
                if "message" in resultado["choices"][0] and "content" in resultado["choices"][0]["message"]:
                    nueva_pregunta = resultado["choices"][0]["message"]["content"].strip()
                    # Limpiar la respuesta si es necesario
                    nueva_pregunta = nueva_pregunta.replace("Entrevistador:", "").strip()
                    return nueva_pregunta
                else:
                    print("Formato de respuesta inesperado. Estructura de 'choices':", resultado["choices"])
            else:
                print("Respuesta sin 'choices' o vacía:", resultado)
            
            # Si llegamos aquí, algo falló en la estructura de la respuesta
            return "¿Podrías contarme más sobre tus habilidades técnicas?"
        
        except Exception as e:
            print(f"Error al generar pregunta con OpenRouter: {str(e)}")
            return "¿Cómo relacionarías tu experiencia previa con este puesto específicamente?"


def generar_pregunta(
    conversacion: List[Dict[str, str]], 
    prompt_base: str, 
    nombre_modelo: Optional[str] = None
) -> str:
    """
    Función principal para generar una nueva pregunta basada en la conversación.
    
    Args:
        conversacion (List[Dict[str, str]]): Lista de diccionarios con la conversación.
        prompt_base (str): Prompt base con instrucciones para el modelo.
        nombre_modelo (Optional[str]): Nombre específico del modelo a utilizar (opcional).
        
    Returns:
        str: La nueva pregunta generada.
    """
    try:
        # Manejar modelos genéricos y convertirlos a IDs válidos de OpenRouter
        modelo_especifico = nombre_modelo or "meta-llama/llama-3.3-8b-instruct:free"
        
        # Mapeo de nombres cortos a IDs completos en OpenRouter
        modelo_mapping = {
            "meta-llama" : "meta-llama/llama-3.3-8b-instruct:free",
        }
        
        # Si se usó un nombre corto, convertirlo al ID completo
        if modelo_especifico in modelo_mapping:
            modelo_especifico = modelo_mapping[modelo_especifico]
            print(f"Usando modelo: {modelo_especifico}")
        
        modelo = OpenRouterConversacion(modelo=modelo_especifico)
        
        # Generar y devolver la pregunta
        return modelo.generar_pregunta(conversacion, prompt_base)
    
    except Exception as e:
        print(f"Error al generar pregunta: {str(e)}")
        # Pregunta de respaldo en caso de error
        return "Interesante. ¿Puedes contarme más sobre tu experiencia en ese aspecto?"


if __name__ == "__main__":
    # Prueba del módulo
    print("Probando módulo de conversación con OpenRouter...")
    
    # Cargar prompt de ejemplo (ajusta la ruta según sea necesario)
    try:
        with open('../data/prompt_base.txt', 'r', encoding='utf-8') as f:
            prompt = f.read()
    except FileNotFoundError:
        prompt = """Eres un entrevistador experimentado para puestos de tecnología.
        Tu objetivo es hacer preguntas relevantes basadas en la conversación previa.
        Genera preguntas profundas que evalúen tanto habilidades técnicas como blandas."""
    
    # Conversación de ejemplo
    conversacion_ejemplo = [
        {"rol": "entrevistador", "texto": "Hola, bienvenido a esta entrevista. ¿Podrías presentarte brevemente?"},
        {"rol": "candidato", "texto": "Hola, soy Juan Pérez, desarrollador fullstack con 5 años de experiencia en Python y JavaScript."},
    ]
    
    # Probar con OpenRouter
    if OPENROUTER_API_KEY:
        # Modelo predeterminado (GPT-3.5)
        print("\nProbando con OpenRouter usando modelo predeterminado:")
        try:
            pregunta_default = generar_pregunta(conversacion_ejemplo, prompt)
            print(f"Pregunta generada: {pregunta_default}")
        except Exception as e:
            print(f"Error con modelo predeterminado: {str(e)}")
        
        # Intenta con modelos alternativos en caso de error
        modelos_alternativos = [
            "gemini",    # Se convierte automáticamente a "google/gemini-pro"
            "mistral"    # Se convierte automáticamente a "mistralai/mistral-7b-instruct"
        ]
        
        for modelo_alt in modelos_alternativos:
            print(f"\nProbando con modelo alternativo: {modelo_alt}")
            try:
                pregunta_alt = generar_pregunta(conversacion_ejemplo, prompt, modelo_alt)
                print(f"Pregunta generada: {pregunta_alt}")
                break  # Si tiene éxito, termina el bucle
            except Exception as e:
                print(f"Error con {modelo_alt}: {str(e)}")
    else:
        print("No se encontró la clave API de OpenRouter. Configura la variable de entorno OPENROUTER_API_KEY.")
        print("Ejemplo: export OPENROUTER_API_KEY='tu_clave_api_aquí'")
        
    print("\nNota importante sobre los modelos:")
    print("- 'gpt' utiliza 'openai/gpt-3.5-turbo'")
    print("- 'gpt4' utiliza 'openai/gpt-4'")
    print("- 'mistral' utiliza 'mistralai/mistral-7b-instruct'")
    print("- 'gemini' utiliza 'google/gemini-pro'")
    print("\nSi sigues experimentando errores, verifica:")
    print("1. Que tu clave API de OpenRouter sea válida")
    print("2. Que tengas conexión a Internet")
    print("3. Que el modelo solicitado esté disponible en tu plan de OpenRouter")
    print("4. Consulta https://openrouter.ai/docs para más información sobre modelos disponibles")