from pydantic import BaseModel, Field

class EmployeeInput(BaseModel):
    id_employe: int
    age: int = Field(..., description="Âge de l'employé", ge=18, le=100)
    salaire: float = Field(..., description="Salaire annuel", ge=0)
    nombre_employee_sous_responsabilite: int = Field(..., ge=0)
    nombre_heures_travailless: float = Field(..., ge=0)

    # Exemple pour la doc interactive /docs
    class Config:
        json_schema_extra = {
            "example": {
                "id_employe": 101,
                "age": 35,
                "salaire": 45000.0,
                "nombre_employee_sous_responsabilite": 2,
                "nombre_heures_travailless": 39.0
            }
        }