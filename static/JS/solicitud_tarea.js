document.addEventListener('click', (event) => {
    if (event.target.classList.contains('btn-solicitud')) {
        const cardUsuario = event.target.closest('.card-usuario');
        const destinatarioId = cardUsuario.dataset.usuarioId;

        const descripcion = prompt('Ingresa una descripción para la solicitud:');
        if (descripcion !== null) {
            fetch('/solicitar-tarea/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ destinatario_id: destinatarioId, descripcion })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert('Solicitud enviada correctamente');
                    } else {
                        alert('Error al enviar la solicitud');
                    }
                })
                .catch(error => console.error('Error:', error));
        }
    }
});
