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

function supprimer(id) {
    if (confirm("Voulez-vous vraiment supprimer cet utilisateur ?")) {
        fetch(`/supprimer/${id}`, { method: "DELETE" })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                location.reload();
            });
    }
}
