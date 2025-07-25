# 🚀 Guide de Déploiement QuantumShield avec VMware Workstation Pro

## 📋 Table des matières
1. [Prérequis](#prérequis)
2. [Configuration VMware](#configuration-vmware)
3. [Installation du Système d'exploitation](#installation-du-système-dexploitation)
4. [Configuration de l'environnement](#configuration-de-lenvironnement)
5. [Installation des dépendances](#installation-des-dépendances)
6. [Configuration de la base de données](#configuration-de-la-base-de-données)
7. [Déploiement du backend](#déploiement-du-backend)
8. [Déploiement du frontend](#déploiement-du-frontend)
9. [Test et vérification](#test-et-vérification)
10. [Dépannage](#dépannage)

---

## ⚙️ PRÉREQUIS

### 🖥️ Configuration Matérielle Minimale
- **RAM** : 8 GB minimum (16 GB recommandé)
- **Stockage** : 50 GB d'espace libre
- **Processeur** : Multi-core 64-bit (Intel i5/AMD Ryzen 5 minimum)
- **Réseau** : Connexion Internet stable

### 📦 Logiciels Requis
- **VMware Workstation Pro 17.x** (version récente)
- **Image ISO Ubuntu 22.04 LTS** ou version récente
- **Accès administrateur** sur votre machine hôte

---

## 🖥️ CONFIGURATION VMWARE

### Étape 1 : Création de la Machine Virtuelle

1. **Lancer VMware Workstation Pro**
2. **Cliquer sur "Create a New Virtual Machine"**
3. **Sélectionner "Typical (recommended)"**

### Étape 2 : Configuration de l'Image ISO

1. **Sélectionner "Installer disc image file (iso)"**
2. **Parcourir et sélectionner votre ISO Ubuntu 22.04 LTS**
3. **Cliquer "Next"**

### Étape 3 : Configuration Utilisateur

```bash
Full Name: QuantumShield Admin
User name: qsadmin
Password: [Choisir un mot de passe fort]
Confirm: [Confirmer le mot de passe]
```

### Étape 4 : Paramètres de la VM

```bash
Virtual machine name: QuantumShield-Ubuntu
Location: C:\Users\[VotreNom]\Documents\Virtual Machines\QuantumShield-Ubuntu
```

### Étape 5 : Configuration du Disque

```bash
Maximum disk size: 50 GB minimum (80 GB recommandé)
☑️ Split virtual disk into multiple files
```

### Étape 6 : Paramètres Matériels Personnalisés

**Avant de terminer, cliquer sur "Customize Hardware"**

#### Mémoire (RAM)
```bash
Memory: 4096 MB minimum (8192 MB recommandé)
```

#### Processeurs
```bash
Number of processors: 2
Number of cores per processor: 2
☑️ Virtualize Intel VT-x/EPT or AMD-V/RVI
☑️ Virtualize CPU performance counters
```

#### Réseau
```bash
Network connection: NAT
☑️ Connect at power on
```

#### USB Controller
```bash
☑️ USB 3.1
☑️ Share Bluetooth devices with the virtual machine
```

### Étape 7 : Finalisation
1. **Cliquer "Close" puis "Finish"**
2. **La VM va se créer et démarrer automatiquement**

---

## 💿 INSTALLATION DU SYSTÈME D'EXPLOITATION

### Étape 1 : Installation Ubuntu

1. **Attendre le démarrage de l'ISO Ubuntu**
2. **Sélectionner votre langue** (Français recommandé)
3. **Choisir "Installer Ubuntu"**

### Étape 2 : Configuration Réseau
```bash
☑️ Se connecter à Internet pendant l'installation
☑️ Installer des logiciels tiers (drivers propriétaires)
```

### Étape 3 : Partitionnement
```bash
Type d'installation: Effacer le disque et installer Ubuntu
☑️ Chiffrement LVM avancé (optionnel pour sécurité)
```

### Étape 4 : Localisation
```bash
Fuseau horaire: Europe/Paris (ou votre région)
Disposition du clavier: French - French (ou votre configuration)
```

### Étape 5 : Compte Utilisateur
```bash
Nom: QuantumShield Admin
Nom d'ordinateur: quantumshield-vm
Nom d'utilisateur: qsadmin
Mot de passe: [Votre mot de passe]
☑️ Demander le mot de passe pour ouvrir une session
```

### Étape 6 : Installation
- **Attendre la fin de l'installation (15-30 minutes)**
- **Redémarrer quand demandé**

---

## 🔧 CONFIGURATION DE L'ENVIRONNEMENT

### Étape 1 : Première Connexion

1. **Se connecter avec les identifiants créés**
2. **Ouvrir un terminal** (Ctrl+Alt+T)

### Étape 2 : Mise à jour du système

```bash
# Mise à jour des paquets
sudo apt update && sudo apt upgrade -y

# Installation d'outils essentiels
sudo apt install -y curl wget git unzip software-properties-common

# Redémarrer si nécessaire
sudo reboot
```

### Étape 3 : Installation des VMware Tools

1. **Dans VMware, aller dans "VM" > "Install VMware Tools"**
2. **Dans Ubuntu :**

```bash
# Monter le CD des VMware Tools
sudo mkdir /mnt/cdrom
sudo mount /dev/cdrom /mnt/cdrom

# Copier et installer
cd /tmp
sudo cp /mnt/cdrom/VMwareTools-*.tar.gz .
sudo tar -xzf VMwareTools-*.tar.gz
cd vmware-tools-distrib/
sudo ./vmware-install.pl

# Accepter toutes les options par défaut (Entrée)
# Redémarrer
sudo reboot
```

### Étape 4 : Configuration du réseau

```bash
# Vérifier la connectivité
ping -c 3 google.com

# Noter l'adresse IP de la VM
ip addr show
```

---

## 📦 INSTALLATION DES DÉPENDANCES

### Étape 1 : Installation Python 3.11

```bash
# Ajouter le repository Python
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Installer Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev
sudo apt install -y python3-pip python3.11-distutils

# Vérifier l'installation
python3.11 --version
```

### Étape 2 : Installation Node.js et Yarn

```bash
# Installer Node.js 18 LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Installer Yarn
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt update && sudo apt install -y yarn

# Vérifier les installations
node --version  # doit afficher v18.x.x
npm --version
yarn --version
```

### Étape 3 : Installation de MongoDB

```bash
# Importer la clé GPG MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Ajouter le repository MongoDB
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Installer MongoDB
sudo apt-get update
sudo apt-get install -y mongodb-org

# Démarrer et activer MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Vérifier le statut
sudo systemctl status mongod
```

### Étape 4 : Installation d'outils supplémentaires

```bash
# Éditeur de texte et outils de développement
sudo apt install -y nano vim code htop tree

# Gestionnaire de processus
sudo apt install -y supervisor

# Serveur web (optionnel pour test)
sudo apt install -y nginx

# Redis (pour le cache)
sudo apt install -y redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

---

## 🗄️ CONFIGURATION DE LA BASE DE DONNÉES

### Étape 1 : Configuration MongoDB

```bash
# Se connecter à MongoDB
mongo

# Dans le shell MongoDB, créer la base de données
use quantumshield
db.test.insertOne({message: "Database créée"})

# Créer un utilisateur (optionnel pour sécurité)
db.createUser({
  user: "qsadmin",
  pwd: "quantumshield2024",
  roles: [{role: "readWrite", db: "quantumshield"}]
})

# Quitter MongoDB
exit
```

### Étape 2 : Test de connexion

```bash
# Tester la connexion
mongo --eval "db.runCommand('ping')"
```

---

## 🔧 DÉPLOIEMENT DU BACKEND

### Étape 1 : Cloner le projet

```bash
# Aller dans le répertoire home
cd ~

# Cloner le projet (déjà fait si vous utilisez le dossier cloné)
# Le code est déjà dans /app, nous allons le copier
sudo cp -r /app ~/quantumshield
cd ~/quantumshield

# Changer les permissions
sudo chown -R $USER:$USER ~/quantumshield
```

### Étape 2 : Configuration de l'environnement Backend

```bash
cd ~/quantumshield/backend

# Créer un environnement virtuel Python
python3.11 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate

# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt
```

### Étape 3 : Configuration des variables d'environnement

```bash
# Modifier le fichier .env
nano .env
```

**Contenu du fichier .env :**
```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=quantumshield
SECRET_KEY=quantumshield_secret_key_2024_super_secure
BLOCKCHAIN_NODE_URL=http://localhost:8545
QS_TOKEN_CONTRACT_ADDRESS=0x123456789abcdef
NTRU_KEY_SIZE=2048
MINING_DIFFICULTY=4
REWARD_AMOUNT=10
```

### Étape 4 : Test du backend

```bash
# Dans le répertoire backend avec venv activé
python server.py

# Le serveur devrait démarrer sur http://localhost:8001
# Tester dans un autre terminal :
curl http://localhost:8001/api/health
```

**Si tout fonctionne, arrêter le serveur (Ctrl+C) et continuer**

---

## 🌐 DÉPLOIEMENT DU FRONTEND

### Étape 1 : Configuration Frontend

```bash
cd ~/quantumshield/frontend

# Installer les dépendances
yarn install
```

### Étape 2 : Configuration des variables d'environnement

```bash
# Vérifier le fichier .env
cat .env

# Le fichier devrait contenir :
# REACT_APP_BACKEND_URL=/api
```

### Étape 3 : Test du frontend en développement

```bash
# Dans le répertoire frontend
yarn start

# L'application devrait s'ouvrir sur http://localhost:3000
```

**Noter : Le frontend va se connecter au backend via proxy (défini dans package.json)**

---

## 🚀 CONFIGURATION POUR PRODUCTION

### Étape 1 : Configuration Supervisor pour Backend

```bash
# Créer le fichier de configuration Supervisor
sudo nano /etc/supervisor/conf.d/quantumshield-backend.conf
```

**Contenu du fichier :**
```ini
[program:quantumshield-backend]
command=/home/qsadmin/quantumshield/backend/venv/bin/python server.py
directory=/home/qsadmin/quantumshield/backend
user=qsadmin
group=qsadmin
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/quantumshield-backend.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=PYTHONPATH="/home/qsadmin/quantumshield/backend",PYTHONUNBUFFERED="1"
```

### Étape 2 : Démarrer Supervisor

```bash
# Recharger la configuration Supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Démarrer le service
sudo supervisorctl start quantumshield-backend

# Vérifier le statut
sudo supervisorctl status quantumshield-backend
```

### Étape 3 : Build de production Frontend

```bash
cd ~/quantumshield/frontend

# Créer un build de production
yarn build

# Le dossier build/ contient les fichiers statiques
```

### Étape 4 : Configuration Nginx

```bash
# Créer la configuration Nginx
sudo nano /etc/nginx/sites-available/quantumshield
```

**Contenu de la configuration :**
```nginx
server {
    listen 80;
    listen [::]:80;
    server_name localhost;

    # Frontend - Fichiers statiques
    root /home/qsadmin/quantumshield/frontend/build;
    index index.html;

    # Gestion des routes React
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    # Proxy pour l'API Backend
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    # Cache pour les assets statiques
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
}
```

### Étape 5 : Activer la configuration Nginx

```bash
# Créer un lien symbolique
sudo ln -s /etc/nginx/sites-available/quantumshield /etc/nginx/sites-enabled/

# Supprimer la configuration par défaut
sudo rm -f /etc/nginx/sites-enabled/default

# Tester la configuration
sudo nginx -t

# Redémarrer Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## 🧪 TEST ET VÉRIFICATION

### Étape 1 : Vérification des Services

```bash
# Vérifier MongoDB
sudo systemctl status mongod

# Vérifier Redis
sudo systemctl status redis-server

# Vérifier Supervisor
sudo supervisorctl status

# Vérifier Nginx
sudo systemctl status nginx

# Vérifier le backend QuantumShield
curl http://localhost:8001/api/health
```

### Étape 2 : Test de l'Application Complète

1. **Ouvrir un navigateur dans la VM**
2. **Aller sur `http://localhost`**
3. **L'interface QuantumShield devrait s'afficher**

### Étape 3 : Test des Fonctionnalités

```bash
# Test des endpoints API
curl -X GET http://localhost/api/health
curl -X GET http://localhost/api/dashboard/stats

# Les réponses devraient être en JSON
```

### Étape 4 : Accès depuis l'hôte

1. **Noter l'IP de la VM :**
```bash
ip addr show
# Noter l'adresse de la forme 192.168.x.x
```

2. **Depuis votre machine hôte, ouvrir un navigateur**
3. **Aller sur `http://[IP-de-la-VM]`**

---

## 🔍 DÉPANNAGE

### Problèmes Courants

#### 1. Backend ne démarre pas
```bash
# Vérifier les logs
sudo supervisorctl tail quantumshield-backend

# Vérifier manuellement
cd ~/quantumshield/backend
source venv/bin/activate
python server.py
```

#### 2. Frontend ne s'affiche pas
```bash
# Vérifier les permissions
sudo chown -R www-data:www-data /home/qsadmin/quantumshield/frontend/build

# Vérifier la configuration Nginx
sudo nginx -t
sudo systemctl status nginx
```

#### 3. Erreurs de base de données
```bash
# Vérifier MongoDB
sudo systemctl status mongod
mongo --eval "db.runCommand('ping')"

# Redémarrer si nécessaire
sudo systemctl restart mongod
```

#### 4. Problèmes de réseau
```bash
# Vérifier la connectivité
ping google.com

# Vérifier les ports
netstat -tlnp | grep :8001
netstat -tlnp | grep :80
```

### Logs utiles

```bash
# Logs Supervisor
sudo tail -f /var/log/supervisor/quantumshield-backend.log

# Logs Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Logs MongoDB
sudo tail -f /var/log/mongodb/mongod.log

# Logs système
sudo journalctl -f
```

---

## 📝 SCRIPTS UTILES

### Script de démarrage automatique

```bash
# Créer le script
nano ~/start-quantumshield.sh
```

**Contenu du script :**
```bash
#!/bin/bash

echo "🚀 Démarrage de QuantumShield..."

# Démarrer MongoDB
sudo systemctl start mongod

# Démarrer Redis
sudo systemctl start redis-server

# Démarrer Supervisor
sudo systemctl start supervisor

# Attendre que les services démarrent
sleep 5

# Démarrer le backend
sudo supervisorctl start quantumshield-backend

# Démarrer Nginx
sudo systemctl start nginx

echo "✅ QuantumShield démarré avec succès!"
echo "🌐 Accès : http://localhost"

# Afficher le statut
sudo supervisorctl status
```

```bash
# Rendre le script exécutable
chmod +x ~/start-quantumshield.sh

# Utiliser le script
~/start-quantumshield.sh
```

### Script d'arrêt

```bash
# Créer le script d'arrêt
nano ~/stop-quantumshield.sh
```

**Contenu :**
```bash
#!/bin/bash

echo "🛑 Arrêt de QuantumShield..."

# Arrêter le backend
sudo supervisorctl stop quantumshield-backend

# Arrêter Nginx
sudo systemctl stop nginx

# Arrêter Supervisor
sudo systemctl stop supervisor

# Arrêter Redis
sudo systemctl stop redis-server

# Arrêter MongoDB
sudo systemctl stop mongod

echo "✅ QuantumShield arrêté proprement!"
```

```bash
chmod +x ~/stop-quantumshield.sh
```

---

## 🎯 PROCHAINES ÉTAPES

Une fois QuantumShield déployé avec succès :

1. **Explorer les fonctionnalités** depuis l'interface web
2. **Tester l'inscription utilisateur** et les fonctionnalités de base
3. **Consulter la documentation API** sur `/api/docs`
4. **Configurer des dispositifs IoT** de test
5. **Explorer les fonctionnalités de mining** et tokens $QS

### Ressources supplémentaires

- **Documentation API** : `http://localhost/api/docs`
- **Interface GraphQL** : `http://localhost/api/graphql`
- **Monitoring** : Configurable via les routes dashboard

---

**🛡️ QuantumShield est maintenant déployé avec succès dans votre VM VMware !**

*Pour toute question ou assistance supplémentaire, consultez la documentation complète ou les fichiers de logs.*