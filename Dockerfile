# Dockerfile
FROM python:3.11-slim

# Métadonnées OCI
LABEL org.opencontainers.image.source="https://github.com/DavidCouronne/youtube-downloader"
LABEL org.opencontainers.image.description="YouTube Downloader Web App with FastAPI"
LABEL org.opencontainers.image.licenses="MIT"

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installation de uv (gestionnaire Python rapide)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Création du répertoire de travail
WORKDIR /app

# Copie des fichiers de requirements en premier (cache Docker)
COPY requirements.txt /app/

# Installation des dépendances Python
RUN uv pip install --system -r requirements.txt && \
    uv pip install --system yt-dlp

# Copie des fichiers de l'application
COPY app.py /app/
COPY config.toml /app/

# Création du dossier de téléchargement
RUN mkdir -p /downloads

# Utilisateur non-root pour la sécurité
RUN useradd -m -u 1000 ytdl && \
    chown -R ytdl:ytdl /app /downloads
USER ytdl

# Exposition du port
EXPOSE 8000

# Variables d'environnement
ENV DOWNLOAD_DIR=/downloads
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Commande de démarrage
CMD ["python", "app.py"]