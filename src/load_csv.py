import os
import pandas as pd
from sqlalchemy import create_engine, text
# on import les params
from .database import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

FILES = {
    "sirh": "data/extrait_sirh.csv",
    "eval": "data/extrait_eval.csv",
    "sondage": "data/extrait_sondage.csv",
}



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

