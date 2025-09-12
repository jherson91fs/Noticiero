FUENTES = [
    {
    "url": "https://rpp.pe/peru/puno",
    "fuente": "RPP Noticias",
    "base": "https://rpp.pe",
    "container": "article.news",                     # bloque artículo
    "title_selector": "h2.news__title a",
    "img_selector": "figure.news__media img",
    "summary_selector": None,
    "author_selector": "span.news__author",
    "date_selector": None,
    "category_selector": "div.news__category a"      # categoría (Noticias, Deportes, Política...)
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
    "category_selector": "a.CardSection_section__category__q0s6z"  # categoría editorial
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
    "category_selector": "a.story-item__section"      # categoría (Política, Deportes, etc.)
    },
    {
    "url": "https://pachamamaradio.org",
    "fuente": "Pachamama Radio",
    "base": "https://pachamamaradio.org",
    "container": "div.td_module_flex",
    "title_selector": "h3.entry-title a",
    "img_selector": "span.entry-thumb",   # extrae data-img-url
    "summary_selector": "div.td-excerpt",
    "author_selector": None,
    "date_selector": None,
    "category_selector": "span.td-post-category a"   # categoría editorial
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
    "category_selector": "div.post-category a"        # categoría editorial
    },

    {
    "url": "https://diariosinfronteras.com.pe",
    "fuente": "Diario Sin Fronteras",
    "base": "https://diariosinfronteras.com.pe",
    "container": "div.post",   # cada bloque de noticia
    "title_selector": "h3.entry-title a",
    "img_selector": "div.ws-thumbnail img",
    "summary_selector": "div.post-excerpt",
    "author_selector": "div.post-author-bd a",
    "date_selector": "div.post-date-bd span",
    "category_selector": "div.post-category a",  # captura categoría editorial (Noticias, Deportes, etc.)
    },
]