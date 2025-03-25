document.querySelector('.an-menu').addEventListener('click', function() {
    const menu = document.querySelector('.menu');
    menu.classList.toggle('active'); // Activa y desactiva el menú lateral
});

// Funcionalidad para cerrar el menú con la 'x'
document.querySelector('.close-menu').addEventListener('click', function() {
    const menu = document.querySelector('.menu');
    menu.classList.remove('active');
});
