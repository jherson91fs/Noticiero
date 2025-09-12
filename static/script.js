let page = 1;
const limit = 6;

function crearNodoNoticia(n) {
    const div = document.createElement('div');
    div.className = "noticia";
    const meta = `<div class="meta"><strong>Fuente:</strong> ${n.fuente || ''} · <strong>Fecha:</strong> ${n.fecha || ''}</div>`;
    const img = n.imagen ? `<img src="${n.imagen}" alt="Imagen de noticia">` : '';
    div.innerHTML = `
        <h2><a href="/noticia?id=${n.id}">${n.titulo}</a></h2>
        ${meta}
        ${img}
        <p>${n.resumen || ''}</p>
    `;
    return div;
}

function cargarNoticias(filtros = {}, append = true) {
    const contenedor = document.getElementById('noticias');
    if (!append) contenedor.innerHTML = '';

    // Preferir endpoint de filtro cuando existan filtros o búsqueda
    const tieneFiltros = filtros.fuente || filtros.categoria || filtros.fecha || filtros.q;
    let url = tieneFiltros
        ? `/api/noticias/filtrar?`
        : `/api/noticias?`;

    const params = new URLSearchParams();
    params.set('page', page);
    params.set('limit', limit);
    if (filtros.fuente) params.set('fuente', filtros.fuente);
    if (filtros.categoria) params.set('categoria', filtros.categoria);
    if (filtros.fecha) params.set('fecha', filtros.fecha);
    if (filtros.q) {
        url = `/api/noticias/buscar?`;
        params.delete('fuente');
        params.delete('categoria');
        params.delete('fecha');
        params.delete('page');
        params.delete('limit');
        params.set('q', filtros.q);
    }

    fetch(url + params.toString())
        .then(res => res.json())
        .then(data => {
            if (data.mensaje) {
                if (!append) contenedor.innerHTML = '';
                const vacio = document.createElement('p');
                vacio.className = 'meta';
                vacio.textContent = data.mensaje;
                contenedor.appendChild(vacio);
                return;
            }
            data.forEach(noticia => contenedor.appendChild(crearNodoNoticia(noticia)));
        })
        .catch(() => {
            const err = document.createElement('p');
            err.className = 'meta';
            err.textContent = 'No se pudieron cargar noticias.';
            contenedor.appendChild(err);
        });
}

// Botón cargar más
const btnMas = document.getElementById('btn-cargar-mas');
if (btnMas) {
    btnMas.addEventListener('click', () => {
        page++;
        cargarNoticias({
            fuente: document.getElementById('filtro-fuente')?.value,
            categoria: document.getElementById('filtro-categoria')?.value,
            q: document.getElementById('busqueda')?.value
        }, true);
    });
}

// Botón filtrar/buscar
const btnFiltrar = document.getElementById('btn-filtrar');
if (btnFiltrar) {
    btnFiltrar.addEventListener('click', () => {
        page = 1;
        cargarNoticias({
            fuente: document.getElementById('filtro-fuente')?.value,
            categoria: document.getElementById('filtro-categoria')?.value,
            q: document.getElementById('busqueda')?.value
        }, false);
    });
}

// Poblar selects de filtros desde la API meta
function poblarFiltros() {
    const selFuente = document.getElementById('filtro-fuente');
    const selCategoria = document.getElementById('filtro-categoria');
    if (!selFuente || !selCategoria) return;
    fetch('/api/meta')
        .then(r => r.json())
        .then(meta => {
            if (meta.fuentes) {
                // limpiar dejando la primera opción
                selFuente.length = 1;
                meta.fuentes.forEach(f => {
                    const opt = document.createElement('option');
                    opt.value = f;
                    opt.textContent = f;
                    selFuente.appendChild(opt);
                });
            }
            if (meta.categorias) {
                selCategoria.length = 1;
                meta.categorias.forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = c;
                    opt.textContent = c;
                    selCategoria.appendChild(opt);
                });
            }
        })
        .catch(() => {});
}

// Página de detalle
function cargarDetalle() {
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');
    if (!id) return;
    fetch(`/api/noticias/${id}`)
        .then(res => res.json())
        .then(n => {
            const cont = document.getElementById('detalle-noticia');
            if (!n || n.mensaje) {
                cont.innerHTML = '<p class="meta">No se encontró la noticia.</p>';
                return;
            }
            const meta = `<div class="meta"><strong>Fuente:</strong> ${n.fuente || ''} · <strong>Fecha:</strong> ${n.fecha || ''}</div>`;
            const img = n.imagen ? `<img src="${n.imagen}" alt="Imagen de noticia">` : '';
            cont.innerHTML = `
                <article class="noticia">
                    <h2>${n.titulo}</h2>
                    ${meta}
                    ${img}
                    <p>${n.resumen || ''}</p>
                    <p><a href="${n.link}" target="_blank" rel="noopener">Ver fuente original ↗</a></p>
                </article>
            `;
        });
}

// Carga inicial según página
if (document.getElementById('noticias')) {
    cargarNoticias({}, true);
}
if (document.getElementById('detalle-noticia')) {
    cargarDetalle();
}

// Theme toggle with persistence
function applyTheme(theme) {
    document.documentElement.classList.remove('theme-light', 'theme-dark');
    if (theme === 'light') {
        document.documentElement.classList.add('theme-light');
    } else if (theme === 'dark') {
        document.documentElement.classList.add('theme-dark');
    }
}

function initTheme() {
    const saved = localStorage.getItem('theme');
    if (saved) applyTheme(saved);
}

function setupThemeToggle() {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;
    initTheme();
    btn.addEventListener('click', () => {
        const current = document.documentElement.classList.contains('theme-dark') ? 'dark'
                        : document.documentElement.classList.contains('theme-light') ? 'light'
                        : null;
        const next = current === 'dark' ? 'light' : 'dark';
        localStorage.setItem('theme', next);
        applyTheme(next);
    });
}

setupThemeToggle();
