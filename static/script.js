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
        <div class="actions">
            <button class="btn-fav-card" data-id="${n.id}">⭐</button>
        </div>
    `;
    return div;
}

function cargarNoticias(filtros = {}, append = true) {
    const contenedor = document.getElementById('noticias');
    if (!append) contenedor.innerHTML = '';

    // Preferir endpoint de filtro cuando existan filtros o búsqueda
    const tieneFiltros = filtros.fuente || filtros.categoria || filtros.fecha || filtros.tipo || filtros.q;
    let url = tieneFiltros
        ? `/api/noticias/filtrar?`
        : `/api/noticias?`;

    const params = new URLSearchParams();
    params.set('page', page);
    params.set('limit', limit);
    if (filtros.fuente) params.set('fuente', filtros.fuente);
    if (filtros.categoria) params.set('categoria', filtros.categoria);
    if (filtros.fecha) params.set('fecha', filtros.fecha);
    if (filtros.tipo) params.set('tipo', filtros.tipo);
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
            bindFavButtons();
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
            tipo: document.getElementById('filtro-tipo')?.value,
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
            tipo: document.getElementById('filtro-tipo')?.value,
            q: document.getElementById('busqueda')?.value
        }, false);
    });
}

// Poblar selects de filtros desde la API meta
function poblarFiltros() {
    const selFuente = document.getElementById('filtro-fuente');
    const selCategoria = document.getElementById('filtro-categoria');
    const selTipo = document.getElementById('filtro-tipo');
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
            if (selTipo && meta.tipos) {
                selTipo.length = 1;
                meta.tipos.forEach(t => {
                    const opt = document.createElement('option');
                    opt.value = t;
                    opt.textContent = t;
                    selTipo.appendChild(opt);
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
                    <div class="actions">
                        <button id="btn-fav" data-id="${n.id}">⭐ Guardar</button>
                        <button id="btn-share" data-id="${n.id}">Compartir</button>
                        <a href="${n.link}" target="_blank" rel="noopener">Ver fuente original ↗</a>
                    </div>
                </article>
            `;
            setupBookmarking(n);
            cargarRelacionadas(n.id);
        });
}

// Bookmarks y compartir
function setupBookmarking(n) {
    const key = 'favoritos';
    const getFavs = () => JSON.parse(localStorage.getItem(key) || '[]');
    const setFavs = (arr) => localStorage.setItem(key, JSON.stringify(arr));
    const btn = document.getElementById('btn-fav');
    const btnShare = document.getElementById('btn-share');
    if (btn) {
        const favs = getFavs();
        const isFav = favs.includes(n.id);
        btn.textContent = isFav ? '★ Guardado' : '⭐ Guardar';
        btn.addEventListener('click', () => {
            const f = getFavs();
            const idx = f.indexOf(n.id);
            if (idx >= 0) f.splice(idx, 1); else f.push(n.id);
            setFavs(f);
            btn.textContent = f.includes(n.id) ? '★ Guardado' : '⭐ Guardar';
        });
    }
    if (btnShare) {
        btnShare.addEventListener('click', async () => {
            const shareData = { title: n.titulo, text: n.resumen || n.titulo, url: window.location.href };
            if (navigator.share) {
                try { await navigator.share(shareData); } catch {}
            } else {
                navigator.clipboard?.writeText(shareData.url);
                alert('Link copiado');
            }
        });
    }
}

function cargarRelacionadas(id) {
    fetch(`/api/noticias/relacionadas?id=${id}&limit=6`)
        .then(r => r.json())
        .then(list => {
            const box = document.getElementById('relacionadas-list');
            if (!box) return;
            box.innerHTML = '';
            (list || []).forEach(n => {
                const d = document.createElement('div');
                d.className = 'noticia';
                d.innerHTML = `<h4><a href="/noticia?id=${n.id}">${n.titulo}</a></h4>`;
                box.appendChild(d);
            });
        });
}

// ----- Favoritos: lista dedicada -----
function getFavs() { return JSON.parse(localStorage.getItem('favoritos') || '[]'); }
function setFavs(arr) { localStorage.setItem('favoritos', JSON.stringify(arr)); }

function bindFavButtons() {
    document.querySelectorAll('.btn-fav-card').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = Number(btn.getAttribute('data-id'));
            const favs = getFavs();
            const idx = favs.indexOf(id);
            if (idx >= 0) favs.splice(idx, 1); else favs.push(id);
            setFavs(favs);
            btn.textContent = favs.includes(id) ? '★' : '⭐';
        });
        const id = Number(btn.getAttribute('data-id'));
        btn.textContent = getFavs().includes(id) ? '★' : '⭐';
    });
}

function renderFavoritos() {
    const list = document.getElementById('lista-favoritos');
    if (!list) return;
    const ids = getFavs();
    if (!ids.length) { list.innerHTML = '<p class="meta">No tienes favoritos aún.</p>'; return; }
    list.innerHTML = '';
    const q = document.getElementById('fav-busqueda')?.value?.toLowerCase() || '';
    Promise.all(ids.map(id => fetch(`/api/noticias/${id}`).then(r => r.json()).catch(() => null)))
        .then(items => {
            items.filter(Boolean).forEach(n => {
                if (q && !(n.titulo?.toLowerCase().includes(q) || n.resumen?.toLowerCase().includes(q))) return;
                list.appendChild(crearNodoNoticia(n));
            });
            bindFavButtons();
        });
    const btnExport = document.getElementById('btn-exportar');
    const btnClear = document.getElementById('btn-limpiar');
    if (btnExport) btnExport.onclick = () => {
        const blob = new Blob([JSON.stringify(ids)], { type: 'application/json' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'favoritos.json';
        a.click();
    };
    if (btnClear) btnClear.onclick = () => {
        if (confirm('¿Limpiar todos los favoritos?')) { localStorage.removeItem('favoritos'); renderFavoritos(); }
    };
    const input = document.getElementById('fav-busqueda');
    if (input) input.oninput = () => renderFavoritos();
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
