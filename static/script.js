// ========== CONFIGURACIÓN GLOBAL ==========
let page = 1;
const limit = 15; // Máximo 15 noticias para infinite scroll
let currentView = 'grid'; // 'grid' o 'list'
let currentFilters = {};
let paginationData = {};
let isInfiniteScroll = true;
let isLoading = false;

// ========== UTILIDADES ==========
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// ========== CREAR NODO DE NOTICIA ==========
function crearNodoNoticia(n, viewType = currentView) {
    const div = document.createElement('div');
    div.className = `noticia ${viewType === 'list' ? 'list-view' : 'grid-view'}`;
    
    const meta = `<div class="meta"><strong>Fuente:</strong> ${n.fuente || ''} · <strong>Fecha:</strong> ${formatDate(n.fecha)}</div>`;
    const img = n.imagen ? `<img src="${n.imagen}" alt="Imagen de noticia" class="news-image" data-src="${n.imagen}">` : '';
    const tipoTag = n.tipo ? `<span class="tag tipo-tag">${n.tipo}</span>` : '';
    const categoriaTag = n.categoria ? `<span class="tag categoria-tag ${n.categoria}">${n.categoria.charAt(0).toUpperCase() + n.categoria.slice(1)}</span>` : '';
    const departamentoTag = n.departamento ? `<span class="tag departamento-tag">${n.departamento.charAt(0).toUpperCase() + n.departamento.slice(1).replace('-', ' ')}</span>` : '';
    const isFav = isFavorito(n.id) ? 'active' : '';
    
    if (viewType === 'list') {
        div.innerHTML = `
            <div class="noticia-content">
                <div class="noticia-image">
                    ${img}
                </div>
                <div class="noticia-text">
                    <div class="noticia-header">
                        <h2><a href="/noticia?id=${n.id}">${n.titulo}</a></h2>
                        <button class="bookmark-btn ${isFav}" data-id="${n.id}" aria-label="Guardar noticia">⭐</button>
                    </div>
                    ${meta}
                    <div class="tags">
                        ${tipoTag}
                        ${categoriaTag}
                        ${departamentoTag}
                    </div>
                    <p>${n.resumen || ''}</p>
                    <div class="actions">
                        <button class="preview-btn" data-id="${n.id}">👁 Vista Previa</button>
                        <button class="share-btn" data-title="${n.titulo}" data-url="/noticia?id=${n.id}">Compartir</button>
                    </div>
                </div>
            </div>
        `;
    } else {
        div.innerHTML = `
            <div class="noticia-header">
                <h2><a href="/noticia?id=${n.id}">${n.titulo}</a></h2>
                <button class="bookmark-btn ${isFav}" data-id="${n.id}" aria-label="Guardar noticia">⭐</button>
            </div>
            ${meta}
            <div class="tags">
                ${tipoTag}
                ${categoriaTag}
            </div>
            ${img}
            <p>${n.resumen || ''}</p>
            <div class="actions">
                <button class="preview-btn" data-id="${n.id}">👁 Vista Previa</button>
                <button class="share-btn" data-title="${n.titulo}" data-url="/noticia?id=${n.id}">Compartir</button>
            </div>
        `;
    }
    
    // Event listeners
    const bookmarkBtn = div.querySelector('.bookmark-btn');
    const shareBtn = div.querySelector('.share-btn');
    const previewBtn = div.querySelector('.preview-btn');
    const image = div.querySelector('.news-image');
    
    if (bookmarkBtn) {
        bookmarkBtn.addEventListener('click', () => toggleFavorito(n.id, bookmarkBtn));
    }
    
    if (shareBtn) {
        shareBtn.addEventListener('click', () => shareNews(shareBtn.dataset.title, shareBtn.dataset.url));
    }
    
    if (previewBtn) {
        previewBtn.addEventListener('click', () => showPreview(n));
    }
    
    if (image) {
        image.addEventListener('click', () => showImageModal(image.src));
    }
    
    return div;
}

// ========== CARGAR NOTICIAS ==========
function cargarNoticias(filtros = {}, append = true, resetPage = false) {
    if (isLoading) return;
    
    if (resetPage) {
        page = 1;
    }
    
    const contenedor = document.getElementById('noticias');
    if (!contenedor) return;
    
    if (!append) contenedor.innerHTML = '';
    
    isLoading = true;
    currentFilters = { ...filtros };
    
    // Determinar endpoint
    const tieneFiltros = filtros.fuente || filtros.categoria || filtros.fecha || filtros.tipo || filtros.q || filtros.fecha_desde || filtros.fecha_hasta;
    let url = tieneFiltros ? `/api/noticias/filtrar?` : `/api/noticias?`;
    
    const params = new URLSearchParams();
    params.set('page', page);
    params.set('limit', limit);
    
    if (filtros.fuente) params.set('fuente', filtros.fuente);
    if (filtros.categoria) params.set('categoria', filtros.categoria);
    if (filtros.fecha) params.set('fecha', filtros.fecha);
    if (filtros.tipo) params.set('tipo', filtros.tipo);
    if (filtros.fecha_desde) params.set('fecha_desde', filtros.fecha_desde);
    if (filtros.fecha_hasta) params.set('fecha_hasta', filtros.fecha_hasta);
    if (filtros.ordenar) params.set('ordenar', filtros.ordenar);
    
    if (filtros.q) {
        url = `/api/noticias/buscar?`;
        params.delete('fuente');
        params.delete('categoria');
        params.delete('fecha');
        params.delete('fecha_desde');
        params.delete('fecha_hasta');
        params.set('q', filtros.q);
    }
    
    fetch(url + params.toString())
        .then(res => res.json())
        .then(data => {
            isLoading = false;
            
            if (data.mensaje) {
                if (!append) contenedor.innerHTML = '';
                const vacio = document.createElement('p');
                vacio.className = 'meta';
                vacio.textContent = data.mensaje;
                contenedor.appendChild(vacio);
                updatePaginationInfo({ total: 0, page: 1, total_pages: 0 });
                return;
            }
            
            const noticias = data.noticias || data;
            paginationData = data.pagination || {};
            
            noticias.forEach(noticia => {
                contenedor.appendChild(crearNodoNoticia(noticia));
            });
            
            updatePaginationInfo(paginationData);
            bindFavButtons();
        })
        .catch(() => {
            isLoading = false;
            const err = document.createElement('p');
            err.className = 'meta';
            err.textContent = 'No se pudieron cargar noticias.';
            contenedor.appendChild(err);
        });
}

// ========== PAGINACIÓN ==========
function updatePaginationInfo(pagination) {
    const paginationText = document.getElementById('pagination-text');
    const btnCargarMas = document.getElementById('btn-cargar-mas');
    const paginationControls = document.getElementById('pagination-controls');
    
    if (paginationText) {
        if (pagination.total > 0) {
            const start = ((pagination.page - 1) * pagination.limit) + 1;
            const end = Math.min(pagination.page * pagination.limit, pagination.total);
            paginationText.textContent = `Mostrando ${start}-${end} de ${pagination.total} noticias`;
        } else {
            paginationText.textContent = 'No hay noticias disponibles';
        }
    }
    
    // Mostrar/ocultar controles según el modo
    if (isInfiniteScroll && pagination.has_next) {
        if (btnCargarMas) btnCargarMas.style.display = 'block';
        if (paginationControls) paginationControls.style.display = 'none';
    } else if (!isInfiniteScroll) {
        if (btnCargarMas) btnCargarMas.style.display = 'none';
        if (paginationControls) {
            paginationControls.style.display = 'flex';
            updatePaginationControls(pagination);
        }
    } else {
        if (btnCargarMas) btnCargarMas.style.display = 'none';
        if (paginationControls) paginationControls.style.display = 'none';
    }
}

function updatePaginationControls(pagination) {
    const pageNumbers = document.getElementById('page-numbers');
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');
    
    if (!pageNumbers || !btnPrev || !btnNext) return;
    
    // Botones anterior/siguiente
    btnPrev.disabled = !pagination.has_prev;
    btnNext.disabled = !pagination.has_next;
    
    // Números de página
    pageNumbers.innerHTML = '';
    const currentPage = pagination.page;
    const totalPages = pagination.total_pages;
    
    // Mostrar máximo 5 páginas
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, currentPage + 2);
    
    if (endPage - startPage < 4) {
        if (startPage === 1) {
            endPage = Math.min(totalPages, startPage + 4);
        } else {
            startPage = Math.max(1, endPage - 4);
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.className = `page-btn ${i === currentPage ? 'active' : ''}`;
        pageBtn.textContent = i;
        pageBtn.addEventListener('click', () => goToPage(i));
        pageNumbers.appendChild(pageBtn);
    }
}

function goToPage(newPage) {
    page = newPage;
    cargarNoticias(currentFilters, false, false);
}

// ========== VISTA PREVIA ==========
function showPreview(noticia) {
    const modal = document.getElementById('preview-modal');
    const content = document.getElementById('preview-content');
    
    if (!modal || !content) return;
    
    content.innerHTML = `
        <h2>${noticia.titulo}</h2>
        <div class="meta">
            <strong>Fuente:</strong> ${noticia.fuente || ''} · 
            <strong>Fecha:</strong> ${formatDate(noticia.fecha)} · 
            <strong>Categoría:</strong> ${noticia.categoria || ''} · 
            <strong>Tipo:</strong> ${noticia.tipo || ''}
        </div>
        ${noticia.imagen ? `<img src="${noticia.imagen}" alt="Imagen de noticia" style="max-width: 100%; height: auto; margin: 10px 0;">` : ''}
        <p>${noticia.resumen || 'No hay resumen disponible.'}</p>
        <div class="actions">
            <a href="/noticia?id=${noticia.id}" class="btn-primary">Leer completo</a>
            <button class="btn-secondary" onclick="closeModal('preview-modal')">Cerrar</button>
        </div>
    `;
    
    modal.style.display = 'block';
}

// ========== MODALES ==========
function showImageModal(imageSrc) {
    const modal = document.getElementById('image-modal');
    const img = document.getElementById('modal-image');
    
    if (!modal || !img) return;
    
    img.src = imageSrc;
    modal.style.display = 'block';
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// ========== FAVORITOS ==========
function normalizeFavoritoId(id) {
    const num = Number(id);
    return Number.isFinite(num) ? num : null;
}

function uniqueFavoritos(ids = []) {
    const result = [];
    ids.forEach(id => {
        const normalized = normalizeFavoritoId(id);
        if (normalized !== null && !result.includes(normalized)) {
            result.push(normalized);
        }
    });
    return result;
}

function getFavoritos() {
    const raw = JSON.parse(localStorage.getItem('favoritos') || '[]');
    return uniqueFavoritos(raw);
}

function setFavoritos(arr) {
    localStorage.setItem('favoritos', JSON.stringify(uniqueFavoritos(arr)));
}

function isFavorito(id) {
    const normalized = normalizeFavoritoId(id);
    return normalized !== null && getFavoritos().includes(normalized);
}

function addFavorito(id) {
    const normalized = normalizeFavoritoId(id);
    if (normalized === null) return;
    const favs = getFavoritos();
    if (!favs.includes(normalized)) {
        favs.push(normalized);
        setFavoritos(favs);
    }
}

function removeFavorito(id) {
    const normalized = normalizeFavoritoId(id);
    if (normalized === null) return;
    const favs = getFavoritos();
    const index = favs.indexOf(normalized);
    if (index > -1) {
        favs.splice(index, 1);
        setFavoritos(favs);
    }
}

function toggleFavorito(id, button) {
    const normalized = normalizeFavoritoId(id);
    if (normalized === null) return;
    if (isFavorito(normalized)) {
        removeFavorito(normalized);
        button.textContent = '⭐';
        button.classList.remove('active');
    } else {
        addFavorito(normalized);
        button.textContent = '★';
        button.classList.add('active');
    }
}

function bindFavButtons() {
    document.querySelectorAll('.bookmark-btn').forEach(btn => {
        const id = normalizeFavoritoId(btn.getAttribute('data-id'));
        const activo = isFavorito(id);
        btn.textContent = activo ? '★' : '⭐';
        btn.classList.toggle('active', activo);
    });
}

// ========== COMPARTIR ==========
function shareNews(title, url) {
    const shareData = {
        title: title,
        text: `Mira esta noticia: ${title}`,
        url: window.location.origin + url
    };
    
    if (navigator.share) {
        navigator.share(shareData).catch(() => {
            copyToClipboard(shareData.url);
        });
    } else {
        copyToClipboard(shareData.url);
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Enlace copiado al portapapeles');
    }).catch(() => {
        showNotification('No se pudo copiar el enlace');
    });
}

// ========== NOTIFICACIONES ==========
function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// ========== MODO LECTURA ==========
let readingMode = false;
let fontSize = 1;

function toggleReadingMode() {
    readingMode = !readingMode;
    const detail = document.getElementById('detalle-noticia');
    const btn = document.getElementById('btn-reading-mode');
    
    if (detail) {
        detail.classList.toggle('reading-mode', readingMode);
    }
    
    if (btn) {
        btn.textContent = readingMode ? 'Salir Modo Lectura' : 'Modo Lectura';
        btn.classList.toggle('active', readingMode);
    }
}

function adjustFontSize(delta) {
    fontSize = Math.max(0.8, Math.min(2, fontSize + delta));
    const detail = document.getElementById('detalle-noticia');
    const display = document.getElementById('font-size-display');
    
    if (detail) {
        detail.style.fontSize = `${fontSize}rem`;
    }
    
    if (display) {
        const sizes = ['Muy pequeño', 'Pequeño', 'Normal', 'Grande', 'Muy grande'];
        const index = Math.round((fontSize - 0.8) / 0.3);
        display.textContent = sizes[Math.min(index, sizes.length - 1)];
    }
}

// ========== AUDIO ==========
let speechSynthesis = window.speechSynthesis;
let currentUtterance = null;

function toggleAudio() {
    const btn = document.getElementById('btn-audio');
    if (!btn) return;
    
    if (currentUtterance && speechSynthesis.speaking) {
        speechSynthesis.cancel();
        btn.textContent = '🔊 Audio';
        btn.classList.remove('active');
    } else {
        const content = document.querySelector('#detalle-noticia p, #detalle-noticia h2');
        if (content) {
            const text = content.textContent;
            currentUtterance = new SpeechSynthesisUtterance(text);
            currentUtterance.lang = 'es-ES';
            currentUtterance.rate = 0.9;
            currentUtterance.pitch = 1;
            
            currentUtterance.onend = () => {
                btn.textContent = '🔊 Audio';
                btn.classList.remove('active');
            };
            
            speechSynthesis.speak(currentUtterance);
            btn.textContent = '⏸ Pausar';
            btn.classList.add('active');
        }
    }
}

// ========== IMPRIMIR ==========
function printNews() {
    const content = document.getElementById('detalle-noticia');
    if (!content) return;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <html>
            <head>
                <title>Imprimir Noticia</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1, h2 { color: #333; }
                    .meta { color: #666; margin-bottom: 20px; }
                    img { max-width: 100%; height: auto; }
                </style>
            </head>
            <body>
                ${content.innerHTML}
            </body>
        </html>
    `);
    printWindow.document.close();
    printWindow.print();
}

// ========== POBLAR FILTROS ==========
function poblarFiltros() {
    const selFuente = document.getElementById('filtro-fuente');
    const selCategoriaPrincipal = document.getElementById('filtro-categoria-principal');
    const selTipo = document.getElementById('filtro-tipo');
    const selDepartamento = document.getElementById('filtro-departamento');
    if (!selFuente) return;
    
    fetch('/api/meta')
        .then(r => r.json())
        .then(meta => {
            if (meta.fuentes) {
                selFuente.length = 1;
                meta.fuentes.forEach(f => {
                    const opt = document.createElement('option');
                    opt.value = f;
                    opt.textContent = f;
                    selFuente.appendChild(opt);
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
            if (selDepartamento && meta.departamentos) {
                selDepartamento.length = 1;
                meta.departamentos.forEach(d => {
                    const opt = document.createElement('option');
                    opt.value = d;
                    opt.textContent = d.charAt(0).toUpperCase() + d.slice(1).replace('-', ' ');
                    selDepartamento.appendChild(opt);
                });
            }
        })
        .catch(() => {});
}

// ========== CARGAR DETALLE ==========
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
            
            const meta = `<div class="meta"><strong>Fuente:</strong> ${n.fuente || ''} · <strong>Fecha:</strong> ${formatDate(n.fecha)}</div>`;
            const img = n.imagen ? `<img src="${n.imagen}" alt="Imagen de noticia" class="news-image" data-src="${n.imagen}">` : '';
            const tipoTag = n.tipo ? `<span class="tag tipo-tag">${n.tipo}</span>` : '';
            const categoriaTag = n.categoria ? `<span class="tag categoria-tag ${n.categoria}">${n.categoria.charAt(0).toUpperCase() + n.categoria.slice(1)}</span>` : '';
            const departamentoTag = n.departamento ? `<span class="tag departamento-tag">${n.departamento.charAt(0).toUpperCase() + n.departamento.slice(1).replace('-', ' ')}</span>` : '';
            
            cont.innerHTML = `
                <article class="noticia">
                    <h2>${n.titulo}</h2>
                    ${meta}
                    <div class="tags">
                        ${categoriaTag}
                        ${departamentoTag}
                        ${tipoTag}
                    </div>
                    ${img}
                    ${n.resumen ? `<div class="resumen"><p>${n.resumen}</p></div>` : ''}
                    ${n.autor ? `<div class="autor"><strong>Autor:</strong> ${n.autor}</div>` : ''}
                    <div class="actions">
                        <button id="btn-fav" data-id="${n.id}">${isFavorito(n.id) ? '★ Guardado' : '⭐ Guardar'}</button>
                        <div class="share-buttons" id="share-buttons">
                            <button class="btn-share-twitter" data-title="${n.titulo}" data-url="${window.location.href}">🐦 Twitter</button>
                            <button class="btn-share-facebook" data-url="${window.location.href}">📘 Facebook</button>
                            <button class="btn-share-whatsapp" data-title="${n.titulo}" data-url="${window.location.href}">💬 WhatsApp</button>
                            <button class="btn-share-telegram" data-title="${n.titulo}" data-url="${window.location.href}">✈️ Telegram</button>
                        </div>
                        <a href="${n.link}" target="_blank" rel="noopener" class="btn-link">Ver fuente original ↗</a>
                    </div>
                    <div id="social-media-content" class="social-media-section">
                        <h3>📱 En Redes Sociales</h3>
                        <div id="social-posts" class="social-posts"></div>
                    </div>
                </article>
            `;
            
            // Event listeners para detalle
            const btnFav = document.getElementById('btn-fav');
            const image = cont.querySelector('.news-image');
            
            if (btnFav) {
                btnFav.addEventListener('click', () => toggleFavorito(n.id, btnFav));
            }
            
            // Configurar botones de compartir
            setupShareButtons(n.titulo, window.location.href);
            
            if (image) {
                image.addEventListener('click', () => showImageModal(image.src));
            }
            
            cargarRelacionadas(n.id);
            cargarRedesSociales(n.id);
        });
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

function setupShareButtons(titulo, url) {
    // Configurar botones de compartir
    const btnTwitter = document.querySelector('.btn-share-twitter');
    const btnFacebook = document.querySelector('.btn-share-facebook');
    const btnWhatsApp = document.querySelector('.btn-share-whatsapp');
    const btnTelegram = document.querySelector('.btn-share-telegram');
    
    if (btnTwitter) {
        btnTwitter.addEventListener('click', () => {
            const texto = btnTwitter.dataset.title || titulo;
            const linkUrl = btnTwitter.dataset.url || url;
            const shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(texto)}&url=${encodeURIComponent(linkUrl)}`;
            window.open(shareUrl, '_blank', 'width=550,height=420');
        });
    }
    
    if (btnFacebook) {
        btnFacebook.addEventListener('click', () => {
            const linkUrl = btnFacebook.dataset.url || url;
            const shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(linkUrl)}`;
            window.open(shareUrl, '_blank', 'width=550,height=420');
        });
    }
    
    if (btnWhatsApp) {
        btnWhatsApp.addEventListener('click', () => {
            const texto = btnWhatsApp.dataset.title || titulo;
            const linkUrl = btnWhatsApp.dataset.url || url;
            const shareUrl = `https://wa.me/?text=${encodeURIComponent(texto + ' ' + linkUrl)}`;
            window.open(shareUrl, '_blank');
        });
    }
    
    if (btnTelegram) {
        btnTelegram.addEventListener('click', () => {
            const texto = btnTelegram.dataset.title || titulo;
            const linkUrl = btnTelegram.dataset.url || url;
            const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(linkUrl)}&text=${encodeURIComponent(texto)}`;
            window.open(shareUrl, '_blank');
        });
    }
}

function cargarRedesSociales(noticiaId) {
    const container = document.getElementById('social-posts');
    if (!container) return;
    
    container.innerHTML = '<p>Cargando contenido de redes sociales...</p>';
    
    fetch(`/api/social/noticia/${noticiaId}`)
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                container.innerHTML = `<p class="error">${data.error}</p>`;
                return;
            }
            
            container.innerHTML = '';
            const results = data.results || {};
            
            if (Object.keys(results).length === 0) {
                container.innerHTML = '<p>No se encontró contenido relacionado en redes sociales.</p>';
                return;
            }
            
            // Mostrar resultados por plataforma
            Object.keys(results).forEach(platform => {
                const posts = results[platform] || [];
                if (posts.length === 0) return;
                
                const platformDiv = document.createElement('div');
                platformDiv.className = `social-platform ${platform}`;
                
                const platformName = platform.charAt(0).toUpperCase() + platform.slice(1);
                platformDiv.innerHTML = `<h4>${getPlatformIcon(platform)} ${platformName}</h4>`;
                
                const postsList = document.createElement('div');
                postsList.className = 'social-posts-list';
                
                posts.forEach(post => {
                    const postDiv = document.createElement('div');
                    postDiv.className = 'social-post';
                    postDiv.innerHTML = `
                        <div class="social-post-header">
                            <strong>${post.author || 'Usuario'}</strong>
                            ${post.timestamp ? `<span class="social-timestamp">${formatDate(post.timestamp)}</span>` : ''}
                        </div>
                        <div class="social-post-text">${post.text || ''}</div>
                        ${post.link ? `<a href="${post.link}" target="_blank" rel="noopener" class="social-link">Ver en ${platformName} →</a>` : ''}
                        ${post.image ? `<img src="${post.image}" alt="Imagen" class="social-image">` : ''}
                    `;
                    postsList.appendChild(postDiv);
                });
                
                platformDiv.appendChild(postsList);
                container.appendChild(platformDiv);
            });
        })
        .catch(err => {
            container.innerHTML = `<p class="error">Error al cargar contenido de redes sociales: ${err.message}</p>`;
        });
}

function getPlatformIcon(platform) {
    const icons = {
        'twitter': '🐦',
        'facebook': '📘',
        'instagram': '📷',
        'whatsapp': '💬',
        'telegram': '✈️'
    };
    return icons[platform] || '📱';
}

function iniciarScrapeoDesdeUI(categoria, button) {
    const originalText = button ? button.textContent : '';
    if (button) {
        button.disabled = true;
        button.textContent = 'Iniciando...';
        button.classList.add('loading');
    }

    const url = categoria ? `/api/scraping/categoria/${categoria}` : '/api/scraping/todos';

    fetch(url, { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            const mensaje = data?.mensaje || 'Scraping iniciado correctamente. Las noticias se actualizarán en breve.';
            alert(mensaje);
            cargarNoticias(currentFilters, false, true);
        })
        .catch(err => {
            alert(`Error al iniciar el scraping: ${err.message}`);
        })
        .finally(() => {
            if (button) {
                button.disabled = false;
                button.textContent = originalText || '🔄 Actualizar noticias';
                button.classList.remove('loading');
            }
        });
}

// ========== RENDERIZAR FAVORITOS ==========
function renderFavoritos() {
    const list = document.getElementById('lista-favoritos');
    if (!list) return;
    
    const ids = getFavoritos();
    if (!ids.length) {
        list.innerHTML = '<p class="meta">No tienes favoritos aún.</p>';
        return;
    }
    
    list.innerHTML = '';
    
    // Aplicar filtros
    const searchQuery = document.getElementById('fav-busqueda')?.value?.toLowerCase() || '';
    const folderFilter = document.getElementById('fav-folder-filter')?.value || '';
    const fechaDesde = document.getElementById('fav-fecha-desde')?.value || '';
    const fechaHasta = document.getElementById('fav-fecha-hasta')?.value || '';
    const ordenar = document.getElementById('fav-ordenar')?.value || 'fecha_desc';
    
    Promise.all(ids.map(id => 
        fetch(`/api/noticias/${id}`)
            .then(r => r.json())
            .catch(() => null)
    ))
    .then(items => {
        let filteredItems = items.filter(Boolean);
        
        // Filtro de búsqueda
        if (searchQuery) {
            filteredItems = filteredItems.filter(n => 
                n.titulo?.toLowerCase().includes(searchQuery) || 
                n.resumen?.toLowerCase().includes(searchQuery)
            );
        }
        
        // Filtro de fecha (comparar como fechas reales)
        if (fechaDesde) {
            const desde = new Date(fechaDesde);
            filteredItems = filteredItems.filter(n => {
                const f = n && n.fecha ? new Date(n.fecha) : null;
                return f ? f >= desde : false;
            });
        }
        if (fechaHasta) {
            const hasta = new Date(fechaHasta);
            filteredItems = filteredItems.filter(n => {
                const f = n && n.fecha ? new Date(n.fecha) : null;
                return f ? f <= hasta : false;
            });
        }
        
        // Ordenamiento
        filteredItems.sort((a, b) => {
            switch (ordenar) {
                case 'fecha_asc':
                    return new Date(a.fecha) - new Date(b.fecha);
                case 'titulo_asc':
                    return a.titulo.localeCompare(b.titulo);
                case 'titulo_desc':
                    return b.titulo.localeCompare(a.titulo);
                default: // fecha_desc
                    return new Date(b.fecha) - new Date(a.fecha);
            }
        });
        
        filteredItems.forEach(n => {
            list.appendChild(crearNodoNoticia(n, 'list'));
        });
        
        bindFavButtons();
    });
}

// ========== NAVEGACIÓN POR TECLADO ==========
function setupKeyboardNavigation() {
    document.addEventListener('keydown', (e) => {
        // Esc para cerrar modales
        if (e.key === 'Escape') {
            closeModal('preview-modal');
            closeModal('image-modal');
            closeModal('folder-modal');
        }
        
        // Ctrl+F para buscar
        if (e.ctrlKey && e.key === 'f') {
            e.preventDefault();
            const searchInput = document.getElementById('busqueda');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Ctrl+P para imprimir (en página de detalle)
        if (e.ctrlKey && e.key === 'p' && document.getElementById('detalle-noticia')) {
            e.preventDefault();
            printNews();
        }
    });
}

// ========== INFINITE SCROLL ==========
function setupInfiniteScroll() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !isLoading && paginationData.has_next) {
                page++;
                cargarNoticias(currentFilters, true, false);
            }
        });
    });
    
    const sentinel = document.createElement('div');
    sentinel.id = 'scroll-sentinel';
    sentinel.style.height = '20px';
    document.body.appendChild(sentinel);
    
    observer.observe(sentinel);
}

// ========== EVENT LISTENERS ==========
document.addEventListener('DOMContentLoaded', function() {
    // Cargar noticias iniciales
    if (document.getElementById('noticias')) {
        cargarNoticias({}, true);
        poblarFiltros();
        setupInfiniteScroll();
    }
    
    // Cargar detalle
    if (document.getElementById('detalle-noticia')) {
        cargarDetalle();
    }
    
    // Renderizar favoritos
    if (document.getElementById('lista-favoritos')) {
        renderFavoritos();
    }
    
    // Configurar navegación por teclado
    setupKeyboardNavigation();
    
    // Botón cargar más
    const btnMas = document.getElementById('btn-cargar-mas');
    if (btnMas) {
        btnMas.addEventListener('click', () => {
            page++;
            cargarNoticias(currentFilters, true, false);
        });
    }
    
    // Botón filtrar
    const btnFiltrar = document.getElementById('btn-filtrar');
    if (btnFiltrar) {
        btnFiltrar.addEventListener('click', () => {
            const filtros = {
                fuente: document.getElementById('filtro-fuente')?.value,
                categoria: document.getElementById('filtro-categoria-principal')?.value,
                tipo: document.getElementById('filtro-tipo')?.value,
                departamento: document.getElementById('filtro-departamento')?.value,
                q: document.getElementById('busqueda')?.value,
                fecha_desde: document.getElementById('fecha-desde')?.value,
                fecha_hasta: document.getElementById('fecha-hasta')?.value,
                ordenar: document.getElementById('ordenar')?.value
            };
            cargarNoticias(filtros, false, true);
        });
    }
    
    // Botón para iniciar scraping
    const btnScrape = document.getElementById('btn-scrape');
    if (btnScrape) {
        btnScrape.addEventListener('click', () => {
            const categoria = document.getElementById('filtro-categoria-principal')?.value;
            iniciarScrapeoDesdeUI(categoria, btnScrape);
        });
    }
    
    // Búsqueda con debounce
    const busqueda = document.getElementById('busqueda');
    if (busqueda) {
        busqueda.addEventListener('input', debounce(() => {
            const filtros = {
                q: busqueda.value,
                fuente: document.getElementById('filtro-fuente')?.value,
                categoria: document.getElementById('filtro-categoria-principal')?.value,
                tipo: document.getElementById('filtro-tipo')?.value,
                departamento: document.getElementById('filtro-departamento')?.value,
                fecha_desde: document.getElementById('fecha-desde')?.value,
                fecha_hasta: document.getElementById('fecha-hasta')?.value,
                ordenar: document.getElementById('ordenar')?.value
            };
            cargarNoticias(filtros, false, true);
        }, 500));
    }
    
    // Filtros avanzados
    const btnAdvanced = document.getElementById('btn-advanced-filters');
    const advancedFilters = document.getElementById('advanced-filters');
    if (btnAdvanced && advancedFilters) {
        btnAdvanced.addEventListener('click', () => {
            const isVisible = advancedFilters.style.display !== 'none';
            advancedFilters.style.display = isVisible ? 'none' : 'block';
            btnAdvanced.textContent = isVisible ? 'Filtros Avanzados' : 'Ocultar Filtros';
        });
    }
    
    // Limpiar filtros
    const btnLimpiar = document.getElementById('btn-limpiar-filtros');
    if (btnLimpiar) {
        btnLimpiar.addEventListener('click', () => {
            document.getElementById('filtro-fuente').value = '';
            document.getElementById('filtro-categoria-principal').value = '';
            document.getElementById('filtro-tipo').value = '';
            document.getElementById('filtro-departamento').value = '';
            document.getElementById('busqueda').value = '';
            document.getElementById('fecha-desde').value = '';
            document.getElementById('fecha-hasta').value = '';
            document.getElementById('ordenar').value = 'fecha_desc';
            cargarNoticias({}, false, true);
        });
    }
    
    // Toggle de vista
    const btnGridView = document.getElementById('btn-grid-view');
    const btnListView = document.getElementById('btn-list-view');
    const noticiasContainer = document.getElementById('noticias');
    
    if (btnGridView && btnListView && noticiasContainer) {
        btnGridView.addEventListener('click', () => {
            currentView = 'grid';
            noticiasContainer.className = 'container grid-view';
            btnGridView.classList.add('active');
            btnListView.classList.remove('active');
            
            // Re-renderizar noticias con nueva vista
            const noticias = noticiasContainer.querySelectorAll('.noticia');
            noticias.forEach(noticia => {
                noticia.className = `noticia grid-view`;
            });
        });
        
        btnListView.addEventListener('click', () => {
            currentView = 'list';
            noticiasContainer.className = 'container list-view';
            btnListView.classList.add('active');
            btnGridView.classList.remove('active');
            
            // Re-renderizar noticias con nueva vista
            const noticias = noticiasContainer.querySelectorAll('.noticia');
            noticias.forEach(noticia => {
                noticia.className = `noticia list-view`;
            });
        });
    }
    
    // Controles de modo lectura
    const btnReadingMode = document.getElementById('btn-reading-mode');
    const btnPrint = document.getElementById('btn-print');
    const btnAudio = document.getElementById('btn-audio');
    const fontSmaller = document.getElementById('font-smaller');
    const fontLarger = document.getElementById('font-larger');
    
    if (btnReadingMode) {
        btnReadingMode.addEventListener('click', toggleReadingMode);
    }
    
    if (btnPrint) {
        btnPrint.addEventListener('click', printNews);
    }
    
    if (btnAudio) {
        btnAudio.addEventListener('click', toggleAudio);
    }
    
    if (fontSmaller) {
        fontSmaller.addEventListener('click', () => adjustFontSize(-0.2));
    }
    
    if (fontLarger) {
        fontLarger.addEventListener('click', () => adjustFontSize(0.2));
    }
    
    // Cerrar modales
    document.querySelectorAll('.close').forEach(closeBtn => {
        closeBtn.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    // Cerrar modal al hacer clic fuera
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });
    
    // Filtros de favoritos
    const favBusqueda = document.getElementById('fav-busqueda');
    const favFolderFilter = document.getElementById('fav-folder-filter');
    const favFechaDesde = document.getElementById('fav-fecha-desde');
    const favFechaHasta = document.getElementById('fav-fecha-hasta');
    const favOrdenar = document.getElementById('fav-ordenar');
    
    [favBusqueda, favFolderFilter, favFechaDesde, favFechaHasta, favOrdenar].forEach(input => {
        if (input) {
            input.addEventListener('change', renderFavoritos);
        }
    });
    
    // Botones de favoritos
    const btnExport = document.getElementById('btn-exportar');
    const btnClear = document.getElementById('btn-limpiar');
    
    if (btnExport) {
        btnExport.addEventListener('click', () => {
            const favs = getFavoritos();
            const blob = new Blob([JSON.stringify(favs, null, 2)], { type: 'application/json' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = 'favoritos.json';
            a.click();
        });
    }
    
    if (btnClear) {
        btnClear.addEventListener('click', () => {
            if (confirm('¿Limpiar todos los favoritos?')) {
                localStorage.removeItem('favoritos');
                renderFavoritos();
            }
        });
    }
});

// ========== TEMA ==========
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
