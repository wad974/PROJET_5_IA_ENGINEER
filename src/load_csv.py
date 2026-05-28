import os
import pandas as pd
from sqlalchemy import create_engine, text
# on import les params
from .database import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
from .database import create_db_engine

FILES = {
    "sirh": "data/extrait_sirh.csv",
    "eval": "data/extrait_eval.csv",
    "sondage": "data/extrait_sondage.csv",
}

# on importe nos données depuis notebook pour lier les data
def analyse_data():
    # on charge les données depuis les fichiers csv
    df_sirh = pd.read_csv(FILES["sirh"])
    df_eval = pd.read_csv(FILES["eval"])
    df_sondage = pd.read_csv(FILES["sondage"])
    
    # on affiche les premières lignes de chaque dataframe pour vérifier que les données sont chargées correctement
    print("Données SIRH :")
    print(df_sirh.head())
    
    print("\nDonnées Evaluation :")
    print(df_eval.head())
    
    print("\nDonnées Sondage :")
    print(df_sondage.head())
    
    df_eval['id_employe'] = df_eval['eval_number'].str.extract(r'(\d+)').astype(int)
    df_eval = df_eval.drop(columns=['eval_number'])
    df_central = pd.merge(df_sirh, df_eval, on='id_employe', how='left')
    df_central = pd.merge(df_central, df_sondage, left_on='id_employe', right_on='id_employe', how='left')
    print("\nDonnées Centrales :")
    print(df_central.head())
    print(df_central.shape)
    
    # on transform les object en numerique pour les analyses statistiques
    for col, value in df_central.dtypes.items():
        if value == 'object':
            #print(col ,'-', value)
            df_central = pd.get_dummies(df_central, columns=[col], drop_first=True)
            
    # on controle de nouveau 
    df_central.info()
    # on converti les bool en int
    # on utilise une boucle 
    df_central = df_central.astype({col:int for col, value in df_central.dtypes.items() if value == 'bool'})

    # on fais un nettoyage des données NaN
    df_central = df_central.dropna()   
    
    # on vois deux colonnes avec des data NaN on vas directement supprimer ces colonnes 
    df_corr = df_central.drop(columns=['nombre_employee_sous_responsabilite', 'nombre_heures_travailless'], axis=1)
    
    return df_corr

# charger les données dans la base de données qui ont etait traiter dans la fonction def analyse_data() et qui sont dans le dataframe df_central
def load_analysed_data_to_db():
    df_corr = analyse_data()
    # on contruit l'url de connexion à la base de données
    conn = create_db_engine().connect()
    # on verifie d'abord que la table et les colonnes n'existent pas déjà dans la base de données
    requete = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = 'data_centrale'
        """)
        )
    if requete.fetchone():
        print("La table data_centrale existe déjà dans la base de données, on la supprime avant de la recréer.")
        # on continue
    # on insert tout avec df.to_sql, on remplace la table si elle existe déjà
    df_corr.to_sql('data_centrale', conn, if_exists='append', index=False)
    return {"status": "success", "message": "Les données analysées ont été chargées dans la base de données avec succès."}



def load_csv_to_db():
    
    try:
    
        # On lui donne le chemin du dossier où se trouvent les fichiers csv
        dossier = "data"

        # récupérer tous les fichiers csv
        fichiers_csv = []
        
        # boucle pour parcourir les fichiers du dossier et ajouter les chemins complets des fichiers csv à la liste
        for fichier in os.listdir(dossier):
            if fichier.endswith(".csv"):
                path_complet = os.path.join(dossier,fichier)
                fichiers_csv.append(path_complet)
                
        print(f"Fichiers CSV trouvés : {fichiers_csv}")
        
        # on creer une boucle pour chaque fichier dans le dictionnaire FILES
        for paths in fichiers_csv:
            
            print(f"Chargement du fichier depuis {paths}")
            
            df = pd.read_csv(paths)
            
            paths = paths.replace("data/extrait_", "")
            paths = paths.replace(".csv", "")
            
            # on contruit l'url de connexion à la base de données
            url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
            engine = create_engine(url)
            conn = engine.connect()
            # on verifie d'abord que la table et les colonnes n'existent pas déjà dans la base de données
            requete = conn.execute(text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = :table_name
                """),
                {"table_name": paths}
                )
            if requete.fetchone():
                print(f"La table {paths} existe déjà dans la base de données, on la supprime avant de la recréer.")
                continue
            
            # on insert tout avec df.to_sql, on remplace la table si elle existe déjà
            df.to_sql(paths, engine, if_exists='append', index=False)
            print(f"Le fichier {paths} a été chargé dans la base de données avec succès.")
                
            #print(df.head())
            #print(type(df.columns))
            
        return {"status": "success", "message": "Tous les fichiers ont été chargés dans la base de données."}
        
    except Exception as e:
        print(f"Erreur lors du chargement des fichiers dans la base de données: {e}")
        return {"status": "error", "message": f"Erreur lors du chargement des fichiers dans la base de données: {e}"}   
    
def get_pg_type(dtype):
    if pd.api.types.is_integer_dtype(dtype): return "INTEGER"
    elif pd.api.types.is_datetime64_any_dtype(dtype): return "TIMESTAMP"
    elif pd.api.types.is_float_dtype(dtype): return "FLOAT"
    elif pd.api.types.is_bool_dtype(dtype): return "BOOLEAN"
    else: return "TEXT"

