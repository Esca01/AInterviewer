#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para el registro y almacenamiento de la conversación de la entrevista.
Guarda la conversación en un archivo JSON.
"""

import os
import json
import datetime
from typing import List, Dict, Any

class EntrevistaLogger:
    """Clase para gestionar el registro de la conversación de la entrevista."""
    
    def __init__(self, directorio="transcripts"):
        """
        Inicializa el logger de la entrevista.
        
        Args:
            directorio (str): Directorio donde se guardarán los archivos de transcripción.
        """
        self.directorio = directorio
        os.makedirs(directorio, exist_ok=True)
        
        # Generar nombre de archivo único basado en la fecha y hora
        ahora = datetime.datetime.now()
        timestamp = ahora.strftime("%Y%m%d_%H%M%S")
        self.archivo_salida = os.path.join(directorio, f"entrevista_{timestamp}.json")
    
    def guardar_conversacion(self, conversacion: List[Dict[str, str]]) -> str:
        """
        Guarda la conversación en un archivo JSON.
        
        Args:
            conversacion (List[Dict[str, str]]): Lista de mensajes de la conversación.
            
        Returns:
            str: Ruta al archivo de conversación guardado.
        """
        # Crear estructura de datos para guardar
        datos = {
            "timestamp": datetime.datetime.now().isoformat(),
            "conversacion": conversacion
        }
        
        # Guardar en archivo JSON
        with open(self.archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        
        return self.archivo_salida
    
    def cargar_conversacion(self, archivo: str = None) -> List[Dict[str, str]]:
        """
        Carga una conversación desde un archivo JSON.
        
        Args:
            archivo (str, opcional): Ruta al archivo a cargar. Si no se especifica,
                                    se utiliza el último archivo guardado.
            
        Returns:
            List[Dict[str, str]]: Lista de mensajes de la conversación.
        """
        if archivo is None:
            archivo = self.archivo_salida
        
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                return datos.get("conversacion", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error al cargar la conversación: {str(e)}")
            return []
    
    def listar_entrevistas(self) -> List[str]:
        """
        Lista todos los archivos de entrevista disponibles.
        
        Returns:
            List[str]: Lista de nombres de archivo de entrevistas.
        """
        try:
            archivos = [f for f in os.listdir(self.directorio) 
                       if f.startswith("entrevista_") and f.endswith(".json")]
            return sorted(archivos)
        except Exception as e:
            print(f"Error al listar entrevistas: {str(e)}")
            return []
    
    def generar_resumen(self, archivo: str = None) -> Dict[str, Any]:
        """
        Genera un resumen básico de la entrevista.
        
        Args:
            archivo (str, opcional): Ruta al archivo a resumir. Si no se especifica,
                                    se utiliza el último archivo guardado.
            
        Returns:
            Dict[str, Any]: Diccionario con información resumida de la entrevista.
        """
        conversacion = self.cargar_conversacion(archivo)
        
        if not conversacion:
            return {"error": "No se encontró conversación para resumir"}
        
        # Contar turnos
        turnos_entrevistador = sum(1 for m in conversacion if m["rol"] == "entrevistador")
        turnos_candidato = sum(1 for m in conversacion if m["rol"] == "candidato")
        
        # Contar caracteres/palabras
        texto_entrevistador = " ".join(m["texto"] for m in conversacion if m["rol"] == "entrevistador")
        texto_candidato = " ".join(m["texto"] for m in conversacion if m["rol"] == "candidato")
        
        palabras_entrevistador = len(texto_entrevistador.split())
        palabras_candidato = len(texto_candidato.split())
        
        # Generar resumen
        resumen = {
            "turnos_totales": len(conversacion),
            "turnos_entrevistador": turnos_entrevistador,
            "turnos_candidato": turnos_candidato,
            "palabras_entrevistador": palabras_entrevistador,
            "palabras_candidato": palabras_candidato,
            "duracion_estimada_minutos": len(conversacion) * 0.5,  # Estimación gruesa
            "primera_pregunta": conversacion[0]["texto"] if conversacion else "",
            "ultima_interaccion": conversacion[-1]["texto"] if conversacion else ""
        }
        
        return resumen

if __name__ == "__main__":
    # Prueba del módulo
    print("Probando módulo de registro de entrevistas...")
    
    logger = EntrevistaLogger()
    
    # Conversación de ejemplo
    conversacion_ejemplo = [
        {"rol": "entrevistador", "texto": "Hola, bienvenido a esta entrevista. ¿Podrías presentarte brevemente?"},
        {"rol": "candidato", "texto": "Hola, soy Juan Pérez, desarrollador fullstack con 5 años de experiencia."},
        {"rol": "entrevistador", "texto": "¿Cuál es tu experiencia con Python?"},
        {"rol": "candidato", "texto": "He trabajado con Python durante los últimos 3 años, principalmente en desarrollo web con Django y Flask."}
    ]
    
    # Guardar la conversación
    archivo = logger.guardar_conversacion(conversacion_ejemplo)
    print(f"Conversación guardada en: {archivo}")
    
    # Generar y mostrar resumen
    resumen = logger.generar_resumen()
    print("\nResumen de la entrevista:")
    for clave, valor in resumen.items():
        print(f"- {clave}: {valor}")