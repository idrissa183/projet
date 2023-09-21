"""module models"""

# importation des bibliothèques
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector

# L'instance de mon API
app = FastAPI()


# Mon modèle utilisateur
class Utilisateur(BaseModel):
    nom: str
    prenom: str
    age: int
    email: str
    passwords: str
    verification: int


# Mon deuxième modèle utilisateur
class User(BaseModel):
    nom: str
    prenom: str
    age: int
    email: str
    passwords: str
    verification: int


# Etablissement de la connexion à la base de données
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="healthcheck"
)


# Message d'accueil
@app.get("/")
def hello():
    return {"message: ": "Bonjour tout le monde!"}


# Creation de nouveaux patients
@app.post("/patients/create")
def create_patient(user: Utilisateur):
    try:
        # Insérer les données dans la base de données
        curseur = connection.cursor()
        curseur.execute("""
                INSERT INTO utilisateurs (nom, 
                prenom, 
                age, 
                email, 
                passwords, 
                verification) VALUES (%s, %s, %s, %s, %s, %s)
            """, (user.nom, user.prenom, user.age, user.email, user.passwords, user.verification))
        connection.commit()
        curseur.close()

        return {
            "Alerte": "INFORMATION",
            "Message": "Patient inséré avec succès dans la BD!"
        }
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Erreur lors de l'insertion du patient dans la base de données : {str(e)}"
                            )


# recherche d'un patient dans la base de données en utilisant son ID
@app.get("/patients/rechercher/{id}")
def rechercher(my_id: int):
    try:
        curseur = connection.cursor(dictionary=True)
        curseur.execute(f"""
                        SELECT * FROM utilisateurs WHERE id = '{my_id}'""")
        donnees = curseur.fetchone()
        print(donnees)
        curseur.close()
        if donnees:
            return {"Le patient recherché est: ": donnees}
        else:
            return {"INFORMATION": f"Le patient à l'ID {my_id} n'existe pas dans la BD!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")


# affichage de tous les patients se trouvant dans la base de données
@app.get("/patients/afficher/")
def afficher():
    try:
        curseur = connection.cursor(dictionary=True)
        curseur.execute(f"""
                        SELECT * FROM utilisateurs""")
        donnees = curseur.fetchall()
        curseur.close()
        return {"Les patients sont: ": donnees}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")


# Mise à jour des données d'un patient
@app.put("/patients/update/{id}", response_model=dict)
def mise_a_jour(my_id: int, user: User):
    try:
        curseur = connection.cursor(dictionary=True)
        curseur.execute(f"""
                                SELECT * FROM utilisateurs WHERE id = '{my_id}'"""
                        )
        donnees = curseur.fetchone()

        if donnees:
            curseur.execute("""UPDATE utilisateurs
                SET nom = %s, prenom = %s, age = %s, email = %s, passwords = %s, verification = %s
                WHERE id = %s""",
                            (user.nom, user.prenom, user.age, user.email, user.passwords, user.verification, my_id)
                            )
            connection.commit()
            curseur.close()
            # return {**donnees, **user.dict()}
            return user.model_dump()

        else:
            return {"INFORMATION": f"Le patient à l'ID {my_id} n'existe pas dans la BD!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")


# Suppression d'un patient en utilisant son ID
@app.delete("/patients/delete/{id}")
def suppression(my_id: int):
    try:
        curseur = connection.cursor(dictionary=True)
        curseur.execute(f"""
                                SELECT id FROM utilisateurs WHERE id = '{my_id}'"""
                        )
        donnees = curseur.fetchone()

        if donnees:
            curseur.execute(f"""
                            DELETE FROM utilisateurs WHERE id = '{my_id}'"""
                            )
            connection.commit()
            curseur.close()
            return {"INFORMATION": f"Le patient à l'ID {my_id} a été supprimé avec succès!"}

        return {"INFORMATION": "Le patient que vous souhaitez supprimer n'existe pas dans la BD!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de base de données : {str(e)}")


# fermeture de la connexion à la base de données
@app.on_event("shutdown")
def fermeture():
    connection.close()
