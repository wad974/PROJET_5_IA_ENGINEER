from .database import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
from .database import create_db_engine
import pandas as pd

# on creer la fonction qui recupere les données depuis la base de données et qui les retourne sous forme de dataframe pandas pour les analyses statistiques et les visualisations 

def get_data_from_db():
    engine = create_db_engine()
    query = "SELECT * FROM data_centrale"
    df_central = pd.read_sql_query(query, engine)
    return df_central