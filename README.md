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

### Prérequis

- Docker/Podman installé
- Pour Podman Quadlet : systemd user services activés

### Option 1 : Docker/Podman Compose (Simple)

```bash
# Créer la structure
mkdir -p ~/youtube-downloader/{config,downloads}

# Créer le fichier de configuration
cat > ~/youtube-downloader/config/config.toml << 'EOF'
[dossier]
download_dir = "/downloads"

[qualite]
cible = "360"
format = "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/worst"

[playlists]
max_videos = 10

[autres]
sleep_seconds = 5
EOF

# Télécharger le docker-compose.yml
cd ~/youtube-downloader
curl -O https://raw.githubusercontent.com/DavidCouronne/youtube-downloader/main/docker-compose.yml

# Lancer
docker compose up -d

# Ou avec Podman
podman compose up -d
```

Accédez à http://localhost:8000

### Option 2 : Podman Quadlet (Production - CachyOS, Arch, Fedora)

Pour une intégration systemd native avec auto-restart et auto-update :

#### 1. Créer la structure des dossiers

```bash
# Dossiers de configuration et téléchargements
mkdir -p ~/youtube-downloader/config
mkdir -p ~/jellyfin/media/youtube

# Créer le fichier de configuration
cat > ~/youtube-downloader/config/config.toml << 'EOF'
[dossier]
download_dir = "/downloads"

[qualite]
cible = "360"
format = "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/worst"

[playlists]
max_videos = 10

[autres]
sleep_seconds = 5
EOF
```

#### 2. Créer le fichier Quadlet

```bash
mkdir -p ~/.config/containers/systemd

cat > ~/.config/containers/systemd/youtube-downloader.container << 'EOF'
[Unit]
Description=YouTube Downloader Web App
After=network-online.target
Wants=network-online.target

[Container]
Image=ghcr.io/davidcouronne/youtube-downloader:latest
ContainerName=youtube-downloader

# Volumes - AJUSTEZ les chemins selon votre configuration
Volume=%h/jellyfin/media/youtube:/downloads:Z,rw
Volume=%h/youtube-downloader/config:/config:Z,ro

# Port
PublishPort=8000:8000

# Variables d'environnement
Environment=DOWNLOAD_DIR=/downloads
Environment=CONFIG_FILE=/config/config.toml
Environment=TZ=Europe/Zurich

# Auto-update
AutoUpdate=registry

[Service]
Restart=always
TimeoutStartSec=900

[Install]
WantedBy=multi-user.target default.target
EOF
```

#### 3. Activer et démarrer le service

```bash
# Recharger systemd
systemctl --user daemon-reload

# Activer le lingering (démarrage au boot)
loginctl enable-linger $USER

# Démarrer le service
systemctl --user start youtube-downloader

# Vérifier le statut
systemctl --user status youtube-downloader

# Voir les logs
journalctl --user -xeu youtube-downloader -f
```

#### 4. Vérification

```bash
# Vérifier que le container tourne
podman ps | grep youtube

# Tester l'interface
curl http://localhost:8000

# Ou ouvrir dans le navigateur
xdg-open http://localhost:8000
```

### Option 3 : Test manuel rapide

```bash
# Créer les dossiers
mkdir -p ~/youtube-downloader/{config,downloads}

# Créer la config (voir ci-dessus)

# Lancer le container manuellement
podman run -d --name youtube-downloader \
  -p 8000:8000 \
  -v ~/youtube-downloader/downloads:/downloads:Z \
  -v ~/youtube-downloader/config:/config:Z,ro \
  -e DOWNLOAD_DIR=/downloads \
  -e CONFIG_FILE=/config/config.toml \
  -e TZ=Europe/Zurich \
  --restart unless-stopped \
  ghcr.io/davidcouronne/youtube-downloader:latest
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

### Structure des dossiers

Avant de lancer le container, créez la structure suivante :

```bash
# Créer les dossiers nécessaires
mkdir -p ~/youtube-downloader/config
mkdir -p ~/jellyfin/media/youtube

# Créer le fichier de configuration
nano ~/youtube-downloader/config/config.toml
```

Contenu du `config.toml` :

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

### Variables d'environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `DOWNLOAD_DIR` | `/downloads` | Dossier de destination |
| `CONFIG_FILE` | `/config/config.toml` | Chemin du fichier de config |
| `TZ` | `UTC` | Fuseau horaire |

**Note** : Les paramètres `MAX_PLAYLIST_VIDEOS` et `VIDEO_QUALITY` sont définis dans le fichier `config.toml` monté en volume.

### Personnalisation avancée

Le fichier `config.toml` supporte les options suivantes :

```toml
[dossier]
download_dir = "/downloads"

[qualite]
cible = "360"  # ou 480, 720, 1080
format = "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/worst"

[playlists]
max_videos = 10  # 0 = illimité

[autres]
sleep_seconds = 5  # Pause entre téléchargements
```

Ce fichier doit être monté dans `/config/config.toml` du container.

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
# Statut du service
systemctl --user status youtube-downloader

# Logs en temps réel
journalctl --user -xeu youtube-downloader -f

# Redémarrer
systemctl --user restart youtube-downloader

# Arrêter
systemctl --user stop youtube-downloader

# Désactiver
systemctl --user disable youtube-downloader

# Vérifier les erreurs Quadlet
journalctl --user -xe | grep -i quadlet
```

### Docker/Podman

```bash
# Logs
docker logs -f youtube-downloader
# ou
podman logs -f youtube-downloader

# Redémarrer
docker restart youtube-downloader

# Accéder au shell
docker exec -it youtube-downloader sh

# Vérifier les volumes
docker inspect youtube-downloader | grep -A 10 Mounts
```

### Mise à jour

```bash
# Avec Podman Quadlet (auto-update activé)
podman auto-update

# Activer les vérifications automatiques quotidiennes
systemctl --user enable --now podman-auto-update.timer

# Avec Docker Compose
docker compose pull
docker compose up -d
```

### Debug

```bash
# Test manuel du container
podman run --rm -it -p 8000:8000 \
  -v ~/jellyfin/media/youtube:/downloads:Z \
  -v ~/youtube-downloader/config:/config:Z,ro \
  ghcr.io/davidcouronne/youtube-downloader:latest

# Vérifier les permissions des volumes
ls -laZ ~/jellyfin/media/youtube/
ls -laZ ~/youtube-downloader/config/

# Tester la connexion
curl http://localhost:8000
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