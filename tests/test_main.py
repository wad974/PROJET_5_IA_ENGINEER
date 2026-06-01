import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import numpy as np

# On importe l'application FastAPI depuis le fichier main
from main import app

client = TestClient(app)

# 1. Test des routes de base (Simples)
def test_page_racine():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur l'API du projet 5 de l'IA Engineer!"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK", "message": "L'API est opérationnelle."}

# 2. Test de la connexion DB (avec Mock pour éviter de toucher à la vraie DB)
@patch("main.test_db_connection")
def test_db_test(mock_db_connect):
    mock_db_connect.return_value = "PostgreSQL 15.2"
    
    response = client.get("/db-test")
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "message": "Test de connexion à la base de données réussie.",
        "version": "PostgreSQL 15.2"
    }

# 3. Test de la prédiction sans entraînement préalable (Doit retourner 503)
def test_predict_without_training():
    # Payload d'exemple basé sur vos features
    payload = {
        "id_employe": 42,
        "age": 35,
        "salaire": 45000,
        "nombre_employee_sous_responsabilite": 2,
        "nombre_heures_travailless": 160
    }
    # On force les variables globales à None pour ce test précis
    import main
    main.trained_model = None
    main.trained_scaler = None

    response = client.post("/predict", json=payload)
    assert response.status_code == 503
    assert "Le modèle n'est pas encore entraîné" in response.json()["detail"]

# 4. Test de l'entraînement du modèle (avec Mock du pipeline de données)
@patch("src.data_fetch.get_data_from_db")
@patch("src.train_model.split_data")
def test_train_model(mock_split_data, mock_get_data):
    # On mocke le retour de la DB et du split_data
    mock_get_data.return_value = MagicMock() # Simulation d'un DataFrame
    
    mock_model = MagicMock()
    mock_scaler = MagicMock()
    mock_score = 0.85678
    mock_split_data.return_value = (mock_model, mock_scaler, mock_score)

    response = client.post("/train-model")
    assert response.status_code == 200
    assert response.json()["status"] == "Success"
    assert response.json()["metric_score_f1"] == 0.8568  # Arrondi à 4 décimales
    
    # On vérifie que les variables globales de main ont bien été injectées
    import main
    assert main.trained_model == mock_model
    assert main.trained_scaler == mock_scaler

# 5. Test de la prédiction QUAND le modèle est entraîné
def test_predict_success():
    import main
    # On prépare des mocks pour le scaler et le modèle installés dans le scope global
    mock_scaler = MagicMock()
    mock_scaler.transform.return_value = np.array([[1, 2, 3, 4, 5]])
    
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([1]) # Simule le départ de l'employé (1)
    
    main.trained_scaler = mock_scaler
    main.trained_model = mock_model

    payload = {
        "id_employe": 42,
        "age": 35,
        "salaire": 45000,
        "nombre_employee_sous_responsabilite": 2,
        "nombre_heures_travailless": 160
    }

    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "Success"
    assert response.json()["prediction"] == 1
    assert response.json()["prediction_text"] == "L'employé va quitter l'entreprise"