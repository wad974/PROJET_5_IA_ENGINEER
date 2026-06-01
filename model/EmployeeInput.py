from pydantic import BaseModel, Field
from typing import Optional

class EmployeeInput(BaseModel):
    # Identifiants et informations de base
    id_employee: int = Field(..., description="ID unique de l'employé")
    age: int = Field(..., description="Âge de l'employé", ge=18, le=100)
    genre: str = Field(..., description="Genre de l'employé")
    statut_marital: str = Field(..., description="Statut marital (Célibataire, Marié, etc.)")
    ayant_enfants: bool = Field(..., description="Indique si l'employé a des enfants")
    distance_domicile_travail: float = Field(..., description="Distance en km entre le domicile et le travail", ge=0)
    
    # Éducation et Profil
    niveau_education: int = Field(..., description="Niveau d'éducation (ex: 1 à 5)", ge=1)
    domaine_etude: str = Field(..., description="Domaine d'études de l'employé")
    
    # Poste et Carrière
    departement: str = Field(..., description="Département dans l'entreprise")
    poste: str = Field(..., description="Poste actuel de l'employé")
    niveau_hierarchique_poste: int = Field(..., description="Niveau hiérarchique du poste", ge=1)
    frequence_deplacement: str = Field(..., description="Fréquence des déplacements professionnels")
    
    # Rémunération et Temps de travail
    revenu_mensuel: float = Field(..., description="Revenu mensuel de l'employé", ge=0)
    augementation_salaire_precedente: float = Field(..., description="Pourcentage ou montant de la dernière augmentation", ge=0)
    nombre_heures_travailless: float = Field(..., description="Nombre d'heures travaillées", ge=0)
    heure_supplementaires: bool = Field(..., description="Effectue des heures supplémentaires")
    
    # Ancienneté et Expérience
    nombre_experiences_precedentes: int = Field(..., ge=0)
    annee_experience_totale: int = Field(..., ge=0)
    annees_dans_l_entreprise: int = Field(..., ge=0)
    annees_dans_le_poste_actuel: int = Field(..., ge=0)
    annees_depuis_la_derniere_promotion: int = Field(..., ge=0)
    annes_sous_responsable_actuel: int = Field(..., ge=0)
    
    # Management et PEE
    nombre_employee_sous_responsabilite: int = Field(..., ge=0)
    nombre_participation_pee: int = Field(..., description="Nombre de participations au PEE", ge=0)
    nb_formations_suivies: int = Field(..., description="Nombre de formations suivies l'année dernière", ge=0)
    
    # Enquêtes de satisfaction (Notes)
    code_sondage: Optional[int] = Field(None, description="Code associé au sondage")
    satisfaction_employee_environnement: int = Field(..., ge=1, le=5, description="Note satisfaction environnement")
    satisfaction_employee_nature_travail: int = Field(..., ge=1, le=5, description="Note satisfaction travail")
    satisfaction_employee_equipe: int = Field(..., ge=1, le=5, description="Note satisfaction équipe")
    satisfaction_employee_equilibre_pro_perso: int = Field(..., ge=1, le=5, description="Note équilibre pro/perso")
    
    # Évaluations professionnelles
    eval_number: Optional[str] = Field(None, description="Identifiant unique de l'évaluation (ex: E_1)")
    note_evaluation_precedente: Optional[float] = Field(None, ge=0)
    note_evaluation_actuelle: Optional[float] = Field(None, ge=0)
    
    # Variable cible (Optionnelle lors d'une prédiction, car on cherche à la deviner)
    a_quitte_l_entreprise: Optional[int] = Field(None, description="Target : 1 si quitté, 0 sinon")

    class Config:
        json_schema_extra = {
            "example": {
                "id_employee": 1,
                "age": 38,
                "genre": "Homme",
                "revenu_mensuel": 3200.0,
                "statut_marital": "Marié",
                "departement": "R&D",
                "poste": "AI Engineer",
                "nombre_experiences_precedentes": 2,
                "nombre_heures_travailless": 151.0,
                "annee_experience_totale": 10,
                "annees_dans_l_entreprise": 4,
                "annees_dans_le_poste_actuel": 2,
                "nombre_participation_pee": 1,
                "nb_formations_suivies": 3,
                "nombre_employee_sous_responsabilite": 0,
                "code_sondage": 1,
                "distance_domicile_travail": 12.5,
                "niveau_education": 4,
                "domaine_etude": "Informatique",
                "ayant_enfants": True,
                "frequence_deplacement": "Rarement",
                "annees_depuis_la_derniere_promotion": 1,
                "annes_sous_responsable_actuel": 2,
                "satisfaction_employee_environnement": 4,
                "note_evaluation_precedente": 3.5,
                "niveau_hierarchique_poste": 2,
                "satisfaction_employee_nature_travail": 4,
                "satisfaction_employee_equipe": 5,
                "satisfaction_employee_equilibre_pro_perso": 4,
                "eval_number": "E_1",
                "note_evaluation_actuelle": 4.0,
                "heure_supplementaires": False,
                "augementation_salaire_precedente": 3.5,
                "a_quitte_l_entreprise": None
            }
        }