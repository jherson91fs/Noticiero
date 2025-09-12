let page = 1;
const limit = 5;

function cargarNoticias(filtros = {}) {
    let url = `/api/noticias?page=${page}&limit=${limit}`;

    if (filtros.fuente) url += `&fuente=${filtros.fuente}`;
    if (filtros.categoria) url += `&categoria=${filtros.categoria}`;
    
    fetch(url)
        .then(res => res.json())
        .then(data => {
            if (data.mensaje) {
                alert(data.mensaje);
                return;
            }
            const contenedor = document.getElementById('noticias');
            data.forEach(noticia => {
                const div = document.createElement('div');
                div.className = "noticia";
                div.innerHTML = `
                    <h2><a href="/noticia?id=${noticia.id}">${noticia.titulo}</a></h2>
                    <p><strong>Fuente:</strong> ${noticia.fuente} | <strong>Fecha:</strong> ${noticia.fecha}</p>
                    ${noticia.imagen ? `<img src="${noticia.imagen}" alt="Imagen">` : ''}
                    <p>${noticia.resumen || ''}</p>
                `;
                contenedor.appendChild(div);
            });
        });
}

document.getElementById('btn-cargar-mas').addEventListener('click', () => {
    page++;
    cargarNoticias({
        fuente: document.getElementById('filtro-fuente').value,
        categoria: document.getElementById('filtro-categoria').value
    });
});

document.getElementById('btn-filtrar').addEventListener('click', () => {
    page = 1;
    document.getElementById('noticias').innerHTML = '';
    cargarNoticias({
        fuente: document.getElementById('filtro-fuente').value,
        categoria: document.getElementById('filtro-categoria').value
    });
});

// Carga inicial
cargarNoticias();
