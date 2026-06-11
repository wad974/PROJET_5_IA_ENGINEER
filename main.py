import os
import shutil
import warnings
import numpy as np
import pandas as pd
from fastapi import FastAPI, UploadFile, HTTPException, File, Request

# On désactive les warnings inutiles
warnings.filterwarnings('ignore')

# Imports de vos modules locaux
from src.database import test_db_connection
from src.data_fetch import get_data_from_db
from model.EmployeeInput import EmployeeInput

# Initialisation de l'application FastAPI
app = FastAPI(
    title="Projet 5 IA Engineer",
    description="API pour le projet 5 de l'IA Engineer",
    version="0.0.1",
)

# ------------------------------------------------------------------
# VARIABLES GLOBALES POUR ÉVITER DE RE-ENTRAINER À CHAQUE PRÉDICTION
# ------------------------------------------------------------------
trained_model = None
trained_scaler = None
x_train_scaled = None

# Chemin vers le dossier de stockage des fichiers
UPLOAD_FOLDER = "data"

# ------------------------------------------------------------------
# ENDPOINTS DE DIAGNOSTIC ET BASE DE DONNÉES
# ------------------------------------------------------------------

@app.get("/", summary="Page d'accueil et catalogue des endpoints")
def page_racine(request: Request):
    # On récupère la base_url de manière dynamique (ex: http://localhost:7860/ ou http://votre-serveur/)
    base_url = str(request.base_url).rstrip("/")
    
    return {
        "message": "Bienvenue sur l'API du projet 5 de l'IA Engineer!",
        "documentation": {
            "swagger_ui": f"{base_url}/docs",
            "redoc": f"{base_url}/redoc"
        },
        "endpoints": {
            "diagnostic": {
                "health_check": {
                    "url": f"{base_url}/health",
                    "method": "GET",
                    "description": "Vérifier si l'API est opérationnelle."
                },
                "db_test": {
                    "url": f"{base_url}/db-test",
                    "method": "GET",
                    "description": "Tester la connexion à la base de données PostgreSQL."
                }
            },
            "data_management": {
                "load_csv": {
                    "url": f"{base_url}/load-csv",
                    "method": "GET",
                    "description": "Charger les fichiers CSV initiaux dans la base de données."
                },
                "upload_csv": {
                    "url": f"{base_url}/upload-csv",
                    "method": "POST",
                    "description": "Télécharger un fichier CSV dans le dossier data (nécessite un fichier multipart)."
                }
            },
            "machine_learning": {
                "train_model": {
                    "url": f"{base_url}/train-model",
                    "method": "POST",
                    "description": "Entraîner le modèle sur les données de la DB et calculer le score F1."
                },
                "predict": {
                    "url": f"{base_url}/predict?id_employee={{id_employee}}",
                    "method": "POST",
                    "description": "Prédire le départ d'un employé. Remplacer {id_employee} par l'identifiant cible."
                }
            }
        }
    }


@app.get("/health", summary="Vérification de l'état de l'API")
def health_check():
    return {"status": "OK", "message": "L'API est opérationnelle."}


@app.get("/db-test", summary="Test de connexion à la base de données")
def db_test():
    version = test_db_connection()
    return {
        "status": "OK", 
        "message": "Test de connexion à la base de données réussie.",
        "version": version
    }


@app.get("/load-csv", summary="Charge les fichiers CSV initiaux dans la base de données")
def load_csv():
    from src.load_csv import load_csv_to_db
    result = load_csv_to_db()
    return result 


@app.post("/upload-csv", summary="Télécharge un nouveau fichier CSV")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Le fichier doit être au format CSV.")
    
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {"status": "success", "message": f"Fichier '{file.filename}' téléchargé avec succès."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du téléchargement du fichier: {e}")


# ------------------------------------------------------------------
# ENDPOINTS MACHINE LEARNING (TRAIN & PREDICT)
# ------------------------------------------------------------------

@app.post("/train-model", summary="Entraîne le modèle et stocke les artifacts")
def train_model():
    global trained_model, trained_scaler, x_train_scaled
    
    try:
        from src import train_model, load_csv, data_fetch
        
        print('[INFO] Démarrage de l\'entraînement du modèle...')
        # Récupération des données consolidées et entraînement du pipeline
        model, scaler, score, x_train_scaled = train_model.split_data(load_csv.analyse_data())
        
        print('Score F1 du modèle entraîné :', round(score, 4))
        print('Model du modèle entraîné :', model)
        print('Scaler du modèle entraîné :', scaler)
        print('x_train_scaled :', x_train_scaled)
        # Stockage dans les variables globales pour les requêtes de prédiction ultérieures
        trained_model = model
        trained_scaler = scaler
        x_train_scaled = x_train_scaled
        
        return {
            "status": "Success",
            "metric_score_f1": round(score, 4),
            "message": "Le pipeline s'est exécuté avec succès sur les dernières données de la base."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'entraînement du modèle: {e}")


@app.post("/predict", summary="Prédire si un employé spécifique va partir à partir de son ID")
def predict_single_employee(id_employee: int):
    global trained_model, trained_scaler, x_train_scaled
    
    train_model()
    # 1. Vérification de la présence du modèle et du scaler
    if trained_model is None or trained_scaler is None:
        raise HTTPException(
            status_code=503, 
            detail="Le modèle n'est pas encore entraîné. Veuillez appeler l'endpoint /train-model d'abord."
        )
    
    try:
        
        # 8. Calcul de la prédiction
        prediction = int(trained_model.predict(x_train_scaled)[0])
        
        return {
            "status": "Success",
            "id_employee": id_employee,
            "prediction": prediction,
            "prediction_text": "L'employé va quitter l'entreprise" if prediction == 1 else "L'employé va rester"
        }
        
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction : {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)