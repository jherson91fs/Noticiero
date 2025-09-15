import requests
from bs4 import BeautifulSoup
from datetime import datetime
from db import guardar_noticia, crear_tabla_si_no_existe
from sources import FUENTES, obtener_fuentes_por_categoria, obtener_categorias_disponibles, clasificar_noticia
from urllib.parse import urljoin
import sys


# FUENTES importadas desde sources.py

# ----------------- FUNCIÓN GENÉRICA -----------------
def scrape_fuente(fuente):
    print(f"🌐 Scrapeando {fuente['fuente']}...")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36 NoticieroBot/1.0"
        }
        response = requests.get(fuente["url"], timeout=12, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        use_container = bool(fuente.get("container"))
        if use_container:
            items = soup.select(fuente["container"]) or []
        else:
            items = soup.select(fuente.get("selector", "a")) or []

        for item in items:
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
            link = urljoin(fuente["base"], link)

            # Imagen
            imagen = None
            if use_container and fuente.get("img_selector"):
                img_sel = fuente["img_selector"]
                css_sel = img_sel.split("::attr(")[0].strip()
                img_el = item.select_one(css_sel)
                if img_el:
                    imagen = img_el.get("src") or img_el.get("data-src") or img_el.get("data-img-url")
                if not imagen and "::attr(" in img_sel:
                    attr_name = img_sel.split("::attr(",1)[1][:-1]
                    if img_el and img_el.get(attr_name):
                        imagen = img_el.get(attr_name)
            elif not use_container and fuente.get("selector_img"):
                el = item.select_one(fuente["selector_img"]) if hasattr(item, 'select_one') else None
                if el:
                    imagen = el.get("src") or el.get("data-src") or el.get("data-img-url")
            if imagen:
                imagen = urljoin(fuente["base"], imagen)

            # Otros datos
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

            # Clasificar la noticia automáticamente
            clasificacion = clasificar_noticia(titulo, resumen, fuente.get("categoria", "nacional"))
            
            guardar_noticia(
                titulo, link, clasificacion["categoria"], fecha, resumen, autor, imagen, fuente["fuente"], clasificacion["departamento"]
            )

    except Exception as e:
        print(f"❌ Error en {fuente['fuente']}: {e}")

# ----------------- FUNCIÓN PARA SCRAPING POR CATEGORÍA -----------------
def scrape_por_categoria(categoria=None):
    """
    Realiza scraping de noticias para una categoría específica o todas las fuentes.
    
    Args:
        categoria: 'nacional', 'internacional', 'regional' o None para todas
    """
    print(f"🚀 Iniciando scraping para: {categoria or 'TODAS LAS CATEGORÍAS'}...")
    
    # Crear tabla si no existe
    crear_tabla_si_no_existe()
    
    # Obtener fuentes según la categoría
    if categoria:
        fuentes = obtener_fuentes_por_categoria(categoria)
        if not fuentes:
            print(f"❌ No se encontraron fuentes para la categoría: {categoria}")
            return
        print(f"📂 Scrapeando {len(fuentes)} fuentes para categoría: {categoria}")
    else:
        fuentes = FUENTES
        print(f"🌍 Scrapeando {len(fuentes)} fuentes de todas las categorías")
    
    # Realizar scraping
    for fuente in fuentes:
        scrape_fuente(fuente)
    
    print(f"✅ Finalizó scraping para: {categoria or 'TODAS LAS CATEGORÍAS'}")

# ----------------- MAIN -----------------
if __name__ == "__main__":
    # Verificar argumentos de línea de comandos
    categoria = None
    if len(sys.argv) > 1:
        categoria = sys.argv[1].lower()
        print(f"📂 Modo categoría: {categoria}")
    
    scrape_por_categoria(categoria)
