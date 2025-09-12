from flask import Flask, jsonify, request, render_template
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import threading
import time
from bs4 import BeautifulSoup
import requests

# ---------------- FLASK ----------------
app = Flask(__name__, template_folder="templates", static_folder="static")

# ---------------- DB ----------------
DB_NAME = "noticiero"

def crear_base_y_tabla():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cursor.execute(f"USE {DB_NAME};")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS noticias (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(500) NOT NULL,
                link VARCHAR(500) NOT NULL,
                categoria VARCHAR(100),
                fecha DATE,
                resumen TEXT,
                autor VARCHAR(255),
                imagen VARCHAR(500),
                fuente VARCHAR(255),
                fecha_scraping DATETIME,
                UNIQUE KEY unique_link (link)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        conn.commit()
        conn.close()
        print(f"✅ Base y tabla '{DB_NAME}.noticias' verificadas/creadas.")
    except Error as e:
        print(f"❌ Error al crear la base o tabla: {e}")

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database=DB_NAME
        )
        return conn
    except Error as e:
        print(f"❌ Error en la conexión a DB: {e}")
        return None

def guardar_noticia(titulo, link, categoria, fecha, resumen, autor, imagen, fuente):
    conn = get_connection()
    if not conn:
        return False, "Error DB"

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM noticias WHERE link = %s OR titulo = %s", (link, titulo))
        if cursor.fetchone():
            conn.close()
            return False, "Duplicado"

        fecha_scraping = datetime.now()
        cursor.execute("""
            INSERT INTO noticias (titulo, link, categoria, fecha, resumen, autor, imagen, fuente, fecha_scraping)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (titulo, link, categoria, fecha, resumen, autor, imagen, fuente, fecha_scraping))
        conn.commit()
        conn.close()
        return True, "Guardado"
    except Error as e:
        print(f"❌ Error al insertar noticia: {e}")
        conn.close()
        return False, "Error DB"

def ultima_fecha_fuente(fuente):
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(fecha_scraping) FROM noticias WHERE fuente = %s", (fuente,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result[0] else None

# ---------------- FUENTES ----------------
FUENTES = [
    {"url": "https://www.bbc.com/mundo", "fuente": "BBC Mundo", "base": "https://www.bbc.com", "selector": "a", "selector_img": "img", "categoria": "Internacional"},
    {"url": "https://rpp.pe/", "fuente": "RPP Noticias", "base": "https://rpp.pe", "selector": "div.block-news a", "selector_img": "div.block-news img", "categoria": "Nacional"},
    {"url": "https://elcomercio.pe/", "fuente": "El Comercio", "base": "https://elcomercio.pe", "selector": "h2 a", "selector_img": "figure img", "categoria": "Nacional"},
    {"url": "https://peru21.pe/", "fuente": "Perú21", "base": "https://peru21.pe", "selector": "h2 a", "selector_img": "figure img", "categoria": "Nacional"},
    {"url": "https://larepublica.pe/", "fuente": "La República", "base": "https://larepublica.pe", "selector": "h2 a", "selector_img": "picture img", "categoria": "Nacional"}
]

# ---------------- SCRAPER ----------------
def scrape_fuente(fuente):
    print(f"🌐 Scrapeando {fuente['fuente']}...")
    ultima_fecha = ultima_fecha_fuente(fuente["fuente"])
    nuevas = duplicados = errores = 0

    try:
        response = requests.get(fuente["url"], timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        articulos = soup.select(fuente["selector"])
        imagenes = soup.select(fuente.get("selector_img", "")) if fuente.get("selector_img") else []

        for i, articulo in enumerate(articulos):
            titulo = articulo.get_text(strip=True)
            link = articulo.get("href")
            if not titulo or not link:
                continue
            if not link.startswith("http"):
                link = fuente["base"] + link

            imagen = None
            if i < len(imagenes):
                img_tag = imagenes[i]
                if img_tag.has_attr("src"):
                    imagen = img_tag["src"]
                elif img_tag.has_attr("data-src"):
                    imagen = img_tag["data-src"]
                if imagen and not imagen.startswith("http"):
                    imagen = fuente["base"] + imagen

            categoria = fuente["categoria"]
            fecha = datetime.today().date()
            resumen = articulo.get("title") if articulo.has_attr("title") else None
            autor = None

            if not ultima_fecha or fecha > ultima_fecha.date():
                ok, mensaje = guardar_noticia(titulo, link, categoria, fecha, resumen, autor, imagen, fuente["fuente"])
                if ok: nuevas += 1
                elif mensaje == "Duplicado": duplicados += 1
                else: errores += 1
            else:
                duplicados += 1

        print(f"✅ {fuente['fuente']} - Nuevas: {nuevas}, Duplicados: {duplicados}, Errores: {errores}")

    except Exception as e:
        print(f"❌ Error en {fuente['fuente']}: {e}")

# ---------------- AUTOMATIZACIÓN ----------------
def scraper_automatico():
    while True:
        print("🔄 Ejecutando scraping incremental automático...")
        for fuente in FUENTES:
            scrape_fuente(fuente)
        print("✅ Scraping incremental finalizado.")
        time.sleep(3600)

# ---------------- RUTAS HTML ----------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/noticia")
def noticia_detalle():
    return render_template("noticia.html")

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")

# ---------------- RUTAS API ----------------
@app.route("/api/noticias", methods=["GET"])
def listar_noticias():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    offset = (page - 1) * limit

    conn = get_connection()
    if not conn: return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM noticias ORDER BY fecha DESC LIMIT %s OFFSET %s", (limit, offset))
    rows = cursor.fetchall()
    conn.close()
    if not rows: return jsonify({"mensaje": "No hay noticias disponibles"}), 404
    return jsonify(rows), 200

@app.route("/api/noticias/filtrar", methods=["GET"])
def filtrar_noticias():
    fuente = request.args.get("fuente")
    categoria = request.args.get("categoria")
    fecha = request.args.get("fecha")

    query = "SELECT * FROM noticias WHERE 1=1"
    params = []

    if fuente: query += " AND fuente = %s"; params.append(fuente)
    if categoria: query += " AND categoria = %s"; params.append(categoria)
    if fecha: query += " AND fecha = %s"; params.append(fecha)

    conn = get_connection()
    if not conn: return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    if not rows: return jsonify({"mensaje": "No se encontraron noticias con esos filtros"}), 404
    return jsonify(rows), 200

@app.route("/api/noticias/<int:noticia_id>", methods=["GET"])
def noticia_por_id(noticia_id):
    conn = get_connection()
    if not conn: return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM noticias WHERE id = %s", (noticia_id,))
    row = cursor.fetchone()
    conn.close()
    if not row: return jsonify({"mensaje": f"No existe la noticia con id {noticia_id}"}), 404
    return jsonify(row), 200

@app.route("/api/noticias/buscar", methods=["GET"])
def buscar_noticias():
    keyword = request.args.get("q")
    if not keyword: return jsonify({"error": "Debe proporcionar un parámetro ?q=palabra"}), 400

    conn = get_connection()
    if not conn: return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM noticias WHERE titulo LIKE %s OR resumen LIKE %s ORDER BY fecha DESC"
    cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
    rows = cursor.fetchall()
    conn.close()
    if not rows: return jsonify({"mensaje": "No se encontraron noticias con esa búsqueda"}), 404
    return jsonify(rows), 200

# ---------------- MAIN ----------------
if __name__ == "__main__":
    crear_base_y_tabla()  # Verifica/crea DB y tabla
    threading.Thread(target=scraper_automatico, daemon=True).start()
    app.run(debug=True, port=5000)
