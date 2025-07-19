# 🚀 Guide de Déploiement en Production - QuantumShield MVP

## 📋 Table des matières
1. [Prérequis et Infrastructure](#prérequis-et-infrastructure)
2. [Configuration des Environnements](#configuration-des-environnements)
3. [Sécurisation et Certificats](#sécurisation-et-certificats)
4. [Déploiement Backend](#déploiement-backend)
5. [Déploiement Frontend](#déploiement-frontend)
6. [Base de Données Production](#base-de-données-production)
7. [Monitoring et Logs](#monitoring-et-logs)
8. [Sauvegardes et Récupération](#sauvegardes-et-récupération)
9. [Performance et Optimisation](#performance-et-optimisation)
10. [Sécurité Avancée](#sécurité-avancée)
11. [CI/CD et Automatisation](#cicd-et-automatisation)
12. [Tests de Production](#tests-de-production)
13. [Maintenance et Updates](#maintenance-et-updates)
14. [Conformité et Réglementation](#conformité-et-réglementation)

---

## 🛠️ PRÉREQUIS ET INFRASTRUCTURE

### 💰 **Budget Estimé**
- **Infrastructure Cloud**: 500-2000€/mois (selon le trafic)
- **Certificats SSL**: 100-300€/an
- **Services tiers**: 200-500€/mois
- **Monitoring/CDN**: 100-400€/mois
- **Sauvegardes**: 50-200€/mois
- **Total**: 1000-3500€/mois pour démarrer

### 🖥️ **Infrastructure Recommandée**

#### **Option 1: Cloud Provider (Recommandé)**
```bash
# AWS
- EC2 instances: t3.large (2 vCPU, 8GB RAM) minimum
- RDS MongoDB: db.t3.medium
- ALB (Application Load Balancer)
- CloudFront CDN
- S3 pour assets statiques
- Route 53 pour DNS

# Azure
- Virtual Machines: Standard_B2s
- Azure Database for MongoDB
- Application Gateway
- Azure CDN
- Blob Storage
- DNS Zone

# Google Cloud
- Compute Engine: e2-standard-2
- MongoDB Atlas
- Cloud Load Balancing
- Cloud CDN
- Cloud Storage
- Cloud DNS
```

#### **Option 2: VPS Dédié (Plus économique)**
```bash
# Configuration minimale
- 4 vCPU, 8GB RAM, 100GB SSD
- Bande passante: 1TB/mois minimum
- OS: Ubuntu 22.04 LTS
- Providers: OVH, Hetzner, DigitalOcean, Linode
```

### 🌐 **Domaine et DNS**
```bash
# Domaine principal
quantumshield.com (ou votre choix)

# Sous-domaines nécessaires
api.quantumshield.com     # Backend API
app.quantumshield.com     # Frontend App
admin.quantumshield.com   # Interface admin
ws.quantumshield.com      # WebSocket
docs.quantumshield.com    # Documentation API
```

---

## ⚙️ CONFIGURATION DES ENVIRONNEMENTS

### 📁 **Structure de Déploiement**
```bash
/opt/quantumshield/
├── backend/
├── frontend/
├── nginx/
├── ssl/
├── logs/
├── backups/
├── scripts/
└── monitoring/
```

### 🔧 **Variables d'Environnement Backend**
```bash
# CRÉER LE FICHIER : /opt/quantumshield/backend/.env.production
# sudo nano /opt/quantumshield/backend/.env.production

NODE_ENV=production
PORT=8001

# Base de données
MONGO_URL=mongodb://mongodb-user:STRONG_PASSWORD@your-mongodb-server:27017/quantumshield?authSource=admin
DB_NAME=quantumshield_prod

# Sécurité
SECRET_KEY=GENERATE_STRONG_256_BIT_KEY_HERE
JWT_SECRET=GENERATE_ANOTHER_STRONG_KEY_HERE
BCRYPT_ROUNDS=12

# Blockchain
BLOCKCHAIN_NODE_URL=http://localhost:8545
QS_TOKEN_CONTRACT_ADDRESS=0x123...
NTRU_KEY_SIZE=2048
MINING_DIFFICULTY=4
REWARD_AMOUNT=10

# Services externes
REDIS_URL=redis://localhost:6379
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@quantumshield.com
SMTP_PASS=app_password_here

# Monitoring
SENTRY_DSN=your_sentry_dsn_here
LOG_LEVEL=info

# Rate Limiting
RATE_LIMIT_MAX=1000
RATE_LIMIT_WINDOW=3600

# CORS
ALLOWED_ORIGINS=https://app.quantumshield.com,https://quantumshield.com
```

### 🖥️ **Variables d'Environnement Frontend**
```bash
# CRÉER LE FICHIER : /opt/quantumshield/frontend/.env.production
# sudo nano /opt/quantumshield/frontend/.env.production

REACT_APP_BACKEND_URL=https://api.quantumshield.com
REACT_APP_WS_URL=wss://ws.quantumshield.com
REACT_APP_CDN_URL=https://cdn.quantumshield.com
REACT_APP_ENVIRONMENT=production
GENERATE_SOURCEMAP=false
```

---

## 🔒 SÉCURISATION ET CERTIFICATS

### 📜 **Certificats SSL/TLS**

#### **Option 1: Let's Encrypt (Gratuit)**
```bash
# Installation Certbot
sudo apt update
sudo apt install snapd
sudo snap install core
sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot

# Génération des certificats
sudo certbot --nginx -d quantumshield.com -d www.quantumshield.com
sudo certbot --nginx -d api.quantumshield.com
sudo certbot --nginx -d app.quantumshield.com
sudo certbot --nginx -d admin.quantumshield.com
sudo certbot --nginx -d ws.quantumshield.com

# Auto-renouvellement
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

#### **Option 2: Certificat Commercial (Recommandé pour production)**
```bash
# Providers recommandés
- DigiCert Extended Validation (EV)
- GlobalSign Organization Validation (OV)
- Sectigo (ex-Comodo)

# Certificat Wildcard pour *.quantumshield.com
# Certificat multi-domaine (SAN)
```

### 🛡️ **Configuration Sécurité Nginx**
```nginx
# CRÉER LE FICHIER : /etc/nginx/snippets/quantumshield-security.conf
# sudo nano /etc/nginx/snippets/quantumshield-security.conf

# Headers de sécurité
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' wss: https:; frame-src 'none';" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
add_header Permissions-Policy "geolocation=(), camera=(), microphone=()" always;

# Configuration SSL moderne
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 1d;
ssl_session_tickets off;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
```

---

## 🏗️ DÉPLOIEMENT BACKEND

### 🐍 **Préparation Serveur Backend**
```bash
# Mise à jour système
sudo apt update && sudo apt upgrade -y

# Installation des dépendances système
sudo apt install -y python3.11 python3.11-venv python3-pip
sudo apt install -y nginx redis-server
sudo apt install -y curl wget git unzip
sudo apt install -y build-essential libssl-dev libffi-dev
sudo apt install -y supervisor htop iotop

# Utilisateur pour l'application
sudo adduser --system --group --no-create-home quantumshield
sudo mkdir -p /opt/quantumshield
sudo chown -R quantumshield:quantumshield /opt/quantumshield
```

### 📦 **Déploiement Code Backend**
```bash
# Clone et setup
cd /opt/quantumshield
sudo -u quantumshield git clone https://github.com/votre-repo/QuantumShield.git .

# Environnement virtuel Python
sudo -u quantumshield python3.11 -m venv venv
sudo -u quantumshield ./venv/bin/pip install --upgrade pip
sudo -u quantumshield ./venv/bin/pip install -r backend/requirements.txt

# Installation dépendances supplémentaires pour production
sudo -u quantumshield ./venv/bin/pip install gunicorn
sudo -u quantumshield ./venv/bin/pip install psutil
sudo -u quantumshield ./venv/bin/pip install sentry-sdk[fastapi]
```

### ⚡ **Configuration Gunicorn**
```python
# CRÉER LE FICHIER : /opt/quantumshield/gunicorn.conf.py  
# sudo nano /opt/quantumshield/gunicorn.conf.py

import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8001"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
timeout = 30
keepalive = 10

# Logging
accesslog = "/opt/quantumshield/logs/gunicorn-access.log"
errorlog = "/opt/quantumshield/logs/gunicorn-error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "quantumshield-backend"

# Server mechanics
daemon = False
pidfile = "/opt/quantumshield/gunicorn.pid"
user = "quantumshield"
group = "quantumshield"
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None
```

### 🔧 **Configuration Supervisor Backend**
```ini
# CRÉER LE FICHIER : /etc/supervisor/conf.d/quantumshield-backend.conf
# sudo nano /etc/supervisor/conf.d/quantumshield-backend.conf

[program:quantumshield-backend]
command=/opt/quantumshield/venv/bin/gunicorn -c /opt/quantumshield/gunicorn.conf.py backend.server:app
directory=/opt/quantumshield
user=quantumshield
group=quantumshield
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/quantumshield/logs/backend-supervisor.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5
environment=PYTHONPATH="/opt/quantumshield",PYTHONUNBUFFERED="1"
```

---

## 🌐 DÉPLOIEMENT FRONTEND

### 📦 **Build de Production**
```bash
# Installation Node.js 18 LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Build frontend
cd /opt/quantumshield/frontend
sudo -u quantumshield npm ci --production=false
sudo -u quantumshield npm run build

# Optimisation du build
sudo -u quantumshield npm install -g @craco/craco
sudo -u quantumshield npm install --save-dev compression-webpack-plugin
sudo -u quantumshield npm install --save-dev bundle-analyzer
```

### 🏗️ **Configuration Nginx Frontend**
```nginx
# CRÉER LE FICHIER : /etc/nginx/sites-available/quantumshield-frontend
# sudo nano /etc/nginx/sites-available/quantumshield-frontend

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name app.quantumshield.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/app.quantumshield.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.quantumshield.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        application/atom+xml
        application/geo+json
        application/javascript
        application/x-javascript
        application/json
        application/ld+json
        application/manifest+json
        application/rdf+xml
        application/rss+xml
        application/xhtml+xml
        application/xml
        font/eot
        font/otf
        font/ttf
        image/svg+xml
        text/css
        text/javascript
        text/plain
        text/xml;

    # Document Root
    root /opt/quantumshield/frontend/build;
    index index.html;

    # Security headers (from security config)
    include /etc/nginx/snippets/quantumshield-security.conf;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header X-Content-Type-Options nosniff;
        access_log off;
    }

    # Handle React Router
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }

    # API Proxy
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

    # WebSocket support
    location /ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name app.quantumshield.com;
    return 301 https://$server_name$request_uri;
}
```

### 📊 **Configuration API Gateway**
```nginx
# CRÉER LE FICHIER : /etc/nginx/sites-available/quantumshield-api
# sudo nano /etc/nginx/sites-available/quantumshield-api

upstream quantumshield_backend {
    server 127.0.0.1:8001;
    # Pour load balancing multiple instances:
    # server 127.0.0.1:8002;
    # server 127.0.0.1:8003;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.quantumshield.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.quantumshield.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.quantumshield.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/s;

    # Security headers
    include /etc/nginx/snippets/quantumshield-security.conf;

    # General API rate limiting
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://quantumshield_backend;
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

        # CORS headers
        add_header Access-Control-Allow-Origin "https://app.quantumshield.com" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type, Accept, Origin, User-Agent, DNT, Cache-Control, X-Mx-ReqToken, Keep-Alive, X-Requested-With, If-Modified-Since" always;
        add_header Access-Control-Allow-Credentials true always;

        if ($request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin "https://app.quantumshield.com";
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "Authorization, Content-Type, Accept, Origin, User-Agent, DNT, Cache-Control, X-Mx-ReqToken, Keep-Alive, X-Requested-With, If-Modified-Since";
            add_header Access-Control-Allow-Credentials true;
            add_header Access-Control-Max-Age 1728000;
            add_header Content-Type 'text/plain; charset=utf-8';
            add_header Content-Length 0;
            return 204;
        }
    }

    # Stricter rate limiting for auth endpoints
    location /api/auth/ {
        limit_req zone=auth burst=10 nodelay;
        
        proxy_pass http://quantumshield_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check (no rate limiting)
    location /api/health {
        proxy_pass http://quantumshield_backend;
        access_log off;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name api.quantumshield.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 🗄️ BASE DE DONNÉES PRODUCTION

### 🍃 **MongoDB Production Setup**

#### **Option 1: MongoDB Atlas (Recommandé)**
```bash
# Avantages
- Gestion automatisée
- Sauvegardes automatiques
- Monitoring intégré
- Scaling automatique
- Sécurité enterprise

# Configuration
1. Créer cluster M10 minimum (2GB RAM, 10GB Storage)
2. Configurer IP Whitelist
3. Créer utilisateur avec rôles appropriés
4. Activer encryption at rest
5. Configurer monitoring et alertes
```

#### **Option 2: MongoDB Self-Hosted**
```bash
# Installation MongoDB 6.0
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# Configuration sécurisée
sudo systemctl start mongod
sudo systemctl enable mongod

# Configuration /etc/mongod.conf
# MODIFIER LE FICHIER : /etc/mongod.conf  
# sudo nano /etc/mongod.conf

storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true
  wiredTiger:
    engineConfig:
      cacheSizeGB: 2
    collectionConfig:
      blockCompressor: snappy

systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log
  logRotate: reopen

net:
  port: 27017
  bindIp: 127.0.0.1

security:
  authorization: enabled
  keyFile: /etc/ssl/mongodb-keyfile

replication:
  replSetName: quantumshield-rs

# Création des utilisateurs
mongo --eval "
db.getSiblingDB('admin').createUser({
  user: 'admin',
  pwd: 'STRONG_ADMIN_PASSWORD',
  roles: [{role: 'root', db: 'admin'}]
})

db.getSiblingDB('quantumshield_prod').createUser({
  user: 'quantumshield',
  pwd: 'STRONG_APP_PASSWORD',
  roles: [{role: 'readWrite', db: 'quantumshield_prod'}]
})
"
```

### 🔒 **Sécurisation Base de Données**
```bash
# Encryption at Rest
sudo openssl rand -base64 756 > /etc/ssl/mongodb-keyfile
sudo chmod 400 /etc/ssl/mongodb-keyfile
sudo chown mongodb:mongodb /etc/ssl/mongodb-keyfile

# Network Security
# - Utiliser VPN ou VPC
# - Whitelist IP uniquement
# - Utiliser SSL/TLS connections

# Monitoring
# - Activer profiling pour queries lentes
# - Configurer alertes sur usage disque/RAM
# - Monitor connexions simultanées
```

---

## 📊 MONITORING ET LOGS

### 📈 **Stack Monitoring Recommandée**

#### **Option 1: Stack ELK (Elasticsearch, Logstash, Kibana)**
```bash
# Installation Elasticsearch
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list
sudo apt update && sudo apt install elasticsearch

# Installation Kibana
sudo apt install kibana

# Installation Logstash
sudo apt install logstash

# Configuration Logstash pour QuantumShield
# /etc/logstash/conf.d/quantumshield.conf
input {
  file {
    path => "/opt/quantumshield/logs/*.log"
    start_position => "beginning"
    codec => "json"
  }
}

filter {
  if [application] == "quantumshield" {
    mutate {
      add_field => { "environment" => "production" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "quantumshield-%{+YYYY.MM.dd}"
  }
}
```

#### **Option 2: Grafana + Prometheus (Plus léger)**
```bash
# Installation Prometheus
sudo useradd --system --no-create-home prometheus
sudo mkdir /etc/prometheus /var/lib/prometheus
sudo chown prometheus:prometheus /etc/prometheus /var/lib/prometheus

wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
tar -xzf prometheus-2.40.0.linux-amd64.tar.gz
sudo cp prometheus-2.40.0.linux-amd64/{prometheus,promtool} /usr/local/bin/
sudo chown prometheus:prometheus /usr/local/bin/{prometheus,promtool}

# Configuration Prometheus
# /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'quantumshield-backend'
    static_configs:
      - targets: ['localhost:8001']
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
  - job_name: 'nginx'
    static_configs:
      - targets: ['localhost:9113']

# Installation Grafana
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update && sudo apt-get install grafana
```

### 📋 **Configuration Logs Structurés**
```python
# Ajout dans backend/server.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_entry)

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler('/opt/quantumshield/logs/app.log'),
        logging.StreamHandler()
    ]
)

for handler in logging.root.handlers:
    handler.setFormatter(JSONFormatter())
```

### 🚨 **Alertes et Notifications**
```yaml
# /etc/prometheus/alert_rules.yml
groups:
  - name: quantumshield_alerts
    rules:
    - alert: HighCPUUsage
      expr: 100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High CPU usage on {{ $labels.instance }}"

    - alert: HighMemoryUsage
      expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 80
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High memory usage on {{ $labels.instance }}"

    - alert: DiskSpaceLow
      expr: (node_filesystem_size_bytes{fstype!="tmpfs"} - node_filesystem_free_bytes{fstype!="tmpfs"}) / node_filesystem_size_bytes{fstype!="tmpfs"} * 100 > 80
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "Disk space low on {{ $labels.instance }}"

    - alert: ApplicationDown
      expr: up{job="quantumshield-backend"} == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "QuantumShield Backend is down"
```

---

## 💾 SAUVEGARDES ET RÉCUPÉRATION

### 📦 **Stratégie de Sauvegarde**
```bash
# Script de sauvegarde automatisé
#!/bin/bash
# /opt/quantumshield/scripts/backup.sh

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/quantumshield/backups"
MONGO_USER="quantumshield"
MONGO_PASS="STRONG_APP_PASSWORD"
MONGO_DB="quantumshield_prod"

# Création du répertoire de sauvegarde
mkdir -p $BACKUP_DIR/$BACKUP_DATE

# Sauvegarde MongoDB
mongodump --host localhost:27017 \
          --username $MONGO_USER \
          --password $MONGO_PASS \
          --db $MONGO_DB \
          --out $BACKUP_DIR/$BACKUP_DATE/

# Sauvegarde des fichiers de configuration
cp -r /opt/quantumshield/backend/.env.production $BACKUP_DIR/$BACKUP_DATE/
cp -r /opt/quantumshield/frontend/.env.production $BACKUP_DIR/$BACKUP_DATE/
cp -r /etc/nginx/sites-available/quantumshield* $BACKUP_DIR/$BACKUP_DATE/

# Compression
tar -czf $BACKUP_DIR/quantumshield_$BACKUP_DATE.tar.gz -C $BACKUP_DIR $BACKUP_DATE
rm -rf $BACKUP_DIR/$BACKUP_DATE

# Upload vers S3 (optionnel)
aws s3 cp $BACKUP_DIR/quantumshield_$BACKUP_DATE.tar.gz s3://quantumshield-backups/

# Nettoyage des anciennes sauvegardes (garder 30 jours)
find $BACKUP_DIR -name "quantumshield_*.tar.gz" -mtime +30 -delete

echo "Backup completed: quantumshield_$BACKUP_DATE.tar.gz"
```

### ⏰ **Automatisation Sauvegardes**
```bash
# Crontab pour sauvegardes automatiques
# sudo crontab -e

# Sauvegarde quotidienne à 2h du matin
0 2 * * * /opt/quantumshield/scripts/backup.sh >> /opt/quantumshield/logs/backup.log 2>&1

# Sauvegarde hebdomadaire complète le dimanche à 1h
0 1 * * 0 /opt/quantumshield/scripts/full-backup.sh >> /opt/quantumshield/logs/backup.log 2>&1

# Vérification de l'espace disque avant sauvegarde
0 1 * * * /opt/quantumshield/scripts/check-disk-space.sh >> /opt/quantumshield/logs/disk-check.log 2>&1
```

### 🔄 **Script de Restauration**
```bash
#!/bin/bash
# /opt/quantumshield/scripts/restore.sh

if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup-file>"
    echo "Available backups:"
    ls -la /opt/quantumshield/backups/quantumshield_*.tar.gz
    exit 1
fi

BACKUP_FILE=$1
RESTORE_DIR="/tmp/quantumshield-restore-$(date +%s)"

echo "🔄 Starting restoration from $BACKUP_FILE"

# Extraction de la sauvegarde
mkdir -p $RESTORE_DIR
tar -xzf $BACKUP_FILE -C $RESTORE_DIR

# Arrêt des services
echo "🛑 Stopping services..."
sudo supervisorctl stop quantumshield-backend
sudo systemctl stop nginx

# Restauration MongoDB
echo "📊 Restoring database..."
mongorestore --host localhost:27017 \
            --username $MONGO_USER \
            --password $MONGO_PASS \
            --db $MONGO_DB \
            --drop \
            $RESTORE_DIR/*/quantumshield_prod/

# Restauration des configurations
echo "⚙️ Restoring configurations..."
cp $RESTORE_DIR/*/.env.production /opt/quantumshield/backend/
cp $RESTORE_DIR/*/.env.production /opt/quantumshield/frontend/

# Redémarrage des services
echo "🚀 Restarting services..."
sudo systemctl start nginx
sudo supervisorctl start quantumshield-backend

# Nettoyage
rm -rf $RESTORE_DIR

echo "✅ Restoration completed successfully!"
```

---

## 🚄 PERFORMANCE ET OPTIMISATION

### ⚡ **Optimisations Backend**
```python
# Ajouts dans backend/server.py pour production

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import redis
import asyncio

app = FastAPI()

# Middleware de compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Restriction des hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["api.quantumshield.com", "app.quantumshield.com"]
)

# Connection Pool Redis pour cache
redis_pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=20,
    retry_on_timeout=True
)
redis_client = redis.Redis(connection_pool=redis_pool)

# Connection Pool MongoDB
from motor.motor_asyncio import AsyncIOMotorClient
mongo_client = AsyncIOMotorClient(
    mongo_url,
    maxPoolSize=50,
    minPoolSize=10,
    maxIdleTimeMS=30000,
    waitQueueTimeoutMS=5000
)
```

### 🎯 **Optimisations Frontend**
```javascript
// Webpack optimizations dans craco.config.js
const path = require('path');
const CompressionPlugin = require('compression-webpack-plugin');

module.exports = {
  webpack: {
    plugins: {
      add: [
        new CompressionPlugin({
          algorithm: 'gzip',
          test: /\.(js|css|html|svg)$/,
          threshold: 8192,
          minRatio: 0.8,
        }),
      ],
    },
    configure: (webpackConfig, { env, paths }) => {
      if (env === 'production') {
        // Code splitting amélioré
        webpackConfig.optimization.splitChunks = {
          chunks: 'all',
          cacheGroups: {
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendors',
              chunks: 'all',
            },
            common: {
              name: 'common',
              minChunks: 2,
              chunks: 'all',
              enforce: true,
            },
          },
        };

        // Tree shaking
        webpackConfig.optimization.usedExports = true;
        webpackConfig.optimization.sideEffects = false;
      }
      return webpackConfig;
    },
  },
  babel: {
    plugins: [
      // Lazy loading des composants
      ['import', {
        libraryName: 'lodash',
        libraryDirectory: '',
        camel2DashComponentName: false,
      }, 'lodash'],
    ],
  },
};
```

### 🗄️ **Optimisations Base de Données**
```javascript
// Index MongoDB optimisés
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "username": 1 }, { unique: true })
db.users.createIndex({ "created_at": -1 })

db.devices.createIndex({ "user_id": 1, "status": 1 })
db.devices.createIndex({ "device_type": 1, "created_at": -1 })

db.transactions.createIndex({ "user_id": 1, "timestamp": -1 })
db.transactions.createIndex({ "type": 1, "timestamp": -1 })

db.blocks.createIndex({ "height": 1 }, { unique: true })
db.blocks.createIndex({ "timestamp": -1 })
db.blocks.createIndex({ "hash": 1 }, { unique: true })

// Aggregation pipeline pour dashboard
db.users.aggregate([
  {
    $lookup: {
      from: "devices",
      localField: "_id",
      foreignField: "user_id",
      as: "devices"
    }
  },
  {
    $lookup: {
      from: "transactions",
      localField: "_id",
      foreignField: "user_id",
      as: "transactions"
    }
  },
  {
    $project: {
      username: 1,
      email: 1,
      device_count: { $size: "$devices" },
      total_transactions: { $size: "$transactions" },
      last_login: 1
    }
  }
])
```

---

## 🔐 SÉCURITÉ AVANCÉE

### 🛡️ **Hardening Serveur**
```bash
#!/bin/bash
# /opt/quantumshield/scripts/server-hardening.sh

echo "🔒 Starting server hardening..."

# Désactivation des services non nécessaires
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon
sudo systemctl disable cups

# Configuration firewall UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow from 127.0.0.1 to 127.0.0.1 port 27017  # MongoDB local
sudo ufw allow from 127.0.0.1 to 127.0.0.1 port 6379   # Redis local
sudo ufw --force enable

# Configuration SSH sécurisée
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
sudo tee /etc/ssh/sshd_config << EOF
Port 22
Protocol 2
HostKey /etc/ssh/ssh_host_rsa_key
HostKey /etc/ssh/ssh_host_ed25519_key
UsePrivilegeSeparation yes
KeyRegenerationInterval 3600
ServerKeyBits 1024
SyslogFacility AUTH
LogLevel INFO
LoginGraceTime 120
PermitRootLogin no
StrictModes yes
RSAAuthentication yes
PubkeyAuthentication yes
IgnoreRhosts yes
RhostsRSAAuthentication no
HostbasedAuthentication no
PermitEmptyPasswords no
ChallengeResponseAuthentication no
PasswordAuthentication no
X11Forwarding no
X11DisplayOffset 10
PrintMotd no
PrintLastLog yes
TCPKeepAlive yes
MaxStartups 10:30:60
Banner /etc/issue.net
AllowUsers quantumshield
DenyUsers root
EOF

sudo systemctl restart sshd

# Configuration des limites système
sudo tee -a /etc/security/limits.conf << EOF
* soft nofile 65536
* hard nofile 65536
* soft nproc 65536
* hard nproc 65536
quantumshield soft nofile 65536
quantumshield hard nofile 65536
EOF

# Sysctl optimizations
sudo tee -a /etc/sysctl.conf << EOF
# Network optimizations
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 65536 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
net.core.netdev_max_backlog = 30000
net.ipv4.tcp_max_syn_backlog = 30000
net.ipv4.tcp_congestion_control = bbr

# Security optimizations
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0
net.ipv4.conf.all.log_martians = 1
EOF

sudo sysctl -p

echo "✅ Server hardening completed!"
```

### 🔑 **Authentification Multi-Facteur (2FA)**
```python
# Configuration 2FA dans backend
from pyotp import TOTP, random_base32
import qrcode
from io import BytesIO
import base64

class MFAService:
    @staticmethod
    def generate_secret():
        return random_base32()
    
    @staticmethod
    def generate_qr_code(user_email, secret):
        totp = TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_email,
            issuer_name="QuantumShield"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @staticmethod
    def verify_token(secret, token):
        totp = TOTP(secret)
        return totp.verify(token, valid_window=1)
```

### 🚫 **Protection DDoS et Rate Limiting**
```nginx
# Configuration anti-DDoS dans Nginx
# /etc/nginx/conf.d/ddos-protection.conf

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=static:10m rate=30r/s;

# Connection limiting
limit_conn_zone $binary_remote_addr zone=conn_limit_per_ip:10m;
limit_conn_zone $server_name zone=conn_limit_per_server:10m;

# Request size limiting
client_body_buffer_size 200K;
client_header_buffer_size 2k;
client_max_body_size 200k;
large_client_header_buffers 3 1k;

# Timeout settings
client_body_timeout 60s;
client_header_timeout 60s;
keepalive_timeout 10 10;
send_timeout 60s;

# Hide server information
server_tokens off;
more_clear_headers Server;

# Prevent access to hidden files
location ~ /\. {
    deny all;
}

# Block common attacks
location ~* \.(aspx|php|jsp|cgi)$ {
    return 410;
}

# Block suspicious user agents
if ($http_user_agent ~* "(?:acunetix|BurpSuite|nmap|sqlmap|nikto|wpscan|wordpress|wp-admin|wp-login)") {
    return 444;
}

# Geographic restrictions (exemple: bloquer certains pays)
# Requires GeoIP module
# if ($geoip_country_code ~ (CN|RU|KP)) {
#     return 444;
# }
```

---

## 🔄 CI/CD ET AUTOMATISATION

### 🚀 **Pipeline GitHub Actions**
```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  workflow_dispatch:

env:
  NODE_VERSION: '18'
  PYTHON_VERSION: '3.11'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: ${{ env.NODE_VERSION }}
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install Python dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    
    - name: Install Node.js dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run Python tests
      run: |
        cd backend
        pytest tests/ -v
    
    - name: Run Node.js tests
      run: |
        cd frontend
        npm test -- --coverage --watchAll=false
    
    - name: Build frontend
      run: |
        cd frontend
        npm run build
    
    - name: Upload build artifacts
      uses: actions/upload-artifact@v3
      with:
        name: build-files
        path: |
          backend/
          frontend/build/

  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run security scan
      uses: securecodewarrior/github-action-add-sarif@v1
      with:
        sarif-file: security-scan-results.sarif
    
    - name: Python Security Check
      run: |
        pip install safety bandit
        cd backend
        safety check -r requirements.txt
        bandit -r . -x tests/
    
    - name: Node.js Security Check  
      run: |
        cd frontend
        npm audit --audit-level high

  deploy:
    needs: [test, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Download build artifacts
      uses: actions/download-artifact@v3
      with:
        name: build-files
    
    - name: Deploy to production server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.PRODUCTION_HOST }}
        username: ${{ secrets.PRODUCTION_USER }}
        key: ${{ secrets.PRODUCTION_SSH_KEY }}
        script: |
          cd /opt/quantumshield
          
          # Backup current version
          ./scripts/backup-current-version.sh
          
          # Pull latest code
          git pull origin main
          
          # Backend deployment
          cd backend
          ./venv/bin/pip install -r requirements.txt
          
          # Frontend deployment
          cd ../frontend
          npm ci --production=false
          npm run build
          
          # Restart services
          sudo supervisorctl restart quantumshield-backend
          sudo systemctl reload nginx
          
          # Health check
          sleep 10
          curl -f http://localhost:8001/api/health || exit 1
          curl -f https://app.quantumshield.com || exit 1
          
          echo "✅ Deployment successful!"

  notify:
    needs: [deploy]
    runs-on: ubuntu-latest
    if: always()
    
    steps:
    - name: Notify deployment status
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        text: |
          Production deployment ${{ job.status }}!
          Repository: ${{ github.repository }}
          Branch: ${{ github.ref }}
          Commit: ${{ github.sha }}
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### 📋 **Scripts de Déploiement**
```bash
#!/bin/bash
# /opt/quantumshield/scripts/deploy.sh

set -e  # Exit on error

ENVIRONMENT="production"
BACKUP_DIR="/opt/quantumshield/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🚀 Starting deployment for $ENVIRONMENT environment..."

# Pre-deployment checks
echo "🔍 Running pre-deployment checks..."
./scripts/pre-deploy-checks.sh || exit 1

# Create backup before deployment
echo "💾 Creating backup..."
./scripts/backup.sh

# Stop services gracefully
echo "🛑 Stopping services..."
sudo supervisorctl stop quantumshield-backend
sleep 5

# Pull latest code
echo "📦 Updating code..."
git pull origin main

# Update backend dependencies
echo "🐍 Updating backend dependencies..."
cd backend
./venv/bin/pip install -r requirements.txt --quiet

# Build frontend
echo "🌐 Building frontend..."
cd ../frontend
npm ci --silent
npm run build --silent

# Database migrations (if any)
echo "🗄️ Running database migrations..."
cd ../backend
./venv/bin/python -c "
from server import db
# Add any migration scripts here
print('✅ Database migrations completed')
"

# Update configurations
echo "⚙️ Updating configurations..."
# Copy any new config files if needed

# Start services
echo "🚀 Starting services..."
sudo supervisorctl start quantumshield-backend
sudo systemctl reload nginx

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Post-deployment health checks
echo "🏥 Running health checks..."
./scripts/health-check.sh || {
    echo "❌ Health checks failed! Rolling back..."
    ./scripts/rollback.sh
    exit 1
}

# Clear caches
echo "🧹 Clearing caches..."
redis-cli FLUSHALL
curl -X POST https://api.quantumshield.com/api/cache/clear \
     -H "Authorization: Bearer $ADMIN_TOKEN"

echo "✅ Deployment completed successfully!"
echo "📊 Deployment summary:"
echo "  - Environment: $ENVIRONMENT"
echo "  - Timestamp: $TIMESTAMP"
echo "  - Backup: $BACKUP_DIR/quantumshield_$TIMESTAMP.tar.gz"
echo "  - Health: $(curl -s https://api.quantumshield.com/api/health | jq -r .status)"
```

---

## 🧪 TESTS DE PRODUCTION

### 🔄 **Tests d'Intégration Continue**
```python
# tests/test_production_readiness.py
import pytest
import asyncio
import aiohttp
import time
from typing import Dict, Any

class ProductionTests:
    BASE_URL = "https://api.quantumshield.com"
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/api/health") as response:
                assert response.status == 200
                data = await response.json()
                assert data["status"] == "healthy"
                
    @pytest.mark.asyncio  
    async def test_authentication_flow(self):
        async with aiohttp.ClientSession() as session:
            # Register test user
            register_data = {
                "username": f"testuser_{int(time.time())}",
                "email": f"test_{int(time.time())}@example.com",
                "password": "TestPassword123!"
            }
            
            async with session.post(
                f"{self.BASE_URL}/api/auth/register",
                json=register_data
            ) as response:
                assert response.status == 200
                
            # Login
            login_data = {
                "username": register_data["username"],
                "password": register_data["password"]
            }
            
            async with session.post(
                f"{self.BASE_URL}/api/auth/login",
                json=login_data
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert "token" in data
                
    @pytest.mark.asyncio
    async def test_load_balancing(self):
        """Test multiple concurrent requests"""
        tasks = []
        
        async def make_request(session):
            async with session.get(f"{self.BASE_URL}/api/health") as response:
                return response.status
                
        async with aiohttp.ClientSession() as session:
            # 100 concurrent requests
            tasks = [make_request(session) for _ in range(100)]
            results = await asyncio.gather(*tasks)
            
        success_count = sum(1 for status in results if status == 200)
        assert success_count >= 95  # 95% success rate minimum
        
    @pytest.mark.asyncio
    async def test_response_times(self):
        """Test API response times"""
        endpoints = [
            "/api/health",
            "/api/auth/verify-token",  # with valid token
            "/api/dashboard/stats",    # with valid token
        ]
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                start_time = time.time()
                async with session.get(f"{self.BASE_URL}{endpoint}") as response:
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    assert response_time < 1.0  # Max 1 second response time
                    
    def test_ssl_configuration(self):
        """Test SSL/TLS configuration"""
        import ssl
        import socket
        
        context = ssl.create_default_context()
        with socket.create_connection(("api.quantumshield.com", 443)) as sock:
            with context.wrap_socket(sock, server_hostname="api.quantumshield.com") as ssock:
                cipher = ssock.cipher()
                assert cipher is not None
                assert "TLSv1.3" in str(ssock.version()) or "TLSv1.2" in str(ssock.version())
```

### 📊 **Tests de Charge**
```python
# tests/load_tests.py
import asyncio
import aiohttp
import time
from typing import List
import statistics

class LoadTestSuite:
    def __init__(self, base_url: str = "https://api.quantumshield.com"):
        self.base_url = base_url
        self.results = []
        
    async def simulate_user_journey(self, session: aiohttp.ClientSession, user_id: int):
        """Simule un parcours utilisateur complet"""
        try:
            journey_start = time.time()
            
            # 1. Register user
            register_data = {
                "username": f"loadtest_user_{user_id}_{int(time.time())}",
                "email": f"loadtest_{user_id}_{int(time.time())}@example.com",
                "password": "TestPassword123!"
            }
            
            async with session.post(f"{self.base_url}/api/auth/register", json=register_data) as resp:
                if resp.status != 200:
                    return {"success": False, "stage": "register", "status": resp.status}
            
            # 2. Login
            login_data = {
                "username": register_data["username"], 
                "password": register_data["password"]
            }
            
            async with session.post(f"{self.base_url}/api/auth/login", json=login_data) as resp:
                if resp.status != 200:
                    return {"success": False, "stage": "login", "status": resp.status}
                auth_data = await resp.json()
                token = auth_data.get("token")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # 3. Get dashboard
            async with session.get(f"{self.base_url}/api/dashboard/stats", headers=headers) as resp:
                if resp.status != 200:
                    return {"success": False, "stage": "dashboard", "status": resp.status}
            
            # 4. Create device
            device_data = {
                "name": f"Test Device {user_id}",
                "device_type": "sensor",
                "location": "Test Lab"
            }
            
            async with session.post(f"{self.base_url}/api/devices", json=device_data, headers=headers) as resp:
                if resp.status != 200:
                    return {"success": False, "stage": "create_device", "status": resp.status}
            
            # 5. Get user profile
            async with session.get(f"{self.base_url}/api/auth/profile", headers=headers) as resp:
                if resp.status != 200:
                    return {"success": False, "stage": "profile", "status": resp.status}
            
            journey_time = time.time() - journey_start
            
            return {
                "success": True,
                "user_id": user_id,
                "total_time": journey_time
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "user_id": user_id}
    
    async def run_load_test(self, concurrent_users: int = 50, duration: int = 300):
        """Execute load test with specified parameters"""
        print(f"🚀 Starting load test: {concurrent_users} users for {duration} seconds")
        
        connector = aiohttp.TCPConnector(limit=concurrent_users * 2)
        timeout = aiohttp.ClientTimeout(total=60)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            start_time = time.time()
            tasks = []
            user_counter = 0
            
            while time.time() - start_time < duration:
                # Launch new user journeys
                for _ in range(min(concurrent_users, 10)):  # Batch of 10
                    task = asyncio.create_task(
                        self.simulate_user_journey(session, user_counter)
                    )
                    tasks.append(task)
                    user_counter += 1
                
                # Wait a bit before next batch
                await asyncio.sleep(1)
                
                # Clean up completed tasks
                completed_tasks = [task for task in tasks if task.done()]
                for task in completed_tasks:
                    result = await task
                    self.results.append(result)
                    tasks.remove(task)
            
            # Wait for remaining tasks
            if tasks:
                remaining_results = await asyncio.gather(*tasks, return_exceptions=True)
                self.results.extend([r for r in remaining_results if isinstance(r, dict)])
        
        # Analyze results
        self.analyze_results()
    
    def analyze_results(self):
        """Analyze and report load test results"""
        total_requests = len(self.results)
        successful_requests = len([r for r in self.results if r.get("success", False)])
        failed_requests = total_requests - successful_requests
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        successful_times = [r["total_time"] for r in self.results if r.get("success") and "total_time" in r]
        
        if successful_times:
            avg_response_time = statistics.mean(successful_times)
            median_response_time = statistics.median(successful_times)
            p95_response_time = sorted(successful_times)[int(len(successful_times) * 0.95)]
        else:
            avg_response_time = median_response_time = p95_response_time = 0
        
        print("\n📊 LOAD TEST RESULTS")
        print("=" * 50)
        print(f"Total Requests: {total_requests}")
        print(f"Successful Requests: {successful_requests}")
        print(f"Failed Requests: {failed_requests}")
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Average Response Time: {avg_response_time:.2f}s")
        print(f"Median Response Time: {median_response_time:.2f}s")
        print(f"95th Percentile Response Time: {p95_response_time:.2f}s")
        
        # Failure analysis
        if failed_requests > 0:
            print("\n❌ FAILURE ANALYSIS")
            print("-" * 30)
            failure_stages = {}
            for result in self.results:
                if not result.get("success", False):
                    stage = result.get("stage", "unknown")
                    failure_stages[stage] = failure_stages.get(stage, 0) + 1
            
            for stage, count in failure_stages.items():
                print(f"{stage}: {count} failures")

# Script pour exécuter les tests de charge
if __name__ == "__main__":
    async def main():
        load_tester = LoadTestSuite()
        await load_tester.run_load_test(concurrent_users=20, duration=120)  # 2 minutes
    
    asyncio.run(main())
```

---

## 🔧 MAINTENANCE ET UPDATES

### 📅 **Planning de Maintenance**
```bash
# /opt/quantumshield/scripts/maintenance-schedule.sh

# Crontab pour maintenance automatique
# sudo crontab -e

# Mise à jour des paquets système (dimanche 3h)
0 3 * * 0 /opt/quantumshield/scripts/system-updates.sh >> /opt/quantumshield/logs/maintenance.log 2>&1

# Nettoyage des logs (quotidien 4h)
0 4 * * * /opt/quantumshield/scripts/cleanup-logs.sh >> /opt/quantumshield/logs/maintenance.log 2>&1

# Analyse de performance (quotidien 5h)
0 5 * * * /opt/quantumshield/scripts/performance-analysis.sh >> /opt/quantumshield/logs/performance.log 2>&1

# Vérification sécurité (hebdomadaire lundi 2h)
0 2 * * 1 /opt/quantumshield/scripts/security-scan.sh >> /opt/quantumshield/logs/security.log 2>&1

# Optimisation base de données (mensuel 1er dimanche 1h)
0 1 1-7 * 0 /opt/quantumshield/scripts/db-optimization.sh >> /opt/quantumshield/logs/maintenance.log 2>&1

# Renouvellement certificats SSL (check quotidien 6h)  
0 6 * * * certbot renew --quiet >> /opt/quantumshield/logs/ssl.log 2>&1
```

### 🧹 **Scripts de Maintenance**
```bash
#!/bin/bash
# /opt/quantumshield/scripts/cleanup-logs.sh

LOG_RETENTION_DAYS=30
BACKUP_RETENTION_DAYS=90

echo "🧹 Starting log cleanup..."

# Nettoyage logs applicatifs
find /opt/quantumshield/logs -name "*.log" -mtime +$LOG_RETENTION_DAYS -delete
find /var/log/nginx -name "*.log.*" -mtime +$LOG_RETENTION_DAYS -delete
find /var/log/supervisor -name "*.log.*" -mtime +$LOG_RETENTION_DAYS -delete

# Rotation logs MongoDB
mongo --eval "db.runCommand({logRotate:1})"

# Nettoyage anciennes sauvegardes
find /opt/quantumshield/backups -name "*.tar.gz" -mtime +$BACKUP_RETENTION_DAYS -delete

# Nettoyage cache Redis
redis-cli --eval /opt/quantumshield/scripts/cleanup-cache.lua

# Nettoyage fichiers temporaires
find /tmp -name "*quantumshield*" -mtime +7 -delete
find /opt/quantumshield -name "*.pyc" -delete
find /opt/quantumshield -name "__pycache__" -type d -exec rm -rf {} +

# Nettoyage logs système
journalctl --vacuum-time=30d

echo "✅ Log cleanup completed"
```

### 🔄 **Mise à Jour Zero-Downtime**
```bash
#!/bin/bash
# /opt/quantumshield/scripts/zero-downtime-update.sh

set -e

BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ROLLBACK_POINT="/opt/quantumshield/rollback-$BACKUP_TIMESTAMP"

echo "🔄 Starting zero-downtime update..."

# 1. Pre-update backup
echo "💾 Creating rollback point..."
cp -r /opt/quantumshield $ROLLBACK_POINT

# 2. Update code in staging area
echo "📦 Preparing update..."
git fetch origin main
CURRENT_COMMIT=$(git rev-parse HEAD)
LATEST_COMMIT=$(git rev-parse origin/main)

if [ "$CURRENT_COMMIT" = "$LATEST_COMMIT" ]; then
    echo "ℹ️ Already up to date"
    rm -rf $ROLLBACK_POINT
    exit 0
fi

# 3. Build new version
echo "🏗️ Building new version..."
cd /tmp
git clone /opt/quantumshield quantumshield-update-$BACKUP_TIMESTAMP
cd quantumshield-update-$BACKUP_TIMESTAMP
git checkout $LATEST_COMMIT

# Backend preparation
cd backend
python3.11 -m venv venv-new
./venv-new/bin/pip install -r requirements.txt

# Frontend build
cd ../frontend
npm ci
npm run build

# 4. Start new backend instance on different port
echo "🚀 Starting new backend instance..."
cd ../backend
export PORT=8002
./venv-new/bin/gunicorn -c ../gunicorn.conf.py -b 127.0.0.1:8002 server:app &
NEW_BACKEND_PID=$!

# Wait for new instance to be ready
sleep 10
curl -f http://127.0.0.1:8002/api/health || {
    echo "❌ New backend failed to start"
    kill $NEW_BACKEND_PID 2>/dev/null || true
    exit 1
}

# 5. Update nginx to route traffic to new instance
echo "🔄 Switching traffic to new instance..."
sed -i 's/127.0.0.1:8001/127.0.0.1:8002/g' /etc/nginx/sites-available/quantumshield-*
sudo nginx -t && sudo nginx -s reload

# Wait for connections to drain
sleep 30

# 6. Stop old backend
echo "🛑 Stopping old backend..."
sudo supervisorctl stop quantumshield-backend

# 7. Replace old code with new
echo "📁 Replacing application code..."
cd /opt/quantumshield
rm -rf backend.old frontend.old 2>/dev/null || true
mv backend backend.old
mv frontend frontend.old
cp -r /tmp/quantumshield-update-$BACKUP_TIMESTAMP/backend .
cp -r /tmp/quantumshield-update-$BACKUP_TIMESTAMP/frontend .

# 8. Update supervisor to use port 8001 again and start
sed -i 's/127.0.0.1:8002/127.0.0.1:8001/g' /etc/nginx/sites-available/quantumshield-*
sudo nginx -s reload

sudo supervisorctl start quantumshield-backend

# Wait for service to be ready
sleep 10
curl -f http://127.0.0.1:8001/api/health || {
    echo "❌ Failed to start updated backend"
    echo "🔄 Rolling back..."
    ./scripts/rollback.sh $ROLLBACK_POINT
    exit 1
}

# 9. Stop temporary backend instance
kill $NEW_BACKEND_PID 2>/dev/null || true

# 10. Cleanup
rm -rf /tmp/quantumshield-update-$BACKUP_TIMESTAMP
rm -rf backend.old frontend.old
rm -rf $ROLLBACK_POINT

echo "✅ Zero-downtime update completed successfully!"
echo "📊 Updated from $CURRENT_COMMIT to $LATEST_COMMIT"
```

---

## 📋 CONFORMITÉ ET RÉGLEMENTATION

### 🇪🇺 **GDPR Compliance**
```python
# backend/services/gdpr_service.py
from datetime import datetime, timedelta
import asyncio
from typing import Dict, List, Any
import hashlib

class GDPRService:
    def __init__(self, db):
        self.db = db
        
    async def user_data_export(self, user_id: str) -> Dict[str, Any]:
        """Export all user data for GDPR compliance"""
        user_data = {}
        
        # User profile
        user = await self.db.users.find_one({"_id": user_id})
        user_data["profile"] = {
            "username": user["username"],
            "email": user["email"], 
            "created_at": user["created_at"],
            "last_login": user.get("last_login"),
            "preferences": user.get("preferences", {})
        }
        
        # Devices
        devices = await self.db.devices.find({"user_id": user_id}).to_list(None)
        user_data["devices"] = devices
        
        # Transactions
        transactions = await self.db.transactions.find({"user_id": user_id}).to_list(None)
        user_data["transactions"] = transactions
        
        # Logs (last 90 days only)
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        logs = await self.db.user_logs.find({
            "user_id": user_id,
            "timestamp": {"$gte": ninety_days_ago}
        }).to_list(None)
        user_data["logs"] = logs
        
        return user_data
    
    async def user_data_deletion(self, user_id: str, soft_delete: bool = True) -> bool:
        """Delete or anonymize user data"""
        if soft_delete:
            # Anonymize instead of delete (recommended for blockchain integrity)
            anonymous_id = hashlib.sha256(f"anonymous_{user_id}_{datetime.utcnow()}".encode()).hexdigest()[:16]
            
            # Update user record
            await self.db.users.update_one(
                {"_id": user_id},
                {"$set": {
                    "username": f"deleted_user_{anonymous_id}",
                    "email": f"deleted_{anonymous_id}@deleted.local",
                    "gdpr_deleted": True,
                    "deletion_date": datetime.utcnow(),
                    "personal_data_hash": None
                }}
            )
            
            # Anonymize device names
            await self.db.devices.update_many(
                {"user_id": user_id},
                {"$set": {"name": f"Anonymous Device"}}
            )
            
        else:
            # Hard delete (be careful with blockchain data)
            await self.db.users.delete_one({"_id": user_id})
            await self.db.devices.delete_many({"user_id": user_id})
            await self.db.user_logs.delete_many({"user_id": user_id})
            # Note: Keep transaction records for blockchain integrity
            
        return True
    
    async def consent_management(self, user_id: str, consents: Dict[str, bool]):
        """Update user consent preferences"""
        await self.db.users.update_one(
            {"_id": user_id},
            {"$set": {
                "consents": consents,
                "consents_updated": datetime.utcnow()
            }}
        )
        
        # If analytics consent revoked, anonymize past data
        if not consents.get("analytics", False):
            await self.db.user_logs.update_many(
                {"user_id": user_id},
                {"$set": {"user_id": "anonymous", "anonymized": True}}
            )
```

### 🛡️ **Audit Trail Implementation**
```python
# backend/middleware/audit_middleware.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import json
from datetime import datetime
import asyncio

class AuditTrailMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, db):
        super().__init__(app)
        self.db = db
        self.sensitive_endpoints = [
            "/api/auth/login",
            "/api/auth/register", 
            "/api/auth/change-password",
            "/api/users/delete",
            "/api/admin/"
        ]
        
    async def dispatch(self, request: Request, call_next):
        # Start audit record
        audit_record = {
            "timestamp": datetime.utcnow(),
            "method": request.method,
            "url": str(request.url),
            "client_ip": self.get_client_ip(request),
            "user_agent": request.headers.get("User-Agent"),
            "user_id": None,
            "session_id": None,
            "request_id": request.headers.get("X-Request-ID")
        }
        
        # Extract user info if authenticated
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                # Decode JWT to get user info (implement your JWT decode logic)
                user_info = self.decode_jwt(auth_header.split(" ")[1])
                audit_record["user_id"] = user_info.get("user_id")
                audit_record["session_id"] = user_info.get("session_id")
            except:
                pass
        
        # For sensitive endpoints, log request body (be careful with passwords)
        if any(endpoint in audit_record["url"] for endpoint in self.sensitive_endpoints):
            audit_record["is_sensitive"] = True
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    body = await self.get_request_body(request)
                    # Don't log passwords
                    if isinstance(body, dict) and "password" in body:
                        body = {**body, "password": "[REDACTED]"}
                    audit_record["request_body"] = body
                except:
                    audit_record["request_body"] = "[UNABLE_TO_PARSE]"
        
        # Execute request
        start_time = datetime.utcnow()
        try:
            response = await call_next(request)
            audit_record["status_code"] = response.status_code
            audit_record["success"] = True
        except Exception as e:
            audit_record["status_code"] = 500
            audit_record["error"] = str(e)
            audit_record["success"] = False
            raise
        finally:
            # Complete audit record
            audit_record["duration_ms"] = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Save audit record asynchronously
            asyncio.create_task(self.save_audit_record(audit_record))
            
        return response
    
    async def save_audit_record(self, audit_record):
        """Save audit record to database"""
        try:
            await self.db.audit_logs.insert_one(audit_record)
        except Exception as e:
            # Log to file as fallback
            with open("/opt/quantumshield/logs/audit-fallback.log", "a") as f:
                f.write(f"{json.dumps(audit_record)}\n")
    
    def get_client_ip(self, request: Request) -> str:
        """Extract real client IP considering proxies"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
            
        return request.client.host
```

### 📊 **Compliance Reporting**
```python
# backend/services/compliance_service.py
from datetime import datetime, timedelta
import csv
import io
from typing import List, Dict

class ComplianceService:
    def __init__(self, db):
        self.db = db
    
    async def generate_gdpr_report(self, start_date: datetime, end_date: datetime) -> str:
        """Generate GDPR compliance report"""
        report = io.StringIO()
        writer = csv.writer(report)
        
        # Header
        writer.writerow([
            "Date", "User ID", "Action", "Data Type", 
            "Legal Basis", "Retention Period", "Status"
        ])
        
        # Data processing activities
        activities = await self.db.data_processing_activities.find({
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }).to_list(None)
        
        for activity in activities:
            writer.writerow([
                activity["timestamp"],
                activity.get("user_id", "N/A"),
                activity["action"],
                activity["data_type"],
                activity["legal_basis"],
                activity["retention_period"],
                activity["status"]
            ])
        
        return report.getvalue()
    
    async def generate_security_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """Generate security compliance report"""
        
        # Security incidents
        incidents = await self.db.security_incidents.find({
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }).to_list(None)
        
        # Failed login attempts
        failed_logins = await self.db.audit_logs.count_documents({
            "timestamp": {"$gte": start_date, "$lte": end_date},
            "url": {"$regex": "/api/auth/login"},
            "status_code": {"$ne": 200}
        })
        
        # Successful authentications
        successful_logins = await self.db.audit_logs.count_documents({
            "timestamp": {"$gte": start_date, "$lte": end_date},
            "url": {"$regex": "/api/auth/login"},
            "status_code": 200
        })
        
        # Data exports (GDPR requests)
        data_exports = await self.db.gdpr_requests.count_documents({
            "timestamp": {"$gte": start_date, "$lte": end_date},
            "type": "export"
        })
        
        # Data deletions
        data_deletions = await self.db.gdpr_requests.count_documents({
            "timestamp": {"$gte": start_date, "$lte": end_date},
            "type": "deletion"
        })
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "security_incidents": len(incidents),
            "authentication": {
                "successful_logins": successful_logins,
                "failed_logins": failed_logins,
                "success_rate": successful_logins / (successful_logins + failed_logins) * 100 if (successful_logins + failed_logins) > 0 else 0
            },
            "gdpr": {
                "data_exports": data_exports,
                "data_deletions": data_deletions
            },
            "incidents_details": incidents
        }
```

---

## 📋 CHECKLIST FINAL DE DÉPLOIEMENT

### ✅ **Pre-Production Checklist**

#### **Infrastructure**
- [ ] Serveur configuré avec spécifications minimales
- [ ] Nom de domaine acheté et DNS configuré
- [ ] Certificats SSL/TLS installés et testés
- [ ] Firewall configuré et testé
- [ ] Monitoring mis en place (Grafana/Prometheus ou ELK)
- [ ] Sauvegardes automatisées configurées
- [ ] Stratégie de récupération testée

#### **Sécurité** 
- [ ] Hardening serveur effectué
- [ ] Variables d'environnement sécurisées
- [ ] Rate limiting configuré
- [ ] Protection DDoS activée
- [ ] Logs d'audit configurés
- [ ] 2FA activé pour comptes admin
- [ ] Scan de sécurité effectué

#### **Backend**
- [ ] Base de données MongoDB configurée et sécurisée
- [ ] Toutes les dépendances installées
- [ ] Variables d'environnement production configurées
- [ ] Gunicorn configuré avec workers appropriés
- [ ] Supervisor configuré pour auto-restart
- [ ] Tests d'intégration passés
- [ ] Performance tests passés

#### **Frontend**
- [ ] Build de production optimisé
- [ ] Assets statiques compressés
- [ ] PWA configuré (si applicable)
- [ ] CDN configuré pour assets
- [ ] Cache browser configuré
- [ ] React Router configuré pour nginx

#### **Base de Données**
- [ ] Index optimisés créés
- [ ] Utilisateurs DB créés avec permissions appropriées
- [ ] Encryption at rest activé
- [ ] Sauvegardes automatiques configurées
- [ ] Réplication configurée (si applicable)
- [ ] Monitoring queries lentes activé

### ✅ **Post-Deployment Checklist**

#### **Tests Fonctionnels**
- [ ] Page d'accueil se charge correctement
- [ ] Inscription utilisateur fonctionne
- [ ] Connexion utilisateur fonctionne
- [ ] Dashboard utilisateur accessible
- [ ] APIs principales répondent
- [ ] WebSocket connections fonctionnent
- [ ] Gestion des erreurs appropriée

#### **Tests Performance**
- [ ] Temps de réponse < 1 seconde pour pages principales
- [ ] Tests de charge passés (50+ utilisateurs simultanés)
- [ ] Utilisation mémoire/CPU dans limites acceptables
- [ ] Base de données répond rapidement
- [ ] CDN distribue correctement les assets

#### **Tests Sécurité**
- [ ] SSL Labs Score A+ pour tous domaines
- [ ] Scan vulnerability passed
- [ ] Rate limiting fonctionnel
- [ ] Headers sécurité présents
- [ ] Authentication/Authorization fonctionnels
- [ ] Logs d'audit enregistrés

#### **Monitoring & Alertes**
- [ ] Dashboards Grafana/Kibana fonctionnels
- [ ] Alertes configurées et testées
- [ ] Logs structurés et indexés
- [ ] Métriques business remontées
- [ ] Health checks automatisés
- [ ] Notifications Slack/email configurées

### 🚀 **Go-Live Process**

1. **Communication Stakeholders** (J-7)
   - Notification équipe technique
   - Communication clients/utilisateurs
   - Planning maintenance préventive

2. **Final Pre-checks** (J-1)
   - Exécution checklist complète
   - Tests finaux sur environnement staging
   - Validation sauvegardes
   - Préparation rollback procedures

3. **Deployment** (J-Day)
   - Exécution scripts de déploiement
   - Monitoring actif pendant 4h
   - Tests post-déploiement
   - Communication go-live réussi

4. **Post Go-Live** (J+1 à J+7)
   - Monitoring intensif
   - Support utilisateurs renforcé
   - Analyse performances
   - Optimisations si nécessaires

---

## 📞 SUPPORT ET CONTACTS URGENCE

### 🚨 **Contacts d'Urgence**
```
🔧 Équipe Technique
- DevOps Lead: +33 X XX XX XX XX
- Backend Lead: +33 X XX XX XX XX  
- Frontend Lead: +33 X XX XX XX XX

☁️ Providers
- Hébergeur: [Contact provider]
- CDN: [Contact CDN provider]
- DNS: [Contact DNS provider]
- Monitoring: [Contact monitoring service]

🔒 Sécurité
- Incident Response Team: security@quantumshield.com
- CERT: [Contact CERT si applicable]
- Cyber Insurance: [Contact assurance]
```

### 📋 **Procédures d'Urgence**

#### **Site Down**
1. Vérifier status services: `sudo supervisorctl status`
2. Vérifier logs: `tail -f /opt/quantumshield/logs/*.log`
3. Restart services: `sudo supervisorctl restart all`
4. Si problème persiste: exécuter rollback
5. Notifier équipe et utilisateurs

#### **Performance Dégradée**
1. Check CPU/RAM: `htop`, `free -h`
2. Check disk space: `df -h`
3. Check database: MongoDB logs
4. Check network: `iftop`, `netstat`
5. Scale resources si nécessaire

#### **Security Incident**
1. Isoler système compromis
2. Préserver evidence (logs, snapshots)
3. Notifier équipe sécurité
4. Suivre procédures incident response
5. Communication clients si nécessaire

---

**🎯 Ce guide couvre tous les aspects essentiels pour déployer QuantumShield en production de manière sécurisée, performante et conforme aux réglementations. Chaque section doit être adaptée selon vos besoins spécifiques et votre environnement.**

**📞 En cas de questions ou problèmes durant le déploiement, référez-vous aux sections troubleshooting ou contactez l'équipe technique.**

---

*Dernière mise à jour: $(date)*
*Version: 1.0*
*Statut: Production Ready*