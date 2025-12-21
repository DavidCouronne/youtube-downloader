#!/usr/bin/env python3
import subprocess
import os
from pathlib import Path
import tomllib  # Python 3.11+

# Charger la config
CONFIG_FILE = "config.toml"
if not Path(CONFIG_FILE).exists():
    print(f"Erreur : {CONFIG_FILE} manquant. Crée-le avec [dossier], [qualite], [playlists]...")
    exit(1)

with open(CONFIG_FILE, "rb") as f:
    config = tomllib.load(f)

DOWNLOAD_DIR = Path(config["dossier"]["download_dir"])
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

URL_FILE = config["autres"].get("url_file", "a_telecharger.txt")
SLEEP = config["autres"].get("sleep_seconds", 5)

# Qualité
QUALITY_TARGET = config["qualite"]["cible"]
# Utiliser le format du config.toml si défini, sinon format par défaut
FORMAT = config["qualite"].get("format", f"bestvideo[height<={QUALITY_TARGET}]+bestaudio/best")

# Limite pour playlists
MAX_PLAYLIST_VIDEOS = config["playlists"].get("max_videos", 10)

def download_url(url: str):
    """Télécharge en basse qualité, avec fallback et limite playlist"""
    
    is_playlist = "playlist" in url.lower() or "list=" in url.lower()
    
    # Construction de la commande de base
    cmd = [
        "uv", "run", "yt-dlp",
        "--remote-components", "ejs:github",  # Résout les défis JS YouTube
        "-f", FORMAT,
        "--write-info-json",
        "--write-thumbnail",
        "--embed-thumbnail",
        "--sleep-interval", str(SLEEP),
    ]
    
    # Pattern de sortie selon le type
    if is_playlist:
        cmd.extend(["-o", f"{DOWNLOAD_DIR}/%(playlist_title)s/%(playlist_index)s - %(title)s [%(id)s].%(ext)s"])
    else:
        cmd.extend(["-o", f"{DOWNLOAD_DIR}/%(title)s [%(id)s].%(ext)s"])
        cmd.append("--no-playlist")  # Ajout conditionnel propre
    
    # Limite pour playlists
    if is_playlist and MAX_PLAYLIST_VIDEOS > 0:
        cmd.extend(["--playlist-end", str(MAX_PLAYLIST_VIDEOS)])
    
    # URL en dernier
    cmd.append(url)
    
    print(f"Téléchargement : {url}")
    if is_playlist and MAX_PLAYLIST_VIDEOS > 0:
        print(f"   → Limité à {MAX_PLAYLIST_VIDEOS} dernières vidéos")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erreur sur {url} : {e}")

def main():
    if not Path(URL_FILE).exists():
        print(f"Erreur : {URL_FILE} n'existe pas. Crée-le avec une URL par ligne.")
        return
    
    with open(URL_FILE, "r") as f:
        urls = [line.strip() for line in f if line.strip()]
    
    if not urls:
        print("Aucune URL à télécharger.")
        return
    
    for url in urls:
        download_url(url)
    
    print("\nTéléchargements terminés ! Lance un scan dans Jellyfin.")

if __name__ == "__main__":
    main()