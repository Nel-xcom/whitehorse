// flujos_trabajo.js

let currentStep = 0;
const steps = document.querySelectorAll('.progress-bar .step');
const formSteps = document.querySelectorAll('.form-step');
let tareasSeleccionadas = [];
let sectoresRenderizados = {};

// flujos_trabajo.js

document.addEventListener("DOMContentLoaded", function () {
    const btnMostrarFormulario = document.getElementById('btnMostrarFormulario');
    const formContainer = document.getElementById('form-flujo');
    const selectSector = document.getElementById('select-sector');

    // Mostrar formulario al hacer clic en el botón
    btnMostrarFormulario.addEventListener('click', function () {
        formContainer.classList.remove('hidden');
    });

    // Obtener tareas cuando se selecciona un sector
    selectSector.addEventListener('change', function () {
        const sectorId = this.value;
        const sectorNombre = this.options[this.selectedIndex].text;

        if (sectorId && !sectoresRenderizados[sectorId]) {
            fetch(`/api/tareas/?sector=${sectorId}`)
                .then(response => response.json())
                .then(data => {
                    renderizarSector(sectorId, sectorNombre, data);
                    sectoresRenderizados[sectorId] = true; // Evita duplicados
                });
        }
    });
});



function updateProgress(step) {
    steps.forEach((s, index) => {
        s.classList.remove('active');
        if (index <= step) s.classList.add('active');
    });

    formSteps.forEach((f, index) => {
        f.classList.add('hidden');
        if (index === step) f.classList.remove('hidden');
    });

    currentStep = step;
}

function nextStep() {
    if (currentStep < steps.length - 1) {
        updateProgress(currentStep + 1);
        
        if (currentStep === 2) { // Paso 3: Asignar Responsables
            mostrarResponsables();
        }

        if (currentStep === 3) {
            console.log("👉 Renderizando las tareas en el paso 4...");
            mostrarOrdenTareas();
        }
    }
}



// flujos_trabajo.js

document.addEventListener("DOMContentLoaded", function () {
    const selectSector = document.getElementById('select-sector');
    selectSector.addEventListener('change', function () {
        const sectorId = this.value;
        if (sectorId) {
            fetch(`/api/tareas/?sector=${sectorId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Error HTTP: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    renderizarSector(sectorId, data);
                })
                .catch(error => {
                    console.error('Error al cargar tareas:', error);
                });
        }
    });
});

function renderizarSector(sectorId, sectorNombre, tareas) {
    const container = document.getElementById('sectores-tareas-container');
    const sectorContainer = document.createElement('div');
    sectorContainer.classList.add('sector-container');
    sectorContainer.id = `sector-${sectorId}`;

    // ✅ Verificar si tareas está definida y no es null
    if (Array.isArray(tareas) && tareas.length > 0) {
        sectorContainer.innerHTML = `
            <h4>${sectorNombre}</h4>
            ${tareas.map(t => `
                <label>
                    <input type="checkbox" value="${t.id}" data-nombre="${t.nombre}" 
                           data-responsable-id="${t.responsable__id || ''}" 
                           data-responsable-nombre="${t.responsable__username || ''}" 
                           onchange="seleccionarTarea(this)">
                    ${t.nombre} - Responsable: ${t.responsable__username || 'Sin asignar'}
                </label>`).join('')}
        `;
    } else {
        // ✅ Mostrar un mensaje si no hay tareas para ese sector
        sectorContainer.innerHTML = `
            <p>No hay tareas disponibles para este sector.</p>
        `;
    }

    container.appendChild(sectorContainer);
}





function seleccionarTarea(checkbox) {
    const tareaId = checkbox.value;
    const tareaNombre = checkbox.getAttribute('data-nombre');
    let responsableId = checkbox.getAttribute('data-responsable-id');
    let responsableNombre = checkbox.getAttribute('data-responsable-nombre');

    // Si el valor de responsable es 'undefined' o vacío, lo seteamos a null
    if (!responsableId || responsableId === 'undefined' || responsableId.trim() === '') {
        responsableId = null;
        responsableNombre = "Sin asignar";  // Mostramos un texto amigable
    }

    if (checkbox.checked) {
        tareasSeleccionadas.push({
            id: tareaId,
            nombre: tareaNombre,
            responsableId: responsableId,  // Puede ser null sin problema
            responsableNombre: responsableNombre
        });
    } else {
        tareasSeleccionadas = tareasSeleccionadas.filter(t => t.id !== tareaId);
    }

    actualizarListaTareasSeleccionadas();
}



function actualizarListaTareasSeleccionadas() {
    const lista = document.getElementById('lista-tareas-seleccionadas');
    lista.innerHTML = tareasSeleccionadas.map(t => `
        <li>${t.nombre} <button onclick="eliminarTarea('${t.id}')"><i class="fas fa-trash-alt"></i></button></li>`).join('');

    // Habilitar el botón "Continuar" si hay tareas seleccionadas
    document.getElementById('btnContinuar').disabled = tareasSeleccionadas.length === 0;
}

function eliminarTarea(tareaId) {
    tareasSeleccionadas = tareasSeleccionadas.filter(t => t.id !== tareaId);

    // Desmarcar el checkbox correspondiente
    const checkbox = document.querySelector(`input[type="checkbox"][value="${tareaId}"]`);
    if (checkbox) checkbox.checked = false;

    actualizarListaTareasSeleccionadas();
}


function mostrarResponsables() {
    const container = document.getElementById('asignar-responsables');
    container.innerHTML = '';

    tareasSeleccionadas.forEach(tarea => {
        const selectResponsable = document.createElement('select');
        selectResponsable.setAttribute('data-tarea-id', tarea.id);

        fetch(`/api/usuarios_por_tarea/?tarea_id=${tarea.id}`)
            .then(response => response.json())
            .then(usuarios => {
                selectResponsable.innerHTML = usuarios.map(user => `
                    <option value="${user.id}" ${user.id == tarea.responsableId ? 'selected' : ''}>
                        ${user.username}
                    </option>
                `).join('');

                // ✅ Asignar valor correcto al seleccionar un responsable
                selectResponsable.addEventListener('change', function () {
                    let tareaSeleccionada = tareasSeleccionadas.find(t => t.id === tarea.id);

                    if (tareaSeleccionada) {
                        tareaSeleccionada.responsableId = this.value !== 'undefined' ? this.value : null;
                        tareaSeleccionada.responsableNombre = this.options[this.selectedIndex].text;
                    } else {
                        console.warn(`❌ No se encontró la tarea con ID ${tarea.id} en tareasSeleccionadas.`);
                    }
                });

                const label = document.createElement('label');
                label.innerText = `Responsable para ${tarea.nombre}: `;

                container.appendChild(label);
                container.appendChild(selectResponsable);
                container.appendChild(document.createElement('br'));
            });
    });
}

function guardarFlujo() {
    const nombre = document.getElementById('nombre-flujo').value;
    const sector = document.getElementById('select-sector').value;

    // ✅ Validación: Cada tarea debe tener un responsable asignado
    for (const tarea of tareasSeleccionadas) {
        if (tarea.responsableId === 'undefined') {
            tarea.responsableId = null;  //
        }
    }
    

    const tareasData = tareasSeleccionadas.map((tarea, index) => ({
        tarea_id: tarea.id,
        responsable_id: tarea.responsableId && tarea.responsableId !== 'undefined' 
                        ? tarea.responsableId 
                        : null,  // <- Permite null sin alertas
        orden: index + 1
    }));    

    const payload = {
        nombre: nombre,
        sector: sector,
        tareas: tareasData
    };

    console.log("Contenido de tareasSeleccionadas:", tareasSeleccionadas);
    console.log("Payload enviado:", JSON.stringify(payload, null, 2));

    fetch('/flujos_trabajo/guardar/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ Flujo guardado exitosamente');
            window.location.href = '/flujos_trabajo/proceso';
        } else {
            alert(`❌ Error: ${data.message}`);
        }
    });
}




function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

document.addEventListener("DOMContentLoaded", function () {
    if (currentStep === 3) {
        mostrarOrdenTareas();
    }
});

// ✅ Mostrar las tareas seleccionadas para ordenarlas
function mostrarOrdenTareas() {
    const container = document.getElementById('ordenar-tareas');
    container.innerHTML = ''; // Limpiar contenido anterior

    if (tareasSeleccionadas.length === 0) {
        container.innerHTML = '<p>No hay tareas seleccionadas para ordenar.</p>';
        return;
    }

    tareasSeleccionadas.forEach((tarea, index) => {
        const item = document.createElement('div');
        item.classList.add('sortable-item');
        item.setAttribute('data-id', tarea.id);
        item.setAttribute('draggable', true);
        item.innerHTML = `
            <span class="drag-handle">☰</span>
            <span class="orden-numero">${index + 1}.</span>
            <span>${tarea.nombre} - Responsable: ${tarea.responsableNombre || 'Sin asignar'}</span>
        `;

        // Eventos Drag and Drop
        item.addEventListener('dragstart', dragStart);
        item.addEventListener('dragover', dragOver);
        item.addEventListener('drop', drop);
        item.addEventListener('dragend', dragEnd);

        container.appendChild(item);
    });

    actualizarOrdenTareas(); // Asegura que los números de orden se actualicen
}



// ✅ Funciones Drag and Drop
let draggedItem = null;

function dragStart(e) {
    draggedItem = this;
    setTimeout(() => this.classList.add('dragging'), 0);
}

function dragOver(e) {
    e.preventDefault();
    const container = document.getElementById('ordenar-tareas');
    const afterElement = getDragAfterElement(container, e.clientY);
    if (afterElement == null) {
        container.appendChild(draggedItem);
    } else {
        container.insertBefore(draggedItem, afterElement);
    }
}

function drop() {
    this.classList.remove('dragging');
    actualizarOrdenTareas(); // ✅ Se actualiza la numeración después de mover una tarea
}

function dragEnd() {
    draggedItem.classList.remove('dragging');
    actualizarOrdenTareas(); // ✅ Se actualiza la numeración después de soltar
}


// ✅ Función para obtener el elemento debajo del arrastre
function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.sortable-item:not(.dragging)')];
    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        return offset < 0 && offset > closest.offset ? { offset: offset, element: child } : closest;
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

// ✅ Actualizar el orden de las tareas en el array y los números visuales
function actualizarOrdenTareas() {
    const items = document.querySelectorAll('.sortable-item');
    
    tareasSeleccionadas = Array.from(items).map((item, index) => {
        const id = item.getAttribute('data-id');
        const tarea = tareasSeleccionadas.find(t => t.id === id);
        tarea.orden = index + 1; // Ajustar número dinámico

        // ✅ Actualizar el número de orden en la UI
        const ordenNumero = item.querySelector('.orden-numero');
        if (ordenNumero) ordenNumero.textContent = `${index + 1}.`;

        return tarea;
    });
}


// ✅ Guardar el orden de las tareas
function guardarOrden() {
    actualizarOrdenTareas();
    alert('Orden guardado exitosamente: ');
}
