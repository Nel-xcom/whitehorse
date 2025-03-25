document.addEventListener('DOMContentLoaded', () => {
    const modalConfirmacion = document.getElementById('modal-posponer-confirmacion');
    const modalMotivo = document.getElementById('modal-introducir-motivo');
    const overlay = document.getElementById('overlay-posponer');
    let solicitudIdActual = null;

    document.querySelector('.slider').addEventListener('click', (event) => {
        if (event.target.classList.contains('btn-posponer')) {
            const card = event.target.closest('.card-solicitud');
            const formAceptar = card.querySelector('form[action*="aceptar_solicitud"]');
            if (formAceptar) {
                const url = new URL(formAceptar.action, window.location.origin); // Crear una URL válida
                solicitudIdActual = url.pathname.split('/').filter(Boolean).pop(); // Extraer el ID de la URL
                console.log('Solicitud ID obtenido:', solicitudIdActual); // Depuración
            } else {
                console.error('No se encontró el formulario Aceptar para esta tarjeta.');
                return;
            }



            console.log('Solicitud ID:', solicitudIdActual);

            if (solicitudIdActual) {
                modalConfirmacion.classList.add('show');
                overlay.classList.add('show');
            } else {
                alert('No se pudo identificar la solicitud. Intente nuevamente.');
            }
        }
    });

    document.getElementById('form-posponer-motivo').addEventListener('submit', (event) => {
        event.preventDefault();
        const motivo = document.getElementById('motivo-posponer').value.trim();

        if (!motivo) {
            alert('Debes ingresar un motivo.');
            return;
        }

        if (!solicitudIdActual || solicitudIdActual === 'null') {
            alert('No se pudo identificar la solicitud. Intente nuevamente.');
            return;
        }

        fetch(`/solicitudes/${solicitudIdActual}/posponer/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ motivo })
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.status === 'success') {
                    alert('Solicitud Rechazada correctamente.');
                    modalMotivo.classList.remove('show');
                    overlay.classList.remove('show');
                    location.reload();
                } else {
                    alert(`Error: ${data.message}`);
                }
            })
            .catch((error) => console.error('Error al posponer la solicitud:', error));
        
    });
});
