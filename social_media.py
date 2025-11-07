"""
Módulo para integración con redes sociales
Soporta: Twitter/X, Facebook, Instagram
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, quote
import re
import json

# ----------------- CONFIGURACIÓN -----------------
SOCIAL_MEDIA_CONFIG = {
    "twitter": {
        "enabled": True,
        "base_url": "https://twitter.com",
        "search_url": "https://twitter.com/search",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    },
    "facebook": {
        "enabled": True,
        "base_url": "https://www.facebook.com",
        "search_url": "https://www.facebook.com/search",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    },
    "instagram": {
        "enabled": True,
        "base_url": "https://www.instagram.com",
        "search_url": "https://www.instagram.com/explore/tags",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    }
}

# ----------------- FUNCIONES DE BÚSQUEDA -----------------
def buscar_twitter(query, limit=10):
    """
    Busca tweets relacionados con una consulta
    Nota: Twitter requiere autenticación para API oficial
    Esta función hace scraping básico de búsquedas públicas
    """
    try:
        # Construir URL de búsqueda
        search_query = quote(query)
        url = f"https://twitter.com/search?q={search_query}&src=typed_query&f=live"
        
        headers = SOCIAL_MEDIA_CONFIG["twitter"]["headers"]
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        tweets = []
        
        # Buscar tweets en la estructura HTML (esto puede variar)
        # Nota: Twitter cambia frecuentemente su estructura HTML
        tweet_elements = soup.find_all("article", {"data-testid": "tweet"})
        
        for element in tweet_elements[:limit]:
            try:
                # Extraer texto del tweet
                text_elem = element.find("div", {"data-testid": "tweetText"})
                text = text_elem.get_text(strip=True) if text_elem else ""
                
                # Extraer autor
                author_elem = element.find("span")
                author = author_elem.get_text(strip=True) if author_elem else "Usuario"
                
                # Extraer enlace
                link_elem = element.find("a", href=re.compile(r"/status/"))
                link = urljoin(SOCIAL_MEDIA_CONFIG["twitter"]["base_url"], link_elem["href"]) if link_elem else ""
                
                if text:
                    tweets.append({
                        "platform": "twitter",
                        "author": author,
                        "text": text,
                        "link": link,
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                continue
        
        return tweets
        
    except Exception as e:
        print(f"❌ Error buscando en Twitter: {e}")
        return []

def buscar_facebook(query, limit=10):
    """
    Busca posts públicos de Facebook relacionados con una consulta
    Nota: Facebook tiene restricciones estrictas, esta es una implementación básica
    """
    try:
        # Facebook requiere autenticación para búsquedas
        # Por ahora retornamos información básica
        return [{
            "platform": "facebook",
            "author": "Facebook",
            "text": f"Búsqueda de '{query}' en Facebook",
            "link": f"https://www.facebook.com/search/posts/?q={quote(query)}",
            "timestamp": datetime.now().isoformat(),
            "note": "Requiere autenticación para resultados completos"
        }]
        
    except Exception as e:
        print(f"❌ Error buscando en Facebook: {e}")
        return []

def buscar_instagram(query, limit=10):
    """
    Busca posts de Instagram por hashtag
    """
    try:
        # Limpiar query para hashtag
        hashtag = query.replace("#", "").replace(" ", "").lower()
        url = f"https://www.instagram.com/explore/tags/{hashtag}/"
        
        headers = SOCIAL_MEDIA_CONFIG["instagram"]["headers"]
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return []
        
        # Instagram usa JSON embebido en el HTML
        soup = BeautifulSoup(response.text, "html.parser")
        scripts = soup.find_all("script", type="text/javascript")
        
        posts = []
        for script in scripts:
            if script.string and "window._sharedData" in script.string:
                try:
                    # Extraer JSON
                    json_str = script.string.split("window._sharedData = ")[1].split(";</script>")[0]
                    data = json.loads(json_str)
                    
                    # Extraer posts
                    hashtag_data = data.get("entry_data", {}).get("TagPage", [{}])[0]
                    media = hashtag_data.get("tag", {}).get("media", {}).get("nodes", [])
                    
                    for item in media[:limit]:
                        posts.append({
                            "platform": "instagram",
                            "author": item.get("owner", {}).get("username", "Usuario"),
                            "text": item.get("caption", "")[:200] if item.get("caption") else "",
                            "link": f"https://www.instagram.com/p/{item.get('shortcode', '')}/",
                            "image": item.get("display_url", ""),
                            "timestamp": datetime.fromtimestamp(item.get("date", 0)).isoformat() if item.get("date") else datetime.now().isoformat()
                        })
                except Exception:
                    continue
        
        return posts
        
    except Exception as e:
        print(f"❌ Error buscando en Instagram: {e}")
        return []

# ----------------- FUNCIÓN PRINCIPAL -----------------
def buscar_redes_sociales(query, platforms=None, limit=10):
    """
    Busca contenido relacionado en múltiples redes sociales
    
    Args:
        query: Término de búsqueda
        platforms: Lista de plataformas ['twitter', 'facebook', 'instagram'] o None para todas
        limit: Número máximo de resultados por plataforma
    
    Returns:
        dict: Resultados organizados por plataforma
    """
    if platforms is None:
        platforms = ["twitter", "facebook", "instagram"]
    
    resultados = {
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "results": {}
    }
    
    if "twitter" in platforms and SOCIAL_MEDIA_CONFIG["twitter"]["enabled"]:
        resultados["results"]["twitter"] = buscar_twitter(query, limit)
    
    if "facebook" in platforms and SOCIAL_MEDIA_CONFIG["facebook"]["enabled"]:
        resultados["results"]["facebook"] = buscar_facebook(query, limit)
    
    if "instagram" in platforms and SOCIAL_MEDIA_CONFIG["instagram"]["enabled"]:
        resultados["results"]["instagram"] = buscar_instagram(query, limit)
    
    return resultados

# ----------------- FUNCIONES DE COMPARTIR -----------------
def generar_link_compartir_twitter(texto, url):
    """Genera link para compartir en Twitter"""
    texto_encoded = quote(texto)
    url_encoded = quote(url)
    return f"https://twitter.com/intent/tweet?text={texto_encoded}&url={url_encoded}"

def generar_link_compartir_facebook(url):
    """Genera link para compartir en Facebook"""
    url_encoded = quote(url)
    return f"https://www.facebook.com/sharer/sharer.php?u={url_encoded}"

def generar_link_compartir_whatsapp(texto, url):
    """Genera link para compartir en WhatsApp"""
    texto_completo = f"{texto} {url}"
    texto_encoded = quote(texto_completo)
    return f"https://wa.me/?text={texto_encoded}"

def generar_link_compartir_telegram(texto, url):
    """Genera link para compartir en Telegram"""
    texto_completo = f"{texto} {url}"
    texto_encoded = quote(texto_completo)
    return f"https://t.me/share/url?url={url_encoded}&text={texto_encoded}"

# ----------------- FUNCIÓN DE BÚSQUEDA POR NOTICIA -----------------
def buscar_redes_sociales_por_noticia(titulo, departamento=None, categoria=None):
    """
    Busca contenido en redes sociales relacionado con una noticia
    
    Args:
        titulo: Título de la noticia
        departamento: Departamento relacionado (opcional)
        categoria: Categoría de la noticia (opcional)
    
    Returns:
        dict: Resultados de búsqueda
    """
    # Construir query de búsqueda
    query_parts = [titulo]
    
    if departamento:
        query_parts.append(departamento)
    
    if categoria:
        query_parts.append(categoria)
    
    query = " ".join(query_parts)
    
    return buscar_redes_sociales(query, limit=5)

# ----------------- MAIN (para pruebas) -----------------
if __name__ == "__main__":
    print("🔍 Probando integración con redes sociales...")
    
    # Ejemplo de búsqueda
    resultados = buscar_redes_sociales("Puno noticias", limit=3)
    
    print(f"\n📊 Resultados para: {resultados['query']}")
    for plataforma, posts in resultados["results"].items():
        print(f"\n{plataforma.upper()}: {len(posts)} resultados")
        for i, post in enumerate(posts, 1):
            print(f"  {i}. {post.get('author', 'N/A')}: {post.get('text', '')[:50]}...")
