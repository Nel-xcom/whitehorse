function togglePassword(fieldId) {
    const passwordField = document.getElementById(fieldId);
    const icon = document.getElementById('togglePasswordIcon_' + fieldId);
    if (passwordField.type === 'password') {
        passwordField.type = 'text';
        icon.src = '/static/images/eye-open.png';  // Cambia a ojo abierto
    } else {
        passwordField.type = 'password';
        icon.src = '/static/images/eye-closed.png';  // Cambia a ojo cerrado
    }
}
