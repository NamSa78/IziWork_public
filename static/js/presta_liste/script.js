document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".action-btn").forEach(button => {
        button.addEventListener("click", function (event) {
            let dropdown = event.target.nextElementSibling;
            dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
        });
    });
});

function modifier(id) {
    alert("Modifier l'utilisateur " + id);
}




// Variable pour stocker l'ID de l'utilisateur à supprimer
var userIdToDelete = null;

// Cette fonction est appelée lors du clic sur le bouton "Supprimer" de chaque utilisateur
function supprimer(id) {
    userIdToDelete = id;
    document.getElementById("confirmModal").style.display = "block";
}

// Ferme la modal sans action
function closeModal() {
    document.getElementById("confirmModal").style.display = "none";
    userIdToDelete = null;
}

// Confirme la suppression et redirige vers une route de suppression
function confirmDelete() {
    // Vous pourrez ensuite créer la route Flask /delete_user/<id> pour réaliser la suppression
    window.location.href = "/delete_user/" + userIdToDelete;
}