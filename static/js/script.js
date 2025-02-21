document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.querySelector(".sidebar");
    const toggleBtn = document.querySelector(".toggle-btn");
    const sidebarNav = document.querySelector(".sidebar-nav");
    const sidebarFooter = document.querySelector(".sidebar-footer");
    let pinned = false;  // false = non épinglé (comportement hover actif)

    // Fonction pour afficher la sidebar (texte visible)
    function showSidebar() {
        sidebar.style.width = '260px';
        sidebarNav.style.display = "flex";
        sidebarFooter.style.display = "block";
    }

    // Fonction pour cacher la sidebar (texte masqué)
    function hideSidebar() {
        sidebar.style.width = '25px';
        sidebarNav.style.display = "none";
        sidebarFooter.style.display = "none";
    }

    // Lors du clic sur le toggle, on bascule l'état épinglé
    toggleBtn.addEventListener("click", function () {
        pinned = !pinned;
        if (pinned) {
            showSidebar();
        } else {
            hideSidebar();
        }
    });

    // Au survol, si non épinglé, la sidebar s'agrandit et affiche les textes
    sidebar.addEventListener("mouseenter", function () {
        if (!pinned) {
            showSidebar();
        }
    });

    // Quand la souris sort, si non épinglé, la sidebar se rétracte et masque les textes
    sidebar.addEventListener("mouseleave", function () {
        if (!pinned) {
            hideSidebar();
        }
    });

    // Initialisation de l'état (sidebar rétractée avec texte masqué)
    hideSidebar();

    const alerts = document.querySelectorAll('.alert');
        
    alerts.forEach(alert => {
        // Auto-fermeture après 5 secondes
        const timer = setTimeout(() => {
            alert.classList.add('closing');
            setTimeout(() => alert.remove(), 300); // Correspond à la durée de l'animation
        }, 3000);

        // Fermeture manuelle
        alert.querySelector('.close').addEventListener('click', () => {
            clearTimeout(timer); // Annule l'auto-fermeture
            alert.classList.add('closing');
            setTimeout(() => alert.remove(), 300);
        });
    });
});