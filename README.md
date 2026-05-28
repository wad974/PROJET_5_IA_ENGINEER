---
title: Projet 5 IA Engineer
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 📊 Projet 5 IA Engineer - Prédiction d'Attrition

## Description
Ce projet a pour objectif de prédire le risque de départ des employés (attrition) en utilisant un modèle de Machine Learning (RandomForest) entraîné via Scikit-Learn. L'application est industrialisée avec une API FastAPI, testée automatiquement via GitHub Actions (CI/CD) et déployée dans un conteneur Docker sur Hugging Face Spaces.

## Structure du projet
- `src/` : Contient le code source de traitement et d'entraînement (`train_model.py`)
- `tests/` : Contient les tests unitaires Pytest pour valider le pipeline
- `notebooks/` : Contient les phases de recherche et d'analyse exploratoire
- `main.py` : Le point d'entrée de l'API FastAPI lancé par Uvicorn
- `Dockerfile` : Instructions de build pour l'environnement de production Hugging Face
- `pytest.ini` : Configuration du PYTHONPATH pour la reconnaissance des modules

## Installation et Lancement Local

1. **Cloner le projet**
```bash
git clone <lien-de-ton-repo>
cd PROJET_5_IA_ENGINEER