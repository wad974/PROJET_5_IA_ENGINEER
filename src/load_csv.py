import pandas as pd
from database import connect_to_db

FILES = {
    "sirh": "data/extrait_sirh.csv",
    "eval": "data/extrait_eval.csv",
    "sondage": "data/extrait_sondage.csv",
}

def load_csv_to_db(FILES):

    df = pd.read_csv(FILES["sirh"])
    #print(df.head())
    print(type(df.columns))
    for col in df.columns:
        print(col)



load_csv_to_db(FILES)