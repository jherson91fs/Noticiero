import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os
from dotenv import load_dotenv

# ----------------- CONFIG DB -----------------
load_dotenv()
db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "noticiero_db")
}

# ----------------- FUNCIONES -----------------
def conectar():
    """
    Establece conexión con la BD MySQL
    """
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"❌ Error al conectar con MySQL: {e}")
        return None


def guardar_noticia(titulo, link, categoria, fecha, resumen, autor, imagen, fuente, departamento=None):
    """
    Inserta una noticia en la base de datos, evitando duplicados.
    """
    conn = conectar()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # Bloquear cualquier noticia de Peru21/Perú21
        if fuente and fuente.strip().lower() in ("peru21", "perú21"):
            cursor.close()
            conn.close()
            return False

        # Verificar duplicados (por título y link)
        cursor.execute("SELECT id FROM noticias WHERE titulo = %s AND link = %s", (titulo, link))
        existe = cursor.fetchone()

        if not existe:
            cursor.execute("""
                INSERT INTO noticias (titulo, link, categoria, fecha, resumen, autor, imagen, fuente, departamento, fecha_scraping)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                titulo, link, categoria, fecha, resumen, autor, imagen, fuente, departamento, datetime.now()
            ))
            conn.commit()
            print(f"✅ Noticia guardada: {titulo} [{departamento or 'nacional'}]")
            return True
        else:
            print(f"⚠️ Noticia duplicada (omitida): {titulo}")
            return False

    except Error as e:
        print(f"❌ Error al guardar noticia: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def obtener_noticias(limit=20, categoria=None, departamento=None):
    """
    Obtiene las últimas noticias desde la BD, opcionalmente filtradas por categoría y departamento.
    """
    conn = conectar()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM noticias WHERE 1=1"
        params = []
        
        if categoria:
            query += " AND categoria = %s"
            params.append(categoria)
        
        if departamento:
            query += " AND departamento = %s"
            params.append(departamento)
        
        query += " ORDER BY fecha_scraping DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        return resultados
    except Error as e:
        print(f"❌ Error al obtener noticias: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def obtener_departamentos_con_noticias():
    """
    Obtiene lista de departamentos que tienen noticias en la BD.
    """
    conn = conectar()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT departamento, COUNT(*) as cantidad 
            FROM noticias 
            WHERE departamento IS NOT NULL 
            GROUP BY departamento 
            ORDER BY cantidad DESC
        """)
        resultados = cursor.fetchall()
        return [{"departamento": row[0], "cantidad": row[1]} for row in resultados]
    except Error as e:
        print(f"❌ Error al obtener departamentos: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def obtener_categorias_con_noticias():
    """
    Obtiene lista de categorías que tienen noticias en la BD.
    """
    conn = conectar()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT categoria, COUNT(*) as cantidad 
            FROM noticias 
            WHERE categoria IS NOT NULL 
            GROUP BY categoria 
            ORDER BY cantidad DESC
        """)
        resultados = cursor.fetchall()
        return [{"categoria": row[0], "cantidad": row[1]} for row in resultados]
    except Error as e:
        print(f"❌ Error al obtener categorías: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def crear_tabla_si_no_existe():
    """
    Crea la tabla de noticias si no existe, incluyendo el campo departamento.
    """
    conn = conectar()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS noticias (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(500) NOT NULL,
                link VARCHAR(1000) NOT NULL,
                categoria VARCHAR(100),
                fecha DATE,
                resumen TEXT,
                autor VARCHAR(200),
                imagen VARCHAR(1000),
                fuente VARCHAR(100),
                departamento VARCHAR(50),
                fecha_scraping TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_news (titulo, link)
            )
        """)
        
        # Agregar columna departamento si no existe (para bases de datos existentes)
        try:
            cursor.execute("ALTER TABLE noticias ADD COLUMN departamento VARCHAR(50)")
            print("✅ Columna 'departamento' agregada a la tabla noticias")
        except Error:
            # La columna ya existe, no hay problema
            pass
            
        conn.commit()
        print("✅ Tabla 'noticias' verificada/creada correctamente")
        return True
    except Error as e:
        print(f"❌ Error al crear tabla: {e}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
