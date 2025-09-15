#!/usr/bin/env python3
"""
Script para probar el ordenamiento de noticias
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import crear_tabla_si_no_existe, obtener_noticias
from sources import clasificar_noticia
from datetime import datetime

def test_ordenamiento():
    """Prueba el ordenamiento de noticias"""
    print("🧪 Probando ordenamiento de noticias...")
    
    # Crear tabla si no existe
    if not crear_tabla_si_no_existe():
        print("❌ Error al crear tabla")
        return
    
    # Obtener noticias ordenadas
    noticias = obtener_noticias(limit=10)
    
    if not noticias:
        print("⚠️ No hay noticias en la base de datos")
        print("💡 Ejecuta el scraper primero: python scraper.py")
        return
    
    print(f"📰 Mostrando {len(noticias)} noticias más recientes:")
    print("-" * 80)
    
    for i, noticia in enumerate(noticias, 1):
        fecha_scraping = noticia.get('fecha_scraping', 'N/A')
        fecha_noticia = noticia.get('fecha', 'N/A')
        titulo = noticia.get('titulo', 'Sin título')[:50] + "..."
        categoria = noticia.get('categoria', 'N/A')
        departamento = noticia.get('departamento', 'N/A')
        
        print(f"{i:2d}. {titulo}")
        print(f"    📅 Fecha noticia: {fecha_noticia}")
        print(f"    🕒 Fecha scraping: {fecha_scraping}")
        print(f"    📂 Categoría: {categoria}")
        print(f"    🗺️ Departamento: {departamento}")
        print()

def test_clasificacion():
    """Prueba la clasificación automática"""
    print("\n🤖 Probando clasificación automática...")
    
    casos_prueba = [
        {
            "titulo": "Nuevo presidente en Lima",
            "resumen": "El nuevo presidente asumió funciones en la capital del Perú",
            "categoria_fuente": "nacional"
        },
        {
            "titulo": "Inundaciones en Puno",
            "resumen": "Las lluvias han causado inundaciones en el departamento de Puno",
            "categoria_fuente": "nacional"
        },
        {
            "titulo": "Crisis económica en Estados Unidos",
            "resumen": "La economía estadounidense enfrenta una nueva crisis",
            "categoria_fuente": "nacional"
        },
        {
            "titulo": "Feria en Juliaca",
            "resumen": "Gran feria artesanal se realizará en Juliaca, Puno",
            "categoria_fuente": "regional"
        }
    ]
    
    for i, caso in enumerate(casos_prueba, 1):
        clasificacion = clasificar_noticia(caso["titulo"], caso["resumen"], caso["categoria_fuente"])
        print(f"📰 Caso {i}: {caso['titulo']}")
        print(f"    📂 Categoría: {clasificacion['categoria']}")
        print(f"    🗺️ Departamento: {clasificacion['departamento'] or 'N/A'}")
        print()

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de ordenamiento y clasificación\n")
    
    try:
        test_ordenamiento()
        test_clasificacion()
        
        print("✅ Pruebas completadas")
        print("\n💡 Para ver las noticias más recientes:")
        print("   1. Ejecuta: python scraper.py")
        print("   2. Luego: python app.py")
        print("   3. Abre: http://localhost:5000")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
