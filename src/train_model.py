# on separe ici les données dans le code complet X et y (train/test)
# j'utilise import train_test_split dans sklearn.model_selection (il vient du même module de GriDCV Search)
# liens doc officiel : https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier 
from sklearn.model_selection import GridSearchCV

import pandas as pd

def split_data(df_central):
    
    X = df_central.copy()
    # on supprime la target dans la features pour eviter le data Leakage
    X = X.drop(columns=['a_quitte_l_entreprise_Oui'])
    # on recupere le target
    y = df_central['a_quitte_l_entreprise_Oui']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=5) # 20 pourcent  de train test
    print('Train set : ', X_train.shape)
    print('Test set : ', X_test.shape)
    
    # ici on vas realiser un scaling pour pour ramener toutes les features à la même échelle ex: 0 et 1
    # on utilisera la méthode standardScaler() de sklearn.preprocessing import StandardScaler
    # doc officiel : https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    #scaler.fit(X_train) # on applique uniquement sur le train pour l'apprendre uniquement sur les features X_train
    X_train_scaler = scaler.fit_transform(X_train) # on fit_transformes les données sur X_train 
    X_test_scaler = scaler.transform(X_test) # on transformes les données sur X_test

    
    param_grid = {
        'max_depth': [3, 5, 10, 15, 20, None],
        'n_estimators': [50, 100, 200]
    }
    grid = GridSearchCV(
        RandomForestClassifier(random_state=42),
        param_grid=param_grid,
        cv=5,
        scoring={
            'precision': 'precision',
            'recall': 'recall',
            'f1': 'f1'
        },
        refit='f1', # ici refit vas garder le meilleur selon F1
        n_jobs=-1
    )

    grid.fit(X_train_scaler, y_train)
    model = grid.best_estimator_
    score = model.score(X_test_scaler, y_test)
    print(f'Modèle entrainé avec succès. Score sur le test set : {score:.4f}')
    
    return model, scaler, score