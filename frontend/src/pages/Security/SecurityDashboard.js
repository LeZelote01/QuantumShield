import React, { useState, useEffect } from 'react';
import { 
  ShieldCheckIcon, 
  KeyIcon, 
  ExclamationTriangleIcon,
  CogIcon,
  DocumentReportIcon,
  BackupIcon,
  EyeIcon,
  UserIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import { useToast } from '../../contexts/ToastContext';

const SecurityDashboard = () => {
  const [securityData, setSecurityData] = useState(null);
  const [mfaStatus, setMfaStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [showMFASetup, setShowMFASetup] = useState(false);
  const [totpSetup, setTotpSetup] = useState(null);
  const [totpCode, setTotpCode] = useState('');
  const { showSuccess, showError } = useToast();

  useEffect(() => {
    loadSecurityData();
  }, []);

  const loadSecurityData = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Charger le dashboard sécurité
      const dashboardResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/security/dashboard`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const dashboardData = await dashboardResponse.json();
      
      // Charger le statut MFA
      const mfaResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/security/mfa/status`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const mfaData = await mfaResponse.json();
      
      setSecurityData(dashboardData.dashboard);
      setMfaStatus(mfaData.mfa_status);
      setLoading(false);
    } catch (error) {
      console.error('Erreur chargement données sécurité:', error);
      showError('Erreur lors du chargement des données de sécurité');
      setLoading(false);
    }
  };

  const setupMFA = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/security/mfa/setup-totp`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ service_name: 'QuantumShield' })
      });
      
      const data = await response.json();
      setTotpSetup(data.setup_data);
      setShowMFASetup(true);
    } catch (error) {
      console.error('Erreur configuration MFA:', error);
      showError('Erreur lors de la configuration MFA');
    }
  };

  const verifyMFA = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/security/mfa/verify-setup`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ totp_code: totpCode })
      });
      
      const data = await response.json();
      if (data.status === 'success') {
        showSuccess('MFA activée avec succès !');
        setShowMFASetup(false);
        setTotpSetup(null);
        setTotpCode('');
        loadSecurityData();
      }
    } catch (error) {
      console.error('Erreur vérification MFA:', error);
      showError('Code invalide, veuillez réessayer');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const getSecurityScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSecurityScoreIcon = (score) => {
    if (score >= 80) return <CheckCircleIcon className="h-8 w-8 text-green-600" />;
    if (score >= 60) return <ExclamationTriangleIcon className="h-8 w-8 text-yellow-600" />;
    return <XCircleIcon className="h-8 w-8 text-red-600" />;
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Sécurité Renforcée</h1>
        <p className="text-gray-600">Gestion avancée de la sécurité QuantumShield</p>
      </div>

      {/* Score de sécurité */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {getSecurityScoreIcon(securityData?.security_score || 0)}
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Score de Sécurité</h2>
              <p className="text-gray-600">Évaluation globale de votre sécurité</p>
            </div>
          </div>
          <div className="text-right">
            <div className={`text-3xl font-bold ${getSecurityScoreColor(securityData?.security_score || 0)}`}>
              {securityData?.security_score || 0}/100
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { key: 'overview', label: 'Vue d\'ensemble', icon: ShieldCheckIcon },
              { key: 'mfa', label: 'MFA', icon: KeyIcon },
              { key: 'alerts', label: 'Alertes', icon: ExclamationTriangleIcon },
              { key: 'compliance', label: 'Conformité', icon: DocumentReportIcon }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-5 w-5" />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Contenu des tabs */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Statistiques */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Événements (24h)</h3>
              <ClockIcon className="h-6 w-6 text-gray-400" />
            </div>
            <div className="text-3xl font-bold text-blue-600">
              {securityData?.overview?.events_last_24h || 0}
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Alertes Actives</h3>
              <ExclamationTriangleIcon className="h-6 w-6 text-red-400" />
            </div>
            <div className="text-3xl font-bold text-red-600">
              {securityData?.overview?.active_alerts || 0}
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Utilisateurs MFA</h3>
              <UserIcon className="h-6 w-6 text-green-400" />
            </div>
            <div className="text-3xl font-bold text-green-600">
              {securityData?.overview?.mfa_enabled_users || 0}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'mfa' && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Authentification Multi-Facteur</h3>
            <KeyIcon className="h-6 w-6 text-blue-600" />
          </div>

          {!mfaStatus?.mfa_enabled ? (
            <div className="text-center py-8">
              <KeyIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h4 className="text-lg font-medium text-gray-900 mb-2">MFA non activée</h4>
              <p className="text-gray-600 mb-6">Sécurisez votre compte avec l'authentification à deux facteurs</p>
              <button
                onClick={setupMFA}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Configurer MFA
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <CheckCircleIcon className="h-6 w-6 text-green-600" />
                  <div>
                    <p className="font-medium text-green-900">MFA Activée</p>
                    <p className="text-sm text-green-700">Votre compte est protégé par l'authentification à deux facteurs</p>
                  </div>
                </div>
              </div>
              
              {mfaStatus.methods.map((method, index) => (
                <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{method.method.toUpperCase()}</p>
                    <p className="text-sm text-gray-600">
                      Activé le {new Date(method.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">
                      Actif
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'alerts' && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Alertes de Sécurité</h3>
            <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
          </div>

          {securityData?.active_alerts?.length > 0 ? (
            <div className="space-y-4">
              {securityData.active_alerts.map((alert, index) => (
                <div key={index} className="border-l-4 border-red-500 bg-red-50 p-4 rounded-r-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-red-900">{alert.alert_type}</h4>
                      <p className="text-sm text-red-700">
                        Score de risque: {alert.risk_score}
                      </p>
                      <p className="text-xs text-red-600">
                        {new Date(alert.created_at).toLocaleString()}
                      </p>
                    </div>
                    <div className="text-red-600">
                      <ExclamationTriangleIcon className="h-6 w-6" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <CheckCircleIcon className="h-16 w-16 text-green-400 mx-auto mb-4" />
              <h4 className="text-lg font-medium text-gray-900 mb-2">Aucune alerte active</h4>
              <p className="text-gray-600">Votre système est sécurisé</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'compliance' && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Conformité Réglementaire</h3>
            <DocumentReportIcon className="h-6 w-6 text-blue-600" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-4 border rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">GDPR</h4>
              <p className="text-sm text-gray-600 mb-3">Conformité au Règlement Général sur la Protection des Données</p>
              <div className="flex items-center space-x-2">
                <CheckCircleIcon className="h-5 w-5 text-green-600" />
                <span className="text-sm text-green-700">Conforme</span>
              </div>
            </div>

            <div className="p-4 border rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">CCPA</h4>
              <p className="text-sm text-gray-600 mb-3">Conformité à la California Consumer Privacy Act</p>
              <div className="flex items-center space-x-2">
                <CheckCircleIcon className="h-5 w-5 text-green-600" />
                <span className="text-sm text-green-700">Conforme</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal MFA Setup */}
      {showMFASetup && totpSetup && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-md w-full p-6">
            <div className="text-center mb-6">
              <KeyIcon className="h-12 w-12 text-blue-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900">Configuration MFA</h3>
              <p className="text-gray-600">Scannez le QR code avec votre application d'authentification</p>
            </div>

            <div className="text-center mb-6">
              <img
                src={`data:image/png;base64,${totpSetup.qr_code}`}
                alt="QR Code"
                className="mx-auto border rounded-lg"
              />
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Code de vérification
              </label>
              <input
                type="text"
                value={totpCode}
                onChange={(e) => setTotpCode(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Entrez le code à 6 chiffres"
              />
            </div>

            <div className="flex space-x-4">
              <button
                onClick={() => {
                  setShowMFASetup(false);
                  setTotpSetup(null);
                  setTotpCode('');
                }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Annuler
              </button>
              <button
                onClick={verifyMFA}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Vérifier
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SecurityDashboard;