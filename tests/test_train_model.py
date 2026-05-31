import pandas as pd
import numpy as np
from src import train_model


def test_train_model():
    # on va creer un dataframe de test pour tester la fonction train_model
    np.random.seed(42)  # pour la reproductibilité
    data = {
        'id_employe': list(range(1, 21)),
        'age': np.random.randint(22, 60, size=20),
        'salaire': np.random.randint(25000, 80000, size=20),
        'nombre_employee_sous_responsabilite': np.random.randint(0, 5, size=20),
        'nombre_heures_travailless': np.random.randint(0, 10, size=20),
        'a_quitte_l_entreprise_Oui': np.random.randint(0, 2, size=20)
    }
    df_fictif = pd.DataFrame(data)
    
    model, scaler, score = train_model.split_data(df_fictif)
    
    assert model is not None
    assert scaler is not None
    assert isinstance(score, float)
    assert 0 <= score <= 1