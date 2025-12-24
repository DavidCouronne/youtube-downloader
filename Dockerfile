# Dockerfile - Version simplifiée avec uv
FROM python:3.11-slim

# Métadonnées OCI
LABEL org.opencontainers.image.source="https://github.com/DavidCouronne/youtube-downloader"
LABEL org.opencontainers.image.description="YouTube Downloader Web App with FastAPI"
LABEL org.opencontainers.image.licenses="MIT"

# Installation de uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers
WORKDIR /app
COPY pyproject.toml /app/

# Installation des dépendances avec uv pip (pas de sync)
RUN uv pip install --system fastapi uvicorn[standard] pydantic yt-dlp

# Copie de l'application
COPY app.py /app/
COPY config.toml /app/

# Création des répertoires de volumes
RUN mkdir -p /downloads /config

# Utilisateur non-root
RUN useradd -m -u 1000 ytdl && \
    chown -R ytdl:ytdl /app /downloads /config
USER ytdl

EXPOSE 8000

ENV DOWNLOAD_DIR=/downloads
ENV CONFIG_FILE=/config/config.toml
ENV PYTHONUNBUFFERED=1

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Démarrage direct avec uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]