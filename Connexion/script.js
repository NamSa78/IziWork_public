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