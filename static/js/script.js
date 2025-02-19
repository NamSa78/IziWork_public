
document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.querySelector(".sidebar");
    const toggleBtn = document.querySelector(".toggle-btn");

    toggleBtn.addEventListener("click", function () {
        sidebar.classList.toggle("collapsed");
        toggleSidebar();
    });
});

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar.classList.contains('collapsed')) {
        sidebar.style.width = '1%';
    } else {
        sidebar.style.width = '12%';
    }
}       