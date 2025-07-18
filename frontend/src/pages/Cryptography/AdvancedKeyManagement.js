import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  KeyIcon, 
  ShieldCheckIcon, 
  ClockIcon, 
  DocumentTextIcon,
  ArrowPathIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  TrashIcon,
  ArchiveBoxIcon,
  CloudArrowUpIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import advancedCryptoService from '../../services/advancedCryptoService';

const AdvancedKeyManagement = () => {
  const [selectedKeypairs, setSelectedKeypairs] = useState([]);
  const [bulkOperation, setBulkOperation] = useState('rotate');
  const [expirationDays, setExpirationDays] = useState(365);
  const [archiveDays, setArchiveDays] = useState(30);
  const [activeTab, setActiveTab] = useState('dashboard');
  const queryClient = useQueryClient();

  // Récupérer le dashboard cryptographique
  const { data: dashboard, isLoading: dashboardLoading } = useQuery(
    'cryptoDashboard',
    advancedCryptoService.getAdvancedCryptoDashboard,
    {
      refetchInterval: 30000 // Rafraîchir toutes les 30 secondes
    }
  );

  // Récupérer les vérifications d'expiration
  const { data: expirationCheck, isLoading: expirationLoading } = useQuery(
    'keyExpiration',
    advancedCryptoService.checkKeyExpiration,
    {
      refetchInterval: 60000 // Rafraîchir toutes les minutes
    }
  );

  // Récupérer le trail d'audit
  const { data: auditTrail, isLoading: auditLoading } = useQuery(
    'auditTrail',
    () => advancedCryptoService.getAuditTrail(100)
  );

  // Récupérer le check de santé
  const { data: healthCheck } = useQuery(
    'cryptoHealthCheck',
    advancedCryptoService.getCryptoHealthCheck,
    {
      refetchInterval: 60000
    }
  );

  // Mutations
  const setupKeyManagementMutation = useMutation(
    ({ keypairId, expirationDays, archiveDays }) => 
      advancedCryptoService.setupAdvancedKeyManagement(keypairId, expirationDays, archiveDays),
    {
      onSuccess: () => {
        toast.success('Gestion avancée des clés configurée avec succès !');
        queryClient.invalidateQueries('cryptoDashboard');
      },
      onError: (error) => {
        toast.error(`Erreur: ${error.response?.data?.detail || error.message}`);
      }
    }
  );

  const bulkOperationMutation = useMutation(
    ({ operation, keypairIds }) => 
      advancedCryptoService.bulkKeyOperations(operation, keypairIds),
    {
      onSuccess: (data) => {
        const { success_count, failure_count } = data.results;
        toast.success(`Opération terminée: ${success_count} réussies, ${failure_count} échouées`);
        queryClient.invalidateQueries('cryptoDashboard');
        setSelectedKeypairs([]);
      },
      onError: (error) => {
        toast.error(`Erreur: ${error.response?.data?.detail || error.message}`);
      }
    }
  );

  const handleSetupKeyManagement = (keypairId) => {
    setupKeyManagementMutation.mutate({
      keypairId,
      expirationDays,
      archiveDays
    });
  };

  const handleBulkOperation = () => {
    if (selectedKeypairs.length === 0) {
      toast.error('Veuillez sélectionner au moins une paire de clés');
      return;
    }
    
    bulkOperationMutation.mutate({
      operation: bulkOperation,
      keypairIds: selectedKeypairs
    });
  };

  const toggleKeypairSelection = (keypairId) => {
    setSelectedKeypairs(prev => 
      prev.includes(keypairId) 
        ? prev.filter(id => id !== keypairId)
        : [...prev, keypairId]
    );
  };

  const selectAllKeypairs = () => {
    if (expirationCheck?.expiration_check?.expiring_keys) {
      setSelectedKeypairs(expirationCheck.expiration_check.expiring_keys.map(k => k.keypair_id));
    }
  };

  const clearSelection = () => {
    setSelectedKeypairs([]);
  };

  const getStatusColor = (status) => {
    const colors = {
      expired: 'text-red-600 bg-red-100',
      expiring_soon: 'text-orange-600 bg-orange-100',
      warning: 'text-yellow-600 bg-yellow-100',
      healthy: 'text-green-600 bg-green-100'
    };
    return colors[status] || 'text-gray-600 bg-gray-100';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('fr-FR');
  };

  const tabs = [
    { id: 'dashboard', name: 'Tableau de Bord', icon: ChartBarIcon },
    { id: 'expiration', name: 'Expiration des Clés', icon: ClockIcon },
    { id: 'bulk', name: 'Opérations en Masse', icon: ArrowPathIcon },
    { id: 'audit', name: 'Trail d\'Audit', icon: DocumentTextIcon },
    { id: 'health', name: 'Santé Système', icon: ShieldCheckIcon }
  ];

  if (dashboardLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Gestion Avancée des Clés Cryptographiques
        </h1>
        <p className="text-gray-600">
          Gérez le cycle de vie de vos clés post-quantiques avec des fonctionnalités avancées
        </p>
      </div>

      {/* Alertes d'expiration */}
      {expirationCheck?.expiration_check?.critical_count > 0 && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-400 mr-2" />
            <span className="text-red-800 font-medium">
              Attention: {expirationCheck.expiration_check.critical_count} clés expirées !
            </span>
          </div>
        </div>
      )}

      {/* Navigation par onglets */}
      <div className="mb-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center`}
              >
                <tab.icon className="h-5 w-5 mr-2" />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Tableau de bord */}
      {activeTab === 'dashboard' && dashboard && (
        <div className="space-y-6">
          {/* Statistiques générales */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center">
                <KeyIcon className="h-8 w-8 text-blue-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Paires de clés</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {dashboard.dashboard.statistics.keypairs_count}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center">
                <ShieldCheckIcon className="h-8 w-8 text-green-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Preuves ZK</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {dashboard.dashboard.statistics.zk_proofs_count}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center">
                <DocumentTextIcon className="h-8 w-8 text-purple-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Schémas Seuil</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {dashboard.dashboard.statistics.threshold_schemes_count}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center">
                <ArrowPathIcon className="h-8 w-8 text-orange-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Rotations</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {dashboard.dashboard.statistics.key_rotations_count || 0}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Utilisation des algorithmes */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-medium mb-4">Utilisation des Algorithmes</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {dashboard.dashboard.algorithm_usage.map((usage, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium">{usage._id}</span>
                  <span className="text-sm text-gray-600">{usage.count} clés</span>
                </div>
              ))}
            </div>
          </div>

          {/* Activité récente */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-medium mb-4">Activité Récente</h3>
            <div className="space-y-3">
              {dashboard.dashboard.recent_activity.slice(0, 5).map((activity, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                    <span className="text-sm font-medium">{activity.event_type}</span>
                  </div>
                  <span className="text-sm text-gray-600">
                    {formatDate(activity.timestamp)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Expiration des clés */}
      {activeTab === 'expiration' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium">Clés Arrivant à Expiration</h3>
              <div className="flex space-x-2">
                <button
                  onClick={selectAllKeypairs}
                  className="text-sm bg-blue-100 text-blue-700 px-3 py-1 rounded-lg hover:bg-blue-200"
                >
                  Sélectionner tout
                </button>
                <button
                  onClick={clearSelection}
                  className="text-sm bg-gray-100 text-gray-700 px-3 py-1 rounded-lg hover:bg-gray-200"
                >
                  Effacer
                </button>
              </div>
            </div>

            {expirationLoading ? (
              <div className="flex items-center justify-center h-32">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              </div>
            ) : expirationCheck?.expiration_check?.expiring_keys?.length > 0 ? (
              <div className="space-y-3">
                {expirationCheck.expiration_check.expiring_keys.map((key, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        checked={selectedKeypairs.includes(key.keypair_id)}
                        onChange={() => toggleKeypairSelection(key.keypair_id)}
                        className="mr-3"
                      />
                      <div>
                        <p className="font-medium text-sm">{key.keypair_id}</p>
                        <p className="text-xs text-gray-500">
                          Expire le {formatDate(key.expiration_date)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 text-xs rounded ${getStatusColor(key.status)}`}>
                        {key.status === 'expired' ? 'Expirée' : 
                         key.status === 'expiring_soon' ? 'Expire bientôt' : 'Attention'}
                      </span>
                      <span className="text-sm text-gray-600">
                        {key.days_until_expiry} jours
                      </span>
                      <button
                        onClick={() => handleSetupKeyManagement(key.keypair_id)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        <ArrowPathIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">Aucune clé arrivant à expiration</p>
            )}
          </div>

          {/* Configuration de gestion */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-medium mb-4">Configuration de Gestion</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Expiration (jours)
                </label>
                <input
                  type="number"
                  value={expirationDays}
                  onChange={(e) => setExpirationDays(Number(e.target.value))}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Archivage après expiration (jours)
                </label>
                <input
                  type="number"
                  value={archiveDays}
                  onChange={(e) => setArchiveDays(Number(e.target.value))}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Opérations en masse */}
      {activeTab === 'bulk' && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-medium mb-4">Opérations en Masse</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium">Clés sélectionnées</p>
                <p className="text-sm text-gray-600">{selectedKeypairs.length} clés</p>
              </div>
              <select
                value={bulkOperation}
                onChange={(e) => setBulkOperation(e.target.value)}
                className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value="rotate">Rotation</option>
                <option value="archive">Archivage</option>
                <option value="backup">Sauvegarde</option>
                <option value="expire">Expiration</option>
              </select>
            </div>

            <div className="flex space-x-4">
              <button
                onClick={handleBulkOperation}
                disabled={bulkOperationMutation.isLoading || selectedKeypairs.length === 0}
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {bulkOperationMutation.isLoading ? 'Traitement...' : `Effectuer ${bulkOperation}`}
              </button>
            </div>

            {/* Icônes d'opération */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              {[
                { op: 'rotate', icon: ArrowPathIcon, label: 'Rotation', color: 'text-blue-600' },
                { op: 'archive', icon: ArchiveBoxIcon, label: 'Archivage', color: 'text-purple-600' },
                { op: 'backup', icon: CloudArrowUpIcon, label: 'Sauvegarde', color: 'text-green-600' },
                { op: 'expire', icon: TrashIcon, label: 'Expiration', color: 'text-red-600' }
              ].map((item) => (
                <button
                  key={item.op}
                  onClick={() => setBulkOperation(item.op)}
                  className={`flex flex-col items-center p-4 rounded-lg border-2 transition-colors ${
                    bulkOperation === item.op 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <item.icon className={`h-8 w-8 ${item.color} mb-2`} />
                  <span className="text-sm font-medium">{item.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Trail d'audit */}
      {activeTab === 'audit' && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-medium mb-4">Trail d'Audit</h3>
          {auditLoading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
          ) : auditTrail?.audit_trail?.length > 0 ? (
            <div className="space-y-3">
              {auditTrail.audit_trail.map((event, index) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                    <div>
                      <p className="font-medium text-sm">{event.event_type}</p>
                      <p className="text-xs text-gray-500">
                        {formatDate(event.timestamp)}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">{event.user_id}</p>
                    <p className="text-xs text-gray-500">
                      {event.metadata?.action || 'Action'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">Aucun événement d'audit</p>
          )}
        </div>
      )}

      {/* Santé système */}
      {activeTab === 'health' && healthCheck && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h3 className="text-lg font-medium mb-4">État de Santé du Système</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium">Service prêt</span>
                  {healthCheck.health_status.service_ready ? (
                    <CheckCircleIcon className="h-5 w-5 text-green-500" />
                  ) : (
                    <XCircleIcon className="h-5 w-5 text-red-500" />
                  )}
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium">Algorithmes supportés</span>
                  <span className="text-sm text-gray-600">
                    {healthCheck.health_status.supported_algorithms}
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium">Mode fallback</span>
                  {healthCheck.health_status.fallback_mode ? (
                    <span className="text-sm text-orange-600">Activé</span>
                  ) : (
                    <span className="text-sm text-green-600">Désactivé</span>
                  )}
                </div>
              </div>
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-gray-700">Algorithmes Post-Quantiques</h4>
                {Object.entries(healthCheck.health_status.pq_algorithms_available).map(([alg, available]) => (
                  <div key={alg} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <span className="text-sm font-medium capitalize">{alg}</span>
                    {available ? (
                      <CheckCircleIcon className="h-5 w-5 text-green-500" />
                    ) : (
                      <XCircleIcon className="h-5 w-5 text-red-500" />
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdvancedKeyManagement;