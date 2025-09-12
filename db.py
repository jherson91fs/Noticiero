import mysql.connector
from mysql.connector import Error
from datetime import datetime

# ----------------- CONFIG DB -----------------
db_config = {
    "host": "localhost",
    "user": "root",       # root sin password
    "password": "",
    "database": "noticiero_db"
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


def guardar_noticia(titulo, link, categoria, fecha, resumen, autor, imagen, fuente):
    """
    Inserta una noticia en la base de datos, evitando duplicados.
    """
    conn = conectar()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # Verificar duplicados (por título y link)
        cursor.execute("SELECT id FROM noticias WHERE titulo = %s AND link = %s", (titulo, link))
        existe = cursor.fetchone()

        if not existe:
            cursor.execute("""
                INSERT INTO noticias (titulo, link, categoria, fecha, resumen, autor, imagen, fuente, fecha_scraping)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                titulo, link, categoria, fecha, resumen, autor, imagen, fuente, datetime.now()
            ))
            conn.commit()
            print(f"✅ Noticia guardada: {titulo}")
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


def obtener_noticias(limit=20):
    """
    Obtiene las últimas noticias desde la BD.
    """
    conn = conectar()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM noticias ORDER BY fecha_scraping DESC LIMIT %s", (limit,))
        resultados = cursor.fetchall()
        return resultados
    except Error as e:
        print(f"❌ Error al obtener noticias: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
