from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///IZIWORK-BDD.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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
    
    nom = request.form.get('nom')
    email = request.form.get('email')
    password = request.form.get('password')

    if not (nom and email and password):
        return "Tous les champs sont requis", 400
    
    # Hash le mot de passe avant de le stocker
    hashed_password = generate_password_hash(password)
    
    # Crée un nouvel utilisateur (à adapter selon votre modèle)
    new_user = User(
        nom=nom,
        prenom='',  # à compléter si nécessaire
        email=email,
        password=hashed_password,
        naissance='2000-01-01'  # exemple, à adapter
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return "Utilisateur ajouté", 201

@app.route('/api/test')
def test_api():
    return jsonify({'status': 'API fonctionnelle'})

if __name__ == '__main__':
    app.run(debug=True)