# 1. Utiliser une image Python officielle
FROM python:3.9-slim

# 2. Définir le dossier de travail dans le conteneur
WORKDIR /app

# 3. Copier le fichier des dépendances
COPY requirements.txt .

# 4. Installer les bibliothèques
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copier tout le reste du projet dans le conteneur
COPY . .

# 6. Exposer le port utilisé par Flask (5000)
EXPOSE 5000

# 7. Lancer l'application
CMD ["python", "app.py"]