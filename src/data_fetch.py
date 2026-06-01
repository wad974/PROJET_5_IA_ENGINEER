from .database import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
from .database import create_db_engine
import pandas as pd

# on creer la fonction qui recupere les données depuis la base de données et qui les retourne sous forme de dataframe pandas pour les analyses statistiques et les visualisations 

def get_data_from_db():
    engine = create_db_engine()
    query = """
        select * 
        from public.sirh s
        left join public.eval e 
        on cast(replace(e.eval_number, 'E_', '') as integer) = s.id_employee 
        left join public.sondage so
        on so.code_sondage  = s.id_employee;
    """
    df_central = pd.read_sql_query(query, engine)
    print("Données récupérées depuis la base de données :")
    print(df_central.shape[0], "lignes", df_central.shape[1], "colonnes")
    return df_central
