from fastapi import FastAPI, UploadFile, HTTPException, File
import os
import shutil
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import norm
from sklearn.preprocessing import StandardScaler
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

from src.database import test_db_connection

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

@app.get("/")
def page_racine():
    return {"message": "Bienvenue sur l'API du projet 5 de l'IA Engineer!"}

@app.get("/health")
def health_check():
    return {"status": "OK", "message": "L'API est opérationnelle."}

@app.get("/db-test")
def db_test():
    version = test_db_connection()
    return {"status": "OK", 
            "message": "Test de connexion à la base de données réussie.",
            "version" : version}
    
@app.get("/load-csv")
def load_csv():
    from src.load_csv import load_csv_to_db
    result = load_csv_to_db()
    return result 

# chemin vers le dossier data
UPLOAD_FOLDER = "data"

@app.post("/upload-csv")
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


"""
Lancer le traitement et obtenier les predictions du modèle entrainé :
"""

@app.post("/train-model", summary="Entraîne le modèle et retourne les prédictions")
def train_model():
    
    global trained_model, trained_scaler
    try:
        from src import train_model, data_fetch
        
        # on recupere les données depuis la base de données et on les split pour entrainer le modèle
        model, scaler, score = train_model.split_data(data_fetch.get_data_from_db())
        trained_model = model
        trained_scaler = scaler
        # on retourne le score du modèle sur le test set
        return {
            "status": "Success",
            "metric_score_f1": round(score, 4),
            "message": "Le pipeline s'est exécuté avec succès sur les dernières données de la base."
        }
        
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'entraînement du modèle: {e}")

# on importe le schéma de validation Pydantic pour la prédiction d'un employé spécifique
from model.EmployeeInput import EmployeeInput

@app.post("/predict", summary="Prédire si un employé spécifique va partir")
def predict_single_employee(employee: EmployeeInput):
    # On vérifie si le modèle a bien été entraîné au moins une fois via /train-model
    if trained_model is None or trained_scaler is None:
        raise HTTPException(
            status_code=503, 
            detail="Le modèle n'est pas encore entraîné. Veuillez appeler l'endpoint /train-model d'abord."
        )
    
    try:
        # On convertit les données validées par Pydantic en DataFrame
        data_dict = employee.model_dump()
        df = pd.DataFrame([data_dict])
        
        # ⚠️ Pour éviter le Data Leakage comme dans train_model.py,
        # on retire la colonne cible si elle est créée par défaut (ici elle n'y est pas)
        # Mais on doit s'assurer que l'ordre correspond EXACTEMENT au X_train
        X_features = df[['id_employe', 'age', 'salaire', 'nombre_employee_sous_responsabilite', 'nombre_heures_travailless']]
        
        # Application du scaler entraîné
        X_scaled = trained_scaler.transform(X_features)
        
        # Prédiction
        prediction = int(trained_model.predict(X_scaled)[0])
        
        return {
            "status": "Success",
            "id_employe": employee.id_employe,
            "prediction": prediction,
            "prediction_text": "L'employé va quitter l'entreprise" if prediction == 1 else "L'employé va rester"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction : {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)