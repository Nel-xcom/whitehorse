document.addEventListener("DOMContentLoaded", function () {
    const textElement = document.getElementById("typewriter-text");
    const text = textElement.textContent.trim(); // Obtener el texto original
    textElement.textContent = ""; // Limpiar el texto antes de empezar

    let index = 0;
    function typeWriter() {
        if (index < text.length) {
            textElement.textContent += text.charAt(index);
            index++;
            setTimeout(typeWriter, 20); // Velocidad de la animación
        } else {
            textElement.style.borderRight = "none"; // Quitar cursor al final
        }
    }

    setTimeout(typeWriter, 500); // Retraso inicial antes de iniciar
});
