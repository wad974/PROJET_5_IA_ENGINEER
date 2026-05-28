import pandas as pd
import numpy as np
from src import train_model


def test_train_model():
    # on va creer un dataframe de test pour tester la fonction train_model
    data = {
        'id_employe': [1, 2, 3, 4, 5],
        'age': [25, 30, 35, 40, 45],
        'salaire': [30000, 40000, 50000, 60000, 70000],
        'nombre_employee_sous_responsabilite': [0, 1, 2, 3, 4],
        'nombre_heures_travailless': [0, 1, 2, 3, 4],
        'a_quitte_l_entreprise_Oui': [0, 0, 1, 1, 0]
    }
    df_fictif = pd.DataFrame(data)
    
    model, scaler, score = train_model.split_data(df_fictif)
    
    assert model is not None
    assert scaler is not None
    assert isinstance(score, float)
    assert 0 <= score <= 1