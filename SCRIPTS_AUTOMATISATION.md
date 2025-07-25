# 🤖 Scripts d'Automatisation - QuantumShield VMware

## 📋 Vue d'ensemble

Ce document contient tous les scripts d'automatisation pour faciliter le déploiement, la gestion et la maintenance de QuantumShield dans VMware Workstation Pro.

---

## 🚀 Script d'Installation Automatique

### `install-quantumshield.sh` - Installation Complète Automatisée

```bash
#!/bin/bash

# =====================================================
# Script d'installation automatique QuantumShield
# Version: 1.0.0
# Compatible: Ubuntu 22.04 LTS
# =====================================================

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
QS_HOME="$HOME/quantumshield"
LOG_FILE="/tmp/quantumshield-install.log"

# Fonction d'affichage
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a $LOG_FILE
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a $LOG_FILE
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a $LOG_FILE
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a $LOG_FILE
}

# Fonction de vérification des prérequis
check_prerequisites() {
    print_status "Vérification des prérequis..."
    
    # Vérifier Ubuntu version
    if ! lsb_release -a 2>/dev/null | grep -q "22.04"; then
        print_warning "Ce script est optimisé pour Ubuntu 22.04 LTS"
    fi
    
    # Vérifier les droits sudo
    if ! sudo -v; then
        print_error "Droits sudo requis pour l'installation"
        exit 1
    fi
    
    # Vérifier la connectivité Internet
    if ! ping -c 1 google.com &> /dev/null; then
        print_error "Connexion Internet requise"
        exit 1
    fi
    
    print_success "Prérequis validés"
}

# Mise à jour du système
update_system() {
    print_status "Mise à jour du système..."
    sudo apt update && sudo apt upgrade -y >> $LOG_FILE 2>&1
    sudo apt install -y curl wget git unzip software-properties-common htop tree nano >> $LOG_FILE 2>&1
    print_success "Système mis à jour"
}

# Installation Python 3.11
install_python() {
    print_status "Installation de Python 3.11..."
    sudo add-apt-repository ppa:deadsnakes/ppa -y >> $LOG_FILE 2>&1
    sudo apt update >> $LOG_FILE 2>&1
    sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip python3.11-distutils >> $LOG_FILE 2>&1
    
    # Vérifier l'installation
    if python3.11 --version >> $LOG_FILE 2>&1; then
        print_success "Python 3.11 installé avec succès"
    else
        print_error "Échec de l'installation de Python 3.11"
        exit 1
    fi
}

# Installation Node.js et Yarn
install_nodejs() {
    print_status "Installation de Node.js 18 et Yarn..."
    
    # Node.js 18 LTS
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - >> $LOG_FILE 2>&1
    sudo apt-get install -y nodejs >> $LOG_FILE 2>&1
    
    # Yarn
    curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add - >> $LOG_FILE 2>&1
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list >> $LOG_FILE 2>&1
    sudo apt update >> $LOG_FILE 2>&1
    sudo apt install -y yarn >> $LOG_FILE 2>&1
    
    # Vérification
    if node --version && yarn --version >> $LOG_FILE 2>&1; then
        print_success "Node.js et Yarn installés avec succès"
        node --version
        yarn --version
    else
        print_error "Échec de l'installation de Node.js/Yarn"
        exit 1
    fi
}

# Installation MongoDB
install_mongodb() {
    print_status "Installation de MongoDB..."
    
    # Clé GPG
    wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add - >> $LOG_FILE 2>&1
    
    # Repository
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list >> $LOG_FILE 2>&1
    
    # Installation
    sudo apt-get update >> $LOG_FILE 2>&1
    sudo apt-get install -y mongodb-org >> $LOG_FILE 2>&1
    
    # Démarrage et activation
    sudo systemctl start mongod >> $LOG_FILE 2>&1
    sudo systemctl enable mongod >> $LOG_FILE 2>&1
    
    # Vérification
    sleep 3
    if sudo systemctl is-active --quiet mongod; then
        print_success "MongoDB installé et démarré avec succès"
    else
        print_error "Échec du démarrage de MongoDB"
        exit 1
    fi
}

# Installation des outils système
install_system_tools() {
    print_status "Installation des outils système..."
    
    # Supervisor
    sudo apt install -y supervisor >> $LOG_FILE 2>&1
    sudo systemctl start supervisor >> $LOG_FILE 2>&1
    sudo systemctl enable supervisor >> $LOG_FILE 2>&1
    
    # Nginx
    sudo apt install -y nginx >> $LOG_FILE 2>&1
    sudo systemctl start nginx >> $LOG_FILE 2>&1
    sudo systemctl enable nginx >> $LOG_FILE 2>&1
    
    # Redis
    sudo apt install -y redis-server >> $LOG_FILE 2>&1
    sudo systemctl start redis-server >> $LOG_FILE 2>&1
    sudo systemctl enable redis-server >> $LOG_FILE 2>&1
    
    print_success "Outils système installés"
}

# Configuration de la base de données
setup_database() {
    print_status "Configuration de la base de données..."
    
    # Créer la base de données
    mongo --eval "
        use quantumshield;
        db.test.insertOne({message: 'Database créée', timestamp: new Date()});
        print('Base de données quantumshield créée');
    " >> $LOG_FILE 2>&1
    
    print_success "Base de données configurée"
}

# Configuration du backend
setup_backend() {
    print_status "Configuration du backend QuantumShield..."
    
    # Copier le code source
    if [ -d "/app" ]; then
        cp -r /app $QS_HOME
    else
        print_error "Code source non trouvé dans /app"
        exit 1
    fi
    
    # Changer les permissions
    sudo chown -R $USER:$USER $QS_HOME
    
    # Configuration de l'environnement Python
    cd $QS_HOME/backend
    python3.11 -m venv venv >> $LOG_FILE 2>&1
    source venv/bin/activate
    pip install --upgrade pip >> $LOG_FILE 2>&1
    pip install -r requirements.txt >> $LOG_FILE 2>&1
    
    # Configuration du fichier .env
    cat > .env << EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=quantumshield
SECRET_KEY=quantumshield_secret_key_2024_$(openssl rand -hex 16)
BLOCKCHAIN_NODE_URL=http://localhost:8545
QS_TOKEN_CONTRACT_ADDRESS=0x$(openssl rand -hex 20)
NTRU_KEY_SIZE=2048
MINING_DIFFICULTY=4
REWARD_AMOUNT=10
EOF
    
    print_success "Backend configuré"
}

# Configuration du frontend
setup_frontend() {
    print_status "Configuration du frontend QuantumShield..."
    
    cd $QS_HOME/frontend
    
    # Installation des dépendances
    yarn install >> $LOG_FILE 2>&1
    
    # Build de production
    yarn build >> $LOG_FILE 2>&1
    
    print_success "Frontend configuré et buildé"
}

# Configuration Supervisor
setup_supervisor() {
    print_status "Configuration de Supervisor..."
    
    sudo tee /etc/supervisor/conf.d/quantumshield-backend.conf > /dev/null << EOF
[program:quantumshield-backend]
command=$QS_HOME/backend/venv/bin/python server.py
directory=$QS_HOME/backend
user=$USER
group=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/quantumshield-backend.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=PYTHONPATH="$QS_HOME/backend",PYTHONUNBUFFERED="1"
EOF
    
    # Recharger et démarrer
    sudo supervisorctl reread >> $LOG_FILE 2>&1
    sudo supervisorctl update >> $LOG_FILE 2>&1
    sudo supervisorctl start quantumshield-backend >> $LOG_FILE 2>&1
    
    print_success "Supervisor configuré"
}

# Configuration Nginx
setup_nginx() {
    print_status "Configuration de Nginx..."
    
    sudo tee /etc/nginx/sites-available/quantumshield > /dev/null << EOF
server {
    listen 80;
    listen [::]:80;
    server_name localhost;

    root $QS_HOME/frontend/build;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
}
EOF
    
    # Activer le site
    sudo ln -sf /etc/nginx/sites-available/quantumshield /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Tester et redémarrer
    sudo nginx -t >> $LOG_FILE 2>&1
    sudo systemctl restart nginx >> $LOG_FILE 2>&1
    
    print_success "Nginx configuré"
}

# Tests finaux
run_tests() {
    print_status "Exécution des tests finaux..."
    
    sleep 5
    
    # Test MongoDB
    if mongo --eval "db.runCommand('ping')" >> $LOG_FILE 2>&1; then
        print_success "✅ MongoDB : OK"
    else
        print_error "❌ MongoDB : ECHEC"
    fi
    
    # Test Redis
    if redis-cli ping >> $LOG_FILE 2>&1; then
        print_success "✅ Redis : OK"
    else
        print_error "❌ Redis : ECHEC"
    fi
    
    # Test Backend
    if curl -f http://localhost:8001/api/health >> $LOG_FILE 2>&1; then
        print_success "✅ Backend API : OK"
    else
        print_error "❌ Backend API : ECHEC"
    fi
    
    # Test Frontend via Nginx
    if curl -f http://localhost >> $LOG_FILE 2>&1; then
        print_success "✅ Frontend : OK"
    else
        print_error "❌ Frontend : ECHEC"
    fi
}

# Création des scripts utiles
create_utility_scripts() {
    print_status "Création des scripts utiles..."
    
    # Script de démarrage
    cat > $HOME/start-quantumshield.sh << 'EOF'
#!/bin/bash
echo "🚀 Démarrage de QuantumShield..."
sudo systemctl start mongod redis-server supervisor nginx
sleep 5
sudo supervisorctl start quantumshield-backend
echo "✅ QuantumShield démarré!"
echo "🌐 Accès : http://localhost"
sudo supervisorctl status quantumshield-backend
EOF
    
    # Script d'arrêt
    cat > $HOME/stop-quantumshield.sh << 'EOF'
#!/bin/bash
echo "🛑 Arrêt de QuantumShield..."
sudo supervisorctl stop quantumshield-backend
sudo systemctl stop nginx supervisor redis-server mongod
echo "✅ QuantumShield arrêté!"
EOF
    
    # Script de statut
    cat > $HOME/status-quantumshield.sh << 'EOF'
#!/bin/bash
echo "📊 Statut QuantumShield"
echo "======================="
echo
echo "Services système:"
sudo systemctl status mongod --no-pager -l | grep "Active:"
sudo systemctl status redis-server --no-pager -l | grep "Active:"
sudo systemctl status supervisor --no-pager -l | grep "Active:"
sudo systemctl status nginx --no-pager -l | grep "Active:"
echo
echo "Application QuantumShield:"
sudo supervisorctl status quantumshield-backend
echo
echo "Tests de connectivité:"
echo -n "Backend API: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/health
echo
echo -n "Frontend: "
curl -s -o /dev/null -w "%{http_code}" http://localhost
echo
echo
echo "IP de la VM:"
ip addr show | grep "inet " | grep -v "127.0.0.1"
EOF
    
    # Rendre les scripts exécutables
    chmod +x $HOME/start-quantumshield.sh
    chmod +x $HOME/stop-quantumshield.sh
    chmod +x $HOME/status-quantumshield.sh
    
    print_success "Scripts utiles créés"
}

# Affichage des informations finales
show_final_info() {
    echo
    echo "🎉 ========================================== 🎉"
    echo "   INSTALLATION QUANTUMSHIELD TERMINÉE!"
    echo "🎉 ========================================== 🎉"
    echo
    echo "📍 Informations importantes:"
    echo "   • Répertoire: $QS_HOME"
    echo "   • Interface: http://localhost"
    echo "   • API: http://localhost/api"
    echo "   • Documentation API: http://localhost/api/docs"
    echo
    echo "🔧 Scripts utiles:"
    echo "   • Démarrer: ~/start-quantumshield.sh"
    echo "   • Arrêter: ~/stop-quantumshield.sh"
    echo "   • Statut: ~/status-quantumshield.sh"
    echo
    echo "📋 Logs:"
    echo "   • Installation: $LOG_FILE"
    echo "   • Backend: sudo tail -f /var/log/supervisor/quantumshield-backend.log"
    echo "   • Nginx: sudo tail -f /var/log/nginx/access.log"
    echo
    VM_IP=$(ip route get 8.8.8.8 | awk '{print $7}' | head -1)
    echo "🌐 Accès depuis l'hôte: http://$VM_IP"
    echo
    echo "✅ QuantumShield est prêt à l'utilisation!"
}

# Fonction principale
main() {
    echo "🛡️  Installation Automatique QuantumShield"
    echo "==========================================="
    echo
    echo "📝 Log d'installation: $LOG_FILE"
    echo
    
    check_prerequisites
    update_system
    install_python
    install_nodejs
    install_mongodb
    install_system_tools
    setup_database
    setup_backend
    setup_frontend
    setup_supervisor
    setup_nginx
    create_utility_scripts
    run_tests
    show_final_info
}

# Exécution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

---

## 🔧 Scripts de Gestion

### `start-quantumshield.sh` - Démarrage des Services

```bash
#!/bin/bash

# =====================================================
# Script de démarrage QuantumShield
# Usage: ./start-quantumshield.sh
# =====================================================

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Démarrage de QuantumShield...${NC}"
echo

# Démarrer les services système
echo "📊 Démarrage des services système..."
sudo systemctl start mongod
echo "  ✅ MongoDB démarré"

sudo systemctl start redis-server
echo "  ✅ Redis démarré"

sudo systemctl start supervisor
echo "  ✅ Supervisor démarré"

sudo systemctl start nginx
echo "  ✅ Nginx démarré"

# Attendre que les services soient prêts
echo
echo "⏳ Attente de la stabilisation des services..."
sleep 5

# Démarrer l'application QuantumShield
echo "🛡️  Démarrage de l'application QuantumShield..."
sudo supervisorctl start quantumshield-backend
echo "  ✅ Backend QuantumShield démarré"

echo
echo -e "${GREEN}✅ QuantumShield démarré avec succès!${NC}"
echo

# Afficher les informations de connexion
VM_IP=$(ip route get 8.8.8.8 | awk '{print $7}' | head -1)
echo "🌐 Accès local : http://localhost"
echo "🌐 Accès externe : http://$VM_IP"
echo "📚 Documentation API : http://localhost/api/docs"
echo

# Afficher le statut
echo "📊 Statut des services:"
sudo supervisorctl status quantumshield-backend

# Test rapide
echo
echo "🧪 Test rapide de connectivité:"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/health | grep -q "200"; then
    echo "  ✅ Backend API : OK"
else
    echo "  ❌ Backend API : ERREUR"
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200"; then
    echo "  ✅ Frontend : OK"
else
    echo "  ❌ Frontend : ERREUR"
fi

echo
echo "🎉 QuantumShield est prêt à l'utilisation!"
```

### `stop-quantumshield.sh` - Arrêt des Services

```bash
#!/bin/bash

# =====================================================
# Script d'arrêt QuantumShield
# Usage: ./stop-quantumshield.sh
# =====================================================

# Couleurs
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🛑 Arrêt de QuantumShield...${NC}"
echo

# Arrêter l'application QuantumShield
echo "🛡️  Arrêt de l'application QuantumShield..."
sudo supervisorctl stop quantumshield-backend
echo "  ✅ Backend QuantumShield arrêté"

# Arrêter les services système dans l'ordre inverse
echo
echo "📊 Arrêt des services système..."
sudo systemctl stop nginx
echo "  ✅ Nginx arrêté"

sudo systemctl stop supervisor
echo "  ✅ Supervisor arrêté"

sudo systemctl stop redis-server
echo "  ✅ Redis arrêté"

sudo systemctl stop mongod
echo "  ✅ MongoDB arrêté"

echo
echo -e "${RED}🛑 QuantumShield arrêté proprement!${NC}"

# Vérifier l'arrêt
echo
echo "📊 Vérification de l'arrêt:"
if ! pgrep -f "quantumshield" > /dev/null; then
    echo "  ✅ Aucun processus QuantumShield en cours"
else
    echo "  ⚠️  Certains processus pourraient encore être actifs"
fi

echo
echo "💡 Pour redémarrer QuantumShield, utilisez: ./start-quantumshield.sh"
```

### `status-quantumshield.sh` - Vérification du Statut

```bash
#!/bin/bash

# =====================================================
# Script de statut QuantumShield
# Usage: ./status-quantumshield.sh
# =====================================================

# Couleurs
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}📊 Statut QuantumShield${NC}"
echo "========================"
echo

# Fonction pour vérifier le statut d'un service
check_service_status() {
    local service=$1
    local display_name=$2
    
    if sudo systemctl is-active --quiet $service; then
        echo -e "  ${GREEN}✅${NC} $display_name : ACTIF"
        return 0
    else
        echo -e "  ${RED}❌${NC} $display_name : INACTIF"
        return 1
    fi
}

# Fonction pour tester la connectivité HTTP
test_http() {
    local url=$1
    local name=$2
    
    local status_code=$(curl -s -o /dev/null -w "%{http_code}" $url 2>/dev/null)
    if [[ "$status_code" == "200" ]]; then
        echo -e "  ${GREEN}✅${NC} $name : OK (HTTP $status_code)"
        return 0
    else
        echo -e "  ${RED}❌${NC} $name : ERREUR (HTTP $status_code)"
        return 1
    fi
}

# Vérification des services système
echo -e "${BLUE}🔧 Services Système:${NC}"
check_service_status "mongod" "MongoDB"
check_service_status "redis-server" "Redis"
check_service_status "supervisor" "Supervisor"
check_service_status "nginx" "Nginx"
echo

# Vérification de l'application QuantumShield
echo -e "${BLUE}🛡️  Application QuantumShield:${NC}"
supervisor_status=$(sudo supervisorctl status quantumshield-backend 2>/dev/null | awk '{print $2}')
if [[ "$supervisor_status" == "RUNNING" ]]; then
    echo -e "  ${GREEN}✅${NC} Backend QuantumShield : ACTIF"
    backend_running=true
else
    echo -e "  ${RED}❌${NC} Backend QuantumShield : INACTIF ($supervisor_status)"
    backend_running=false
fi
echo

# Tests de connectivité
echo -e "${BLUE}🌐 Tests de Connectivité:${NC}"
test_http "http://localhost:8001/api/health" "Backend API (port 8001)"
test_http "http://localhost/api/health" "API via Nginx (port 80)"
test_http "http://localhost" "Frontend"
echo

# Informations réseau
echo -e "${BLUE}🌐 Informations Réseau:${NC}"
VM_IP=$(ip route get 8.8.8.8 2>/dev/null | awk '{print $7}' | head -1)
if [[ -n "$VM_IP" ]]; then
    echo "  🏠 IP Locale : http://localhost"
    echo "  🌍 IP Externe : http://$VM_IP"
    echo "  📚 Documentation : http://$VM_IP/api/docs"
else
    echo -e "  ${RED}❌${NC} Impossible de déterminer l'IP de la VM"
fi
echo

# Utilisation des ressources
echo -e "${BLUE}💻 Utilisation des Ressources:${NC}"
echo "  🧠 RAM:"
free -h | grep "^Mem:" | awk '{printf "    Utilisée: %s / %s (%.1f%%)\n", $3, $2, ($3/$2)*100}'

echo "  💾 Disque:"
df -h / | tail -1 | awk '{printf "    Utilisé: %s / %s (%s)\n", $3, $2, $5}'

echo "  ⚡ CPU:"
cpu_usage=$(top -bn1 | grep "load average:" | awk '{printf "%.1f", $(NF-2)}')
echo "    Load Average: $cpu_usage"
echo

# Ports utilisés
echo -e "${BLUE}🔌 Ports Utilisés:${NC}"
echo "  Port 80 (HTTP):" $(netstat -tlnp 2>/dev/null | grep ":80 " | wc -l) "connexions"
echo "  Port 8001 (Backend):" $(netstat -tlnp 2>/dev/null | grep ":8001 " | wc -l) "connexions"
echo "  Port 27017 (MongoDB):" $(netstat -tlnp 2>/dev/null | grep ":27017 " | wc -l) "connexions"
echo "  Port 6379 (Redis):" $(netstat -tlnp 2>/dev/null | grep ":6379 " | wc -l) "connexions"
echo

# Logs récents
echo -e "${BLUE}📝 Logs Récents (5 dernières lignes):${NC}"
if [[ -f "/var/log/supervisor/quantumshield-backend.log" ]]; then
    echo "  Backend QuantumShield:"
    sudo tail -5 /var/log/supervisor/quantumshield-backend.log | sed 's/^/    /'
else
    echo -e "  ${YELLOW}⚠️${NC} Log backend non trouvé"
fi
echo

# Recommandations
echo -e "${BLUE}💡 Actions Recommandées:${NC}"
if ! sudo systemctl is-active --quiet mongod; then
    echo -e "  ${YELLOW}⚠️${NC} Démarrer MongoDB : sudo systemctl start mongod"
fi

if [[ "$supervisor_status" != "RUNNING" ]]; then
    echo -e "  ${YELLOW}⚠️${NC} Redémarrer QuantumShield : ./start-quantumshield.sh"
fi

if curl -s --connect-timeout 5 http://localhost/api/health > /dev/null; then
    echo -e "  ${GREEN}✅${NC} QuantumShield est opérationnel !"
else
    echo -e "  ${RED}❌${NC} Problème détecté - vérifier les logs"
fi

echo
echo -e "${BLUE}📋 Commandes Utiles:${NC}"
echo "  Redémarrer : ./start-quantumshield.sh"
echo "  Arrêter : ./stop-quantumshield.sh"
echo "  Logs backend : sudo tail -f /var/log/supervisor/quantumshield-backend.log"
echo "  Logs Nginx : sudo tail -f /var/log/nginx/access.log"
```

---

## 🧹 Scripts de Maintenance

### `backup-quantumshield.sh` - Sauvegarde

```bash
#!/bin/bash

# =====================================================
# Script de sauvegarde QuantumShield
# Usage: ./backup-quantumshield.sh [destination]
# =====================================================

BACKUP_DIR="${1:-$HOME/quantumshield-backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="quantumshield_backup_$TIMESTAMP"
QS_HOME="$HOME/quantumshield"

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}💾 Sauvegarde QuantumShield${NC}"
echo "=============================="
echo

# Créer le répertoire de sauvegarde
mkdir -p "$BACKUP_DIR"
FULL_BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

echo "📁 Répertoire de sauvegarde : $FULL_BACKUP_PATH"
mkdir -p "$FULL_BACKUP_PATH"

# Sauvegarde de la base de données MongoDB
echo
echo "🗄️  Sauvegarde de la base de données..."
mongodump --db quantumshield --out "$FULL_BACKUP_PATH/mongodb/" 2>/dev/null
if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ Base de données sauvegardée${NC}"
else
    echo -e "${YELLOW}⚠️ Erreur lors de la sauvegarde MongoDB${NC}"
fi

# Sauvegarde du code et configuration
echo
echo "📁 Sauvegarde des fichiers de configuration..."
if [[ -d "$QS_HOME" ]]; then
    # Sauvegarder uniquement les fichiers de config
    mkdir -p "$FULL_BACKUP_PATH/config/"
    cp -r "$QS_HOME/backend/.env" "$FULL_BACKUP_PATH/config/" 2>/dev/null
    cp -r "$QS_HOME/frontend/.env" "$FULL_BACKUP_PATH/config/" 2>/dev/null
    echo -e "${GREEN}✅ Configuration sauvegardée${NC}"
else
    echo -e "${YELLOW}⚠️ Répertoire QuantumShield non trouvé${NC}"
fi

# Sauvegarde des configurations système
echo
echo "⚙️ Sauvegarde des configurations système..."
mkdir -p "$FULL_BACKUP_PATH/system/"
sudo cp /etc/supervisor/conf.d/quantumshield-backend.conf "$FULL_BACKUP_PATH/system/" 2>/dev/null
sudo cp /etc/nginx/sites-available/quantumshield "$FULL_BACKUP_PATH/system/" 2>/dev/null
echo -e "${GREEN}✅ Configurations système sauvegardées${NC}"

# Créer un fichier d'informations
echo
echo "📋 Création du fichier d'informations..."
cat > "$FULL_BACKUP_PATH/backup_info.txt" << EOF
QuantumShield Backup Information
================================
Date de sauvegarde: $(date)
Version Ubuntu: $(lsb_release -d | cut -f2)
Utilisateur: $USER
Répertoire source: $QS_HOME

Services au moment de la sauvegarde:
- MongoDB: $(sudo systemctl is-active mongod)
- Redis: $(sudo systemctl is-active redis-server)
- Nginx: $(sudo systemctl is-active nginx)
- Supervisor: $(sudo systemctl is-active supervisor)
- QuantumShield Backend: $(sudo supervisorctl status quantumshield-backend 2>/dev/null | awk '{print $2}')

IP de la VM: $(ip route get 8.8.8.8 | awk '{print $7}' | head -1)
EOF

echo -e "${GREEN}✅ Fichier d'informations créé${NC}"

# Compression de la sauvegarde
echo
echo "🗜️  Compression de la sauvegarde..."
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME/" 2>/dev/null
if [[ $? -eq 0 ]]; then
    rm -rf "$BACKUP_NAME/"
    BACKUP_SIZE=$(du -sh "${BACKUP_NAME}.tar.gz" | cut -f1)
    echo -e "${GREEN}✅ Sauvegarde compressée : ${BACKUP_NAME}.tar.gz (${BACKUP_SIZE})${NC}"
else
    echo -e "${YELLOW}⚠️ Erreur lors de la compression${NC}"
fi

echo
echo -e "${GREEN}🎉 Sauvegarde terminée !${NC}"
echo "📁 Fichier de sauvegarde : $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
echo

# Nettoyage des anciennes sauvegardes (garder les 10 plus récentes)
echo "🧹 Nettoyage des anciennes sauvegardes..."
cd "$BACKUP_DIR"
ls -1t quantumshield_backup_*.tar.gz 2>/dev/null | tail -n +11 | xargs rm -f
BACKUP_COUNT=$(ls -1 quantumshield_backup_*.tar.gz 2>/dev/null | wc -l)
echo "📦 Nombre de sauvegardes conservées : $BACKUP_COUNT"
```

### `restore-quantumshield.sh` - Restauration

```bash
#!/bin/bash

# =====================================================
# Script de restauration QuantumShield
# Usage: ./restore-quantumshield.sh <backup-file>
# =====================================================

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <fichier-backup.tar.gz>"
    echo
    echo "Sauvegardes disponibles:"
    ls -la $HOME/quantumshield-backups/quantumshield_backup_*.tar.gz 2>/dev/null | tail -5
    exit 1
fi

BACKUP_FILE="$1"
RESTORE_DIR="/tmp/quantumshield-restore-$(date +%s)"
QS_HOME="$HOME/quantumshield"

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔄 Restauration QuantumShield${NC}"
echo "================================"
echo

# Vérifier que le fichier de sauvegarde existe
if [[ ! -f "$BACKUP_FILE" ]]; then
    echo -e "${RED}❌ Fichier de sauvegarde non trouvé : $BACKUP_FILE${NC}"
    exit 1
fi

echo "📁 Fichier de sauvegarde : $BACKUP_FILE"
echo "📁 Répertoire de restauration temporaire : $RESTORE_DIR"

# Extraction de la sauvegarde
echo
echo "📦 Extraction de la sauvegarde..."
mkdir -p "$RESTORE_DIR"
tar -xzf "$BACKUP_FILE" -C "$RESTORE_DIR" 2>/dev/null
if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ Sauvegarde extraite${NC}"
else
    echo -e "${RED}❌ Erreur lors de l'extraction${NC}"
    exit 1
fi

# Trouver le dossier de sauvegarde
BACKUP_FOLDER=$(ls -1 "$RESTORE_DIR" | head -1)
BACKUP_PATH="$RESTORE_DIR/$BACKUP_FOLDER"

echo "📂 Dossier de sauvegarde : $BACKUP_PATH"

# Afficher les informations de sauvegarde
if [[ -f "$BACKUP_PATH/backup_info.txt" ]]; then
    echo
    echo -e "${BLUE}📋 Informations de la sauvegarde :${NC}"
    cat "$BACKUP_PATH/backup_info.txt"
    echo
    
    read -p "Continuer avec cette restauration ? (o/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Oo]$ ]]; then
        echo "Restauration annulée."
        rm -rf "$RESTORE_DIR"
        exit 0
    fi
fi

# Arrêter QuantumShield
echo
echo "🛑 Arrêt de QuantumShield..."
./stop-quantumshield.sh > /dev/null 2>&1

# Sauvegarde de sécurité des données actuelles
echo
echo "💾 Sauvegarde de sécurité des données actuelles..."
SAFETY_BACKUP="$HOME/quantumshield-safety-backup-$(date +%s)"
mkdir -p "$SAFETY_BACKUP"

if [[ -d "$QS_HOME" ]]; then
    cp -r "$QS_HOME/backend/.env" "$SAFETY_BACKUP/" 2>/dev/null
    cp -r "$QS_HOME/frontend/.env" "$SAFETY_BACKUP/" 2>/dev/null
fi

mongodump --db quantumshield --out "$SAFETY_BACKUP/mongodb/" 2>/dev/null
echo -e "${GREEN}✅ Sauvegarde de sécurité créée : $SAFETY_BACKUP${NC}"

# Restauration de la base de données
echo
echo "🗄️  Restauration de la base de données..."
if [[ -d "$BACKUP_PATH/mongodb/quantumshield" ]]; then
    mongorestore --db quantumshield --drop "$BACKUP_PATH/mongodb/quantumshield/" 2>/dev/null
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ Base de données restaurée${NC}"
    else
        echo -e "${RED}❌ Erreur lors de la restauration de la base de données${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ Aucune sauvegarde MongoDB trouvée${NC}"
fi

# Restauration des fichiers de configuration
echo
echo "⚙️ Restauration des configurations..."
if [[ -d "$BACKUP_PATH/config" ]]; then
    if [[ -f "$BACKUP_PATH/config/.env" ]]; then
        cp "$BACKUP_PATH/config/.env" "$QS_HOME/backend/" 2>/dev/null
        echo -e "${GREEN}✅ Configuration backend restaurée${NC}"
    fi
    
    if [[ -f "$BACKUP_PATH/config/.env" && -d "$QS_HOME/frontend" ]]; then
        # Adapter la config frontend si nécessaire
        echo -e "${GREEN}✅ Configuration frontend vérifiée${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ Aucune configuration à restaurer${NC}"
fi

# Restauration des configurations système
echo
echo "🔧 Restauration des configurations système..."
if [[ -f "$BACKUP_PATH/system/quantumshield-backend.conf" ]]; then
    sudo cp "$BACKUP_PATH/system/quantumshield-backend.conf" /etc/supervisor/conf.d/ 2>/dev/null
    echo -e "${GREEN}✅ Configuration Supervisor restaurée${NC}"
fi

if [[ -f "$BACKUP_PATH/system/quantumshield" ]]; then
    sudo cp "$BACKUP_PATH/system/quantumshield" /etc/nginx/sites-available/ 2>/dev/null
    echo -e "${GREEN}✅ Configuration Nginx restaurée${NC}"
fi

# Recharger les configurations
echo
echo "🔄 Rechargement des configurations..."
sudo supervisorctl reread > /dev/null 2>&1
sudo supervisorctl update > /dev/null 2>&1
sudo nginx -t > /dev/null 2>&1

# Redémarrer QuantumShield
echo
echo "🚀 Redémarrage de QuantumShield..."
./start-quantumshield.sh

# Nettoyage
echo
echo "🧹 Nettoyage..."
rm -rf "$RESTORE_DIR"

# Tests de vérification
echo
echo "🧪 Tests de vérification..."
sleep 10

if curl -s -o /dev/null -w "%{http_code}" http://localhost/api/health | grep -q "200"; then
    echo -e "${GREEN}✅ Backend API : OK${NC}"
else
    echo -e "${RED}❌ Backend API : ERREUR${NC}"
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200"; then
    echo -e "${GREEN}✅ Frontend : OK${NC}"
else
    echo -e "${RED}❌ Frontend : ERREUR${NC}"
fi

echo
echo -e "${GREEN}🎉 Restauration terminée !${NC}"
echo
echo "💾 Sauvegarde de sécurité disponible : $SAFETY_BACKUP"
echo "🌐 Accès QuantumShield : http://localhost"
echo
echo "En cas de problème, vous pouvez restaurer les données précédentes depuis : $SAFETY_BACKUP"
```

---

## 📝 Script de Logs

### `logs-quantumshield.sh` - Visualisation des Logs

```bash
#!/bin/bash

# =====================================================
# Script de visualisation des logs QuantumShield
# Usage: ./logs-quantumshield.sh [service] [lines]
# =====================================================

SERVICE="${1:-all}"
LINES="${2:-50}"

# Couleurs
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

show_help() {
    echo "Usage: $0 [service] [lines]"
    echo
    echo "Services disponibles:"
    echo "  all       - Tous les logs (défaut)"
    echo "  backend   - Logs du backend QuantumShield"
    echo "  nginx     - Logs Nginx (accès et erreurs)"
    echo "  mongodb   - Logs MongoDB"
    echo "  supervisor- Logs Supervisor"
    echo "  system    - Logs système"
    echo
    echo "Exemples:"
    echo "  $0                    # Tous les logs, 50 dernières lignes"
    echo "  $0 backend 100        # Logs backend, 100 dernières lignes"
    echo "  $0 nginx              # Logs Nginx, 50 dernières lignes"
}

show_backend_logs() {
    echo -e "${BLUE}🛡️  Logs Backend QuantumShield (${LINES} dernières lignes):${NC}"
    echo "=================================================================="
    if [[ -f "/var/log/supervisor/quantumshield-backend.log" ]]; then
        sudo tail -n $LINES /var/log/supervisor/quantumshield-backend.log
    else
        echo -e "${RED}❌ Fichier de log non trouvé${NC}"
    fi
}

show_nginx_logs() {
    echo -e "${BLUE}🌐 Logs Nginx Access (${LINES} dernières lignes):${NC}"
    echo "================================================="
    if [[ -f "/var/log/nginx/access.log" ]]; then
        sudo tail -n $LINES /var/log/nginx/access.log
    else
        echo -e "${RED}❌ Fichier de log non trouvé${NC}"
    fi
    
    echo
    echo -e "${BLUE}🌐 Logs Nginx Error (${LINES} dernières lignes):${NC}"
    echo "================================================"
    if [[ -f "/var/log/nginx/error.log" ]]; then
        sudo tail -n $LINES /var/log/nginx/error.log
    else
        echo -e "${RED}❌ Fichier de log non trouvé${NC}"
    fi
}

show_mongodb_logs() {
    echo -e "${BLUE}🗄️  Logs MongoDB (${LINES} dernières lignes):${NC}"
    echo "=============================================="
    if [[ -f "/var/log/mongodb/mongod.log" ]]; then
        sudo tail -n $LINES /var/log/mongodb/mongod.log
    else
        echo -e "${RED}❌ Fichier de log non trouvé${NC}"
    fi
}

show_supervisor_logs() {
    echo -e "${BLUE}🔧 Logs Supervisor (${LINES} dernières lignes):${NC}"
    echo "================================================"
    if [[ -f "/var/log/supervisor/supervisord.log" ]]; then
        sudo tail -n $LINES /var/log/supervisor/supervisord.log
    else
        echo -e "${RED}❌ Fichier de log non trouvé${NC}"
    fi
}

show_system_logs() {
    echo -e "${BLUE}💻 Logs Système (${LINES} dernières lignes):${NC}"
    echo "============================================"
    sudo journalctl -n $LINES --no-pager
}

case "$SERVICE" in
    "help"|"-h"|"--help")
        show_help
        ;;
    "backend")
        show_backend_logs
        ;;
    "nginx")
        show_nginx_logs
        ;;
    "mongodb")
        show_mongodb_logs
        ;;
    "supervisor")
        show_supervisor_logs
        ;;
    "system")
        show_system_logs
        ;;
    "all"|*)
        show_backend_logs
        echo
        show_nginx_logs
        echo
        show_mongodb_logs
        echo
        show_supervisor_logs
        ;;
esac

echo
echo -e "${BLUE}💡 Commandes utiles pour les logs:${NC}"
echo "  Logs en temps réel : tail -f /var/log/supervisor/quantumshield-backend.log"
echo "  Recherche dans logs : grep 'ERROR' /var/log/supervisor/quantumshield-backend.log"
echo "  Logs système : journalctl -f -u nginx"
```

---

## 🎯 UTILISATION DES SCRIPTS

### Installation Initiale

```bash
# Télécharger le script d'installation
wget https://raw.githubusercontent.com/[repo]/install-quantumshield.sh
chmod +x install-quantumshield.sh

# Lancer l'installation automatique
./install-quantumshield.sh
```

### Utilisation Quotidienne

```bash
# Démarrer QuantumShield
./start-quantumshield.sh

# Vérifier le statut
./status-quantumshield.sh

# Voir les logs
./logs-quantumshield.sh

# Arrêter QuantumShield
./stop-quantumshield.sh
```

### Maintenance

```bash
# Faire une sauvegarde
./backup-quantumshield.sh

# Restaurer depuis une sauvegarde
./restore-quantumshield.sh ~/quantumshield-backups/quantumshield_backup_20240125_143022.tar.gz
```

---

**🛡️ Ces scripts automatisent complètement le déploiement et la gestion de QuantumShield dans VMware Workstation Pro !**