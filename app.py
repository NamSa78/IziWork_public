from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import select
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from functools import wraps
from flask import abort
from datetime import time, date
from sqlalchemy import and_
from enum import Enum
from flask_mail import Mail, Message


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///IZIWORK-BDD.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '123456789'  # N'oubliez pas de mettre une clé secrète sécurisée

db = SQLAlchemy(app)

# Configuration de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Remplacez par votre serveur SMTP
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'nathan.linet2304@gmail.com'  # Remplacez par votre e-mail
app.config['MAIL_PASSWORD'] = 'kyjo nevb tcom njau'  # Remplacez par votre mot de passe
app.config['MAIL_DEFAULT_SENDER'] = 'nathan.linet2304@gmail.com'  # Remplacez par votre e-mail

mail = Mail(app)


# Créer un décorateur personnalisé pour les admins
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)  # Accès interdit
        return f(*args, **kwargs)
    return decorated_function

# Initialisation de flask-login
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Nom de la fonction de connexion

class UserRole(Enum):
    USER = 'user'
    ADMIN = 'admin'

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
    siret = db.Column('SIRET', db.String(14), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin' ou 'user'

    
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

class Shift(db.Model):
    __tablename__ = 'Shift'
    id = db.Column('ID', db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column('User_ID', db.Integer, db.ForeignKey('USERS.ID'), nullable=False)
    date_debut = db.Column('Date_debut', db.Date, nullable=False)
    date_fin = db.Column('Date_fin', db.Date, nullable=False)
    horaire_debut = db.Column('Horaire_debut', db.Time, nullable=False)
    horaire_fin = db.Column('Horaire_fin', db.Time, nullable=False)
    hotel = db.Column('Hotel', db.String(255), nullable=False)
    adresse_hotel = db.Column('Adresse_hotel', db.String(255), nullable=False)
    fonction = db.Column('Fonction', db.String(255), nullable=False)

with app.app_context():
    db.create_all()
    

@app.route('/admin/ajout/hotels', methods=['GET'])
@login_required
@admin_required
def ajout_hotel():
    hotel = Dictionnaire(nom="Novotel Paris coeur d'orly")
    db.session.add(hotel)
    hotel = Dictionnaire(nom="Ibis Paris coeur d'orly")
    db.session.add(hotel)
    hotel = Dictionnaire(nom="Novotel Evry")
    db.session.add(hotel)
    db.session.commit()
    return jsonify({"message": "Hotels added successfully"}), 201

# Fonction pour charger un utilisateur
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Route de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Pour la connexion via formulaire (cf. templates/login/connexion.html)
        email = request.form.get('email')  # Assurez-vous que le champ HTML s'appelle 'email'
        password = request.form.get('password')
        user = db.session.scalars(select(User).where(User.email == email)).first()
        
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
    users = db.session.scalars(select(User)).all()
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


@app.route('/admin/modify/prestataires', methods=['GET', 'POST'])
@login_required
@admin_required
def modifier():
    if request.method == 'GET':
        user_id = request.args.get('id')
        if not user_id:
            flash("Aucun utilisateur spécifié", "error")
            return redirect(url_for('compte'))
        
        user = db.session.get(User, int(user_id))
        if not user:
            flash("Utilisateur non trouvé", "error")
            return redirect(url_for('compte'))

        # Préparation des données initiales
        form_data = {
            'id': user.id,
            'nom': user.nom,
            'prenom': user.prenom,
            'email': user.email,
            'phone': user.telephone,
            'fonction': user.fonction,
            'date-ajout': user.naissance.strftime("%Y-%m-%d") if user.naissance else "",
            'siret': user.siret if user.siret else ""
        }

        adresse = db.session.scalars(
            select(AdressePostale).where(AdressePostale.user_id == user.id)
        ).first()
        if adresse:
            form_data.update({
                'street': adresse.rue,
                'postal-code': adresse.code_postal,
                'city': adresse.ville
            })

        return render_template('admin_modify_presta/modify_prestataires.html', form_data=form_data, UserRole=UserRole)

    elif request.method == 'POST' and request.form.get("_method"):
        user_id = request.form.get('id')
        if not user_id:
            flash("Aucun utilisateur spécifié", "error")
            return redirect(url_for('compte'))

        # Récupération de l'utilisateur à modifier
        user_to_modify = db.session.get(User, int(user_id))
        if not user_to_modify:
            flash("Utilisateur non trouvé", "error")
            return redirect(url_for('compte'))

        # Dictionnaire des modifications
        updates = {}

        # Vérification champ par champ
        fields = ['nom', 'prenom', 'email', 'phone', 'fonction', 'siret']
        for field in fields:
            new_value = request.form.get(field)
            current_value = getattr(user_to_modify, field, None)
            
            if new_value and new_value != current_value:
                updates[field] = new_value

        # Traitement spécial pour l'email
        if 'email' in updates:
            existing_user = db.session.scalars(
                select(User).where(User.email == updates['email'])
            ).first()
            if existing_user and existing_user.id != user_to_modify.id:
                flash("Email déjà utilisé", "error")
                return redirect(url_for('modifier', id=user_id))

        # Traitement spécial pour le mot de passe
        new_password = request.form.get('new-password')
        confirm_password = request.form.get('confirm-password')
        if new_password:
            if new_password != confirm_password:
                flash("Les mots de passe ne correspondent pas", "error")
                return redirect(url_for('modifier', id=user_id))
            updates['password'] = generate_password_hash(new_password)

        # Mise à jour de la date de naissance
        new_date = request.form.get('date-ajout')
        if new_date:
            try:
                updates['naissance'] = datetime.strptime(new_date, "%Y-%m-%d").date()
            except ValueError:
                flash("Format de date invalide", "error")

        # Application des modifications
        for key, value in updates.items():
            setattr(user_to_modify, key, value)

        # Gestion de l'adresse postale
        street = request.form.get('street')
        postal_code = request.form.get('postal-code')
        city = request.form.get('city')

        adresse = db.session.scalars(
            select(AdressePostale).where(AdressePostale.user_id == user_to_modify.id)
        ).first()

        if adresse:
            # Mise à jour partielle
            if street: adresse.rue = street
            if postal_code: adresse.code_postal = postal_code
            if city: adresse.ville = city
        elif street and postal_code and city:
            # Création nouvelle adresse
            new_address = AdressePostale(
                user_id=user_to_modify.id,
                rue=street,
                code_postal=postal_code,
                ville=city,
                pays="France"
            )
            db.session.add(new_address)

        try:
            db.session.commit()
            flash("Modifications enregistrées avec succès", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de la mise à jour: {str(e)}", "error")

        # Rechargement des données fraîches depuis la BDD
        db.session.refresh(user_to_modify)
        adresse = db.session.scalars(
            select(AdressePostale).where(AdressePostale.user_id == user_to_modify.id)
        ).first()

        # Reconstruction du form_data avec les nouvelles valeurs
        new_form_data = {
            'id': user_to_modify.id,
            'nom': user_to_modify.nom,
            'prenom': user_to_modify.prenom,
            'email': user_to_modify.email,
            'phone': user_to_modify.telephone,
            'fonction': user_to_modify.fonction,
            'date-ajout': user_to_modify.naissance.strftime("%Y-%m-%d") if user_to_modify.naissance else "",
            'siret': user_to_modify.siret
        }

        if adresse:
            new_form_data.update({
                'street': adresse.rue,
                'postal-code': adresse.code_postal,
                'city': adresse.ville
            })

        return render_template('admin_modify_presta/modify_prestataires.html', form_data=new_form_data)
    
@app.route('/')
@login_required
def compte():
    user = current_user
    adresse = db.session.scalars(
        select(AdressePostale).where(AdressePostale.user_id == user.id)
    ).first()
    
    return render_template('compte/compte.html', user=user, adresse=adresse)

@app.route('/api/test')
def test_api():
    return jsonify(db.session.scalars(select(User)).all())

@app.route('/admin/ajout/prestataires', methods=['GET', 'POST'])
@login_required
@admin_required
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
        role = request.form.get('role', UserRole.USER.value)
        
        # Vérification des champs obligatoires
        if not (nom and prenom and email and new_password):
            flash("Tous les champs obligatoires ne sont pas remplis", "error")
            return render_template('admin_ajout_prestataire/ajout_prestataire.html', form_data=request.form), 400
        if new_password != confirm_password:
            flash("Les mots de passe ne correspondent pas", "error")
            return render_template('admin_ajout_prestataire/ajout_prestataire.html', form_data=request.form), 400

        # Vérification du conflit d'email
        existing_user = db.session.scalars(
            select(User).where(User.email == email)
        ).first()
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
            photo="",
            role=role,
            siret=siret
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
        users = db.session.scalars(select(User)).all()
        return render_template('liste_presta/liste_presta.html', users=users), 201

    # Pour le GET, on peut envoyer un dictionnaire vide
    return render_template('admin_ajout_prestataire/ajout_prestataire.html', form_data={}, UserRole=UserRole)

@app.route('/prestataires', methods=['GET', 'DELETE'])
@login_required
@admin_required
def prestataires():
    if request.method == 'DELETE':
        data = request.get_json()
        user_id = data.get("id")
        if not user_id:
            return jsonify({"error": "ID manquant"}), 400
        
        user_to_delete = db.session.get(User,user_id)
        if not user_to_delete:
            return jsonify({"error": "Utilisateur non trouvé"}), 404

        # Supprimer l'adresse liée
        adresse = db.session.scalars(
            select(AdressePostale).where(AdressePostale.user_id == user_id)
        ).first()
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
    users = db.session.scalars(select(User)).all()  # Récupération des utilisateurs depuis la base de données
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
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Vérification des champs obligatoires
        if not new_password:
            flash("Tous les champs obligatoires ne sont pas remplis", "error")
            return render_template('modify/password.html'), 400
        if new_password != confirm_password:
            flash("Les mots de passe ne correspondent pas", "error")
            return render_template('modify/password.html'), 400
        
        # Hash du mot de passe
        hashed_password = generate_password_hash(new_password)
        
        # Modification du mot de passe
        user = current_user
        user.password = hashed_password
        db.session.commit()
        
        flash("Mot de passe modifié", "success")
        return render_template('modify/password.html'), 201
        
    
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

@app.route('/historique', methods=['GET'])
@login_required
def historique():
    # Récupérer tous les shifts passés pour l'utilisateur connecté
    today = date.today()
    past_shifts = Shift.query.filter(
        Shift.user_id == current_user.id,
        Shift.date_fin < today
    ).order_by(Shift.date_debut.desc()).all()
    
    return render_template('prestataire_historique/historique.html', shifts=past_shifts)

@app.route('/prestataires/planning', methods=['GET'])
@login_required
def planning():
    # On peut accéder aux disponibilités via la relation définie dans le modèle
    dispo_records = current_user.disponibilites  
    # Ou : dispo_records = Disponibilite.query.filter_by(user_id=current_user.id).all()
    return render_template('presta_planning/planning.html', planning=dispo_records)

# Routes pour le planning
@app.route('/api/planning')
@login_required
def get_planning():
    # Récupérer l'ID de l'utilisateur connecté
    user_id = current_user.id

    events = []

    # Récupérer les disponibilités de l'utilisateur connecté
    dispo = Disponibilite.query.filter_by(user_id=user_id).all()
    for d in dispo:
        events.append({
            'title': "Disponible",
            'start': f"{d.date_debut}T{d.horaire_debut}",
            'end': f"{d.date_fin}T{d.horaire_fin}",
            'color': '#142849'  # Couleur pour les disponibilités
        })

    # Récupérer les indisponibilités de l'utilisateur connecté
    indispo = Indisponibilite.query.filter_by(user_id=user_id).all()
    for i in indispo:
        events.append({
            'title': "Indisponible",
            'start': f"{i.date_debut}T{i.horaire_debut}",
            'end': f"{i.date_fin}T{i.horaire_fin}",
            'color': '#652C41'  # Couleur pour les indisponibilités
        })

    # Récupérer les shifts de l'utilisateur connecté
    shifts = Shift.query.filter_by(user_id=user_id).all()
    for s in shifts:
        events.append({
            'title': f"{s.hotel} - {s.fonction}",  # Titre du shift
            'start': f"{s.date_debut}T{s.horaire_debut}",
            'end': f"{s.date_fin}T{s.horaire_fin}",
            'color': '#1b2b50',  # Couleur pour les shifts
            'extendedProps': {
                'hotel': s.hotel,
                'adresse': s.adresse_hotel,
                'fonction': s.fonction
            }
        })

    return jsonify(events)

@app.route('/api/disponibilites', methods=['POST'])
@login_required
def add_disponibilite():
    try:
        data = request.get_json()
        
        # Validation obligatoire
        if 'type' not in data or data['type'] not in ['disponibilite', 'indisponibilite']:
            return jsonify({"error": "Type d'événement invalide"}), 400

        # Conversion des dates avec vérification
        try:
            start = datetime.fromisoformat(data['start'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(data['end'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Format de date/heure invalide"}), 400

        # Vérification cohérence des dates
        if end <= start:
            return jsonify({"error": "La fin doit être après le début"}), 400

        # Création de l'entrée
        if data['type'] == 'disponibilite':
            new_entry = Disponibilite(
                user_id=current_user.id,
                date_debut=start.date(),
                date_fin=end.date(),
                horaire_debut=start.time(),
                horaire_fin=end.time()
            )
        else:
            new_entry = Indisponibilite(
                user_id=current_user.id,
                date_debut=start.date(),
                date_fin=end.date(),
                horaire_debut=start.time(),
                horaire_fin=end.time()
            )

        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"message": "Événement enregistré"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/admin/planning', methods=['GET'])
@login_required
@admin_required
def admin_planning():
    # Récupérer tous les prestataires (utilisateurs avec le rôle 'user')
    prestataires = User.query.filter_by(role='user').all()
    # Rendre la page avec la liste des prestataires
    return render_template('admin_planning/admin_planning.html', prestataires=prestataires)


@app.route('/api/admin-planning')
@login_required
@admin_required
def get_admin_planning():
    prestataire_id = request.args.get('prestataire_id')
    
    events = []
    
    # Si un prestataire est sélectionné, filtrer les disponibilités et indisponibilités par son ID
    if prestataire_id:
        dispo = Disponibilite.query.filter_by(user_id=prestataire_id).all()
        indispo = Indisponibilite.query.filter_by(user_id=prestataire_id).all()
        # Ajouter les disponibilités aux événements
        for d in dispo:
            user = db.session.get(User, d.user_id)
            events.append({
                'title': f"{user.nom} {user.prenom} - Disponible",
                'start': f"{d.date_debut}T{d.horaire_debut}",
                'end': f"{d.date_fin}T{d.horaire_fin}",
                'color': '#142849'
            })
        
        # Ajouter les indisponibilités aux événements
        for i in indispo:
            user = db.session.get(User, i.user_id)
            events.append({
                'title': f"{user.nom} {user.prenom} - Indisponible",
                'start': f"{i.date_debut}T{i.horaire_debut}",
                'end': f"{i.date_fin}T{i.horaire_fin}",
                'color': '#652C41'
            })

    # Gestion des shifts
    if prestataire_id:
        shifts = Shift.query.filter_by(user_id=prestataire_id).all()
    else:
        shifts = Shift.query.all()
    
    for s in shifts:
        user = db.session.get(User, s.user_id)
        events.append({
            'title': f"{user.nom} {user.prenom} - {s.hotel} - {s.fonction}",
            'start': f"{s.date_debut}T{s.horaire_debut}",
            'end': f"{s.date_fin}T{s.horaire_fin}",
            'color': '#1b2b50',
            'extendedProps': {
                'hotel': s.hotel,
                'adresse': s.adresse_hotel
            }
        })
    
    return jsonify(events)

@app.route('/api/shifts', methods=['POST'])
@login_required
@admin_required
def add_shift():
    try:
        data = request.get_json()
        
        # Validation des données
        required_fields = ['user_id', 'hotel', 'adresse_hotel', 'fonction', 'start', 'end']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Champs manquants"}), 400

        # Conversion des dates
        start = datetime.fromisoformat(data['start'])
        end = datetime.fromisoformat(data['end'])

        # Création du shift
        new_shift = Shift(
            user_id=data['user_id'],
            hotel=data['hotel'],
            adresse_hotel=data['adresse_hotel'],
            fonction=data['fonction'],
            date_debut=start.date(),
            date_fin=end.date(),
            horaire_debut=start.time(),
            horaire_fin=end.time()
        )

        db.session.add(new_shift)
        db.session.commit()
        return jsonify({"message": "Shift ajouté avec succès"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Route pour afficher la page "mdp-oublie.html"
@app.route('/mdp-oublie', methods=['GET'])
def mdp_oublie():
    return render_template('/mot-de-passe-oublie/mdp-oublie.html')

# Route pour gérer la soumission du formulaire
@app.route('/mdp-oublie', methods=['POST'])
def mdp_oublie_submit():
    email = request.form.get('email')

    # Vérifier si l'e-mail existe dans la base de données
    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Aucun utilisateur trouvé avec cette adresse e-mail.", "error")
        return redirect(url_for('mdp_oublie'))

    # Générer un token de réinitialisation de mot de passe (simplifié ici)

    # Envoyer un e-mail avec le lien de réinitialisation
    msg = Message("Réinitialisation de votre mot de passe", recipients=[user.email])
    msg.body = f"Test"
    
    try:
        mail.send(msg)
        flash("Un e-mail de réinitialisation a été envoyé à votre adresse e-mail.", "success")
        print("envoye")
    except Exception as e:
        print("fail")
        flash("Une erreur s'est produite lors de l'envoi de l'e-mail. Veuillez réessayer.", "error")
        print(f"Erreur lors de l'envoi de l'e-mail : {e}")

    return redirect(url_for('mdp_oublie'))



if __name__ == '__main__':
    app.run(debug=True)