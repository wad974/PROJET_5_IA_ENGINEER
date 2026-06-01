---
title: API Prediction Attrition
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
sdk_version: "latest"
python_version: "3.13"
app_file: app.py
pinned: false
---

# 🚀 Projet 5 : API de Prédiction d'Attrition des Employés — AI Engineer

Ce dépôt héberge l'architecture complète d'une API REST développée avec **FastAPI**. L'objectif principal du projet est de centraliser, nettoyer et consolider les données provenant de plusieurs systèmes d'information (RH, Évaluations et Sondages) afin d'entraîner un modèle de Machine Learning capable de prédire l'attrition des employés (risque de démission) et d'exposer ces prédictions via un endpoint de prédiction unitaire.

---

## 🏗️ Architecture du Projet

Le projet adopte une architecture modulaire séparant clairement la couche d'accès aux données, la validation métier, le pipeline de Machine Learning et la suite de tests automatisés.

```text
├── data/                  # Stockage local des fichiers CSV téléversés
├── model/
│   └── EmployeeInput.py   # Schéma de validation Pydantic complet (35 variables)
├── src/
│   ├── database.py        # Gestion de la connexion SQLAlchemy et tests de connectivité
│   ├── data_fetch.py      # Extraction, nettoyage et consolidation des tables SQL
│   ├── load_csv.py        # Logique d'ingestion et d'initialisation des données
│   └── train_model.py     # Pipeline d'entraînement, preprocessing et calcul du F1-score
├── tests/
│   ├── test_main.py       # Suite de tests unitaires et d'intégration (100 % mockée)
│   └── test_train_model.py# Tests dédiés au pipeline d'entraînement
├── docker-compose.yml     # Configuration PostgreSQL
├── main.py                # Point d'entrée de l'API
├── pytest.ini             # Configuration Pytest
└── requirements.txt       # Dépendances Python
```

## 🛠️ Installation et Déploiement

### 1. Prérequis

- Python 3.13+
- Docker
- Docker Compose

### 2. Lancement de l'infrastructure de données

Le projet s'appuie sur une instance PostgreSQL exécutée via Docker.

```bash
docker compose up -d
```

## 3. Environnement Virtuel et Dépendances

Activez votre environnement virtuel et installez l'ensemble des modules requis :

```bash
python -m venv env

source env/bin/activate  # Sur Linux/macOS
# ou : env\Scripts\activate sur Windows

pip install -r requirements.txt
```

## 4. Démarrage de l'API

```bash
python main.py
```

L'API s'exécute par défaut à l'adresse suivante :

```text
http://localhost:7860
```

# 🔌 Spécifications de l'API REST

L'API applique les principes de conception **HATEOAS (Hypermedia As The Engine Of Application State)**.

La route racine (`/`) expose dynamiquement le catalogue complet des fonctionnalités et des hyperliens mis à jour selon l'hôte.

## Liste des Endpoints

| Domaine | Méthode | Route | Description |
|----------|----------|----------|----------|
| Navigation | GET | `/` | Catalogue dynamique des routes et accès à la documentation |
| Système | GET | `/health` | Vérification de la disponibilité opérationnelle de l'API |
| Système | GET | `/db-test` | Test d'interconnexion avec l'instance PostgreSQL |
| Données | GET | `/load-csv` | Ingestion et synchronisation des données initiales vers la DB |
| Données | POST | `/upload-csv` | Téléversement de fichiers multipart `.csv` dans l'espace de stockage |
| Machine Learning | POST | `/train-model` | Exécution du pipeline de traitement, entraînement et mise en cache. Retourne le F1-Score au format JSON |
| Machine Learning | POST | `/predict` | Prédiction d'attrition unitaire via le Query Parameter `id_employee` |

> 💡 **Interface Interactive** : La documentation Swagger complète et interactive est disponible en continu sur la route `/docs`.

# 🗄️ Couche d'Accès aux Données & Consolidation SQL

Pour éviter toute désynchronisation et centraliser la logique métier, l'extraction de l'échantillon global est gérée directement dans le moteur de base de données via la fonction `get_data_from_db()`.

Un double `LEFT JOIN` consolide les tables `sirh`, `eval` et `sondage`. La jointure résout dynamiquement le formatage hétérogène des identifiants (chaînes de caractères de type `'E_1'` converties pour correspondre aux entiers de la table principale) :

```sql
SELECT *
FROM public.sirh s
LEFT JOIN public.eval e
    ON CAST(REPLACE(e.eval_number, 'E_', '') AS INTEGER) = s.id_employee
LEFT JOIN public.sondage so
    ON so.code_sondage = s.id_employee;
```

# 📐 Validation Métier (`EmployeeInput`)

La robustesse du point de terminaison `/predict` est garantie par un modèle de validation **Pydantic** strict composé de 35 variables caractérisant de manière exhaustive la situation démographique, professionnelle et psychologique de l'employé.

```python
# Extrait du schéma de validation (model/EmployeeInput.py)

class EmployeeInput(BaseModel):
    id_employee: int = Field(..., description="ID unique de l'employé")
    age: int = Field(..., ge=18, le=100)
    revenu_mensuel: float = Field(..., ge=0)
    nombre_heures_travailless: float = Field(..., ge=0)
    satisfaction_employee_environnement: int = Field(..., ge=1, le=5)
    heure_supplementaires: bool

    # ... (Modèle complet de 35 variables métier)
```

# 🧪 Stratégie de Test et Intégration Continue (CI/CD)

Le projet intègre une suite de tests unitaires et d'intégration configurée pour s'exécuter de manière **100 % isolée et autonome**.

Afin de garantir une intégration continue fluide (notamment lors de l'exécution des workflows GitHub Actions) sans contraindre l'environnement de build à instancier ou exposer une base de données PostgreSQL en ligne, l'intégralité des flux de données et des artefacts de modèle (*StandardScaler*, estimateurs) sont substitués par des **Mocks** (`unittest.mock.patch`).

## Exécution locale de la suite de tests

```bash
pytest
```

## Comportements validés

### ✅ Comportement Nominal des Routes de Base
Validation des statuts `200 OK` sur l'index et le healthcheck.

### ✅ Isolation des États du Modèle
Levée systématique d'une erreur `503 Service Unavailable` si l'endpoint de prédiction est sollicité alors que le modèle global n'a pas encore été initialisé par `/train-model`.

### ✅ Validation de l'Entraînement
Vérification de l'extraction, du calcul du F1-score et de la bonne injection des objets entraînés dans le scope de l'application.

### ✅ Prédiction et Typage Pydantic
Simulation d'une structure de données complète (35 variables en dur) pour valider la réponse `200 OK` et le format de la réponse de prédiction.

### ✅ Gestion des Exceptions Métier
Retour d'un code statut `404 Not Found` lorsqu'un identifiant utilisateur est absent de la base consolidée.