document.addEventListener("DOMContentLoaded", function () {
    const ctxProductividad = document.getElementById("productividad-chart").getContext("2d");
    const ctxActividadSemanal = document.getElementById("actividad-semanal-chart").getContext("2d");

    // Gráfico de Productividad
    new Chart(ctxProductividad, {
        type: 'doughnut',
        data: {
            labels: ['Informatica', 'Comercial', 'Marketing'],
            datasets: [{
                data: [65, 25, 10],
                backgroundColor: ['#28a745', '#ffc107', '#dc3545'],
            }]
        }
    });

    // Gráfico de Actividad Semanal
    new Chart(ctxActividadSemanal, {
        type: 'line',
        data: {
            labels: ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'],
            datasets: [{
                label: 'Tareas Completadas',
                data: [10, 15, 20, 15, 25],
                borderColor: '#4070B7',
                fill: true,
                backgroundColor: 'rgba(64, 112, 183, 0.1)'
            }]
        }
    });
});
