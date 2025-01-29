document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Ici, vous pouvez ajouter la logique pour vérifier les identifiants
    console.log('Identifiant:', username);
    console.log('Mot de passe:', password);

    // Exemple de redirection après connexion réussie
    // window.location.href = 'espace-personnel.html';
});

window.addEventListener('resize', positionIcon);
window.addEventListener('load', positionIcon);

function positionIcon() {
    const icon = document.querySelector('.icone');
    const footerBackground = document.querySelector('.footer-background');
    const footerRect = footerBackground.getBoundingClientRect();
    icon.style.bottom = `${window.innerHeight - footerRect.top}px`; // Adjusted to be 20px lower
}