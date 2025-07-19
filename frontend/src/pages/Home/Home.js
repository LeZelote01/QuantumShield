import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ShieldCheckIcon, 
  CpuChipIcon,
  CubeTransparentIcon,
  BanknotesIcon,
  DevicePhoneMobileIcon,
  ChartBarIcon,
  GlobeAltIcon,
  ClockIcon,
  UserGroupIcon,
  LockClosedIcon,
  PlayIcon,
  CheckIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';

const Home = () => {
  const features = [
    {
      icon: <ShieldCheckIcon className="h-6 w-6" />,
      title: "Cryptographie Post-Quantique NTRU++",
      description: "Protection avancée contre les menaces quantiques avec algorithmes Kyber, Dilithium et preuves zero-knowledge"
    },
    {
      icon: <CubeTransparentIcon className="h-6 w-6" />,
      title: "Blockchain Privée",
      description: "Blockchain sécurisée avec consensus Proof of Work, gouvernance décentralisée et smart contracts"
    },
    {
      icon: <BanknotesIcon className="h-6 w-6" />,
      title: "Système de Tokens $QS",
      description: "Économie de tokens intégrée avec récompenses, staking, marketplace et DeFi"
    },
    {
      icon: <DevicePhoneMobileIcon className="h-6 w-6" />,
      title: "Gestion IoT Avancée",
      description: "Support de 8 types d'appareils avec protocoles MQTT, CoAP, LoRaWAN, Zigbee et mises à jour OTA"
    },
    {
      icon: <ChartBarIcon className="h-6 w-6" />,
      title: "Mining Distribué",
      description: "Pool collaborative de mining avec récompenses automatiques et statistiques en temps réel"
    },
    {
      icon: <LockClosedIcon className="h-6 w-6" />,
      title: "Sécurité Renforcée",
      description: "2FA/MFA, honeypots, audit automatisé et conformité GDPR/CCPA"
    }
  ];

  const advancedFeatures = [
    "IA Analytics et détection d'anomalies",
    "Services de géolocalisation sécurisée",
    "Certificats X.509 et PKI",
    "API GraphQL et webhooks",
    "Recommandations personnalisées",
    "Dashboards personnalisables",
    "Intégrations cloud (AWS, Azure, GCP)",
    "Connecteurs ERP/CRM",
    "Conformité et audit automatisé",
    "API Gateway avec rate limiting"
  ];

  const benefits = [
    {
      title: "Sécurité Maximale",
      description: "Protection contre les attaques quantiques futures",
      icon: <ShieldCheckIcon className="h-8 w-8 text-indigo-600" />
    },
    {
      title: "Évolutivité",
      description: "Architecture modulaire s'adaptant à vos besoins",
      icon: <CubeTransparentIcon className="h-8 w-8 text-purple-600" />
    },
    {
      title: "Économie Intégrée",
      description: "Monétisez vos données IoT avec les tokens $QS",
      icon: <BanknotesIcon className="h-8 w-8 text-green-600" />
    }
  ];

  const stats = [
    { number: "21+", label: "Services Intégrés", icon: <CpuChipIcon className="h-6 w-6" /> },
    { number: "8", label: "Protocoles IoT", icon: <DevicePhoneMobileIcon className="h-6 w-6" /> },
    { number: "7", label: "Algorithmes Crypto", icon: <LockClosedIcon className="h-6 w-6" /> },
    { number: "∞", label: "Appareils Supportés", icon: <GlobeAltIcon className="h-6 w-6" /> }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <ShieldCheckIcon className="h-8 w-8 text-gray-900" />
              <span className="text-2xl font-bold text-gray-900">QuantumShield</span>
            </div>
            <div className="flex space-x-4">
              <Link
                to="/login"
                className="text-gray-700 hover:text-gray-900 px-4 py-2 rounded-lg transition-colors font-medium"
              >
                Se connecter
              </Link>
              <Link
                to="/register"
                className="bg-gray-900 text-white hover:bg-gray-800 px-6 py-2 rounded-lg font-medium transition-colors"
              >
                S'inscrire
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              L'avenir de la <span className="text-gray-600">Sécurité IoT</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              QuantumShield révolutionne la sécurité des objets connectés avec la cryptographie post-quantique, 
              une blockchain privée et un écosystème complet de tokens $QS pour l'ère quantique.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                to="/register"
                className="bg-gray-900 hover:bg-gray-800 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all flex items-center space-x-2"
              >
                <PlayIcon className="h-5 w-5" />
                <span>Commencer maintenant</span>
              </Link>
              <Link
                to="/login"
                className="bg-white text-gray-900 hover:bg-gray-50 px-8 py-4 rounded-xl font-semibold text-lg transition-all border border-gray-200"
              >
                Déjà membre ? Se connecter
              </Link>
            </div>
          </div>
        </div>

        {/* Hero Image */}
        <div className="mt-16 max-w-6xl mx-auto px-4">
          <div className="bg-white rounded-2xl border border-gray-200 shadow-lg overflow-hidden">
            <img
              src="https://images.unsplash.com/photo-1550751827-4bd374c3f58b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwxfHxjeWJlcnNlY3VyaXR5fGVufDB8fHx8MTc1MjkyNTI5MHww&ixlib=rb-4.1.0&q=85"
              alt="Cybersecurity Technology"
              className="w-full h-64 object-cover"
            />
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white border-y border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="flex justify-center mb-3">
                  <div className="bg-gray-100 p-3 rounded-lg">
                    {React.cloneElement(stat.icon, { className: "h-6 w-6 text-gray-700" })}
                  </div>
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">{stat.number}</div>
                <div className="text-gray-600 font-medium">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Fonctionnalités Principales
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Une suite complète d'outils pour sécuriser, gérer et monétiser vos appareils IoT
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm hover:shadow-md transition-all">
                <div className="w-12 h-12 bg-gray-100 text-gray-700 rounded-lg flex items-center justify-center mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Advanced Features */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Fonctionnalités Avancées
            </h2>
            <p className="text-xl text-gray-600">
              Plus de 10 services additionnels pour une expérience complète
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {advancedFeatures.map((feature, index) => (
              <div key={index} className="bg-gray-50 rounded-lg p-4 border border-gray-200 flex items-center space-x-3">
                <CheckIcon className="h-5 w-5 text-gray-700 flex-shrink-0" />
                <span className="text-gray-900 font-medium">{feature}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Pourquoi Choisir QuantumShield ?
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {benefits.map((benefit, index) => (
              <div key={index} className="text-center">
                <div className="bg-white w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 border border-gray-200 shadow-sm">
                  {React.cloneElement(benefit.icon, { className: "h-8 w-8 text-gray-700" })}
                </div>
                <h3 className="text-2xl font-semibold text-gray-900 mb-4">{benefit.title}</h3>
                <p className="text-gray-600 text-lg">{benefit.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Security Images */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white rounded-xl overflow-hidden border border-gray-200 shadow-sm">
              <img
                src="https://images.unsplash.com/photo-1550751827-4bd374c3f58b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2Mzl8MHwxfHNlYXJjaHwxfHxjeWJlcnNlY3VyaXR5fGVufDB8fHx8MTc1MjkyNTI5MHww&ixlib=rb-4.1.0&q=85"
                alt="Cybersecurity Technology"
                className="w-full h-48 object-cover"
              />
              <div className="p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Sécurité Cyber Avancée</h3>
                <p className="text-gray-600">Protection multi-couches contre toutes les menaces</p>
              </div>
            </div>
            <div className="bg-white rounded-xl overflow-hidden border border-gray-200 shadow-sm">
              <img
                src="https://images.unsplash.com/photo-1553341640-9397992456f3?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHxxdWFudHVtJTIwY29tcHV0aW5nfGVufDB8fHx8MTc1MjkyNTI4M3ww&ixlib=rb-4.1.0&q=85"
                alt="IoT Technology"
                className="w-full h-48 object-cover"
              />
              <div className="p-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">IoT Nouvelle Génération</h3>
                <p className="text-gray-600">Connectivité intelligente et sécurisée pour tous vos appareils</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Prêt à Sécuriser Votre Avenir ?
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Rejoignez l'écosystème QuantumShield et protégez vos appareils IoT avec la cryptographie post-quantique
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="bg-gray-900 hover:bg-gray-800 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all flex items-center justify-center space-x-2"
            >
              <UserGroupIcon className="h-5 w-5" />
              <span>Créer un compte gratuit</span>
              <ArrowRightIcon className="h-5 w-5" />
            </Link>
            <Link
              to="/login"
              className="bg-white text-gray-900 hover:bg-gray-50 px-8 py-4 rounded-xl font-semibold text-lg transition-all border border-gray-200"
            >
              Accéder à mon compte
            </Link>
          </div>

          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
            <div className="bg-white rounded-lg p-6 border border-gray-200 shadow-sm">
              <ClockIcon className="h-8 w-8 text-gray-700 mb-3" />
              <h3 className="text-gray-900 font-semibold mb-2">Inscription Rapide</h3>
              <p className="text-gray-600 text-sm">Créez votre compte en moins de 2 minutes et commencez immédiatement</p>
            </div>
            <div className="bg-white rounded-lg p-6 border border-gray-200 shadow-sm">
              <BanknotesIcon className="h-8 w-8 text-gray-700 mb-3" />
              <h3 className="text-gray-900 font-semibold mb-2">Wallet $QS Gratuit</h3>
              <p className="text-gray-600 text-sm">Recevez automatiquement votre wallet de tokens $QS sécurisé</p>
            </div>
            <div className="bg-white rounded-lg p-6 border border-gray-200 shadow-sm">
              <ShieldCheckIcon className="h-8 w-8 text-gray-700 mb-3" />
              <h3 className="text-gray-900 font-semibold mb-2">Sécurité Maximale</h3>
              <p className="text-gray-600 text-sm">Authentification 2FA et cryptographie post-quantique incluses</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-3 mb-4 md:mb-0">
              <ShieldCheckIcon className="h-8 w-8 text-white" />
              <span className="text-2xl font-bold text-white">QuantumShield</span>
            </div>
            <div className="text-gray-300 text-center md:text-right">
              <p>© 2025 QuantumShield. Cryptographie post-quantique pour l'IoT.</p>
              <p className="text-sm mt-1">Protégez votre avenir dès aujourd'hui.</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home;