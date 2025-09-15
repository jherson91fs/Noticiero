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
from sources import FUENTES, obtener_fuentes_por_categoria, obtener_categorias_disponibles, clasificar_noticia
from db import crear_tabla_si_no_existe, obtener_departamentos_con_noticias, obtener_categorias_con_noticias
import re

# ---------------- FLASK ----------------
app = Flask(__name__, template_folder="templates", static_folder="static")

# Cargar variables de entorno
load_dotenv()

# ---------------- DB ----------------
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "noticiero_db")

# Sanitizar el nombre de la base de datos para evitar inyección en DDL
def _sanitize_db_name(db_name):
    # Permitir solo letras, números y guiones bajos
    clean = re.sub(r"[^0-9A-Za-z_]", "", db_name or "")
    return clean or "noticiero_db"

DB_NAME = _sanitize_db_name(DB_NAME)

def crear_base_y_tabla():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cursor.execute(f"USE `{DB_NAME}`;")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS noticias (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(500) NOT NULL,
                link VARCHAR(500) NOT NULL,
                categoria VARCHAR(100),
                tipo VARCHAR(50),
                fecha DATE,
                resumen TEXT,
                autor VARCHAR(255),
                imagen VARCHAR(500),
                fuente VARCHAR(255),
                departamento VARCHAR(50),
                fecha_scraping DATETIME,
                UNIQUE KEY unique_link (link)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        # Intentar agregar columna tipo si la tabla ya existía
        try:
            cursor.execute("ALTER TABLE noticias ADD COLUMN tipo VARCHAR(50)")
        except Exception:
            pass
        # Intentar agregar columna departamento si la tabla ya existía
        try:
            cursor.execute("ALTER TABLE noticias ADD COLUMN departamento VARCHAR(50)")
        except Exception:
            pass
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
            cursor.execute("CREATE INDEX idx_departamento ON noticias (departamento)")
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

def guardar_noticia(titulo, link, categoria, fecha, resumen, autor, imagen, fuente, departamento=None):
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
        tipo = clasificar_tipo(titulo, resumen, categoria, fuente)
        
        # Si no se especifica categoría, clasificar automáticamente
        if not categoria:
            clasificacion = clasificar_noticia(titulo, resumen, "nacional")
            categoria = clasificacion["categoria"]
            if not departamento:
                departamento = clasificacion["departamento"]
        
        cursor.execute("""
            INSERT INTO noticias (titulo, link, categoria, tipo, fecha, resumen, autor, imagen, fuente, departamento, fecha_scraping)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (titulo, link, categoria, tipo, fecha, resumen, autor, imagen, fuente, departamento, fecha_scraping))
        conn.commit()
        conn.close()
        return True, "Guardado"
    except Error as e:
        print(f"❌ Error al insertar noticia: {e}")
        conn.close()
        return False, "Error DB"

# ---------------- CLASIFICACIÓN ----------------
def clasificar_tipo(titulo, resumen, categoria, fuente):
    texto = " ".join([str(x or "") for x in [titulo, resumen, categoria, fuente]]).lower()
    reglas = [
        ("deporte", ["deporte", "futbol", "fútbol", "liga", "partido", "gol", "selección", "mundial"]),
        ("comedia", ["humor", "broma", "meme", "parodia", "satira", "sátira", "chiste"]),
        ("economía", ["economía", "dólar", "inflación", "bcr", "mercado", "bolsa"]),
        ("política", ["congreso", "presidente", "ministro", "política", "gobierno", "elecciones"]),
        ("policial", ["policía", "pnp", "homicidio", "robo", "capturan", "detienen"]),
        ("salud", ["salud", "hospital", "covid", "vacuna", "epidemia"]),
        ("educación", ["educación", "universidad", "colegio", "estudiantes", "sunedu"]),
    ]
    for etiqueta, palabras in reglas:
        if any(p in texto for p in palabras):
            return etiqueta
    return "informativo"

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

            # Categoría: usar category_selector si existe, si no, la fija de la fuente (si la hubiera)
            categoria = None
            if use_container and fuente.get("category_selector"):
                cat_el = item.select_one(fuente["category_selector"]) 
                if cat_el:
                    categoria = cat_el.get_text(strip=True)
            if not categoria:
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
                # Clasificar automáticamente la noticia
                clasificacion = clasificar_noticia(titulo, resumen, fuente.get("categoria", "nacional"))
                
                ok, mensaje = guardar_noticia(
                    titulo, link, clasificacion["categoria"], fecha, resumen, autor, imagen, 
                    fuente["fuente"], clasificacion["departamento"]
                )
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

@app.route("/favoritos")
def favoritos():
    return render_template("favoritos.html")

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
    tipo = request.args.get("tipo")
    departamento = request.args.get("departamento")
    fecha_desde = request.args.get("fecha_desde")
    fecha_hasta = request.args.get("fecha_hasta")
    ordenar = request.args.get("ordenar", "fecha_desc")  # fecha_desc, fecha_asc, titulo_asc, titulo_desc

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
    if tipo:
        base_query += " AND tipo = %s"
        params.append(tipo)
    if departamento:
        base_query += " AND departamento = %s"
        params.append(departamento)
    if fecha_desde:
        base_query += " AND fecha >= %s"
        params.append(fecha_desde)
    if fecha_hasta:
        base_query += " AND fecha <= %s"
        params.append(fecha_hasta)
    
    # Ordenamiento - priorizar noticias más recientes
    order_clause = "ORDER BY "
    if ordenar == "fecha_asc":
        order_clause += "fecha ASC, fecha_scraping DESC"
    elif ordenar == "titulo_asc":
        order_clause += "titulo ASC, fecha_scraping DESC"
    elif ordenar == "titulo_desc":
        order_clause += "titulo DESC, fecha_scraping DESC"
    else:  # fecha_desc por defecto - mostrar las más recientes primero
        order_clause += "fecha_scraping DESC, fecha DESC"
    
    base_query += f" {order_clause} LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    cursor.execute(base_query, tuple(params))
    rows = cursor.fetchall()
    
    # Contar total para paginación
    count_query = "SELECT COUNT(*) as total FROM noticias WHERE 1=1"
    count_params = []
    count_query += " AND (fuente IS NULL OR fuente NOT IN ('Perú21','Peru21'))"
    if fuente:
        count_query += " AND fuente = %s"
        count_params.append(fuente)
    if categoria:
        count_query += " AND categoria = %s"
        count_params.append(categoria)
    if tipo:
        count_query += " AND tipo = %s"
        count_params.append(tipo)
    if departamento:
        count_query += " AND departamento = %s"
        count_params.append(departamento)
    if fecha_desde:
        count_query += " AND fecha >= %s"
        count_params.append(fecha_desde)
    if fecha_hasta:
        count_query += " AND fecha <= %s"
        count_params.append(fecha_hasta)
    
    cursor.execute(count_query, tuple(count_params))
    total = cursor.fetchone()["total"]
    
    conn.close()
    if not rows: return jsonify({"mensaje": "No hay noticias disponibles", "total": 0, "page": page, "total_pages": 0}), 404
    
    total_pages = (total + limit - 1) // limit
    return jsonify({
        "noticias": rows,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }), 200

@app.route("/api/noticias/filtrar", methods=["GET"])
def filtrar_noticias():
    fuente = request.args.get("fuente")
    categoria = request.args.get("categoria")
    fecha = request.args.get("fecha")
    tipo = request.args.get("tipo")
    departamento = request.args.get("departamento")
    fecha_desde = request.args.get("fecha_desde")
    fecha_hasta = request.args.get("fecha_hasta")
    ordenar = request.args.get("ordenar", "fecha_desc")
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    offset = (page - 1) * limit

    query = "SELECT * FROM noticias WHERE 1=1"
    params = []

    if fuente: query += " AND fuente = %s"; params.append(fuente)
    if categoria: query += " AND categoria = %s"; params.append(categoria)
    if fecha: query += " AND fecha = %s"; params.append(fecha)
    if tipo: query += " AND tipo = %s"; params.append(tipo)
    if departamento: query += " AND departamento = %s"; params.append(departamento)
    if fecha_desde: query += " AND fecha >= %s"; params.append(fecha_desde)
    if fecha_hasta: query += " AND fecha <= %s"; params.append(fecha_hasta)
    # Excluir Peru21 de forma global
    query += " AND (fuente IS NULL OR fuente NOT IN ('Perú21','Peru21'))"

    conn = get_connection()
    if not conn: return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = conn.cursor(dictionary=True)
    
    # Ordenamiento - priorizar noticias más recientes
    order_clause = "ORDER BY "
    if ordenar == "fecha_asc":
        order_clause += "fecha ASC, fecha_scraping DESC"
    elif ordenar == "titulo_asc":
        order_clause += "titulo ASC, fecha_scraping DESC"
    elif ordenar == "titulo_desc":
        order_clause += "titulo DESC, fecha_scraping DESC"
    else:  # fecha_desc por defecto - mostrar las más recientes primero
        order_clause += "fecha_scraping DESC, fecha DESC"
    
    query += f" {order_clause} LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    
    # Contar total para paginación
    count_query = "SELECT COUNT(*) as total FROM noticias WHERE 1=1"
    count_params = []
    if fuente: count_query += " AND fuente = %s"; count_params.append(fuente)
    if categoria: count_query += " AND categoria = %s"; count_params.append(categoria)
    if fecha: count_query += " AND fecha = %s"; count_params.append(fecha)
    if tipo: count_query += " AND tipo = %s"; count_params.append(tipo)
    if departamento: count_query += " AND departamento = %s"; count_params.append(departamento)
    if fecha_desde: count_query += " AND fecha >= %s"; count_params.append(fecha_desde)
    if fecha_hasta: count_query += " AND fecha <= %s"; count_params.append(fecha_hasta)
    count_query += " AND (fuente IS NULL OR fuente NOT IN ('Perú21','Peru21'))"
    
    cursor.execute(count_query, tuple(count_params))
    total = cursor.fetchone()["total"]
    
    conn.close()
    if not rows: return jsonify({"mensaje": "No se encontraron noticias con esos filtros", "total": 0, "page": page, "total_pages": 0}), 404
    
    total_pages = (total + limit - 1) // limit
    return jsonify({
        "noticias": rows,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }), 200

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
    ordenar = request.args.get("ordenar", "fecha_desc")
    
    query = "SELECT * FROM noticias WHERE (fuente IS NULL OR fuente NOT IN ('Perú21','Peru21')) AND (titulo LIKE %s OR resumen LIKE %s)"
    
    # Ordenamiento - priorizar noticias más recientes
    order_clause = "ORDER BY "
    if ordenar == "fecha_asc":
        order_clause += "fecha ASC, fecha_scraping DESC"
    elif ordenar == "titulo_asc":
        order_clause += "titulo ASC, fecha_scraping DESC"
    elif ordenar == "titulo_desc":
        order_clause += "titulo DESC, fecha_scraping DESC"
    else:  # fecha_desc por defecto - mostrar las más recientes primero
        order_clause += "fecha_scraping DESC, fecha DESC"
    
    query += f" {order_clause} LIMIT %s OFFSET %s"
    cursor.execute(query, (f"%{keyword}%", f"%{keyword}%", limit, offset))
    rows = cursor.fetchall()
    
    # Contar total para paginación
    count_query = "SELECT COUNT(*) as total FROM noticias WHERE (fuente IS NULL OR fuente NOT IN ('Perú21','Peru21')) AND (titulo LIKE %s OR resumen LIKE %s)"
    cursor.execute(count_query, (f"%{keyword}%", f"%{keyword}%"))
    total = cursor.fetchone()["total"]
    
    conn.close()
    if not rows: return jsonify({"mensaje": "No se encontraron noticias con esa búsqueda", "total": 0, "page": page, "total_pages": 0}), 404
    
    total_pages = (total + limit - 1) // limit
    return jsonify({
        "noticias": rows,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }), 200

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
    cursor.execute("SELECT DISTINCT tipo FROM noticias WHERE tipo IS NOT NULL AND tipo <> ''")
    tipos = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT departamento FROM noticias WHERE departamento IS NOT NULL AND departamento <> ''")
    departamentos = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify({"fuentes": fuentes, "categorias": categorias, "tipos": tipos, "departamentos": departamentos}), 200

@app.route("/api/categorias", methods=["GET"])
def listar_categorias():
    """Devuelve lista de categorías disponibles con conteo de noticias"""
    conn = get_connection()
    if not conn: return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT categoria, COUNT(*) as cantidad 
        FROM noticias 
        WHERE categoria IS NOT NULL AND categoria <> '' 
        GROUP BY categoria 
        ORDER BY cantidad DESC
    """)
    categorias = cursor.fetchall()
    conn.close()
    return jsonify({"categorias": categorias}), 200

@app.route("/api/noticias/categoria/<categoria>", methods=["GET"])
def noticias_por_categoria(categoria):
    """Obtiene noticias de una categoría específica"""
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    offset = (page - 1) * limit
    
    conn = get_connection()
    if not conn: return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = conn.cursor(dictionary=True)
    
    # Obtener noticias de la categoría
    cursor.execute("""
        SELECT * FROM noticias 
        WHERE categoria = %s 
        ORDER BY fecha_scraping DESC 
        LIMIT %s OFFSET %s
    """, (categoria, limit, offset))
    noticias = cursor.fetchall()
    
    # Contar total
    cursor.execute("SELECT COUNT(*) as total FROM noticias WHERE categoria = %s", (categoria,))
    total = cursor.fetchone()["total"]
    
    conn.close()
    
    total_pages = (total + limit - 1) // limit
    return jsonify({
        "noticias": noticias,
        "categoria": categoria,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }), 200

@app.route("/api/departamentos", methods=["GET"])
def listar_departamentos():
    """Devuelve lista de departamentos disponibles con conteo de noticias"""
    conn = get_connection()
    if not conn: return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT departamento, COUNT(*) as cantidad 
        FROM noticias 
        WHERE departamento IS NOT NULL AND departamento <> '' 
        GROUP BY departamento 
        ORDER BY cantidad DESC
    """)
    departamentos = cursor.fetchall()
    conn.close()
    return jsonify({"departamentos": departamentos}), 200

@app.route("/api/noticias/departamento/<departamento>", methods=["GET"])
def noticias_por_departamento(departamento):
    """Obtiene noticias de un departamento específico"""
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    offset = (page - 1) * limit
    
    conn = get_connection()
    if not conn: return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = conn.cursor(dictionary=True)
    
    # Obtener noticias del departamento
    cursor.execute("""
        SELECT * FROM noticias 
        WHERE departamento = %s 
        ORDER BY fecha_scraping DESC 
        LIMIT %s OFFSET %s
    """, (departamento, limit, offset))
    noticias = cursor.fetchall()
    
    # Contar total
    cursor.execute("SELECT COUNT(*) as total FROM noticias WHERE departamento = %s", (departamento,))
    total = cursor.fetchone()["total"]
    
    conn.close()
    
    total_pages = (total + limit - 1) // limit
    return jsonify({
        "noticias": noticias,
        "departamento": departamento,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }), 200

@app.route("/api/noticias/relacionadas", methods=["GET"])
def noticias_relacionadas():
    noticia_id = request.args.get("id")
    limit = int(request.args.get("limit", 6))
    modo = request.args.get("modo", "categoria")  # categoria | tipo | random
    if not noticia_id:
        return jsonify({"error": "Falta ?id"}), 400
    conn = get_connection()
    if not conn: return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
    cur = conn.cursor(dictionary=True)
    # Buscar noticia base
    cur.execute("SELECT categoria, tipo, fuente FROM noticias WHERE id = %s", (noticia_id,))
    base = cur.fetchone()
    if not base:
        conn.close()
        return jsonify({"mensaje": "No existe la noticia"}), 404
    if modo == "random":
        cur.execute(
            """
            SELECT * FROM noticias
            WHERE id <> %s
              AND (fuente IS NULL OR fuente NOT IN ('Perú21','Peru21'))
            ORDER BY RAND()
            LIMIT %s
            """,
            (noticia_id, limit)
        )
    elif modo == "tipo":
        cur.execute(
            """
            SELECT * FROM noticias
            WHERE id <> %s
              AND (tipo IS NOT NULL AND tipo = %s)
              AND (fuente IS NULL OR fuente NOT IN ('Perú21','Peru21'))
            ORDER BY fecha DESC
            LIMIT %s
            """,
            (noticia_id, base.get("tipo"), limit)
        )
    else:
        # categoria (por defecto)
        cur.execute(
            """
            SELECT * FROM noticias
            WHERE id <> %s
              AND (categoria IS NOT NULL AND categoria = %s)
              AND (fuente IS NULL OR fuente NOT IN ('Perú21','Peru21'))
            ORDER BY fecha DESC
            LIMIT %s
            """,
            (noticia_id, base.get("categoria"), limit)
        )
    rows = cur.fetchall()
    conn.close()
    return jsonify(rows), 200

@app.route("/api/scraping/categoria/<categoria>", methods=["POST"])
def ejecutar_scraping_categoria(categoria):
    """Ejecuta scraping para una categoría específica"""
    try:
        # Importar funciones de scraping
        from scraper import scrape_por_categoria
        
        # Ejecutar scraping en un hilo separado
        def scraping_thread():
            scrape_por_categoria(categoria)
        
        thread = threading.Thread(target=scraping_thread)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "mensaje": f"Scraping iniciado para categoría: {categoria}",
            "categoria": categoria
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Error al iniciar scraping: {str(e)}"}), 500

@app.route("/api/scraping/todos", methods=["POST"])
def ejecutar_scraping_todos():
    """Ejecuta scraping para todas las categorías"""
    try:
        # Importar funciones de scraping
        from scraper import scrape_por_categoria
        
        # Ejecutar scraping en un hilo separado
        def scraping_thread():
            scrape_por_categoria()
        
        thread = threading.Thread(target=scraping_thread)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "mensaje": "Scraping iniciado para todas las categorías",
            "categoria": "todos"
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Error al iniciar scraping: {str(e)}"}), 500

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
