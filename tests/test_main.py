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

# ------------------------------------------------------------------
# 1. TEST DES ROUTES DE BASE
# ------------------------------------------------------------------
def test_page_racine():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur l'API du projet 5 de l'IA Engineer!"}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK", "message": "L'API est opérationnelle."}


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

# ------------------------------------------------------------------
# 2. TEST DE LA PRÉDICTION SANS ENTRAÎNEMENT PRÉALABLE (503)
# ------------------------------------------------------------------
def test_predict_without_training():
    # On récupère les vraies données depuis la DB pour extraire un ID existant
    df_real_data = get_data_from_db()
    assert not df_real_data.empty, "La base de données est vide, impossible de faire le test."
    
    # Extraction du premier ID valide présent dans votre table sirh
    valid_id = int(df_real_data.iloc[0]["id_employee"])
    
    # On force les variables globales de l'API à None
    import main
    main.trained_model = None
    main.trained_scaler = None

    # On passe l'id en Query Parameter : /predict?id_employee=X
    response = client.post(f"/predict?id_employee={valid_id}")
    
    assert response.status_code == 503
    assert "Le modèle n'est pas encore entraîné" in response.json()["detail"]

# ------------------------------------------------------------------
# 3. TEST DE L'ENTRAÎNEMENT DU MODÈLE
# ------------------------------------------------------------------
@patch("main.get_data_from_db")  # On patche là où il est appelé (dans main)
@patch("src.train_model.split_data")
def test_train_model(mock_split_data, mock_get_data):
    mock_get_data.return_value = MagicMock()  # Simulation d'un DataFrame
    
    mock_model = MagicMock()
    mock_scaler = MagicMock()
    mock_score = 0.85678
    mock_split_data.return_value = (mock_model, mock_scaler, mock_score)

    response = client.post("/train-model")
    assert response.status_code == 200
    assert response.json()["status"] == "Success"
    assert response.json()["metric_score_f1"] == 0.8568  # Arrondi à 4 décimales
    
    import main
    assert main.trained_model == mock_model
    assert main.trained_scaler == mock_scaler

# ------------------------------------------------------------------
# 4. TEST DE LA PRÉDICTION QUAND LE MODÈLE EST ENTRAÎNÉ (SUCCÈS & 404)
# ------------------------------------------------------------------
@patch("main.get_data_from_db")
def test_predict_success(mock_get_data):
    import main
    
    # 1. On injecte de faux artifacts entraînés dans l'API globale pour le test
    mock_scaler = MagicMock()
    mock_scaler.transform.return_value = np.array([[1] * 32])  # 32 features attendues
    
    mock_model = MagicMock()
    mock_model.predict.return_value = np.array([1])  # Simule le départ de l'employé
    
    main.trained_scaler = mock_scaler
    main.trained_model = mock_model

    # 2. On simule un retour de DB contenant exactement les données requises par EmployeeInput
    # (Tous vos 35 champs réels doivent être simulés ici pour passer la validation Pydantic)
    fake_employee_data = {
        "id_employee": 99, "age": 38, "genre": "Homme", "revenu_mensuel": 3500.0,
        "statut_marital": "Marié", "departement": "R&D", "poste": "AI Engineer",
        "nombre_experiences_precedentes": 2, "nombre_heures_travailless": 151.0,
        "annee_experience_totale": 10, "annees_dans_l_entreprise": 4, "annees_dans_le_poste_actuel": 2,
        "nombre_participation_pee": 1, "nb_formations_suivies": 3, "nombre_employee_sous_responsabilite": 0,
        "code_sondage": 1, "distance_domicile_travail": 12.5, "niveau_education": 4,
        "domaine_etude": "Informatique", "ayant_enfants": True, "frequence_deplacement": "Rarement",
        "annees_depuis_la_derniere_promotion": 1, "annes_sous_responsable_actuel": 2,
        "satisfaction_employee_environnement": 4, "note_evaluation_precedente": 3.5, "niveau_hierarchique_poste": 2,
        "satisfaction_employee_nature_travail": 4, "satisfaction_employee_equipe": 5,
        "satisfaction_employee_equilibre_pro_perso": 4, "eval_number": "E_99", "note_evaluation_actuelle": 4.0,
        "heure_supplementaires": False, "augementation_salaire_precedente": 3.5, "a_quitte_l_entreprise": None
    }
    mock_get_data.return_value = pd.DataFrame([fake_employee_data])

    # 3. Exécution du test sur l'id_employee=99
    response = client.post("/predict?id_employee=99")
    
    assert response.status_code == 200
    assert response.json()["status"] == "Success"
    assert response.json()["id_employee"] == 99
    assert response.json()["prediction"] == 1
    assert response.json()["prediction_text"] == "L'employé va quitter l'entreprise"


@patch("main.get_data_from_db")
def test_predict_not_found(mock_get_data):
    import main
    # Initialisation minimale des variables globales pour éviter la 503
    main.trained_scaler = MagicMock()
    main.trained_model = MagicMock()
    
    # On simule une DB vide ou un ID qui n'existe pas
    mock_get_data.return_value = pd.DataFrame(columns=["id_employee"])

    # On cherche l'ID 999 qui n'existe pas
    response = client.post("/predict?id_employee=999")
    
    assert response.status_code == 404
    assert "n'a pas été trouvé dans la base de données" in response.json()["detail"]