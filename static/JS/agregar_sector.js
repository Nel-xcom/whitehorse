document.addEventListener("DOMContentLoaded", function () {
    let modal = document.getElementById("confirm-delete-modal");
    let overlay = document.querySelector(".modal-overlay");
    let confirmDeleteBtn = document.getElementById("confirm-delete-btn");
    let cancelDeleteBtn = document.getElementById("cancel-delete-btn");
    let sectorIdToDelete = null;
    let sectorLiToDelete = null;

    // Obtener el token CSRF desde la metaetiqueta
    let csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Usar event delegation para detectar clics en ".delete-sector"
    document.addEventListener("click", function (event) {
        if (event.target.closest(".delete-sector")) {
            event.preventDefault();
            let deleteButton = event.target.closest(".delete-sector");
            sectorIdToDelete = deleteButton.getAttribute("data-sector-id");
            sectorLiToDelete = deleteButton.closest('li');

            // Agregar clase active para mostrar el modal
            modal.classList.add("active");
            overlay.classList.add("active");
        }
    });

    // Confirmar eliminación
    confirmDeleteBtn.addEventListener("click", function () {
        if (sectorIdToDelete) {
            fetch(`/borrar-sector/${sectorIdToDelete}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    sectorLiToDelete.remove();
                    alert(data.message);
                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            })
            .finally(() => {
                modal.classList.remove("active");
                overlay.classList.remove("active");
                sectorIdToDelete = null;
                sectorLiToDelete = null;
            });
        }
    });

    // Cancelar eliminación
    cancelDeleteBtn.addEventListener("click", function () {
        modal.classList.remove("active");
        overlay.classList.remove("active");
        sectorIdToDelete = null;
        sectorLiToDelete = null;
    });

    // Cerrar modal al hacer clic fuera
    overlay.addEventListener("click", function () {
        modal.classList.remove("active");
        overlay.classList.remove("active");
        sectorIdToDelete = null;
        sectorLiToDelete = null;
    });

    // Cerrar modal con tecla Escape
    window.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            modal.classList.remove("active");
            overlay.classList.remove("active");
            sectorIdToDelete = null;
            sectorLiToDelete = null;
        }
    });
});
