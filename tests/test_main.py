import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import numpy as np
import pandas as pd

# On importe l'application FastAPI depuis le fichier main
from main import app
# On importe la fonction pour récupérer les vraies données de la DB pour le test d'intégration
from src.data_fetch import get_data_from_db

client = TestClient(app)


FAKE_EMPLOYEE_DATA = {
    "id_employee": 42, "age": 38, "genre": "Homme", "revenu_mensuel": 3500.0,
    "statut_marital": "Marié", "departement": "R&D", "poste": "AI Engineer",
    "nombre_experiences_precedentes": 2, "nombre_heures_travailless": 151.0,
    "annee_experience_totale": 10, "annees_dans_l_entreprise": 4, "annees_dans_le_poste_actuel": 2,
    "nombre_participation_pee": 1, "nb_formations_suivies": 3, "nombre_employee_sous_responsabilite": 0,
    "code_sondage": 1, "distance_domicile_travail": 12.5, "niveau_education": 4,
    "domaine_etude": "Informatique", "ayant_enfants": True, "frequence_deplacement": "Rarement",
    "annees_depuis_la_derniere_promotion": 1, "annes_sous_responsable_actuel": 2,
    "satisfaction_employee_environnement": 4, "note_evaluation_precedente": 3.5, "niveau_hierarchique_poste": 2,
    "satisfaction_employee_nature_travail": 4, "satisfaction_employee_equipe": 5,
    "satisfaction_employee_equilibre_pro_perso": 4, "eval_number": "E_42", "note_evaluation_actuelle": 4.0,
    "heure_supplementaires": False, "augementation_salaire_precedente": 3.5, "a_quitte_l_entreprise": None
}

# ------------------------------------------------------------------
# 1. TEST DES ROUTES DE BASE
# ------------------------------------------------------------------

def test_page_racine():
    response = client.get("/")
    assert response.status_code == 200
    assert "Bienvenue sur l'API" in response.json()["message"]

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK", "message": "L'API est opérationnelle."}


@patch("main.test_db_connection")
def test_db_test(mock_db_connect):
    mock_db_connect.return_value = "PostgreSQL 18.4"
    
    response = client.get("/db-test")
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "message": "Test de connexion à la base de données réussie.",
        "version": "PostgreSQL 18.4"
    }

# 2. Test de la prédiction sans entraînement (MOCKÉ - Plus besoin de DB)
@patch("main.get_data_from_db")
def test_predict_without_training(mock_get_data):
    # On force la fonction à retourner notre fausse ligne en dur dans un DataFrame
    mock_get_data.return_value = pd.DataFrame([FAKE_EMPLOYEE_DATA])
    
    # On force l'état non entraîné
    import main
    main.trained_model = None
    main.trained_scaler = None

    # On teste l'appel avec l'ID de notre employé en dur (42)
    response = client.post("/predict?id_employee=42")
    
    assert response.status_code == 503
    assert "Le modèle n'est pas encore entraîné" in response.json()["detail"]

# 3. Test de l'entraînement du modèle
@patch("main.get_data_from_db")
@patch("src.train_model.split_data")
def test_train_model(mock_split_data, mock_get_data):
    mock_get_data.return_value = pd.DataFrame([FAKE_EMPLOYEE_DATA])
    
    mock_model = MagicMock()
    mock_scaler = MagicMock()
    mock_score = 0.85678
    mock_x_train_scaled = np.array([[1, 2], [3, 4]])
    mock_split_data.return_value = (mock_model, mock_scaler, mock_score, mock_x_train_scaled) 

    response = client.post("/train-model")
    assert response.status_code == 200
    assert response.json()["metric_score_f1"] == 0.8568
    
    import main
    assert main.trained_model == mock_model

# 4. Test de la prédiction QUAND le modèle est entraîné
@patch("main.get_data_from_db")
def test_predict_success(mock_get_data):
    import main
    
    mock_scaler = MagicMock()
    mock_scaler.transform.return_value = np.array([[1] * 32])
    
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([1]) # Simule le départ
    
    main.trained_scaler = mock_scaler
    main.trained_model = mock_model

    mock_get_data.return_value = pd.DataFrame([FAKE_EMPLOYEE_DATA])

    response = client.post("/predict?id_employee=42")
    
    assert response.status_code == 200
    assert response.json()["status"] == "Success"
    assert response.json()["id_employee"] == 42
    assert response.json()["prediction"] == 1

# 5. Test de l'erreur 404 (ID inexistant)
#@patch("main.get_data_from_db")
@patch("src.load_csv.analyse_data")
def test_predict_not_found(mock_get_data):
    import main
    main.trained_scaler = MagicMock()
    main.trained_model = MagicMock()
    
    # On simule un retour vide de la DB
    mock_get_data.return_value = pd.DataFrame(columns=["id_employee"])

    response = client.post("/predict?id_employee=999")
    
    assert response.status_code == 404
    assert "n'a pas été trouvé" in response.json()["detail"]