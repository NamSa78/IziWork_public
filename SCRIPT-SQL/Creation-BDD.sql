-- Création de la table Dictionnaire (pour les hôtels)
CREATE TABLE Dictionnaire (
    ID INT PRIMARY KEY,
    NOM VARCHAR(255) NOT NULL
);

-- Création de la table AdressePostale
CREATE TABLE AdressePostale (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    User_ID INT NOT NULL UNIQUE,  -- Une seule adresse par utilisateur
    Rue VARCHAR(255) NOT NULL,
    Code_postal VARCHAR(20) NOT NULL,
    Ville VARCHAR(255) NOT NULL,
    Pays VARCHAR(255) NOT NULL,
    FOREIGN KEY (User_ID) REFERENCES USERS(ID)
);

-- Création de la table USERS
CREATE TABLE USERS (
    ID INT PRIMARY KEY,
    Adresse_mail VARCHAR(255) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL,  -- Stockage du hash
    Nom VARCHAR(255) NOT NULL,
    Prenom VARCHAR(255) NOT NULL,
    Photo_de_profil VARCHAR(255),   -- Lien vers l'image
    Numero_telephone VARCHAR(20),   -- Stocké en string pour flexibilité
    Date_naissance DATE NOT NULL,
    Fonction VARCHAR(255)
);

-- Création de la table HISTORIQUE (liée à USERS et Dictionnaire)
CREATE TABLE Historique (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    User_ID INT NOT NULL,
    Hotel_ID INT NOT NULL,          -- Référence à Dictionnaire
    Date DATE NOT NULL,             -- Format: DD/MM/YYYY
    Horaire_debut TIME NOT NULL,    -- Format: HH:MM
    Horaire_fin TIME NOT NULL,
    FOREIGN KEY (User_ID) REFERENCES USERS(ID),
    FOREIGN KEY (Hotel_ID) REFERENCES Dictionnaire(ID)
);

-- Création de la table Disponibilité (liée à USERS)
CREATE TABLE Disponibilite (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    User_ID INT NOT NULL,
    Date_debut DATE NOT NULL,
    Date_fin DATE NOT NULL,
    Horaire_debut TIME NOT NULL,
    Horaire_fin TIME NOT NULL,
    FOREIGN KEY (User_ID) REFERENCES USERS(ID)
);

-- Création de la table Indisponibilité (liée à USERS)
CREATE TABLE Indisponibilite (
    ID INT AUTO_INCREMENT PRIMARY KEY,
    User_ID INT NOT NULL,
    Date_debut DATE NOT NULL,
    Date_fin DATE NOT NULL,
    Horaire_debut TIME NOT NULL,
    Horaire_fin TIME NOT NULL,
    FOREIGN KEY (User_ID) REFERENCES USERS(ID)
);

-- Création de la table Definition
CREATE TABLE Definition (
    ID INT PRIMARY KEY,
    CODE VARCHAR(50) NOT NULL UNIQUE,
    DEFINITION TEXT NOT NULL
);