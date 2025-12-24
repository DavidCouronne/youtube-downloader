# Dockerfile - Optimisé avec uv moderne
FROM python:3.11-slim

# Métadonnées OCI
LABEL org.opencontainers.image.source="https://github.com/DavidCouronne/youtube-downloader"
LABEL org.opencontainers.image.description="YouTube Downloader Web App with FastAPI"
LABEL org.opencontainers.image.licenses="MIT"

# Installation de uv (méthode officielle)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copie de l'application
COPY . /app

# Installation des dépendances Python
WORKDIR /app
RUN uv sync --frozen --no-cache

# Création des répertoires de volumes
RUN mkdir -p /downloads /config

# Utilisateur non-root pour la sécurité
RUN useradd -m -u 1000 ytdl && \
    chown -R ytdl:ytdl /app /downloads /config
USER ytdl

# Exposition du port
EXPOSE 8000

# Variables d'environnement
ENV DOWNLOAD_DIR=/downloads
ENV CONFIG_FILE=/config/config.toml
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Commande de démarrage avec uv
CMD ["/app/.venv/bin/fastapi", "run", "app.py", "--port", "8000", "--host", "0.0.0.0"]