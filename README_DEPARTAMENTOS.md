# 🗺️ Sistema de Categorías y Departamentos - Noticiero

## 📋 Resumen de Cambios

Se ha implementado exitosamente el sistema de 3 categorías principales con los 24 departamentos del Perú y clasificación automática de noticias.

### ✅ Funcionalidades Implementadas

1. **Sistema de 3 Categorías Principales**:
   - **Nacional**: Noticias que afectan a los 24 departamentos del Perú
   - **Internacional**: Noticias de otros países o eventos globales
   - **Regional**: Noticias específicas del departamento de Puno

2. **24 Departamentos del Perú**: Lista completa de todos los departamentos
3. **Clasificación Automática**: Sistema inteligente que detecta departamentos en el texto
4. **Base de Datos Actualizada**: Campos `categoria` y `departamento` optimizados
5. **API Mejorada**: Nuevas rutas para filtrar por categorías y departamentos
6. **Interfaz de Usuario**: Filtros de categorías principales y departamentos
7. **Ordenamiento Optimizado**: Noticias más recientes aparecen primero (ordenado por `fecha_scraping`)

## 🚀 Uso del Sistema

### Scraping por Categoría

```bash
# Scrapear todas las fuentes (todas las categorías)
python scraper.py

# Scrapear por categoría específica
python scraper.py nacional      # Noticias nacionales
python scraper.py internacional # Noticias internacionales
python scraper.py regional      # Noticias regionales (Puno)
```

### API Endpoints

#### Nuevos Endpoints

```bash
# Obtener lista de categorías con conteo
GET /api/categorias

# Obtener lista de departamentos con conteo
GET /api/departamentos

# Obtener noticias de una categoría específica
GET /api/noticias/categoria/{categoria}?page=1&limit=10

# Obtener noticias de un departamento específico
GET /api/noticias/departamento/{departamento}?page=1&limit=10

# Filtrar noticias por categoría y departamento
GET /api/noticias?categoria=nacional&departamento=lima

# Ejecutar scraping por categoría
POST /api/scraping/categoria/{categoria}

# Ejecutar scraping para todos
POST /api/scraping/todos
```

#### Endpoints Actualizados

```bash
# Meta información ahora incluye categorías y departamentos
GET /api/meta

# Filtros actualizados con categoría y departamento
GET /api/noticias/filtrar?categoria=nacional&departamento=puno&fuente=RPP Noticias
```

### Interfaz Web

1. **Filtro de Categorías Principales**: Selector con las 3 categorías (Nacional, Internacional, Regional)
2. **Filtro de Departamentos**: Selector con los 24 departamentos del Perú
3. **Etiquetas Visuales**: 
   - Categorías con colores distintivos (azul=nacional, naranja=internacional, púrpura=regional)
   - Departamentos con etiquetas púrpuras
4. **Filtros Combinados**: Puedes combinar categoría, departamento y otros filtros

## ⏰ Ordenamiento de Noticias

### Prioridad de Ordenamiento
1. **Fecha de Scraping** (más reciente primero) - `fecha_scraping DESC`
2. **Fecha de Noticia** (más reciente primero) - `fecha DESC`

### Comportamiento
- Las noticias recién scrapeadas aparecen **siempre primero**
- Dentro del mismo momento de scraping, se ordenan por fecha de noticia
- Esto garantiza que las noticias más actuales sean visibles inmediatamente

### Opciones de Ordenamiento
- **Por defecto**: Noticias más recientes primero
- **Por título A-Z**: Orden alfabético + fecha de scraping
- **Por título Z-A**: Orden alfabético inverso + fecha de scraping
- **Por fecha ascendente**: Fecha antigua + fecha de scraping

## 📊 Sistema de Categorías

### Categoría Nacional
- **Fuentes**: RPP, La República, Diario Correo, El Comercio, Perú21
- **Departamentos**: Todos los 24 departamentos del Perú
- **Clasificación**: Automática basada en detección de departamentos en el texto

### Categoría Internacional
- **Clasificación**: Noticias que no mencionan departamentos del Perú
- **Ejemplos**: Crisis en Estados Unidos, guerra en Ucrania, etc.

### Categoría Regional (Puno)
- **Fuentes Específicas**: Pachamama Radio, Diario Sin Fronteras
- **Departamento**: Puno
- **Clasificación**: Fuentes específicas de Puno + detección automática

## 🛠️ Estructura de Base de Datos

### Tabla `noticias` Actualizada

```sql
CREATE TABLE noticias (
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
    departamento VARCHAR(50),  -- NUEVO CAMPO
    fecha_scraping DATETIME,
    UNIQUE KEY unique_link (link)
);
```

### Índices Agregados

```sql
CREATE INDEX idx_departamento ON noticias (departamento);
```

## 🎨 Interfaz de Usuario

### Nuevos Elementos Visuales

1. **Selector de Departamento**: Dropdown con todos los departamentos disponibles
2. **Etiqueta de Departamento**: Badge púrpura que muestra el departamento de cada noticia
3. **Filtros Combinados**: Los filtros funcionan en conjunto (departamento + fuente + categoría, etc.)

### Estilos CSS

```css
.departamento-tag {
    background: rgba(168, 85, 247, 0.2);
    color: #a855f7;
    border: 1px solid rgba(168, 85, 247, 0.3);
}
```

## 🧪 Pruebas

Ejecuta el script de prueba para verificar la funcionalidad:

```bash
python test_departamentos.py
```

## 📝 Archivos Modificados

### Backend
- `sources.py`: Agregadas fuentes nacionales y por departamento
- `scraper.py`: Implementado scraping por departamento
- `db.py`: Funciones para manejar departamentos
- `app.py`: Nuevas rutas API y filtros

### Frontend
- `templates/index.html`: Selector de departamentos
- `static/script.js`: Lógica de filtros actualizada
- `static/styles.css`: Estilos para etiquetas de departamento

### Nuevos Archivos
- `test_departamentos.py`: Script de pruebas
- `README_DEPARTAMENTOS.md`: Esta documentación

## 🔧 Configuración

### Variables de Entorno

Asegúrate de tener configurado tu archivo `.env`:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=noticiero_db
```

### Instalación de Dependencias

```bash
pip install -r requirements.txt
```

## 🚀 Inicio Rápido

1. **Configurar base de datos**:
   ```bash
   python -c "from db import crear_tabla_si_no_existe; crear_tabla_si_no_existe()"
   ```

2. **Ejecutar scraping inicial**:
   ```bash
   python scraper.py
   ```

3. **Iniciar aplicación web**:
   ```bash
   python app.py
   ```

4. **Abrir navegador**: `http://localhost:5000`

## 📈 Próximas Mejoras

- [ ] Agregar más departamentos del Perú
- [ ] Implementar scraping por regiones
- [ ] Agregar estadísticas por departamento
- [ ] Notificaciones por departamento favorito
- [ ] Mapa interactivo de noticias por región

## 🤝 Contribución

Para agregar nuevos departamentos:

1. Edita `sources.py` y agrega las fuentes del departamento
2. Actualiza `DEPARTAMENTOS` si es necesario
3. Ejecuta pruebas con `python test_departamentos.py`
4. Actualiza esta documentación

---

**¡La funcionalidad de departamentos está lista para usar! 🎉**
