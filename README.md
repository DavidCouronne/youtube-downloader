# YouTube Downloader Web App

[![GitHub Container Registry](https://img.shields.io/badge/ghcr.io-youtube--downloader-blue)](https://github.com/DavidCouronne/youtube-downloader/pkgs/container/youtube-downloader)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Podman Quadlet](https://img.shields.io/badge/Podman-Quadlet-892CA0)](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html)

Une interface web moderne pour télécharger des vidéos et playlists YouTube, optimisée pour Jellyfin et Podman Quadlet.

## ✨ Fonctionnalités

- 🎯 **Interface web intuitive** - Copier-coller une URL et c'est parti
- 📊 **Suivi en temps réel** - Progression des téléchargements visible instantanément
- 🎬 **Vidéos & Playlists** - Support complet des vidéos uniques et playlists
- 📁 **Organisation automatique** - Structure de dossiers prête pour Jellyfin
- 🐋 **Conteneurisé** - Image Docker/Podman légère et sécurisée
- ⚙️ **Podman Quadlet** - Intégration systemd native
- 🔄 **Auto-restart** - Redémarre automatiquement après un reboot

## 🚀 Démarrage rapide

### Option 1 : Docker/Podman Compose (Simple)

```bash
# Télécharger le docker-compose.yml
curl -O https://raw.githubusercontent.com/DavidCouronne/youtube-downloader/main/docker-compose.yml

# Lancer
docker compose up -d

# Ou avec Podman
podman compose up -d
```

Accédez à http://localhost:8000

### Option 2 : Podman Quadlet (Production)

Pour CachyOS, Arch, Fedora ou toute distribution avec systemd :

```bash
# 1. Créer le fichier Quadlet
mkdir -p ~/.config/containers/systemd
nano ~/.config/containers/systemd/youtube-downloader.container
```

Collez cette configuration :

```ini
[Unit]
Description=YouTube Downloader Web App
After=network-online.target

[Container]
Image=ghcr.io/davidcouronne/youtube-downloader:latest
ContainerName=youtube-downloader

# Montez votre dossier Jellyfin (ajustez le chemin)
Volume=%h/jellyfin/media/youtube:/downloads:Z,rw

PublishPort=8000:8000

Environment=TZ=Europe/Zurich
Restart=always

[Service]
Restart=always
TimeoutStartSec=900

[Install]
WantedBy=multi-user.target default.target
```

Activez le service :

```bash
systemctl --user daemon-reload
systemctl --user enable --now youtube-downloader.container
```

## 📁 Structure des téléchargements

```
/downloads/
├── videos-uniques/
│   └── Titre de la vidéo [ID].mp4
└── Nom de la Playlist/
    ├── 1 - Première vidéo [ID].mp4
    ├── 2 - Deuxième vidéo [ID].mp4
    └── ...
```

## ⚙️ Configuration

### Variables d'environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `DOWNLOAD_DIR` | `/downloads` | Dossier de destination |
| `TZ` | `UTC` | Fuseau horaire |
| `MAX_PLAYLIST_VIDEOS` | `10` | Limite de vidéos par playlist |
| `VIDEO_QUALITY` | `360` | Hauteur max en pixels |

### Personnalisation avancée

Créez un fichier `config.toml` personnalisé :

```toml
[dossier]
download_dir = "/downloads"

[qualite]
cible = "360"
format = "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/worst"

[playlists]
max_videos = 10

[autres]
sleep_seconds = 5
```

Montez-le dans le container :

```bash
-v ./config.toml:/app/config.toml:ro
```

## 🎬 Intégration Jellyfin

### 1. Installer le plugin YouTube Metadata

```bash
# Dans Jellyfin : Tableau de bord → Plugins → Dépôts
# Ajoutez ce dépôt :
https://raw.githubusercontent.com/ankenyr/jellyfin-youtube-metadata-plugin/master/manifest.json
```

### 2. Créer une bibliothèque YouTube

1. **Tableau de bord** → **Bibliothèques** → **Ajouter**
2. Type : **Séries**
3. Dossier : `/chemin/vers/downloads/`
4. **Agents de métadonnées** :
   - ✅ Activez **YouTube Metadata**
   - ❌ Désactivez TheTVDB, TMDb, etc.

Le plugin utilisera automatiquement les IDs YouTube `[...]` dans les noms de fichiers.

## 🛠️ Commandes utiles

### Podman Quadlet

```bash
# Statut
systemctl --user status youtube-downloader.container

# Logs en temps réel
journalctl --user -xeu youtube-downloader.container -f

# Redémarrer
systemctl --user restart youtube-downloader.container

# Arrêter
systemctl --user stop youtube-downloader.container

# Désactiver
systemctl --user disable youtube-downloader.container
```

### Docker/Podman

```bash
# Logs
docker logs -f youtube-downloader

# Redémarrer
docker restart youtube-downloader

# Accéder au shell
docker exec -it youtube-downloader sh
```

## 🔧 Développement

### Prérequis

- Python 3.11+
- uv (gestionnaire de paquets)
- ffmpeg

### Installation locale

```bash
git clone https://github.com/DavidCouronne/youtube-downloader.git
cd youtube-downloader

# Installer les dépendances
uv pip install -r requirements.txt

# Lancer l'app
uv run app.py
```

### Build de l'image

```bash
# Docker
docker build -t youtube-downloader .

# Podman
podman build -t youtube-downloader .
```

## 📝 Notes légales

### ⚠️ Disclaimer important

**Cet outil est destiné à un usage personnel et éducatif uniquement.**

- ✅ Téléchargez **uniquement** du contenu dont vous possédez les droits ou qui est sous licence libre
- ✅ Respectez les conditions d'utilisation de YouTube et des autres plateformes
- ❌ Ne téléchargez **pas** de contenu protégé par le droit d'auteur sans autorisation
- ❌ L'utilisation abusive peut entraîner la suspension de votre compte YouTube

**L'auteur décline toute responsabilité en cas d'utilisation inappropriée de cet outil.**

### Licences des composants

| Composant | Licence | Lien |
|-----------|---------|------|
| YouTube Downloader | MIT | [LICENSE](LICENSE) |
| yt-dlp | Unlicense | [yt-dlp/LICENSE](https://github.com/yt-dlp/yt-dlp/blob/master/LICENSE) |
| FastAPI | MIT | [fastapi/LICENSE](https://github.com/fastapi/fastapi/blob/master/LICENSE) |
| ffmpeg | Varie (GPL/LGPL) | [ffmpeg.org/legal](https://ffmpeg.org/legal.html) |

## 🤝 Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📜 Changelog

### v1.0.0 (2025-01-XX)

- ✨ Interface web avec FastAPI
- 📊 Suivi de progression en temps réel
- 🐋 Support Docker/Podman
- ⚙️ Configuration Podman Quadlet
- 📁 Organisation automatique pour Jellyfin

## 🙏 Remerciements

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Le meilleur téléchargeur YouTube
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderne
- [Jellyfin YouTube Metadata Plugin](https://github.com/ankenyr/jellyfin-youtube-metadata-plugin) - Métadonnées YouTube pour Jellyfin

## 📧 Contact

David Couronne - [@DavidCouronne](https://github.com/DavidCouronne)

Lien du projet : [https://github.com/DavidCouronne/youtube-downloader](https://github.com/DavidCouronne/youtube-downloader)

---

**⭐ Si ce projet vous est utile, n'oubliez pas de lui donner une étoile !**