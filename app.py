from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///IZIWORK-BDD.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '123456789'  # N'oubliez pas de mettre une clé secrète sécurisée

db = SQLAlchemy(app)

# Initialisation de flask-login
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Nom de la fonction de connexion

# Modèles
class User(UserMixin, db.Model):
    __tablename__ = 'USERS'
    id = db.Column('ID', db.Integer, primary_key=True)
    email = db.Column('Adresse_mail', db.String(255), unique=True, nullable=False)
    password = db.Column('Password', db.String(255), nullable=False)
    nom = db.Column('Nom', db.String(255), nullable=False)
    prenom = db.Column('Prenom', db.String(255), nullable=False)
    photo = db.Column('Photo_de_profil', db.String(255))
    telephone = db.Column('Numero_telephone', db.String(20))
    naissance = db.Column('Date_naissance', db.Date, nullable=False)
    fonction = db.Column('Fonction', db.String(255))
    
    adresse = db.relationship('AdressePostale', backref='user', uselist=False)
    historique = db.relationship('Historique', backref='user')
    disponibilites = db.relationship('Disponibilite', backref='user')
    indisponibilites = db.relationship('Indisponibilite', backref='user')

class AdressePostale(db.Model):
    __tablename__ = 'AdressePostale'
    id = db.Column('ID', db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column('User_ID', db.Integer, db.ForeignKey('USERS.ID'), unique=True, nullable=False)
    rue = db.Column('Rue', db.String(255), nullable=False)
    code_postal = db.Column('Code_postal', db.String(20), nullable=False)
    ville = db.Column('Ville', db.String(255), nullable=False)
    pays = db.Column('Pays', db.String(255), nullable=False)

class Historique(db.Model):
    __tablename__ = 'Historique'
    id = db.Column('ID', db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column('User_ID', db.Integer, db.ForeignKey('USERS.ID'), nullable=False)
    hotel_id = db.Column('Hotel_ID', db.Integer, db.ForeignKey('Dictionnaire.ID'), nullable=False)
    date = db.Column('Date', db.Date, nullable=False)
    debut = db.Column('Horaire_debut', db.Time, nullable=False)
    fin = db.Column('Horaire_fin', db.Time, nullable=False)

class Dictionnaire(db.Model):
    __tablename__ = 'Dictionnaire'
    id = db.Column('ID', db.Integer, primary_key=True)
    nom = db.Column('NOM', db.String(255), nullable=False)

class Disponibilite(db.Model):
    __tablename__ = 'Disponibilite'
    id = db.Column('ID', db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column('User_ID', db.Integer, db.ForeignKey('USERS.ID'), nullable=False)
    date_debut = db.Column('Date_debut', db.Date, nullable=False)
    date_fin = db.Column('Date_fin', db.Date, nullable=False)
    horaire_debut = db.Column('Horaire_debut', db.Time, nullable=False)
    horaire_fin = db.Column('Horaire_fin', db.Time, nullable=False)

class Indisponibilite(db.Model):
    __tablename__ = 'Indisponibilite'
    id = db.Column('ID', db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column('User_ID', db.Integer, db.ForeignKey('USERS.ID'), nullable=False)
    date_debut = db.Column('Date_debut', db.Date, nullable=False)
    date_fin = db.Column('Date_fin', db.Date, nullable=False)
    horaire_debut = db.Column('Horaire_debut', db.Time, nullable=False)
    horaire_fin = db.Column('Horaire_fin', db.Time, nullable=False)

with app.app_context():
    db.create_all()

# Fonction pour charger un utilisateur
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Pour la connexion via formulaire (cf. templates/login/connexion.html)
        email = request.form.get('email')  # Assurez-vous que le champ HTML s'appelle 'email'
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('compte'))
        else:
            flash("Identifiants invalides")
            return render_template('login/connexion.html')
    return render_template('login/connexion.html')

# Route de déconnexion
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Exemple de route protégée
@app.route('/users', methods=['GET'])
@login_required
def get_all_users():
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            'id': user.id,
            'email': user.email,
            'nom': user.nom,
            'prenom': user.prenom,
            'photo': user.photo,
            'telephone': user.telephone,
            'naissance': user.naissance.isoformat() if user.naissance else None,
            'fonction': user.fonction
        })
    return jsonify(result)



@app.route('/ajouter', methods=['POST'])
def ajouter():
    from werkzeug.security import generate_password_hash

    # Récupération des valeurs du formulaire
    nom = request.form.get('nom')
    prenom = request.form.get('prenom')
    email = request.form.get('email')
    phone = request.form.get('phone')
    street = request.form.get('street')
    postal = request.form.get('postal-code')
    city = request.form.get('city')
    fonction = request.form.get('fonction')
    date_ajout = request.form.get('date-ajout')
    siret = request.form.get('siret')
    
    new_password = request.form.get('new-password')
    confirm_password = request.form.get('confirm-password')
    
    # Vérification des champs obligatoires
    if not (nom and prenom and email and new_password):
        return "Tous les champs obligatoires ne sont pas remplis", 400
    if new_password != confirm_password:
        return "Les mots de passe ne correspondent pas", 400
    
    # Hash du mot de passe
    hashed_password = generate_password_hash(new_password)
    
    # Utilisation de la date fournie ou d'une valeur par défaut et conversion en objet date
    if not date_ajout:
        date_ajout = '2000-01-01'
    try:
        date_naissance = datetime.strptime(date_ajout, "%Y-%m-%d").date()
    except ValueError:
        return "Format de date invalide", 400
        
    # Création du nouvel utilisateur
    new_user = User(
        nom=nom,
        prenom=prenom,
        email=email,
        password=hashed_password,
        telephone=phone,
        naissance=date_naissance,
        fonction=fonction,
        photo=""
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    # Ajout de l'adresse si les informations sont fournies
    if street and postal and city:
        new_address = AdressePostale(
            user_id=new_user.id,
            rue=street,
            code_postal=postal,
            ville=city,
            pays="France"  # Valeur par défaut
        )
        db.session.add(new_address)
        db.session.commit()
    
    return "Utilisateur ajouté", 201


@app.route('/')
@login_required
def compte():
    user = current_user
    adresse = AdressePostale.query.filter_by(user_id=user.id).first()
    
    return render_template('compte/compte.html', user=user, adresse=adresse)

@app.route('/api/test')
def test_api():
    return jsonify(User.query.all())

@app.route('/admin/ajout/prestataires', methods=['GET', 'POST'])
@login_required
def presta():
    if request.method == 'POST':
        from werkzeug.security import generate_password_hash

        # Récupération des valeurs du formulaire
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        email = request.form.get('email')
        phone = request.form.get('phone')
        street = request.form.get('street')
        postal = request.form.get('postal-code')
        city = request.form.get('city')
        fonction = request.form.get('fonction')
        date_ajout = request.form.get('date-ajout')
        siret = request.form.get('siret')
        new_password = request.form.get('new-password')
        confirm_password = request.form.get('confirm-password')
        
        # Vérification des champs obligatoires
        if not (nom and prenom and email and new_password):
            flash("Tous les champs obligatoires ne sont pas remplis", "error")
            return render_template('admin_ajout_prestataire/ajout_prestataire.html', form_data=request.form), 400
        if new_password != confirm_password:
            flash("Les mots de passe ne correspondent pas", "error")
            return render_template('admin_ajout_prestataire/ajout_prestataire.html', form_data=request.form), 400

        # Vérification du conflit d'email
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Un utilisateur avec cet email existe déjà", "error")
            return render_template('admin_ajout_prestataire/ajout_prestataire.html', form_data=request.form), 400
        
        # Hash du mot de passe
        hashed_password = generate_password_hash(new_password)
        
        # Conversion de la date ou valeur par défaut
        if not date_ajout:
            date_ajout = '2000-01-01'
        try:
            date_naissance = datetime.strptime(date_ajout, "%Y-%m-%d").date()
        except ValueError:
            flash("Format de date invalide", "error")
            return render_template('admin_ajout_prestataire/ajout_prestataire.html', form_data=request.form), 400
            
        # Création du nouvel utilisateur
        new_user = User(
            nom=nom,
            prenom=prenom,
            email=email,
            password=hashed_password,
            telephone=phone,
            naissance=date_naissance,
            fonction=fonction,
            photo=""
        )
        db.session.add(new_user)
        db.session.commit()
        
        # Ajout de l'adresse si fournie
        if street and postal and city:
            new_address = AdressePostale(
                user_id=new_user.id,
                rue=street,
                code_postal=postal,
                ville=city,
                pays="France"
            )
            db.session.add(new_address)
            db.session.commit()
        
        flash("Utilisateur ajouté", "success")
        users = User.query.all()
        return render_template('liste_presta/liste_presta.html', users=users), 201

    # Pour le GET, on peut envoyer un dictionnaire vide
    return render_template('admin_ajout_prestataire/ajout_prestataire.html', form_data={})

@app.route('/prestataires', methods=['GET', 'DELETE'])
@login_required
def prestataires():
    if request.method == 'DELETE':
        data = request.get_json()
        user_id = data.get("id")
        if not user_id:
            return jsonify({"error": "ID manquant"}), 400
        
        user_to_delete = User.query.get(user_id)
        if not user_to_delete:
            return jsonify({"error": "Utilisateur non trouvé"}), 404

        # Supprimer l'adresse liée
        adresse = AdressePostale.query.filter_by(user_id=user_id).first()
        if adresse:
            db.session.delete(adresse)
        
        # Supprimer les historiques liés
        historiques = Historique.query.filter_by(user_id=user_id).all()
        for hist in historiques:
            db.session.delete(hist)
        
        # Supprimer les disponibilités liées
        disponibilites = Disponibilite.query.filter_by(user_id=user_id).all()
        for dispo in disponibilites:
            db.session.delete(dispo)
        
        # Supprimer les indisponibilités liées
        indisponibilites = Indisponibilite.query.filter_by(user_id=user_id).all()
        for indispo in indisponibilites:
            db.session.delete(indispo)
        
        # Supprimer l'utilisateur
        db.session.delete(user_to_delete)
        db.session.commit()
        return jsonify({"message": "Utilisateur et toutes ses relations supprimés"}), 200

    # Méthode GET : afficher la liste des prestataires
    users = User.query.all()  # Récupération des utilisateurs depuis la base de données
    return render_template('liste_presta/liste_presta.html', users=users)

# @app.route('/compte')
# @login_required
# def compte():
#     return render_template('adminCompte/compte.html')

@app.route('/modify/password', methods=['GET', 'POST'])
@login_required
def forgotPassword():
    if request.method == 'POST':
        from werkzeug.security import generate_password_hash

        # Récupération des valeurs du formulaire
        old_password = request.form.get('old-password')
        new_password = request.form.get('new-password')
        confirm_password = request.form.get('confirm-password')
        
        # Vérification des champs obligatoires
        if not new_password:
            return "Tous les champs obligatoires ne sont pas remplis", 400
        if new_password != confirm_password:
            return "Les mots de passe ne correspondent pas", 400
        
        # Hash du mot de passe
        hashed_password = generate_password_hash(new_password)
        
        # Modification du mot de passe
        user = current_user
        user.password = hashed_password
        db.session.commit()
        
        return "Mot de passe modifié", 201
        
    
    return render_template('modify/password.html')

@app.route('/modify/email', methods=['GET', 'POST'])
@login_required
def forgotEmail():
    if request.method == 'POST':
        from werkzeug.security import generate_password_hash

        # Récupération des valeurs du formulaire
        old_email = request.form.get('old-email')
        new_email = request.form.get('new-email')
        confirm_email = request.form.get('confirm-email')
        
        # Vérification des champs obligatoires
        if not new_email:
            return "Tous les champs obligatoires ne sont pas remplis", 400
        if new_email != confirm_email:
            return "Les 2 adresses e-mails ne correspondent pas", 400
        
        
        # Modification du mot de passe
        user = current_user
        user.email = new_email
        db.session.commit()
        
        return "E-mail modifié", 201
        
    
    return render_template('modify/email.html')



if __name__ == '__main__':
    app.run(debug=True)