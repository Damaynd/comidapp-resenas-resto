
// Definimos método que se ejecute al cargar al DOM
document.addEventListener('DOMContentLoaded', function() {

    // Definimos las funciones y las adjuntamos al objeto window 
    // para poder usarlas en el HTML (onclick="openModal()")

    // Para abrir Modal
    window.openModal = function() {
        const modal = document.getElementById('reviewModal');
        if (modal) {
            modal.style.display = 'flex';
        }
    };
    // Para cerrar Modal
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