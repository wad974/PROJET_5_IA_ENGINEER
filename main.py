from fastapi import FastAPI
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import norm
from sklearn.preprocessing import StandardScaler
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

from src.database import test_db_connection

app = FastAPI(
    title="Projet 5 IA Engineer",
    description="API pour le projet 5 de l'IA Engineer",
    version="0.0.1",
)

@app.get("/")
def page_racine():
    return {"message": "Bienvenue sur l'API du projet 5 de l'IA Engineer!"}

@app.get("/health")
def health_check():
    return {"status": "OK", "message": "L'API est opérationnelle."}

@app.get("/db-test")
def db_test():
    version = test_db_connection()
    return {"status": "OK", 
            "message": "Test de connexion à la base de données réussie.",
            "version" : version}
    
@app.get("/load-csv")
def load_csv():
    from src.load_csv import load_csv_to_db
    result = load_csv_to_db()
    return result 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)