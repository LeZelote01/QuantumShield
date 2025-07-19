import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import api from '../../services/api';

const APIGateway = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [apiKeys, setApiKeys] = useState([]);
  const [gatewayHealth, setGatewayHealth] = useState(null);
  const [usageStats, setUsageStats] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [createKeyForm, setCreateKeyForm] = useState({
    tier: 'free',
    description: ''
  });

  // Récupérer les données du dashboard
  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      
      // Santé de l'API Gateway
      const healthResponse = await api.get('/api/api-gateway/health');
      setGatewayHealth(healthResponse.data.health);
      
      // Mes clés API
      const keysResponse = await api.get('/api/api-gateway/api-keys/my-keys');
      setApiKeys(keysResponse.data.data.api_keys || []);
      
      // Statistiques d'utilisation
      const statsResponse = await api.get('/api/api-gateway/analytics/usage-stats');
      setUsageStats(statsResponse.data.data.stats || {});
      
    } catch (error) {
      console.error('Erreur chargement dashboard:', error);
      toast.error('Erreur lors du chargement des données');
    } finally {
      setIsLoading(false);
    }
  };

  // Créer une nouvelle clé API
  const createApiKey = async () => {
    try {
      const response = await api.post('/api/api-gateway/api-keys/create', createKeyForm);
      const newKey = response.data.data;
      
      toast.success('Clé API créée avec succès !');
      
      // Afficher la clé et le secret (une seule fois)
      const keyInfo = `
Clé API: ${newKey.api_key}
Secret: ${newKey.api_secret}

⚠️ Notez bien ces informations, elles ne seront plus affichées !
      `;
      
      // Copier dans le presse-papier
      if (navigator.clipboard) {
        await navigator.clipboard.writeText(`API Key: ${newKey.api_key}\nAPI Secret: ${newKey.api_secret}`);
        toast.success('Informations copiées dans le presse-papier');
      }
      
      alert(keyInfo);
      
      // Réinitialiser le formulaire et recharger
      setCreateKeyForm({ tier: 'free', description: '' });
      fetchDashboardData();
      
    } catch (error) {
      console.error('Erreur création clé API:', error);
      toast.error('Erreur lors de la création de la clé API');
    }
  };

  // Révoquer une clé API
  const revokeApiKey = async (apiKey) => {
    if (!window.confirm('Êtes-vous sûr de vouloir révoquer cette clé API ?')) {
      return;
    }
    
    try {
      await api.post('/api/api-gateway/api-keys/revoke', { api_key: apiKey });
      toast.success('Clé API révoquée');
      fetchDashboardData();
    } catch (error) {
      console.error('Erreur révocation clé:', error);
      toast.error('Erreur lors de la révocation');
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const renderDashboard = () => (
    <div className="space-y-6">
      {/* Santé de l'API Gateway */}
      {gatewayHealth && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">État de l'API Gateway</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-green-800 font-semibold">Statut</div>
              <div className={`text-2xl font-bold ${gatewayHealth.status === 'healthy' ? 'text-green-600' : 'text-red-600'}`}>
                {gatewayHealth.status === 'healthy' ? '✅ En ligne' : '❌ Hors ligne'}
              </div>
            </div>
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-blue-800 font-semibold">Requêtes (5min)</div>
              <div className="text-2xl font-bold text-blue-600">{gatewayHealth.recent_requests_5min}</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-purple-800 font-semibold">Clés API actives</div>
              <div className="text-2xl font-bold text-purple-600">{gatewayHealth.active_api_keys}</div>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-orange-800 font-semibold">IPs bloquées</div>
              <div className="text-2xl font-bold text-orange-600">{gatewayHealth.blocked_ips}</div>
            </div>
          </div>
        </div>
      )}

      {/* Statistiques d'utilisation */}
      {usageStats && usageStats.overview && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Statistiques d'utilisation</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">{usageStats.overview.total_requests}</div>
              <div className="text-gray-600">Requêtes totales</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">{usageStats.overview.successful_requests}</div>
              <div className="text-gray-600">Succès</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-red-600">{usageStats.overview.failed_requests}</div>
              <div className="text-gray-600">Échecs</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600">{usageStats.overview.rate_limited_requests}</div>
              <div className="text-gray-600">Rate limited</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderApiKeys = () => (
    <div className="space-y-6">
      {/* Formulaire de création */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Créer une nouvelle clé API</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Tier</label>
            <select
              value={createKeyForm.tier}
              onChange={(e) => setCreateKeyForm({ ...createKeyForm, tier: e.target.value })}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="free">Gratuit (10 req/min)</option>
              <option value="basic">Basique (50 req/min)</option>
              <option value="pro">Pro (200 req/min)</option>
              <option value="enterprise">Entreprise (1000 req/min)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <input
              type="text"
              value={createKeyForm.description}
              onChange={(e) => setCreateKeyForm({ ...createKeyForm, description: e.target.value })}
              placeholder="Description de la clé API"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={createApiKey}
              className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
            >
              Créer la clé
            </button>
          </div>
        </div>
      </div>

      {/* Liste des clés API */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Mes clés API</h3>
        {apiKeys.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            Aucune clé API créée
          </div>
        ) : (
          <div className="space-y-4">
            {apiKeys.map((key) => (
              <div key={key.api_key} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="font-mono text-sm bg-gray-100 p-2 rounded">
                      {key.api_key}
                    </div>
                    <div className="mt-2 text-sm text-gray-600">
                      <div>Tier: <span className="font-semibold">{key.tier}</span></div>
                      <div>Description: {key.description || 'Aucune'}</div>
                      <div>Créée: {new Date(key.created_at).toLocaleDateString()}</div>
                      <div>Dernière utilisation: {key.last_used ? new Date(key.last_used).toLocaleDateString() : 'Jamais'}</div>
                    </div>
                    {key.usage_stats && (
                      <div className="mt-2 flex space-x-4 text-xs">
                        <span className="text-blue-600">Total: {key.usage_stats.total_requests || 0}</span>
                        <span className="text-green-600">Succès: {key.usage_stats.successful_requests || 0}</span>
                        <span className="text-red-600">Échecs: {key.usage_stats.failed_requests || 0}</span>
                      </div>
                    )}
                  </div>
                  <div className="ml-4">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      key.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {key.is_active ? 'Active' : 'Inactive'}
                    </span>
                    {key.is_active && (
                      <button
                        onClick={() => revokeApiKey(key.api_key)}
                        className="ml-2 bg-red-600 text-white px-3 py-1 text-xs rounded hover:bg-red-700"
                      >
                        Révoquer
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  const renderConfiguration = () => (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Configuration Rate Limiting</h3>
      <div className="space-y-6">
        {/* Limites par tier */}
        <div>
          <h4 className="text-lg font-semibold mb-3">Limites par tier</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {['free', 'basic', 'pro', 'enterprise'].map((tier) => (
              <div key={tier} className="border border-gray-200 rounded-lg p-4">
                <h5 className="font-semibold capitalize mb-2">{tier}</h5>
                <div className="text-sm space-y-1">
                  <div>Par minute: {tier === 'free' ? '10' : tier === 'basic' ? '50' : tier === 'pro' ? '200' : '1000'}</div>
                  <div>Par heure: {tier === 'free' ? '100' : tier === 'basic' ? '1k' : tier === 'pro' ? '5k' : '50k'}</div>
                  <div>Par jour: {tier === 'free' ? '1k' : tier === 'basic' ? '10k' : tier === 'pro' ? '50k' : '500k'}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Endpoints sensibles */}
        <div>
          <h4 className="text-lg font-semibold mb-3">Endpoints sensibles</h4>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <strong>/api/auth/login:</strong> 5 req/min
              </div>
              <div>
                <strong>/api/auth/register:</strong> 3 req/min
              </div>
              <div>
                <strong>/api/crypto/generate-keys:</strong> 20 req/min
              </div>
              <div>
                <strong>/api/mining/submit:</strong> 100 req/min
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800">API Gateway</h1>
          <p className="text-gray-600 mt-2">
            Gestion des clés API, rate limiting et monitoring
          </p>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-lg p-1 mb-6">
          <div className="flex space-x-1">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: '📊' },
              { id: 'api-keys', label: 'Clés API', icon: '🔑' },
              { id: 'config', label: 'Configuration', icon: '⚙️' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-6 py-3 rounded-lg transition ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {isLoading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <>
              {activeTab === 'dashboard' && renderDashboard()}
              {activeTab === 'api-keys' && renderApiKeys()}
              {activeTab === 'config' && renderConfiguration()}
            </>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default APIGateway;