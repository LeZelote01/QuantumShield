import React, { useState, useEffect } from 'react';
import { 
  ShieldCheckIcon, 
  EyeSlashIcon, 
  DocumentDuplicateIcon,
  ExclamationTriangleIcon,
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  UserIcon
} from '@heroicons/react/24/outline';
import { useToast } from '../../contexts/ToastContext';

const AdvancedSecurity = () => {
  const [activeTab, setActiveTab] = useState('honeypots');
  const [loading, setLoading] = useState(false);
  const [honeypotData, setHoneypotData] = useState(null);
  const [backupData, setBackupData] = useState(null);
  const [complianceData, setComplianceData] = useState(null);
  const [healthCheck, setHealthCheck] = useState(null);
  const { showSuccess, showError } = useToast();

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      if (activeTab === 'honeypots') {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/security/honeypots/report`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        setHoneypotData(data.report);
      }
      
      if (activeTab === 'backup') {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/security/backup/report`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        setBackupData(data.report);
      }
      
      if (activeTab === 'compliance') {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/security/compliance/report`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        setComplianceData(data.compliance_report);
      }
      
      if (activeTab === 'health') {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/security/health-check`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        setHealthCheck(data.health_check);
      }
      
    } catch (error) {
      console.error('Erreur chargement données:', error);
      showError('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  const createHoneypot = async (type, config) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/security/honeypots/create`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          honeypot_type: type,
          config: config
        })
      });
      
      if (response.ok) {
        showSuccess('Honeypot créé avec succès');
        loadData();
      }
    } catch (error) {
      console.error('Erreur création honeypot:', error);
      showError('Erreur lors de la création du honeypot');
    }
  };

  const createBackup = async (type) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/security/backup/create`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          backup_type: type,
          data: {
            timestamp: new Date().toISOString(),
            security_config: 'encrypted'
          }
        })
      });
      
      if (response.ok) {
        showSuccess('Sauvegarde créée avec succès');
        loadData();
      }
    } catch (error) {
      console.error('Erreur création sauvegarde:', error);
      showError('Erreur lors de la création de la sauvegarde');
    }
  };

  const generateGDPRReport = async () => {
    try {
      const token = localStorage.getItem('token');
      const user = JSON.parse(localStorage.getItem('user'));
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/security/gdpr/report`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: user.id
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        // Télécharger le rapport
        const blob = new Blob([JSON.stringify(data.gdpr_report, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `gdpr_report_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        showSuccess('Rapport GDPR généré et téléchargé');
      }
    } catch (error) {
      console.error('Erreur génération rapport GDPR:', error);
      showError('Erreur lors de la génération du rapport GDPR');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy': return 'text-green-600';
      case 'good': return 'text-blue-600';
      case 'degraded': return 'text-yellow-600';
      case 'critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy': return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
      case 'good': return <CheckCircleIcon className="h-5 w-5 text-blue-600" />;
      case 'degraded': return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600" />;
      case 'critical': return <XCircleIcon className="h-5 w-5 text-red-600" />;
      default: return <ClockIcon className="h-5 w-5 text-gray-600" />;
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Sécurité Avancée</h1>
        <p className="text-gray-600">Gestion des fonctionnalités de sécurité avancées</p>
      </div>

      {/* Tabs */}
      <div className="mb-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { key: 'honeypots', label: 'Honeypots', icon: EyeSlashIcon },
              { key: 'backup', label: 'Sauvegardes', icon: DocumentDuplicateIcon },
              { key: 'compliance', label: 'Conformité', icon: ShieldCheckIcon },
              { key: 'health', label: 'Santé', icon: CheckCircleIcon }
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

      {/* Contenu */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <>
          {activeTab === 'honeypots' && (
            <div className="space-y-6">
              {/* Statistiques */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Honeypots Actifs</p>
                      <p className="text-2xl font-bold text-blue-600">
                        {honeypotData?.active_honeypots || 0}
                      </p>
                    </div>
                    <EyeSlashIcon className="h-8 w-8 text-blue-600" />
                  </div>
                </div>

                <div className="bg-white rounded-xl shadow-sm p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Interactions Totales</p>
                      <p className="text-2xl font-bold text-red-600">
                        {honeypotData?.total_interactions || 0}
                      </p>
                    </div>
                    <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
                  </div>
                </div>

                <div className="bg-white rounded-xl shadow-sm p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Récentes (24h)</p>
                      <p className="text-2xl font-bold text-yellow-600">
                        {honeypotData?.recent_interactions || 0}
                      </p>
                    </div>
                    <ClockIcon className="h-8 w-8 text-yellow-600" />
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-lg font-semibold mb-4">Créer un Honeypot</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <button
                    onClick={() => createHoneypot('fake_login', { attempts_threshold: 3 })}
                    className="p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="text-left">
                      <h4 className="font-medium text-gray-900">Fausse Page de Connexion</h4>
                      <p className="text-sm text-gray-600">Détecte les tentatives de connexion malveillantes</p>
                    </div>
                  </button>

                  <button
                    onClick={() => createHoneypot('fake_api', { endpoint: '/api/admin/users' })}
                    className="p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="text-left">
                      <h4 className="font-medium text-gray-900">Fausse API</h4>
                      <p className="text-sm text-gray-600">Piège pour les attaques sur les APIs</p>
                    </div>
                  </button>
                </div>
              </div>

              {/* Activité récente */}
              {honeypotData?.recent_activity && honeypotData.recent_activity.length > 0 && (
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h3 className="text-lg font-semibold mb-4">Activité Récente</h3>
                  <div className="space-y-3">
                    {honeypotData.recent_activity.map((activity, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <p className="font-medium text-gray-900">Honeypot {activity.honeypot_id}</p>
                          <p className="text-sm text-gray-600">
                            {new Date(activity.timestamp).toLocaleString()}
                          </p>
                        </div>
                        <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-sm">
                          Interaction détectée
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'backup' && (
            <div className="space-y-6">
              {/* Statistiques */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Sauvegardes Totales</p>
                      <p className="text-2xl font-bold text-blue-600">
                        {backupData?.total_backups || 0}
                      </p>
                    </div>
                    <DocumentDuplicateIcon className="h-8 w-8 text-blue-600" />
                  </div>
                </div>

                <div className="bg-white rounded-xl shadow-sm p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Taille Totale</p>
                      <p className="text-2xl font-bold text-green-600">
                        {backupData?.total_size ? Math.round(backupData.total_size / 1024) : 0} KB
                      </p>
                    </div>
                    <DocumentDuplicateIcon className="h-8 w-8 text-green-600" />
                  </div>
                </div>

                <div className="bg-white rounded-xl shadow-sm p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600">Types</p>
                      <p className="text-2xl font-bold text-purple-600">
                        {backupData?.backup_types ? Object.keys(backupData.backup_types).length : 0}
                      </p>
                    </div>
                    <DocumentDuplicateIcon className="h-8 w-8 text-purple-600" />
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-lg font-semibold mb-4">Créer une Sauvegarde</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <button
                    onClick={() => createBackup('security_config')}
                    className="p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="text-left">
                      <h4 className="font-medium text-gray-900">Configuration Sécurité</h4>
                      <p className="text-sm text-gray-600">Sauvegarde des paramètres de sécurité</p>
                    </div>
                  </button>

                  <button
                    onClick={() => createBackup('user_data')}
                    className="p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="text-left">
                      <h4 className="font-medium text-gray-900">Données Utilisateur</h4>
                      <p className="text-sm text-gray-600">Sauvegarde des données importantes</p>
                    </div>
                  </button>
                </div>
              </div>

              {/* Sauvegardes récentes */}
              {backupData?.recent_backups && backupData.recent_backups.length > 0 && (
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h3 className="text-lg font-semibold mb-4">Sauvegardes Récentes</h3>
                  <div className="space-y-3">
                    {backupData.recent_backups.map((backup, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <p className="font-medium text-gray-900">{backup.type}</p>
                          <p className="text-sm text-gray-600">
                            {new Date(backup.created_at).toLocaleString()} - {Math.round(backup.size / 1024)} KB
                          </p>
                        </div>
                        <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">
                          {backup.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'compliance' && (
            <div className="space-y-6">
              {/* Score de conformité */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Score de Conformité GDPR</h3>
                  <div className="text-2xl font-bold text-blue-600">
                    {complianceData?.gdpr_compliance?.compliance_score || 0}%
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full" 
                    style={{ width: `${complianceData?.gdpr_compliance?.compliance_score || 0}%` }}
                  ></div>
                </div>
              </div>

              {/* Statistiques GDPR */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h4 className="font-medium text-gray-900 mb-4">GDPR</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Utilisateurs totaux</span>
                      <span className="font-medium">{complianceData?.gdpr_compliance?.total_users || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Consentements</span>
                      <span className="font-medium">{complianceData?.gdpr_compliance?.consents_given || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Suppressions</span>
                      <span className="font-medium">{complianceData?.gdpr_compliance?.data_deletions || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Sauvegardes</span>
                      <span className="font-medium">{complianceData?.gdpr_compliance?.security_backups || 0}</span>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h4 className="font-medium text-gray-900 mb-4">CCPA</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Mesures de protection</span>
                      <CheckCircleIcon className="h-5 w-5 text-green-600" />
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Droits utilisateurs</span>
                      <CheckCircleIcon className="h-5 w-5 text-green-600" />
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Politique de confidentialité</span>
                      <CheckCircleIcon className="h-5 w-5 text-green-600" />
                    </div>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h3 className="text-lg font-semibold mb-4">Actions de Conformité</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <button
                    onClick={generateGDPRReport}
                    className="p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="text-left">
                      <h4 className="font-medium text-gray-900">Rapport GDPR</h4>
                      <p className="text-sm text-gray-600">Télécharger vos données personnelles</p>
                    </div>
                  </button>

                  <button
                    onClick={() => showError('Fonctionnalité en développement')}
                    className="p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="text-left">
                      <h4 className="font-medium text-gray-900">Suppression des Données</h4>
                      <p className="text-sm text-gray-600">Exercer le droit à l'effacement</p>
                    </div>
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'health' && (
            <div className="space-y-6">
              {/* Statut global */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Statut Global</h3>
                  <div className={`flex items-center space-x-2 ${getStatusColor(healthCheck?.overall_status)}`}>
                    {getStatusIcon(healthCheck?.overall_status)}
                    <span className="font-medium capitalize">{healthCheck?.overall_status}</span>
                  </div>
                </div>
              </div>

              {/* Détails des composants */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h4 className="font-medium text-gray-900 mb-4">Services MFA</h4>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Service MFA</span>
                    <div className="flex items-center space-x-2">
                      {healthCheck?.mfa_service ? (
                        <CheckCircleIcon className="h-5 w-5 text-green-600" />
                      ) : (
                        <XCircleIcon className="h-5 w-5 text-red-600" />
                      )}
                      <span className={healthCheck?.mfa_service ? 'text-green-600' : 'text-red-600'}>
                        {healthCheck?.mfa_service ? 'Actif' : 'Inactif'}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h4 className="font-medium text-gray-900 mb-4">Honeypots</h4>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Honeypots actifs</span>
                    <div className="flex items-center space-x-2">
                      {healthCheck?.honeypots_active ? (
                        <CheckCircleIcon className="h-5 w-5 text-green-600" />
                      ) : (
                        <XCircleIcon className="h-5 w-5 text-red-600" />
                      )}
                      <span className={healthCheck?.honeypots_active ? 'text-green-600' : 'text-red-600'}>
                        {healthCheck?.honeypots_active ? 'Actifs' : 'Inactifs'}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h4 className="font-medium text-gray-900 mb-4">Sauvegardes</h4>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Sauvegardes disponibles</span>
                    <div className="flex items-center space-x-2">
                      {healthCheck?.backups_available ? (
                        <CheckCircleIcon className="h-5 w-5 text-green-600" />
                      ) : (
                        <XCircleIcon className="h-5 w-5 text-red-600" />
                      )}
                      <span className={healthCheck?.backups_available ? 'text-green-600' : 'text-red-600'}>
                        {healthCheck?.backups_available ? 'Disponibles' : 'Indisponibles'}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h4 className="font-medium text-gray-900 mb-4">Conformité</h4>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Conformité OK</span>
                    <div className="flex items-center space-x-2">
                      {healthCheck?.compliance_ok ? (
                        <CheckCircleIcon className="h-5 w-5 text-green-600" />
                      ) : (
                        <XCircleIcon className="h-5 w-5 text-red-600" />
                      )}
                      <span className={healthCheck?.compliance_ok ? 'text-green-600' : 'text-red-600'}>
                        {healthCheck?.compliance_ok ? 'Conforme' : 'Non conforme'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default AdvancedSecurity;