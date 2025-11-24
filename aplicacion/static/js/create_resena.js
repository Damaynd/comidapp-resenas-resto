// static/js/create_resena.js

document.addEventListener('DOMContentLoaded', function() {
    // Definimos las funciones y las adjuntamos al objeto window 
    // para poder usarlas en el HTML (onclick="openModal()")
    
    window.openModal = function() {
        const modal = document.getElementById('reviewModal');
        if (modal) {
            modal.style.display = 'flex';
        }
    };

    window.closeModal = function() {
        const modal = document.getElementById('reviewModal');
        if (modal) {
            modal.style.display = 'none';
        }
    };

    // Cerrar si se hace click fuera del contenido (en el fondo oscuro)
    const modal = document.getElementById('reviewModal');
    if (modal) {
        window.onclick = function(event) {
            if (event.target == modal) {
                window.closeModal();
            }
        };
    }
});