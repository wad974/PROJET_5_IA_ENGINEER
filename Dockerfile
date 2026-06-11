FROM python:3.13

# 1. En tant que root : créer l'utilisateur ET donner les droits
RUN useradd -m -u 1000 user
WORKDIR /app
RUN chown user:user /app  # ✅ Exécuté en root

# 2. Basculer sur l'utilisateur non-root
USER user
ENV PATH=/home/user/.local/bin:$PATH

# 3. Copier et installer les dépendances
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copier les fichiers
COPY --chown=user:user . .
COPY --chown=user:user params/config.ini /app/params/
COPY --chown=user:user ./bdd/dump-projet5-202606042043.sql /app/bdd/dump.sql

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]