#!/usr/bin/env python3
"""
Script para verificar que las noticias se muestren correctamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import crear_tabla_si_no_existe, obtener_noticias
import mysql.connector
from mysql.connector import Error

def verificar_estructura_bd():
    """Verifica la estructura de la base de datos"""
    print("🔍 Verificando estructura de la base de datos...")
    
    try:
        from db import conectar
        conn = conectar()
        if not conn:
            print("❌ No se pudo conectar a la base de datos")
            return False
        
        cursor = conn.cursor()
        
        # Verificar si existe la columna departamento
        cursor.execute("DESCRIBE noticias")
        columnas = cursor.fetchall()
        
        print("📋 Columnas de la tabla 'noticias':")
        for columna in columnas:
            print(f"   - {columna[0]} ({columna[1]})")
        
        # Verificar si hay noticias con departamento
        cursor.execute("SELECT COUNT(*) FROM noticias WHERE departamento IS NOT NULL")
        count_dept = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM noticias")
        count_total = cursor.fetchone()[0]
        
        print(f"\n📊 Estadísticas:")
        print(f"   - Total de noticias: {count_total}")
        print(f"   - Noticias con departamento: {count_dept}")
        
        conn.close()
        return True
        
    except Error as e:
        print(f"❌ Error al verificar BD: {e}")
        return False

def mostrar_noticias_recientes():
    """Muestra las noticias más recientes con sus departamentos"""
    print("\n📰 Mostrando noticias más recientes:")
    print("=" * 80)
    
    noticias = obtener_noticias(limit=5)
    
    if not noticias:
        print("⚠️ No hay noticias en la base de datos")
        return
    
    for i, noticia in enumerate(noticias, 1):
        print(f"\n{i}. {noticia.get('titulo', 'Sin título')}")
        print(f"   📅 Fecha: {noticia.get('fecha', 'N/A')}")
        print(f"   🕒 Scraping: {noticia.get('fecha_scraping', 'N/A')}")
        print(f"   📂 Categoría: {noticia.get('categoria', 'N/A')}")
        print(f"   🗺️ Departamento: {noticia.get('departamento', 'N/A')}")
        print(f"   📰 Fuente: {noticia.get('fuente', 'N/A')}")
        print(f"   🔗 Link: {noticia.get('link', 'N/A')[:50]}...")

def verificar_ordenamiento():
    """Verifica que las noticias estén ordenadas correctamente"""
    print("\n🔄 Verificando ordenamiento...")
    
    try:
        from db import conectar
        conn = conectar()
        if not conn:
            print("❌ No se pudo conectar a la base de datos")
            return
        
        cursor = conn.cursor()
        
        # Consulta con ordenamiento por fecha_scraping DESC
        cursor.execute("""
            SELECT titulo, fecha_scraping, categoria, departamento 
            FROM noticias 
            ORDER BY fecha_scraping DESC 
            LIMIT 3
        """)
        
        noticias = cursor.fetchall()
        
        print("📋 Últimas 3 noticias por fecha_scraping:")
        for i, (titulo, fecha_scraping, categoria, departamento) in enumerate(noticias, 1):
            print(f"   {i}. {titulo[:40]}...")
            print(f"      🕒 {fecha_scraping} | 📂 {categoria} | 🗺️ {departamento or 'N/A'}")
        
        conn.close()
        
    except Error as e:
        print(f"❌ Error al verificar ordenamiento: {e}")

def main():
    """Función principal"""
    print("🚀 Verificando sistema de noticias\n")
    
    try:
        # Crear tabla si no existe
        if not crear_tabla_si_no_existe():
            print("❌ Error al crear tabla")
            return 1
        
        # Verificar estructura
        if not verificar_estructura_bd():
            return 1
        
        # Mostrar noticias
        mostrar_noticias_recientes()
        
        # Verificar ordenamiento
        verificar_ordenamiento()
        
        print("\n✅ Verificación completada")
        print("\n💡 Si no ves departamentos:")
        print("   1. Ejecuta: python scraper.py")
        print("   2. Luego: python app.py")
        print("   3. Abre: http://localhost:5000")
        
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
