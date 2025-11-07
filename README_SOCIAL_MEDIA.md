# 📱 Integración con Redes Sociales

## 🎯 Descripción

Se ha implementado una integración completa con redes sociales que permite:
- Buscar contenido relacionado en Twitter, Facebook e Instagram
- Compartir noticias en múltiples plataformas
- Visualizar posts de redes sociales relacionados con cada noticia

## ✅ Funcionalidades Implementadas

### 1. **Búsqueda en Redes Sociales**
- Búsqueda en Twitter/X por palabras clave
- Búsqueda en Facebook (requiere autenticación para resultados completos)
- Búsqueda en Instagram por hashtags
- Búsqueda automática relacionada con noticias específicas

### 2. **Compartir en Redes Sociales**
- Compartir en Twitter
- Compartir en Facebook
- Compartir en WhatsApp
- Compartir en Telegram

### 3. **Visualización de Contenido Social**
- Sección de redes sociales en página de detalles de noticia
- Posts relacionados organizados por plataforma
- Enlaces directos a posts originales

## 🚀 Uso del Sistema

### API Endpoints

#### Buscar en Redes Sociales
```bash
GET /api/social/buscar?q=busqueda&platforms=twitter,facebook,instagram&limit=10
```

#### Redes Sociales por Noticia
```bash
GET /api/social/noticia/{noticia_id}
```

#### Generar Links de Compartir
```bash
GET /api/social/compartir?texto=Título&url=https://ejemplo.com
```

### Interfaz de Usuario

1. **Botones de Compartir**: En cada noticia, hay botones para compartir en:
   - 🐦 Twitter
   - 📘 Facebook
   - 💬 WhatsApp
   - ✈️ Telegram

2. **Sección de Redes Sociales**: En la página de detalles de cada noticia, se muestra:
   - Posts relacionados de Twitter
   - Posts relacionados de Facebook
   - Posts relacionados de Instagram

## 📋 Plataformas Soportadas

### Twitter/X
- ✅ Búsqueda por palabras clave
- ✅ Compartir con texto y URL
- ✅ Visualización de tweets relacionados

### Facebook
- ⚠️ Búsqueda básica (requiere autenticación para resultados completos)
- ✅ Compartir con URL
- ✅ Visualización de posts relacionados

### Instagram
- ✅ Búsqueda por hashtags
- ✅ Visualización de posts con imágenes
- ⚠️ Requiere autenticación para algunas funcionalidades

### WhatsApp
- ✅ Compartir con texto y URL
- ✅ Enlace directo a WhatsApp Web/App

### Telegram
- ✅ Compartir con texto y URL
- ✅ Enlace directo a Telegram

## 🔧 Configuración

### Variables de Entorno

Puedes configurar las redes sociales en `social_media.py`:

```python
SOCIAL_MEDIA_CONFIG = {
    "twitter": {
        "enabled": True,
        # ... configuración
    },
    "facebook": {
        "enabled": True,
        # ... configuración
    },
    "instagram": {
        "enabled": True,
        # ... configuración
    }
}
```

### Notas Importantes

⚠️ **Limitaciones**:
- Twitter cambia frecuentemente su estructura HTML, el scraping puede requerir actualizaciones
- Facebook requiere autenticación para búsquedas completas
- Instagram tiene restricciones de rate limiting
- Algunas plataformas pueden bloquear scraping automático

✅ **Recomendaciones**:
- Para producción, considera usar APIs oficiales de las plataformas
- Implementa rate limiting para evitar bloqueos
- Usa autenticación OAuth para acceso completo

## 📝 Ejemplo de Uso

### En Python
```python
from social_media import buscar_redes_sociales, buscar_redes_sociales_por_noticia

# Buscar contenido relacionado
resultados = buscar_redes_sociales("Puno noticias", limit=5)

# Buscar por noticia
resultados = buscar_redes_sociales_por_noticia(
    "Título de noticia",
    departamento="puno",
    categoria="nacional"
)
```

### En JavaScript
```javascript
// Cargar contenido de redes sociales para una noticia
fetch(`/api/social/noticia/${noticiaId}`)
    .then(r => r.json())
    .then(data => {
        console.log(data.results);
    });
```

## 🎨 Estilos CSS

Los estilos para redes sociales están en `static/styles.css`:
- `.social-media-section`: Contenedor principal
- `.social-post`: Post individual
- `.share-buttons`: Botones de compartir
- `.btn-share-*`: Estilos específicos por plataforma

## 🔄 Mejoras Futuras

- [ ] Integración con APIs oficiales de redes sociales
- [ ] Autenticación OAuth para acceso completo
- [ ] Cache de resultados de búsqueda
- [ ] Rate limiting para evitar bloqueos
- [ ] Análisis de sentimientos en posts
- [ ] Estadísticas de engagement
- [ ] Notificaciones de nuevas menciones

## 📚 Referencias

- [Twitter API](https://developer.twitter.com/)
- [Facebook Graph API](https://developers.facebook.com/docs/graph-api)
- [Instagram Basic Display API](https://developers.facebook.com/docs/instagram-basic-display-api)

---

**¡La integración con redes sociales está lista para usar! 🎉**
