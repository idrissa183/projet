"""from flask import Flask, render_template


application = Flask(__name__)


@application.route("/")
def bonjour():
    return render_template("index.html")


if __name__ == "__main__":
    application.run(debug=True)"""

"""main module"""

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import mysql.connector
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

class Utilisateur(BaseModel):
    nom: str
    prenom: str
    age: int
    email: str
    passwords: str
    verification: int


class User(BaseModel):
    nom: str
    prenom: str
    age: int
    email: str
    passwords: str
    verification: int


# Etablir une connexion à la BD
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="healthcheck"
)


# Message d'accueil
@app.get("/")
def hello(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


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
        # connection.close()

        return {
            "Alerte": "INFORMATION",
            "Message": "Patient inséré avec succès dans la BD!"
        }
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Erreur lors de l'insertion du patient dans la base de données : {str(e)}"
                            )


# rechercher un patient en utilisant son ID
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


# afficher tout les patients qui se trouvent dans la BD
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


# Mise à jour d'un patient
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
            raise HTTPException(status_code=404, detail="Patient non trouvé")
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


@app.on_event("shutdown")
def fermeture():
    connection.close()

