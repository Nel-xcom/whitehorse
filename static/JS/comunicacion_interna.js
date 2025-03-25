document.addEventListener('DOMContentLoaded', () => {
    const slider = document.querySelector('.slider');
    const btnLeft = document.querySelector('.slider-btn-left');
    const btnRight = document.querySelector('.slider-btn-right');
    const modalPosponer = document.getElementById('modal-posponer');
    const closeModal = document.querySelector('.close-modal');
    const btnEnviarPosponer = document.getElementById('btn-enviar-posponer');
    const motivoInput = document.getElementById('motivo-posponer');
    let solicitudIdSeleccionada = null;

    const getCsrfToken = () => {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    };

    const cargarSolicitudesPendientes = () => {
        fetch('/comunicacion-interna/solicitudes-pendientes/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
            .then((response) => response.json())
            .then((data) => {
                slider.innerHTML = ''; // Limpiar solicitudes previas

                if (data.results.length > 0) {
                    data.results.forEach((solicitud) => {
                        const card = `
                            <div class="card-solicitud" data-solicitud-id="${solicitud.id}">
                                <h3>${solicitud.solicitante}</h3>
                                <p>Descripción: ${solicitud.descripcion}</p>
                                <p>Fecha de Finalización: ${solicitud.fecha_finalizacion}</p>
                                <div class="acciones-solicitud">
                                    <form method="post" action="/solicitudes/${solicitud.id}/aceptar/">
                                        <input type="hidden" name="csrfmiddlewaretoken" value="${getCsrfToken()}">
                                        <button type="submit" class="btn-aceptar">Aceptar</button>
                                    </form>
                                    <button class="btn-posponer" data-solicitud-id="${solicitud.id}">Rechazar</button>
                                </div>
                            </div>`;
                        slider.innerHTML += card;
                    });
                } else {
                    slider.innerHTML = '<p>No tienes solicitudes pendientes.</p>';
                }
            })
            .catch((error) => console.error('Error al cargar solicitudes pendientes:', error));
    };

    slider.addEventListener('click', (event) => {
        if (event.target.classList.contains('btn-posponer')) {
            solicitudIdSeleccionada = event.target.getAttribute('data-solicitud-id');
            modalPosponer.style.display = 'block';
        }
    });

    closeModal.addEventListener('click', () => {
        modalPosponer.style.display = 'none';
        motivoInput.value = '';
    });

    btnEnviarPosponer.addEventListener('click', () => {
        const motivo = motivoInput.value.trim();
        if (!motivo) {
            alert('El motivo es obligatorio.');
            return;
        }

        fetch(`/solicitudes/${solicitudIdSeleccionada}/posponer/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ motivo }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.status === 'success') {
                    alert(data.message);
                    cargarSolicitudesPendientes();
                    modalPosponer.style.display = 'none';
                    motivoInput.value = '';
                } else {
                    alert(data.message);
                }
            })
            .catch((error) => console.error('Error al posponer la solicitud:', error));
    });

    btnLeft.addEventListener('click', () => {
        scrollPosition = Math.max(scrollPosition - cardWidth, 0);
        slider.style.transform = `translateX(-${scrollPosition}px)`;
    });

    btnRight.addEventListener('click', () => {
        scrollPosition = Math.min(scrollPosition + cardWidth, slider.scrollWidth - slider.offsetWidth);
        slider.style.transform = `translateX(-${scrollPosition}px)`;
    });

    cargarSolicitudesPendientes();
});



document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.querySelector('.barra-busqueda input');
    const resultadosBusqueda = document.querySelector('.resultados-busqueda');

    // Función para actualizar resultados en la UI
    const actualizarResultados = (usuarios) => {
        resultadosBusqueda.innerHTML = ''; // Limpiar resultados previos

        if (usuarios.length > 0) {
            usuarios.forEach((usuario) => {
                const card = `
                    <div class="card-usuario" data-usuario-id="${usuario.id}">
                        <div class="info-usuario">
                            <h3>${usuario.first_name} ${usuario.last_name}</h3>
                            <p>Sector: ${usuario.sector}</p>
                        </div>
                        <div class="acciones-usuario">
                            <button class="btn-solicitud">Solicitar Tarea</button>
                            <button class="btn-tareas" data-id="${usuario.id}">Ver Perfil</button>
                        </div>
                    </div>`;
                resultadosBusqueda.innerHTML += card;
            });

            // Agregar evento a los botones "Ver Perfil"
            const botonesVerPerfil = document.querySelectorAll('.btn-tareas');
            botonesVerPerfil.forEach((boton) => {
                boton.addEventListener('click', (e) => {
                    const usuarioId = e.target.getAttribute('data-id');
                    if (usuarioId) {
                        window.location.href = `/perfil/${usuarioId}/`;
                    }
                });
            });
        } else {
            resultadosBusqueda.innerHTML = '<p>No se encontraron usuarios.</p>';
        }
    };

    // Función para realizar la búsqueda
    const buscarUsuarios = (query = '') => {
        fetch(`/comunicacion-interna/buscar-usuarios/?q=${query}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
            .then((response) => response.json())
            .then((data) => {
                actualizarResultados(data.results);
            })
            .catch((error) => {
                console.error('Error en la búsqueda:', error);
            });
    };

    // Cargar usuarios por defecto al iniciar
    buscarUsuarios();

    // Escuchar los cambios en el input de búsqueda
    searchInput.addEventListener('input', () => {
        const query = searchInput.value.trim();
        buscarUsuarios(query);
    });
});


document.addEventListener('DOMContentLoaded', () => {
    const resultadosBusqueda = document.querySelector('.resultados-busqueda');
    const modal = document.getElementById('modal-solicitud');
    const modalOverlay = document.createElement('div');
    modalOverlay.classList.add('modal-overlay');
    document.body.appendChild(modalOverlay);

    // Mostrar modal al hacer clic en "Solicitar Tarea"
    resultadosBusqueda.addEventListener('click', (event) => {
        if (event.target.classList.contains('btn-solicitud')) {
            const cardUsuario = event.target.closest('.card-usuario');
            const destinatarioId = cardUsuario.dataset.usuarioId;

            // Guardar el destinatario en el modal
            modal.dataset.destinatarioId = destinatarioId;

            // Mostrar modal y superposición
            modal.classList.add('show');
            modalOverlay.classList.add('show');
        }
    });

    // Cerrar modal al hacer clic en "Cancelar" o en la superposición
    modalOverlay.addEventListener('click', () => {
        modal.classList.remove('show');
        modalOverlay.classList.remove('show');
    });

    modal.querySelector('.btn-cancelar').addEventListener('click', () => {
        modal.classList.remove('show');
        modalOverlay.classList.remove('show');
    });

    // Enviar la solicitud
    modal.querySelector('form').addEventListener('submit', (e) => {
        e.preventDefault();
        const descripcion = modal.querySelector('#descripcion').value.trim();
        const fechaFinalizacion = modal.querySelector('#fecha_finalizacion').value;
        const destinatarioId = modal.dataset.destinatarioId;

        if (!descripcion || !fechaFinalizacion) {
            alert('Todos los campos son obligatorios.');
            return;
        }

        fetch('/solicitar-tarea/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                destinatario_id: destinatarioId,
                descripcion,
                fecha_finalizacion: fechaFinalizacion
            })
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.status === 'success') {
                    alert('Solicitud enviada correctamente');
                    modal.classList.remove('show');
                    modalOverlay.classList.remove('show');
                } else {
                    alert(`Error: ${data.message}`);
                }
            })
            .catch((error) => console.error('Error:', error));
    });
});


