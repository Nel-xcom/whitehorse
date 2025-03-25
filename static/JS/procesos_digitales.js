function abrirModal(tipo) {
    cargarProcesos(tipo); // ✅ Asegurar que los procesos se carguen antes
    document.getElementById("modal-overlay").classList.add("active");
    document.getElementById("modal-eliminar").classList.add("active");
}

function cerrarModal() {
    document.getElementById("modal-overlay").classList.remove("active");
    document.getElementById("modal-eliminar").classList.remove("active");
}

function cargarProcesos() {
    const tipo = document.getElementById("tipo-proceso").value;
    const selectProceso = document.getElementById("proceso-select");

    selectProceso.innerHTML = '<option value="">Seleccione un proceso</option>';

    if (procesos[tipo]) {
        procesos[tipo].forEach(proceso => {
            const option = document.createElement("option");
            option.value = proceso.id;
            option.textContent = proceso.nombre;
            selectProceso.appendChild(option);
        });
    }
}

function eliminarProceso() {
    const procesoId = document.getElementById("proceso-select").value;
    if (!procesoId) {
        alert("Seleccione un proceso para eliminar.");
        return;
    }

    fetch(`/procesos/${procesoId}/eliminar/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Error en la eliminación del proceso.");
        }

        // 🔹 Manejo especial para respuestas 204 No Content
        if (response.status === 204) {
            alert("Proceso eliminado correctamente.");
            location.reload();  // ✅ Recargar la página tras cerrar la alerta
            return;
        }

        // 🔹 Si la respuesta es JSON, la procesamos, sino mostramos mensaje
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            return response.json();
        } else {
            alert("Proceso eliminado correctamente.");
            location.reload();  // ✅ Recargar la página tras cerrar la alerta
            return;
        }
    })
    .then(data => {
        if (data && data.status === "success") {
            alert("Proceso eliminado correctamente.");
            location.reload();
        } else if (data) {
            alert("Error: " + data.message);
        }
    })
    .catch(error => {
        alert("Error al conectar con el servidor. Inténtalo nuevamente.");
        console.error("Error al eliminar:", error);
    });
}


// ✅ Evento para actualizar el select de procesos dinámicamente
document.addEventListener("DOMContentLoaded", function () {
    const selectTipo = document.getElementById("tipo-proceso");
    if (selectTipo) {
        selectTipo.addEventListener("change", function () {
            cargarProcesos(this.value);
        });
    }
});
