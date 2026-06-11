FROM python:3.13

# 1. On crée l'utilisateur exigé par Hugging Face (UID 1000)
RUN useradd -m -u 1000 user
WORKDIR /app
USER 1000

# 2. On change le propriétaire du dossier pour que l'utilisateur puisse écrire dedans
RUN chown user:user /app

# 3. On bascule sur cet utilisateur pour la suite
USER user
ENV PATH=/home/user/.local/bin:$PATH

# 4. Le reste de ton code reste identique 👍
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user:user . .
COPY --chown=1000:1000 params/config.ini /app/params/
COPY --chown=1000:1000 ./bdd/dump-projet5-202606042043.sql /app/bdd/dump.sql
COPY --chown=1000:1000 . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]