from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///IZIWORK-BDD.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

# Modèles
class User(db.Model):
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

# Routes
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    
    if user and check_password_hash(user.password, data.get('password')):
        return jsonify({
            'id': user.id,
            'email': user.email,
            'nom': user.nom,
            'prenom': user.prenom
        }), 200
    
    return jsonify({'message': 'Identifiants invalides'}), 401

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

@app.route('/api/test')
def test_api():
    return jsonify(User.query.all())

@app.route('/presta', methods=['GET', 'POST'])
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
            return "Tous les champs obligatoires ne sont pas remplis", 400
        if new_password != confirm_password:
            return "Les mots de passe ne correspondent pas", 400
        
        # Vérification des conflits : ici, on s'assure que l'email n'est pas déjà utilisé
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "Un utilisateur avec cet email existe déjà", 400
        
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

    return render_template('prestataire/presta.html')

@app.route('/users', methods=['GET'])
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

if __name__ == '__main__':
    app.run(debug=True)