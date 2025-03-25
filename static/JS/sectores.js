document.addEventListener("DOMContentLoaded", () => {
    const sectorCheckboxes = document.querySelectorAll('input[name="sector_ids"]');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    sectorCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            const sectorId = checkbox.value;
            const action = checkbox.checked ? 'add' : 'remove';

            fetch('/actualizar_sectores/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({ sector_id: sectorId, action: action }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert(`Sector ${data.action} exitosamente.`);
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});
