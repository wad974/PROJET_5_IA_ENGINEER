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
    global trained_model, trained_scaler
    try:
        from src import train_model, load_csv, data_fetch
        
        print('[INFO] Démarrage de l\'entraînement du modèle...')
        # Récupération des données consolidées et entraînement du pipeline
        model, scaler, score = train_model.split_data(load_csv.analyse_data())
        
        print('Score F1 du modèle entraîné :', round(score, 4))
        print('Model du modèle entraîné :', model)
        print('Scaler du modèle entraîné :', scaler)
        # Stockage dans les variables globales pour les requêtes de prédiction ultérieures
        trained_model = model
        trained_scaler = scaler
        
        return {
            "status": "Success",
            "metric_score_f1": round(score, 4),
            "message": "Le pipeline s'est exécuté avec succès sur les dernières données de la base."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'entraînement du modèle: {e}")


@app.post("/predict", summary="Prédire si un employé spécifique va partir à partir de son ID")
def predict_single_employee(id_employee: int):
    # 1. Vérification de la présence du modèle et du scaler
    if trained_model is None or trained_scaler is None:
        raise HTTPException(
            status_code=503, 
            detail="Le modèle n'est pas encore entraîné. Veuillez appeler l'endpoint /train-model d'abord."
        )
    
    try:
        # 2. Récupération de l'ensemble des données consolidées de la DB
        df_all = get_data_from_db()
        
        # 3. Extraction de la ligne correspondant à l'ID fourni
        df_employee = df_all[df_all['id_employee'] == id_employee]
        
        if df_employee.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"L'employé avec l'ID {id_employee} n'a pas été trouvé dans la base de données."
            )
            
        # 4. Validation structurelle via le modèle Pydantic EmployeeInput
        employee_dict = df_employee.iloc[0].to_dict()
        validated_employee = EmployeeInput(**employee_dict)
        
        # 5. Reconstruction d'un DataFrame propre
        df_features = pd.DataFrame([validated_employee.model_dump()])
        
        # 6. Alignement strict de l'ordre des features (Exclusion de l'ID et de la Target)
        X_features = df_features[[
            'age', 'genre', 'revenu_mensuel', 'statut_marital', 'departement', 'poste', 
            'nombre_experiences_precedentes', 'nombre_heures_travailless', 'annee_experience_totale', 
            'annees_dans_l_entreprise', 'annees_dans_le_poste_actuel', 'nombre_participation_pee', 
            'nb_formations_suivies', 'nombre_employee_sous_responsabilite', 'code_sondage', 
            'distance_domicile_travail', 'niveau_education', 'domaine_etude', 'ayant_enfants', 
            'frequence_deplacement', 'annees_depuis_la_derniere_promotion', 'annes_sous_responsable_actuel',
            'satisfaction_employee_environnement', 'note_evaluation_precedente', 'niveau_hierarchique_poste', 
            'satisfaction_employee_nature_travail', 'satisfaction_employee_equipe', 
            'satisfaction_employee_equilibre_pro_perso', 'eval_number', 'note_evaluation_actuelle', 
            'heure_supplementaires', 'augementation_salaire_precedente'
        ]]
        
        # 7. Standardisation des données
        X_scaled = trained_scaler.transform(X_features)
        
        # 8. Calcul de la prédiction
        prediction = int(trained_model.predict(X_scaled)[0])
        
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