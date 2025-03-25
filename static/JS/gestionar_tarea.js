document.addEventListener("DOMContentLoaded", function () {
    const tareaId = document.getElementById("tarea-id").textContent.trim();
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Referencias para actualizar datos del ticket
    const btnActualizar = document.getElementById("btn-actualizar");
    const btnGuardar = document.getElementById("btn-guardar");
    const btnFinalizar = document.getElementById("btn-finalizar"); // Usar el botón estático
    const descripcionTexto = document.getElementById("descripcion-texto");
    const descripcionInput = document.getElementById("descripcion-input");
    const fechaTexto = document.getElementById("fecha-texto");
    const fechaInput = document.getElementById("fecha-input");
    const estadoTexto = document.getElementById("estado-texto");
    const estadoSelect = document.getElementById("estado-select");

    // Funcionalidad para actualizar datos del ticket
    btnActualizar.addEventListener("click", function () {
        descripcionTexto.style.display = "none";
        descripcionInput.style.display = "block";

        fechaTexto.style.display = "none";
        fechaInput.style.display = "block";

        estadoTexto.style.display = "none";
        estadoSelect.style.display = "block";

        btnActualizar.style.display = "none";
        btnGuardar.style.display = "inline-block";
    });

    btnGuardar.addEventListener("click", function () {
        const data = {
            descripcion: descripcionInput.value.trim(),
            fecha_finalizacion: fechaInput.value,
            estado: estadoSelect.value,
        };

        fetch(`/tareas/${tareaId}/actualizar/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify(data),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.status === "success") {
                    // Actualizar los datos en la vista
                    descripcionTexto.textContent = data.tarea.descripcion;
                    fechaTexto.textContent = data.tarea.fecha_finalizacion;
                    estadoTexto.textContent = data.tarea.estado_display;

                    // Volver al modo visual
                    descripcionTexto.style.display = "block";
                    descripcionInput.style.display = "none";

                    fechaTexto.style.display = "block";
                    fechaInput.style.display = "none";

                    estadoTexto.style.display = "block";
                    estadoSelect.style.display = "none";

                    btnGuardar.style.display = "none";
                    btnActualizar.style.display = "inline-block";

                    alert("Tarea actualizada correctamente.");
                } else {
                    alert("Error al actualizar la tarea: " + data.message);
                }
            })
            .catch((error) => {
                console.error("Error al actualizar la tarea:", error);
                alert("Hubo un error al actualizar la tarea.");
            });
    });

    // Funcionalidad para finalizar la tarea
    btnFinalizar.addEventListener("click", function () {
        if (confirm("¿Estás seguro de que deseas finalizar esta tarea?")) {
            fetch(`/tareas/${tareaId}/finalizar/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken,
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.status === "success") {
                        alert("La tarea se ha finalizado correctamente.");
                        window.location.href = "/comunicacion-interna/"; // Redirigir al panel
                    } else {
                        alert("Error al finalizar la tarea: " + data.message);
                    }
                })
                .catch((error) => {
                    console.error("Error al finalizar la tarea:", error);
                    alert("Hubo un error al finalizar la tarea. Inténtalo de nuevo.");
                });
        }
    });

    // Agregar un nuevo comentario
    const btnComentar = document.querySelector(".btn-comentar");
    const comentarioInput = document.querySelector(".comentario-input");
    const comentariosLista = document.querySelector(".comentarios-lista");

    btnComentar.addEventListener("click", function () {
        const texto = comentarioInput.value.trim();
        if (!texto) {
            alert("El comentario no puede estar vacío.");
            return;
        }

        fetch(`/tareas/${tareaId}/comentarios/crear/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify({ texto }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.status === "success") {
                    const comentarioHTML = `
                        <div class="comentario" data-id="${data.comentario.id}">
                            <img src="https://via.placeholder.com/50" alt="User Avatar" class="user-avatar">
                            <div class="comentario-detalle">
                                <h4>${data.comentario.usuario}</h4>
                                <p class="comentario-texto">${data.comentario.texto}</p>
                                <textarea class="comentario-editar" style="display: none;"></textarea>
                                <small>${data.comentario.fecha_creacion}</small>
                            </div>
                            <div class="comentario-acciones">
                                <button class="btn-editar" title="Editar"><i class="fas fa-edit"></i></button>
                                <button class="btn-eliminar" title="Eliminar"><i class="fas fa-trash"></i></button>
                            </div>
                        </div>
                    `;
                    comentariosLista.insertAdjacentHTML("afterbegin", comentarioHTML);
                    comentarioInput.value = ""; // Limpiar el input
                } else {
                    alert(data.message);
                }
            })
            .catch((error) => console.error("Error al crear el comentario:", error));
    });

    // Delegación de eventos para editar y eliminar comentarios
    comentariosLista.addEventListener("click", function (e) {
        const comentarioElement = e.target.closest(".comentario");
        if (!comentarioElement) return;

        const comentarioId = comentarioElement.getAttribute("data-id");

        if (e.target.closest(".btn-editar")) {
            const textoElement = comentarioElement.querySelector(".comentario-texto");
            const editarElement = comentarioElement.querySelector(".comentario-editar");

            if (editarElement.style.display === "none") {
                editarElement.value = textoElement.textContent;
                textoElement.style.display = "none";
                editarElement.style.display = "block";
            } else {
                const nuevoTexto = editarElement.value.trim();
                fetch(`/comentarios/${comentarioId}/editar/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrftoken,
                    },
                    body: JSON.stringify({ texto: nuevoTexto }),
                })
                    .then((response) => response.json())
                    .then((data) => {
                        if (data.status === "success") {
                            textoElement.textContent = nuevoTexto;
                            textoElement.style.display = "block";
                            editarElement.style.display = "none";
                        } else {
                            alert(data.message);
                        }
                    })
                    .catch((error) => console.error("Error al editar el comentario:", error));
            }
        }

        if (e.target.closest(".btn-eliminar")) {
            if (confirm("¿Estás seguro de eliminar este comentario?")) {
                fetch(`/comentarios/${comentarioId}/eliminar/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrftoken,
                    },
                })
                    .then((response) => response.json())
                    .then((data) => {
                        if (data.status === "success") {
                            comentarioElement.remove();
                        } else {
                            alert(data.message);
                        }
                    })
                    .catch((error) => console.error("Error al eliminar el comentario:", error));
            }
        }
    });
});
