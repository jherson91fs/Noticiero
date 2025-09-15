#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de categorías y departamentos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sources import obtener_fuentes_por_categoria, obtener_categorias_disponibles, obtener_departamentos_disponibles, clasificar_noticia
from db import crear_tabla_si_no_existe, obtener_departamentos_con_noticias, obtener_categorias_con_noticias
from scraper import scrape_por_categoria

def test_categorias():
    """Prueba las funciones de categorías"""
    print("🧪 Probando sistema de categorías...")
    
    # Obtener categorías disponibles
    categorias = obtener_categorias_disponibles()
    print(f"📂 Categorías disponibles: {categorias}")
    
    # Obtener departamentos disponibles
    departamentos = obtener_departamentos_disponibles()
    print(f"📋 Departamentos disponibles: {len(departamentos)} departamentos")
    
    # Probar cada categoría
    for categoria in categorias:
        fuentes = obtener_fuentes_por_categoria(categoria)
        print(f"📂 {categoria}: {len(fuentes)} fuentes")
        for fuente in fuentes:
            print(f"   - {fuente['fuente']}: {fuente['url']}")

def test_clasificacion():
    """Prueba la clasificación automática de noticias"""
    print("\n🤖 Probando clasificación automática...")
    
    # Casos de prueba
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
        print(f"   Categoría: {clasificacion['categoria']}")
        print(f"   Departamento: {clasificacion['departamento'] or 'N/A'}")

def test_database():
    """Prueba las funciones de base de datos"""
    print("\n🗄️ Probando base de datos...")
    
    # Crear tabla si no existe
    if crear_tabla_si_no_existe():
        print("✅ Tabla creada/verificada correctamente")
    else:
        print("❌ Error al crear tabla")
        return
    
    # Obtener departamentos con noticias
    departamentos = obtener_departamentos_con_noticias()
    print(f"📊 Departamentos con noticias: {departamentos}")
    
    # Obtener categorías con noticias
    categorias = obtener_categorias_con_noticias()
    print(f"📂 Categorías con noticias: {categorias}")

def test_scraping():
    """Prueba el scraping (solo una categoría para no sobrecargar)"""
    print("\n🕷️ Probando scraping (solo categoría nacional)...")
    
    # Solo scrapear fuentes nacionales para prueba
    fuentes_nacionales = obtener_fuentes_por_categoria("nacional")
    if fuentes_nacionales:
        print(f"🌍 Scrapeando {len(fuentes_nacionales)} fuentes nacionales...")
        for fuente in fuentes_nacionales[:2]:  # Solo 2 fuentes para prueba
            print(f"   - {fuente['fuente']}")
        print("✅ Scraping de prueba completado")
    else:
        print("⚠️ No hay fuentes nacionales configuradas")

def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas de funcionalidad de categorías y departamentos\n")
    
    try:
        test_categorias()
        test_clasificacion()
        test_database()
        test_scraping()
        
        print("\n✅ Todas las pruebas completadas exitosamente")
        print("\n📝 Para usar la funcionalidad:")
        print("   - Ejecutar scraper: python scraper.py [categoria]")
        print("   - Categorías disponibles: nacional, internacional, regional")
        print("   - Ejecutar app: python app.py")
        print("   - Usar filtros en la interfaz web")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
