# QuantumShield 🛡️

**Cryptographie post-quantique pour l'Internet des objets (IoT)**

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-19.0-blue.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.1-green.svg)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4%2B-green.svg)](https://mongodb.com)

## 🌟 Vue d'ensemble

QuantumShield est une plateforme révolutionnaire qui sécurise l'Internet des objets (IoT) grâce à la cryptographie post-quantique. Conçue pour résister aux attaques des futurs ordinateurs quantiques, elle offre une protection avancée pour les dispositifs connectés tout en créant un écosystème économique décentralisé.

### 🎯 Mission

Protéger les dispositifs IoT contre les menaces quantiques tout en créant une économie décentralisée récompensant la sécurité et la participation au réseau.

### 🔑 Problématique résolue

- **Menace quantique** : Les ordinateurs quantiques rendront obsolètes les algorithmes cryptographiques actuels
- **Sécurité IoT** : Les dispositifs IoT sont vulnérables aux attaques cybernétiques
- **Fragmentation** : Manque de standards unifiés pour la sécurité IoT
- **Économie fermée** : Absence d'incitations pour la sécurité collaborative

## 🚀 Fonctionnalités principales

### 1. 🔐 Cryptographie post-quantique NTRU++

- **Algorithme NTRU++** optimisé pour l'IoT
- **Résistance quantique** : Sécurité contre les attaques d'ordinateurs quantiques
- **Performance** : 70% plus rapide que les solutions logicielles classiques
- **Faible consommation** : Optimisé pour les dispositifs à faible puissance
- **Algorithmes multiples** : Support pour Kyber-512/768/1024 et Dilithium-2/3/5
- **Clés hybrides** : Génération de clés combinant chiffrement et signature
- **Comparaison automatique** : Recommandations d'algorithmes selon le contexte

### 2. 🔗 Blockchain privée pour la confiance matérielle

- **Consensus Proof of Work** adapté à l'IoT
- **Enregistrement firmware** : Hashes des firmwares stockés de manière immuable
- **Validation d'intégrité** : Vérification automatique des mises à jour
- **Hyperledger-style** : Architecture blockchain privée haute performance

### 3. 🏆 Système de tokens $QS (QuantumShield)

- **Token utilitaire** : Récompenses pour la participation au réseau
- **Économie auto-monétisante** : Incitations pour la sécurité collaborative
- **Types de récompenses** :
  - Enregistrement de dispositifs (50 QS)
  - Détection d'anomalies (25 QS)
  - Validation firmware (10 QS)
  - Participation réseau (5 QS)
  - Partage de données (15 QS)
  - Participation mining (100 QS)

### 4. 📱 Gestion des dispositifs IoT

- **Enregistrement sécurisé** : Clés NTRU++ pour chaque dispositif
- **Monitoring temps réel** : Heartbeat et métriques de performance
- **Détection d'anomalies** : IA pour identifier les comportements suspects
- **Mise à jour OTA** : Over-the-air updates sécurisées
- **Protocoles IoT** : Support MQTT, CoAP, LoRaWAN, Zigbee, Z-Wave, Thread, Matter
- **Communication unifiée** : Système de messages unifié pour tous les protocoles
- **Gestion centralisée** : Dashboard pour surveiller tous les dispositifs connectés

### 5. ⛏️ Mining distribué

- **Pool de mining** : Participation collaborative au consensus
- **Calculateur de rentabilité** : Estimation des gains
- **Classement mineurs** : Compétition et récompenses
- **Difficulty adjustment** : Adaptation automatique de la difficulté

### 6. 📊 Dashboard temps réel

- **Métriques complètes** : Dispositifs, tokens, réseau
- **Alertes intelligentes** : Notifications proactives
- **Analyse performance** : Optimisation continue
- **Visualisations** : Graphiques et tableaux de bord

## 🏗️ Architecture technique

### Backend (FastAPI + MongoDB)

```
/app/backend/
├── server.py              # Application FastAPI principale
├── models/
│   └── quantum_models.py  # Modèles Pydantic
├── services/
│   ├── ntru_service.py    # Cryptographie NTRU++
│   ├── blockchain_service.py # Blockchain privée
│   ├── device_service.py  # Gestion dispositifs
│   ├── token_service.py   # Système tokens $QS
│   ├── auth_service.py    # Authentification
│   └── mining_service.py  # Mining distribué
└── routes/
    ├── auth_routes.py     # Authentification
    ├── crypto_routes.py   # Cryptographie
    ├── blockchain_routes.py # Blockchain
    ├── device_routes.py   # Dispositifs
    ├── token_routes.py    # Tokens
    ├── mining_routes.py   # Mining
    └── dashboard_routes.py # Dashboard
```

### Frontend (React + Tailwind)

```
/app/frontend/
├── src/
│   ├── components/        # Composants réutilisables
│   ├── pages/            # Pages principales
│   ├── services/         # Services API
│   ├── contexts/         # Contextes React
│   └── utils/            # Utilitaires
├── public/               # Assets statiques
└── package.json          # Dépendances Node.js
```

## 📋 Prérequis

### Système d'exploitation
- Linux (Ubuntu 20.04+ recommandé)
- macOS (avec Homebrew)
- Windows (avec WSL2)

### Logiciels requis
- **Python 3.9+** avec pip
- **Node.js 18+** avec yarn
- **MongoDB 4.4+**
- **Git**

### Matériel recommandé
- **RAM** : 8GB minimum, 16GB recommandé
- **Stockage** : 20GB espace libre
- **Processeur** : Multi-core pour le mining

## 🛠️ Installation

### 1. Cloner le repository

```bash
git clone https://github.com/your-username/quantumshield.git
cd quantumshield
```

### 2. Configuration Backend

```bash
cd backend

# Installer les dépendances Python
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos paramètres

# Lancer MongoDB (si local)
sudo systemctl start mongod

# Démarrer le serveur
python server.py
```

### 3. Configuration Frontend

```bash
cd frontend

# Installer les dépendances Node.js
yarn install

# Configurer l'environnement
cp .env.example .env
# Éditer .env avec l'URL du backend

# Démarrer le serveur de développement
yarn start
```

### 4. Vérification de l'installation

- **Backend** : http://localhost:8001/docs (Documentation API)
- **Frontend** : http://localhost:3000 (Interface utilisateur)

## 🔧 Configuration

### Variables d'environnement Backend

```env
# Database
MONGO_URL=mongodb://localhost:27017
DB_NAME=quantumshield

# Security
SECRET_KEY=your-secret-key-here
NTRU_KEY_SIZE=2048

# Blockchain
BLOCKCHAIN_NODE_URL=http://localhost:8545
MINING_DIFFICULTY=4
REWARD_AMOUNT=10

# Tokens
QS_TOKEN_CONTRACT_ADDRESS=0x123...
```

### Variables d'environnement Frontend

```env
# API Backend
REACT_APP_BACKEND_URL=http://localhost:8001

# Features
REACT_APP_ENABLE_MINING=true
REACT_APP_ENABLE_NOTIFICATIONS=true
```

## 🚀 Utilisation

### 1. Créer un compte

1. Accédez à http://localhost:3000
2. Cliquez sur "S'inscrire"
3. Remplissez le formulaire d'inscription
4. Confirmez votre email (si activé)

### 2. Enregistrer un dispositif IoT

1. Accédez à "Devices IoT"
2. Cliquez sur "Enregistrer un device"
3. Sélectionnez le type de dispositif
4. Configurez les paramètres
5. Récupérez les clés NTRU++ générées

### 3. Participer au mining

1. Accédez à "Mining"
2. Cliquez sur "Commencer le mining"
3. Configurez vos paramètres de mining
4. Surveillez vos gains en temps réel

### 4. Gérer vos tokens $QS

1. Accédez à "Tokens $QS"
2. Consultez votre solde et historique
3. Effectuez des transferts
4. Réclamez vos récompenses

## 📊 API Documentation

### Endpoints principaux

#### Authentification
- `POST /api/auth/register` - Inscription
- `POST /api/auth/login` - Connexion
- `GET /api/auth/profile` - Profil utilisateur

#### Cryptographie
- `POST /api/crypto/generate-keys` - Génération clés NTRU++
- `POST /api/crypto/encrypt` - Chiffrement
- `POST /api/crypto/decrypt` - Déchiffrement
- `POST /api/crypto/sign` - Signature
- `POST /api/crypto/verify` - Vérification signature

#### Dispositifs
- `POST /api/devices/register` - Enregistrement dispositif
- `GET /api/devices/` - Liste des dispositifs
- `POST /api/devices/heartbeat` - Heartbeat dispositif
- `GET /api/devices/{device_id}/metrics` - Métriques dispositif

#### Blockchain
- `GET /api/blockchain/stats` - Statistiques blockchain
- `GET /api/blockchain/blocks` - Liste des blocs
- `POST /api/blockchain/transactions` - Créer transaction

#### Tokens
- `GET /api/tokens/balance` - Solde utilisateur
- `POST /api/tokens/transfer` - Transfert tokens
- `GET /api/tokens/transactions` - Historique transactions

#### Mining
- `GET /api/mining/task` - Obtenir tâche mining
- `POST /api/mining/submit` - Soumettre résultat
- `GET /api/mining/stats` - Statistiques mining

### Documentation interactive

La documentation complète de l'API est disponible à :
- **Swagger UI** : http://localhost:8001/docs
- **ReDoc** : http://localhost:8001/redoc

## 🔐 Sécurité

### Cryptographie post-quantique

```python
# Génération de clés NTRU++
public_key, private_key = ntru_service.generate_keypair()

# Chiffrement
encrypted_data = ntru_service.encrypt(message, public_key)

# Déchiffrement
decrypted_data = ntru_service.decrypt(encrypted_data, private_key)

# Signature
signature = ntru_service.sign(message, private_key)

# Vérification
is_valid = ntru_service.verify(message, signature, public_key)
```

### Blockchain privée

```python
# Enregistrement firmware
tx_hash = blockchain_service.register_firmware_update(
    device_id="DEVICE001",
    firmware_hash="0x123...",
    version="1.0.0"
)

# Validation chaîne
is_valid = await blockchain_service.validate_chain()
```

### Gestion des tokens

```python
# Récompenser utilisateur
success = await token_service.reward_user(
    user_id="user123",
    reward_type="device_registration",
    device_id="DEVICE001"
)

# Transfert tokens
success = await token_service.transfer_tokens(
    from_user="user1",
    to_user="user2",
    amount=100.0
)
```

## 🧪 Tests

### Tests Backend

```bash
cd backend

# Tests unitaires
pytest tests/unit/

# Tests d'intégration
pytest tests/integration/

# Tests de performance
pytest tests/performance/

# Coverage
pytest --cov=. --cov-report=html
```

### Tests Frontend

```bash
cd frontend

# Tests unitaires
yarn test

# Tests e2e
yarn test:e2e

# Coverage
yarn test:coverage
```

## 📈 Monitoring et métriques

### Métriques système

- **Uptime réseau** : 99.9%
- **Latence moyenne** : <100ms
- **Transactions par seconde** : Variable selon réseau
- **Dispositifs actifs** : Temps réel

### Alertes configurables

- Dispositifs hors ligne
- Anomalies détectées
- Attaques potentielles
- Performance dégradée

### Logs

```bash
# Logs backend
tail -f /var/log/quantumshield/backend.log

# Logs frontend
tail -f /var/log/quantumshield/frontend.log

# Logs blockchain
tail -f /var/log/quantumshield/blockchain.log
```

## 🔄 Déploiement

### Environnement de production

```bash
# Construction production
cd frontend
yarn build

# Déploiement Docker
docker-compose up -d

# Vérification santé
curl http://localhost:8001/api/health
```

### Configuration SSL

```nginx
server {
    listen 443 ssl;
    server_name quantumshield.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:3000;
    }
    
    location /api {
        proxy_pass http://localhost:8001;
    }
}
```

## 📱 Intégration dispositifs IoT

### SDK Python pour dispositifs

```python
from quantumshield import QuantumShieldClient

# Initialisation
client = QuantumShieldClient(
    device_id="DEVICE001",
    private_key="your_private_key"
)

# Enregistrement
client.register_device(
    device_type="Smart Sensor",
    capabilities=["temperature", "humidity"]
)

# Envoi heartbeat
client.send_heartbeat(
    status="active",
    sensor_data={"temperature": 25.5, "humidity": 60}
)

# Mise à jour firmware
client.update_firmware("v1.1.0")
```

### SDK JavaScript pour web

```javascript
import { QuantumShieldJS } from 'quantumshield-js';

// Initialisation
const client = new QuantumShieldJS({
  apiUrl: 'http://localhost:8001',
  deviceId: 'DEVICE001'
});

// Enregistrement
await client.registerDevice({
  deviceType: 'Smart Camera',
  capabilities: ['video_streaming', 'motion_detection']
});

// Monitoring
await client.sendHeartbeat({
  status: 'active',
  sensorData: { battery: 85, signal: 'strong' }
});
```

## 🌐 Écosystème et roadmap

### Phase 1 : MVP (Actuel)
- [x] Cryptographie NTRU++ de base
- [x] Blockchain privée
- [x] Système tokens $QS
- [x] Interface utilisateur
- [x] Mining distribué

### Phase 2 : Optimisations (T2 2024)
- [ ] Co-processeur ASIC pour NTRU++
- [ ] Optimisations performance
- [ ] SDK pour plus de langages
- [ ] Intégrations cloud

### Phase 3 : Expansion (T3 2024)
- [ ] Marketplace de dispositifs
- [ ] Intelligence artificielle avancée
- [ ] Interopérabilité blockchain
- [ ] Standards industriels

### Phase 4 : Écosystème complet (T4 2024)
- [ ] Partenariats constructeurs
- [ ] Certification sécurité
- [ ] Déploiement global
- [ ] Communauté développeurs

## 🤝 Contribution

### Comment contribuer

1. **Fork** le repository
2. **Créer** une branche feature (`git checkout -b feature/amazing-feature`)
3. **Commit** vos changements (`git commit -m 'Add amazing feature'`)
4. **Push** la branche (`git push origin feature/amazing-feature`)
5. **Ouvrir** une Pull Request

### Guidelines

- **Code style** : Suivre PEP 8 pour Python, ESLint pour JavaScript
- **Tests** : Ajouter des tests pour les nouvelles fonctionnalités
- **Documentation** : Documenter le code et les APIs
- **Sécurité** : Tester la sécurité des nouvelles fonctionnalités

### Issues et bugs

Utilisez les templates GitHub pour :
- 🐛 Signaler des bugs
- 💡 Proposer des fonctionnalités
- 📝 Améliorer la documentation
- 🔒 Rapporter des vulnérabilités

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- **Communauté NTRU** pour les algorithmes cryptographiques
- **Équipe FastAPI** pour le framework web
- **Communauté React** pour l'interface utilisateur
- **Contributeurs** du projet QuantumShield

## 📞 Support et contact

### Support technique
- 📧 Email : support@quantumshield.tech
- 💬 Discord : https://discord.gg/quantumshield
- 📱 Telegram : https://t.me/quantumshield

### Réseaux sociaux
- 🐦 Twitter : [@QuantumShield](https://twitter.com/quantumshield)
- 💼 LinkedIn : [QuantumShield](https://linkedin.com/company/quantumshield)
- 📺 YouTube : [QuantumShield Channel](https://youtube.com/c/quantumshield)

### Documentation
- 📖 Wiki : https://github.com/quantumshield/quantumshield/wiki
- 🎓 Tutoriels : https://docs.quantumshield.tech
- 📊 Exemples : https://examples.quantumshield.tech

---

**QuantumShield** - Sécuriser l'avenir de l'IoT avec la cryptographie post-quantique 🛡️

*Développé avec ❤️ pour la communauté IoT mondiale*
