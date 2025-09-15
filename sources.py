# ----------------- LISTA DE FUENTES -----------------
# Atributos:
#   - url: página principal
#   - fuente: nombre del medio
#   - base: dominio (para links relativos)
#   - selector: selector CSS para noticias
#   - selector_img: selector CSS para imágenes (opcional)
#   - categoria: categoría general
#   - departamento: departamento específico (opcional)

# ----------------- DEPARTAMENTOS DEL PERÚ (24 DEPARTAMENTOS) -----------------
DEPARTAMENTOS = [
    "amazonas", "ancash", "apurimac", "arequipa", "ayacucho", "cajamarca", 
    "callao", "cusco", "huancavelica", "huanuco", "ica", "junin", 
    "la-libertad", "lambayeque", "lima", "loreto", "madre-de-dios", 
    "moquegua", "pasco", "piura", "puno", "san-martin", "tacna", 
    "tumbes", "ucayali"
]

# Mapeo de nombres de departamentos para búsqueda
DEPARTAMENTOS_MAP = {
    "amazonas": ["amazonas", "amazonas"],
    "ancash": ["ancash", "ancash"],
    "apurimac": ["apurimac", "apurimac"],
    "arequipa": ["arequipa", "arequipa"],
    "ayacucho": ["ayacucho", "ayacucho"],
    "cajamarca": ["cajamarca", "cajamarca"],
    "callao": ["callao", "callao"],
    "cusco": ["cusco", "cusco", "cuzco"],
    "huancavelica": ["huancavelica", "huancavelica"],
    "huanuco": ["huanuco", "huanuco", "huánuco"],
    "ica": ["ica", "ica"],
    "junin": ["junin", "junin", "junjín"],
    "la-libertad": ["la-libertad", "la libertad", "libertad"],
    "lambayeque": ["lambayeque", "lambayeque"],
    "lima": ["lima", "lima"],
    "loreto": ["loreto", "loreto"],
    "madre-de-dios": ["madre-de-dios", "madre de dios"],
    "moquegua": ["moquegua", "moquegua"],
    "pasco": ["pasco", "pasco"],
    "piura": ["piura", "piura"],
    "puno": ["puno", "puno"],
    "san-martin": ["san-martin", "san martín", "san martin"],
    "tacna": ["tacna", "tacna"],
    "tumbes": ["tumbes", "tumbes"],
    "ucayali": ["ucayali", "ucayali", "ucayali"]
}

# ----------------- CATEGORÍAS PRINCIPALES -----------------
CATEGORIAS = {
    "nacional": "Noticias que afectan a los 24 departamentos del Perú",
    "internacional": "Noticias de otros países o eventos globales",
    "regional": "Noticias específicas del departamento de Puno"
}

FUENTES = [
    # ----------------- FUENTES NACIONALES -----------------
    {
        "url": "https://rpp.pe/peru",
        "fuente": "RPP Noticias",
        "base": "https://rpp.pe",
        "container": "article.news",
        "title_selector": "h2.news__title a",
        "img_selector": "figure.news__media img",
        "summary_selector": None,
        "author_selector": "span.news__author",
        "date_selector": None,
        "category_selector": "div.news__category a",
        "categoria": "nacional"
    },
    {
        "url": "https://larepublica.pe",
        "fuente": "La República",
        "base": "https://larepublica.pe",
        "container": "div.ListSection_list__section--item__zeP_z",
        "title_selector": "h2.ListSection_list__section--title__hwhjX a",
        "img_selector": "figure img",
        "summary_selector": None,
        "author_selector": "span.AuthorSign_authorSign__name__FXLMu",
        "date_selector": "time.ListSection_list__section--time__2cnSA",
        "category_selector": "a.CardSection_section__category__q0s6z",
        "categoria": "nacional"
    },
    {
        "url": "https://diariocorreo.pe",
        "fuente": "Diario Correo",
        "base": "https://diariocorreo.pe",
        "container": "div.story-item",
        "title_selector": "h2.story-item__content-title a",
        "img_selector": "img.story-item__img",
        "summary_selector": "p.story-item__subtitle",
        "author_selector": "div.story-item__author-wrapper a",
        "date_selector": "p.story-item__date",
        "category_selector": "a.story-item__section",
        "categoria": "nacional"
    },
    {
        "url": "https://elcomercio.pe",
        "fuente": "El Comercio",
        "base": "https://elcomercio.pe",
        "container": "div.story-item",
        "title_selector": "h2.story-item__content-title a",
        "img_selector": "img.story-item__img",
        "summary_selector": "p.story-item__subtitle",
        "author_selector": "div.story-item__author-wrapper a",
        "date_selector": "p.story-item__date",
        "category_selector": "a.story-item__section",
        "categoria": "nacional"
    },
    {
        "url": "https://peru21.pe",
        "fuente": "Perú21",
        "base": "https://peru21.pe",
        "container": "article.news",
        "title_selector": "h2.news__title a",
        "img_selector": "figure.news__media img",
        "summary_selector": None,
        "author_selector": "span.news__author",
        "date_selector": None,
        "category_selector": "div.news__category a",
        "categoria": "nacional"
    },
    
    # ----------------- FUENTES POR DEPARTAMENTO - PUNO -----------------
    {
        "url": "https://rpp.pe/peru/puno",
        "fuente": "RPP Noticias",
        "base": "https://rpp.pe",
        "container": "article.news",
        "title_selector": "h2.news__title a",
        "img_selector": "figure.news__media img",
        "summary_selector": None,
        "author_selector": "span.news__author",
        "date_selector": None,
        "category_selector": "div.news__category a",
        "categoria": "regional"
    },
    {
        "url": "https://larepublica.pe/tag/puno",
        "fuente": "La República",
        "base": "https://larepublica.pe",
        "container": "div.ListSection_list__section--item__zeP_z",
        "title_selector": "h2.ListSection_list__section--title__hwhjX a",
        "img_selector": "figure img",
        "summary_selector": None,
        "author_selector": "span.AuthorSign_authorSign__name__FXLMu",
        "date_selector": "time.ListSection_list__section--time__2cnSA",
        "category_selector": "a.CardSection_section__category__q0s6z",
        "categoria": "regional"
    },
    {
        "url": "https://diariocorreo.pe/edicion/puno",
        "fuente": "Diario Correo",
        "base": "https://diariocorreo.pe",
        "container": "div.story-item",
        "title_selector": "h2.story-item__content-title a",
        "img_selector": "img.story-item__img",
        "summary_selector": "p.story-item__subtitle",
        "author_selector": "div.story-item__author-wrapper a",
        "date_selector": "p.story-item__date",
        "category_selector": "a.story-item__section",
        "categoria": "regional"
    },
    {
        "url": "https://pachamamaradio.org",
        "fuente": "Pachamama Radio",
        "base": "https://pachamamaradio.org",
        "container": "div.td_module_flex",
        "title_selector": "h3.entry-title a",
        "img_selector": "span.entry-thumb",
        "summary_selector": "div.td-excerpt",
        "author_selector": None,
        "date_selector": None,
        "category_selector": "span.td-post-category a",
        "categoria": "regional"
    },
    {
        "url": "https://diariosinfronteras.com.pe",
        "fuente": "Diario Sin Fronteras",
        "base": "https://diariosinfronteras.com.pe",
        "container": "div.post",
        "title_selector": "h3.entry-title a",
        "img_selector": "div.ws-thumbnail img",
        "summary_selector": "div.post-excerpt",
        "author_selector": "div.post-author-bd a",
        "date_selector": "div.post-date-bd span",
        "category_selector": "div.post-category a",
        "categoria": "regional"
    },

    # ----------------- FUENTES POR DEPARTAMENTO - LIMA -----------------
    {
        "url": "https://rpp.pe/peru/lima",
        "fuente": "RPP Noticias",
        "base": "https://rpp.pe",
        "container": "article.news",
        "title_selector": "h2.news__title a",
        "img_selector": "figure.news__media img",
        "summary_selector": None,
        "author_selector": "span.news__author",
        "date_selector": None,
        "category_selector": "div.news__category a",
        "categoria": "nacional"
    },
    {
        "url": "https://larepublica.pe/tag/lima",
        "fuente": "La República",
        "base": "https://larepublica.pe",
        "container": "div.ListSection_list__section--item__zeP_z",
        "title_selector": "h2.ListSection_list__section--title__hwhjX a",
        "img_selector": "figure img",
        "summary_selector": None,
        "author_selector": "span.AuthorSign_authorSign__name__FXLMu",
        "date_selector": "time.ListSection_list__section--time__2cnSA",
        "category_selector": "a.CardSection_section__category__q0s6z",
        "categoria": "nacional"
    },

    # ----------------- FUENTES POR DEPARTAMENTO - AREQUIPA -----------------
    {
        "url": "https://rpp.pe/peru/arequipa",
        "fuente": "RPP Noticias",
        "base": "https://rpp.pe",
        "container": "article.news",
        "title_selector": "h2.news__title a",
        "img_selector": "figure.news__media img",
        "summary_selector": None,
        "author_selector": "span.news__author",
        "date_selector": None,
        "category_selector": "div.news__category a",
        "categoria": "nacional"
    },
    {
        "url": "https://larepublica.pe/tag/arequipa",
        "fuente": "La República",
        "base": "https://larepublica.pe",
        "container": "div.ListSection_list__section--item__zeP_z",
        "title_selector": "h2.ListSection_list__section--title__hwhjX a",
        "img_selector": "figure img",
        "summary_selector": None,
        "author_selector": "span.AuthorSign_authorSign__name__FXLMu",
        "date_selector": "time.ListSection_list__section--time__2cnSA",
        "category_selector": "a.CardSection_section__category__q0s6z",
        "categoria": "nacional"
    },

    # ----------------- FUENTES POR DEPARTAMENTO - CUSCO -----------------
    {
        "url": "https://rpp.pe/peru/cusco",
        "fuente": "RPP Noticias",
        "base": "https://rpp.pe",
        "container": "article.news",
        "title_selector": "h2.news__title a",
        "img_selector": "figure.news__media img",
        "summary_selector": None,
        "author_selector": "span.news__author",
        "date_selector": None,
        "category_selector": "div.news__category a",
        "categoria": "nacional"
    },
    {
        "url": "https://larepublica.pe/tag/cusco",
        "fuente": "La República",
        "base": "https://larepublica.pe",
        "container": "div.ListSection_list__section--item__zeP_z",
        "title_selector": "h2.ListSection_list__section--title__hwhjX a",
        "img_selector": "figure img",
        "summary_selector": None,
        "author_selector": "span.AuthorSign_authorSign__name__FXLMu",
        "date_selector": "time.ListSection_list__section--time__2cnSA",
        "category_selector": "a.CardSection_section__category__q0s6z",
        "categoria": "nacional"
    },

    # ----------------- FUENTES POR DEPARTAMENTO - LA LIBERTAD -----------------
    {
        "url": "https://rpp.pe/peru/la-libertad",
        "fuente": "RPP Noticias",
        "base": "https://rpp.pe",
        "container": "article.news",
        "title_selector": "h2.news__title a",
        "img_selector": "figure.news__media img",
        "summary_selector": None,
        "author_selector": "span.news__author",
        "date_selector": None,
        "category_selector": "div.news__category a",
        "categoria": "nacional"
    },
    {
        "url": "https://larepublica.pe/tag/la-libertad",
        "fuente": "La República",
        "base": "https://larepublica.pe",
        "container": "div.ListSection_list__section--item__zeP_z",
        "title_selector": "h2.ListSection_list__section--title__hwhjX a",
        "img_selector": "figure img",
        "summary_selector": None,
        "author_selector": "span.AuthorSign_authorSign__name__FXLMu",
        "date_selector": "time.ListSection_list__section--time__2cnSA",
        "category_selector": "a.CardSection_section__category__q0s6z",
        "categoria": "nacional"
    },

    # ----------------- FUENTES POR DEPARTAMENTO - PIURA -----------------
    {
        "url": "https://rpp.pe/peru/piura",
        "fuente": "RPP Noticias",
        "base": "https://rpp.pe",
        "container": "article.news",
        "title_selector": "h2.news__title a",
        "img_selector": "figure.news__media img",
        "summary_selector": None,
        "author_selector": "span.news__author",
        "date_selector": None,
        "category_selector": "div.news__category a",
        "categoria": "nacional"
    },
    {
        "url": "https://larepublica.pe/tag/piura",
        "fuente": "La República",
        "base": "https://larepublica.pe",
        "container": "div.ListSection_list__section--item__zeP_z",
        "title_selector": "h2.ListSection_list__section--title__hwhjX a",
        "img_selector": "figure img",
        "summary_selector": None,
        "author_selector": "span.AuthorSign_authorSign__name__FXLMu",
        "date_selector": "time.ListSection_list__section--time__2cnSA",
        "category_selector": "a.CardSection_section__category__q0s6z",
        "categoria": "nacional"
    }
]

# ----------------- FUNCIÓN PARA OBTENER FUENTES POR DEPARTAMENTO -----------------
def obtener_fuentes_por_departamento(departamento=None):
    """
    Obtiene fuentes filtradas por departamento.
    Si no se especifica departamento, retorna todas las fuentes.
    """
    if not departamento:
        return FUENTES
    
    return [fuente for fuente in FUENTES if fuente.get('departamento') == departamento]

def obtener_departamentos_disponibles():
    """
    Obtiene lista de departamentos disponibles en las fuentes.
    """
    return DEPARTAMENTOS

def obtener_categorias_disponibles():
    """
    Obtiene lista de categorías disponibles.
    """
    return list(CATEGORIAS.keys())

def detectar_departamento_en_texto(texto):
    """
    Detecta si el texto menciona algún departamento del Perú.
    Retorna el departamento encontrado o None.
    """
    if not texto:
        return None
    
    texto_lower = texto.lower()
    
    for dept, variantes in DEPARTAMENTOS_MAP.items():
        for variante in variantes:
            if variante in texto_lower:
                return dept
    
    return None

def clasificar_noticia(titulo, resumen, categoria_fuente):
    """
    Clasifica una noticia en una de las 3 categorías principales.
    
    Args:
        titulo: Título de la noticia
        resumen: Resumen de la noticia
        categoria_fuente: Categoría asignada por la fuente
    
    Returns:
        dict: {
            'categoria': 'nacional'|'internacional'|'regional',
            'departamento': nombre_departamento|None
        }
    """
    texto_completo = f"{titulo or ''} {resumen or ''}".lower()
    
    # Detectar departamento en el texto
    departamento = detectar_departamento_en_texto(texto_completo)
    
    # Si la fuente ya está clasificada como regional (Puno), mantenerlo
    if categoria_fuente == "regional":
        return {
            'categoria': 'regional',
            'departamento': 'puno'
        }
    
    # Si se detecta un departamento específico, clasificar como nacional
    if departamento:
        return {
            'categoria': 'nacional',
            'departamento': departamento
        }
    
    # Si la fuente está clasificada como nacional, mantenerlo
    if categoria_fuente == "nacional":
        return {
            'categoria': 'nacional',
            'departamento': None
        }
    
    # Por defecto, clasificar como internacional
    return {
        'categoria': 'internacional',
        'departamento': None
    }

def obtener_fuentes_por_categoria(categoria=None):
    """
    Obtiene fuentes filtradas por categoría.
    Si no se especifica categoría, retorna todas las fuentes.
    """
    if not categoria:
        return FUENTES
    
    return [fuente for fuente in FUENTES if fuente.get('categoria') == categoria]