document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".action-btn").forEach(button => {
        button.addEventListener("click", function (event) {
            let dropdown = event.target.nextElementSibling;
            dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
        });
    });
});

function modifier(id) {
    window.location.href = "/admin/modify/prestataires?id=" + id;
}

// Variable pour stocker l'ID de l'utilisateur à supprimer
var userIdToDelete = null;

// Cette fonction est appelée lors du clic sur le bouton "Supprimer" de chaque utilisateur
function supprimer(id, nom, prenom) {
    userIdToDelete = id;
    // Mettre à jour le texte du modal si vous avez récupéré le nom de l'utilisateur, par exemple via un data-attribute
    document.getElementById("modalText").textContent = "Suppression de " + nom + " " + prenom;
    document.getElementById("confirmModal").style.display = "block";
}

// Ferme la modal sans action
function closeModal() {
    document.getElementById("confirmModal").style.display = "none";
    userIdToDelete = null;
}

// Confirme la suppression et envoie une requête DELETE à la route /prestataire
function confirmDelete() {
    fetch("/admin/prestataires", {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ id: userIdToDelete })
    })
    .then(response => {
        if (response.ok) {
            // Rediriger vers /prestataire en cas de succès
            window.location.href = "/admin/prestataires";
        } else {
            alert("Erreur lors de la suppression");
        }
    })
    .catch(error => {
        console.error("Erreur:", error);
        alert("Erreur lors de la suppression");
    });
}