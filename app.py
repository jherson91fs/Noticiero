from flask import Flask, jsonify, request, render_template
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import threading
import time
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from sources import FUENTES

# ---------------- FLASK ----------------
app = Flask(__name__, template_folder="templates", static_folder="static")

# Cargar variables de entorno
load_dotenv()

# ---------------- DB ----------------
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "noticiero_db")

def crear_base_y_tabla():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
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
        # Índices útiles (si ya existen, ignorar error)
        try:
            cursor.execute("CREATE INDEX idx_fecha ON noticias (fecha)")
        except Exception:
            pass
        try:
            cursor.execute("CREATE INDEX idx_fuente ON noticias (fuente)")
        except Exception:
            pass
        try:
            cursor.execute("CREATE INDEX idx_categoria ON noticias (categoria)")
        except Exception:
            pass
        try:
            cursor.execute("CREATE FULLTEXT INDEX ft_titulo_resumen ON noticias (titulo, resumen)")
        except Exception:
            pass
        conn.commit()
        conn.close()
        print(f"✅ Base y tabla '{DB_NAME}.noticias' verificadas/creadas.")
    except Error as e:
        print(f"❌ Error al crear la base o tabla: {e}")

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
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
        # Bloquear cualquier noticia de Peru21/Perú21
        if fuente and fuente.strip().lower() in ("peru21", "perú21"):
            conn.close()
            return False, "Bloqueado"
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

# ---------------- SCRAPER ----------------
def scrape_fuente(fuente):
    print(f"🌐 Scrapeando {fuente['fuente']}...")
    ultima_fecha = ultima_fecha_fuente(fuente["fuente"])
    nuevas = duplicados = errores = 0

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36 NoticieroBot/1.0"
        }
        response = requests.get(fuente["url"], timeout=12, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # Nuevo esquema basado en container/title_selector/img_selector
        items = []
        use_container = bool(fuente.get("container"))
        if use_container:
            items = soup.select(fuente["container"]) or []
        else:
            articulos = soup.select(fuente.get("selector", "a")) or []
            items = articulos

        for i, item in enumerate(items):
            # Título y enlace
            anchor = None
            if use_container and fuente.get("title_selector"):
                anchor = item.select_one(fuente["title_selector"]) or item.find('a', href=True)
            else:
                anchor = item if getattr(item, 'name', None) == 'a' else item.find('a', href=True)
            link = anchor.get('href') if anchor and anchor.has_attr('href') else None
            titulo = anchor.get_text(strip=True) if anchor else (item.get_text(strip=True) if item else None)
            if not titulo or not link:
                continue
            # Normalizar URL absoluta
            link = urljoin(fuente["base"], link)

            # Imagen por item
            imagen = None
            if use_container and fuente.get("img_selector"):
                img_el = item.select_one(fuente["img_selector"].split("::attr(")[0].strip())
                if img_el:
                    imagen = img_el.get("src") or img_el.get("data-src") or img_el.get("data-img-url")
                # Si el selector especifica ::attr(attr)
                if not imagen and "::attr(" in fuente["img_selector"]:
                    attr_name = fuente["img_selector"].split("::attr(",1)[1][:-1]
                    if img_el and img_el.get(attr_name):
                        imagen = img_el.get(attr_name)
            elif not use_container and fuente.get("selector_img"):
                # compatibilidad con esquema antiguo
                sel_img = fuente["selector_img"]
                if "::attr(" in sel_img and sel_img.endswith(")"):
                    css_sel, attr_part = sel_img.split("::attr(", 1)
                    attr_name = attr_part[:-1]
                    el = soup.select_one(css_sel.strip())
                    imagen = el.get(attr_name) if el else None
                else:
                    el = soup.select_one(sel_img)
                    if el:
                        imagen = el.get("src") or el.get("data-src") or el.get("data-img-url")
            if imagen:
                imagen = urljoin(fuente["base"], imagen)

            categoria = fuente.get("categoria")
            fecha = datetime.today().date()
            resumen = None
            if use_container and fuente.get("summary_selector"):
                sum_el = item.select_one(fuente["summary_selector"]) 
                if sum_el:
                    resumen = sum_el.get_text(strip=True)
            autor = None
            if use_container and fuente.get("author_selector"):
                aut_el = item.select_one(fuente["author_selector"]) 
                if aut_el:
                    autor = aut_el.get_text(strip=True)

            # Intentar extraer fecha desde date_selector si existe
            if use_container and fuente.get("date_selector"):
                date_el = item.select_one(fuente["date_selector"]) 
                if date_el:
                    txt = date_el.get_text(strip=True)
                    parsed = None
                    try:
                        if "/" in txt:
                            parts = [p for p in txt.replace("\u00a0", " ").split("/") if p]
                            if len(parts) >= 3:
                                parsed = datetime(int(parts[2][:4]), int(parts[1]), int(parts[0])).date()
                        elif "-" in txt:
                            parts = [p for p in txt.split("-") if p]
                            if len(parts) >= 3 and len(parts[0]) == 4:
                                parsed = datetime(int(parts[0]), int(parts[1]), int(parts[2][:2])).date()
                    except Exception:
                        parsed = None
                    if parsed:
                        fecha = parsed

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

    # Filtros opcionales para compatibilidad simple
    fuente = request.args.get("fuente")
    categoria = request.args.get("categoria")

    conn = get_connection()
    if not conn: return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = conn.cursor(dictionary=True)
    base_query = "SELECT * FROM noticias WHERE 1=1"
    params = []
    # Excluir Peru21 de forma global
    base_query += " AND (fuente IS NULL OR fuente NOT IN ('Perú21','Peru21'))"
    if fuente:
        base_query += " AND fuente = %s"
        params.append(fuente)
    if categoria:
        base_query += " AND categoria = %s"
        params.append(categoria)
    base_query += " ORDER BY fecha DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    cursor.execute(base_query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    if not rows: return jsonify({"mensaje": "No hay noticias disponibles"}), 404
    return jsonify(rows), 200

@app.route("/api/noticias/filtrar", methods=["GET"])
def filtrar_noticias():
    fuente = request.args.get("fuente")
    categoria = request.args.get("categoria")
    fecha = request.args.get("fecha")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    offset = (page - 1) * limit

    query = "SELECT * FROM noticias WHERE 1=1"
    params = []

    if fuente: query += " AND fuente = %s"; params.append(fuente)
    if categoria: query += " AND categoria = %s"; params.append(categoria)
    if fecha: query += " AND fecha = %s"; params.append(fecha)
    # Excluir Peru21 de forma global
    query += " AND (fuente IS NULL OR fuente NOT IN ('Perú21','Peru21'))"

    conn = get_connection()
    if not conn: return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = conn.cursor(dictionary=True)
    query += " ORDER BY fecha DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
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
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    offset = (page - 1) * limit
    query = "SELECT * FROM noticias WHERE (fuente IS NULL OR fuente NOT IN ('Perú21','Peru21')) AND (titulo LIKE %s OR resumen LIKE %s) ORDER BY fecha DESC LIMIT %s OFFSET %s"
    cursor.execute(query, (f"%{keyword}%", f"%{keyword}%", limit, offset))
    rows = cursor.fetchall()
    conn.close()
    if not rows: return jsonify({"mensaje": "No se encontraron noticias con esa búsqueda"}), 404
    return jsonify(rows), 200

@app.route("/api/meta", methods=["GET"])
def meta_info():
    """Devuelve listas de fuentes y categorías disponibles en la DB"""
    conn = get_connection()
    if not conn: return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT fuente FROM noticias WHERE fuente IS NOT NULL AND fuente <> ''")
    fuentes = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT categoria FROM noticias WHERE categoria IS NOT NULL AND categoria <> ''")
    categorias = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify({"fuentes": fuentes, "categorias": categorias}), 200

# ---------------- MAIN ----------------
if __name__ == "__main__":
    crear_base_y_tabla()  # Verifica/crea DB y tabla
    # Purgar cualquier noticia existente de Peru21/Perú21
    try:
        conn = get_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM noticias WHERE fuente IN (%s, %s)", ("Perú21", "Peru21"))
            conn.commit()
            conn.close()
            print("🧹 Noticias de Perú21 eliminadas.")
    except Exception:
        pass
    threading.Thread(target=scraper_automatico, daemon=True).start()
    app.run(debug=True, port=5000)
