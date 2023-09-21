import mysql.connector


# Etablir une connexion à la BD
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="healthcheck"
)


def create_user(nom, prenom, age):
    curseur = connection.cursor()
    curseur.execute("""
        INSERT INTO utilisateurs () VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nom, prenom, age))
    connection.commit()
    curseur.close()
    connection.close()