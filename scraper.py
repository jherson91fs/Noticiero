import requests
from bs4 import BeautifulSoup
from datetime import datetime
from db import guardar_noticia

# ----------------- LISTA DE FUENTES -----------------
# Atributos:
#   - url: página principal
#   - fuente: nombre del medio
#   - base: dominio (para links relativos)
#   - selector: selector CSS para noticias
#   - selector_img: selector CSS para imágenes (opcional)
#   - categoria: categoría general

FUENTES = [
    {
        "url": "https://www.bbc.com/mundo",
        "fuente": "BBC Mundo",
        "base": "https://www.bbc.com",
        "selector": "a",
        "selector_img": "img",   # ejemplo genérico
        "categoria": "Internacional"
    },
    {
        "url": "https://rpp.pe/",
        "fuente": "RPP Noticias",
        "base": "https://rpp.pe",
        "selector": "div.block-news a",
        "selector_img": "div.block-news img",
        "categoria": "Nacional"
    },
    {
        "url": "https://elcomercio.pe/",
        "fuente": "El Comercio",
        "base": "https://elcomercio.pe",
        "selector": "h2 a",
        "selector_img": "figure img",
        "categoria": "Nacional"
    },
    {
        "url": "https://peru21.pe/",
        "fuente": "Perú21",
        "base": "https://peru21.pe",
        "selector": "h2 a",
        "selector_img": "figure img",
        "categoria": "Nacional"
    },
    {
        "url": "https://larepublica.pe/",
        "fuente": "La República",
        "base": "https://larepublica.pe",
        "selector": "h2 a",
        "selector_img": "picture img",
        "categoria": "Nacional"
    }
]

# ----------------- FUNCIÓN GENÉRICA -----------------
def scrape_fuente(fuente):
    print(f"🌐 Scrapeando {fuente['fuente']}...")

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

            # Imagen asociada (si existe)
            imagen = None
            if i < len(imagenes):
                img_tag = imagenes[i]
                if img_tag.has_attr("src"):
                    imagen = img_tag["src"]
                elif img_tag.has_attr("data-src"):
                    imagen = img_tag["data-src"]

                # Completar si es relativa
                if imagen and not imagen.startswith("http"):
                    imagen = fuente["base"] + imagen

            # Otros datos
            categoria = fuente["categoria"]
            fecha = datetime.today().date()
            resumen = articulo.get("title") if articulo.has_attr("title") else None
            autor = None

            guardar_noticia(
                titulo, link, categoria, fecha, resumen, autor, imagen, fuente["fuente"]
            )

    except Exception as e:
        print(f"❌ Error en {fuente['fuente']}: {e}")

# ----------------- MAIN -----------------
if __name__ == "__main__":
    print("🚀 Iniciando scraping multipáginas con imágenes...")
    for fuente in FUENTES:
        scrape_fuente(fuente)
    print("✅ Finalizó scraping de todas las fuentes.")
