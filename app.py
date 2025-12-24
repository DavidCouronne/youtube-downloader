#!/usr/bin/env python3
"""
YouTube Downloader Web App
Usage: uv run app.py
Puis accédez à http://localhost:8000 ou http://IP-LOCAL:8000
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import subprocess
import tomllib
from pathlib import Path
from datetime import datetime
import asyncio
import json
from typing import Optional

app = FastAPI(title="YouTube Downloader")

# Configuration
CONFIG_FILE = "config.toml"
with open(CONFIG_FILE, "rb") as f:
    config = tomllib.load(f)

DOWNLOAD_DIR = Path(config["dossier"]["download_dir"])
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Historique des téléchargements
downloads_history = []

class DownloadRequest(BaseModel):
    url: str

class DownloadStatus(BaseModel):
    id: str
    url: str
    status: str  # pending, downloading, completed, error
    progress: str
    timestamp: str
    error: Optional[str] = None

def is_playlist(url: str) -> bool:
    return "playlist" in url.lower() or "list=" in url.lower()

def download_video(download_id: str, url: str):
    """Télécharge une vidéo en arrière-plan"""
    
    # Mise à jour du statut
    for dl in downloads_history:
        if dl["id"] == download_id:
            dl["status"] = "downloading"
            dl["progress"] = "Démarrage..."
            break
    
    # Construction de la commande
    is_pl = is_playlist(url)
    quality = config["qualite"]["cible"]
    max_videos = config["playlists"].get("max_videos", 30)
    sleep = config["autres"].get("sleep_seconds", 5)
    
    cmd = [
        "uv", "run", "yt-dlp",
        "--remote-components", "ejs:github",
        "-f", f"bestvideo[height<={quality}]+bestaudio/best/worst",
        "--sleep-interval", str(sleep),
        "--newline",
        "--progress",
    ]
    
    if is_pl:
        cmd.extend(["-o", f"{DOWNLOAD_DIR}/%(playlist_title)s/%(playlist_index)s - %(title)s [%(id)s].%(ext)s"])
        if max_videos > 0:
            cmd.extend(["--playlist-end", str(max_videos)])
    else:
        cmd.extend(["-o", f"{DOWNLOAD_DIR}/videos-uniques/%(title)s [%(id)s].%(ext)s"])
        cmd.append("--no-playlist")
    
    cmd.append(url)
    
    try:
        # Lancement du processus
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Lecture de la progression ligne par ligne
        current_video = ""
        for line in process.stdout:
            line = line.strip()
            
            # Détection du titre de la vidéo
            if "Downloading item" in line or "Extracting URL" in line:
                current_video = line
                for dl in downloads_history:
                    if dl["id"] == download_id:
                        dl["progress"] = line
                        break
            
            # Détection de la progression de téléchargement
            elif "[download]" in line and "%" in line:
                # Extraire juste la partie pertinente
                if "ETA" in line or "at" in line:
                    parts = line.split()
                    percentage = next((p for p in parts if "%" in p), "")
                    size = next((p for p in parts if "iB" in p), "")
                    progress_info = f"⬇️ {percentage} {size}"
                else:
                    progress_info = line
                
                for dl in downloads_history:
                    if dl["id"] == download_id:
                        dl["progress"] = progress_info
                        break
            
            # Autres infos utiles
            elif "[info]" in line:
                for dl in downloads_history:
                    if dl["id"] == download_id:
                        dl["progress"] = line.replace("[info]", "ℹ️")
                        break
        
        process.wait()
        
        # Vérification du résultat
        if process.returncode == 0:
            for dl in downloads_history:
                if dl["id"] == download_id:
                    dl["status"] = "completed"
                    dl["progress"] = "✅ Téléchargement terminé"
                    break
        else:
            raise Exception(f"Code d'erreur {process.returncode}")
            
    except Exception as e:
        for dl in downloads_history:
            if dl["id"] == download_id:
                dl["status"] = "error"
                dl["error"] = str(e)
                dl["progress"] = ""
                break

@app.get("/", response_class=HTMLResponse)
async def home():
    """Interface principale"""
    html = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>YouTube Downloader</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
            }
            .card {
                background: white;
                border-radius: 16px;
                padding: 32px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                margin-bottom: 24px;
            }
            h1 {
                color: #667eea;
                margin-bottom: 8px;
                font-size: 32px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 24px;
                font-size: 14px;
            }
            .input-group {
                margin-bottom: 16px;
            }
            input {
                width: 100%;
                padding: 14px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.3s;
            }
            input:focus {
                outline: none;
                border-color: #667eea;
            }
            button {
                width: 100%;
                padding: 14px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
            }
            button:active {
                transform: translateY(0);
            }
            button:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            .history {
                max-height: 400px;
                overflow-y: auto;
            }
            .download-item {
                padding: 16px;
                border-bottom: 1px solid #e0e0e0;
                animation: slideIn 0.3s ease;
            }
            .download-item:last-child {
                border-bottom: none;
            }
            @keyframes slideIn {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .status {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
                margin-left: 8px;
            }
            .status-pending { background: #fff3cd; color: #856404; }
            .status-downloading { background: #cfe2ff; color: #084298; }
            .status-completed { background: #d1e7dd; color: #0f5132; }
            .status-error { background: #f8d7da; color: #842029; }
            .url-text {
                color: #666;
                font-size: 14px;
                word-break: break-all;
                margin-top: 4px;
            }
            .progress {
                color: #667eea;
                font-size: 13px;
                margin-top: 8px;
                font-family: monospace;
            }
            .error-text {
                color: #dc3545;
                font-size: 13px;
                margin-top: 4px;
            }
            .empty-state {
                text-align: center;
                color: #999;
                padding: 40px;
            }
            .info-banner {
                background: #e7f3ff;
                border-left: 4px solid #667eea;
                padding: 12px 16px;
                border-radius: 4px;
                margin-bottom: 24px;
                font-size: 14px;
                color: #004085;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <h1>📥 YouTube Downloader</h1>
                <p class="subtitle">Téléchargez des vidéos et playlists YouTube</p>
                
                <div class="info-banner">
                    📁 Les fichiers seront sauvegardés dans: <code>./download/</code>
                </div>
                
                <div class="input-group">
                    <input 
                        type="text" 
                        id="urlInput" 
                        placeholder="https://youtube.com/watch?v=... ou playlist URL"
                        autocomplete="off"
                    >
                </div>
                
                <button onclick="submitDownload()" id="submitBtn">
                    Télécharger
                </button>
            </div>
            
            <div class="card">
                <h2 style="margin-bottom: 16px; color: #333;">📜 Historique</h2>
                <div class="history" id="history">
                    <div class="empty-state">Aucun téléchargement pour le moment</div>
                </div>
            </div>
        </div>
        
        <script>
            const urlInput = document.getElementById('urlInput');
            const submitBtn = document.getElementById('submitBtn');
            const historyDiv = document.getElementById('history');
            
            // Auto-focus sur l'input
            urlInput.focus();
            
            // Soumettre avec Entrée
            urlInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') submitDownload();
            });
            
            async function submitDownload() {
                const url = urlInput.value.trim();
                if (!url) {
                    alert('⚠️ Veuillez entrer une URL');
                    return;
                }
                
                if (!url.includes('youtube.com') && !url.includes('youtu.be')) {
                    alert('⚠️ URL YouTube invalide');
                    return;
                }
                
                submitBtn.disabled = true;
                submitBtn.textContent = 'Ajout en cours...';
                
                try {
                    const response = await fetch('/download', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ url })
                    });
                    
                    if (response.ok) {
                        urlInput.value = '';
                        loadHistory();
                    } else {
                        const error = await response.json();
                        alert('❌ Erreur: ' + error.detail);
                    }
                } catch (error) {
                    alert('❌ Erreur réseau: ' + error.message);
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Télécharger';
                }
            }
            
            async function loadHistory() {
                try {
                    const response = await fetch('/history');
                    const data = await response.json();
                    
                    if (data.length === 0) {
                        historyDiv.innerHTML = '<div class="empty-state">Aucun téléchargement pour le moment</div>';
                        return;
                    }
                    
                    historyDiv.innerHTML = data.map(item => `
                        <div class="download-item">
                            <div>
                                <strong>${item.timestamp}</strong>
                                <span class="status status-${item.status}">${getStatusText(item.status)}</span>
                            </div>
                            <div class="url-text">${truncateUrl(item.url)}</div>
                            ${item.progress ? `<div class="progress">${item.progress}</div>` : ''}
                            ${item.error ? `<div class="error-text">⚠️ ${item.error}</div>` : ''}
                        </div>
                    `).join('');
                } catch (error) {
                    console.error('Erreur chargement historique:', error);
                }
            }
            
            function getStatusText(status) {
                const texts = {
                    pending: '⏳ En attente',
                    downloading: '⬇️ Téléchargement',
                    completed: '✓ Terminé',
                    error: '❌ Erreur'
                };
                return texts[status] || status;
            }
            
            function truncateUrl(url) {
                return url.length > 60 ? url.substring(0, 60) + '...' : url;
            }
            
            // Actualiser l'historique toutes les 2 secondes
            setInterval(loadHistory, 2000);
            loadHistory();
        </script>
    </body>
    </html>
    """
    return html

@app.post("/download")
async def add_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    """Ajoute un téléchargement à la file"""
    
    url = request.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL manquante")
    
    if "youtube.com" not in url and "youtu.be" not in url:
        raise HTTPException(status_code=400, detail="URL YouTube invalide")
    
    # Créer un ID unique
    download_id = f"dl_{len(downloads_history)}_{int(datetime.now().timestamp())}"
    
    # Ajouter à l'historique
    download_entry = {
        "id": download_id,
        "url": url,
        "status": "pending",
        "progress": "",
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "error": None
    }
    downloads_history.insert(0, download_entry)
    
    # Lancer le téléchargement en arrière-plan
    background_tasks.add_task(download_video, download_id, url)
    
    return {"success": True, "id": download_id}

@app.get("/history")
async def get_history():
    """Récupère l'historique des téléchargements"""
    return downloads_history[:20]  # Limiter aux 20 derniers

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 YouTube Downloader démarré !")
    print("="*60)
    print(f"📁 Dossier de téléchargement: {DOWNLOAD_DIR.absolute()}")
    print(f"🌐 Interface web: http://localhost:8000")
    print(f"🌐 Accès réseau local: http://<IP-locale>:8000")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)