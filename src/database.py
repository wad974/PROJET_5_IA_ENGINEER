import os
import psycopg
from dotenv import load_dotenv 
import configparser

load_dotenv()  # Charger les variables d'environnement à partir du fichier .env

config = configparser.ConfigParser() # Charger le fichier de configuration
config.read('params/config.ini')

DB_HOST = config.get('database', 'host')
DB_NAME = config.get('database', 'name')
DB_USER = config.get('database', 'user')
DB_PASSWORD = config.get('database', 'password')

# Connexion à la base de données
def connect_to_db():
    try:
        connection = psycopg.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        print("Connexion à la base de données réussie")
        return connection
    except Exception as e:
        print(f"Erreur lors de la connexion à la base de données: {e}")
        return None

def test_db_connection():
    try : 
        connection = connect_to_db()
        if connection:
            cur = connection.cursor()
            cur.execute("SELECT version();")
            db_version = cur.fetchone()
            print(f"Version de la base de données: {db_version[0]}")
            connection.close()
            print("Connexion à la base de données fermée")
            return db_version[0]
    except Exception as e:
        print(f"Erreur lors de la connexion à la base de données: {e}")


#test_db_connection()
