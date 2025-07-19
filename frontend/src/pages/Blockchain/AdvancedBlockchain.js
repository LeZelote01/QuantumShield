import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  ServerStackIcon, 
  CubeIcon, 
  ChartBarIcon, 
  GlobeAltIcon,
  ShieldCheckIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  FireIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../contexts/ToastContext';
import api from '../../services/api';

const AdvancedBlockchain = () => {
  const { user } = useAuth();
  const { showSuccess, showError } = useToast();
  
  const [overview, setOverview] = useState(null);
  const [smartContracts, setSmartContracts] = useState([]);
  const [proposals, setProposals] = useState([]);
  const [validators, setValidators] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [overviewRes, contractsRes, proposalsRes, validatorsRes, metricsRes, healthRes] = await Promise.all([
        api.get('/api/advanced-blockchain/overview'),
        api.get('/api/advanced-blockchain/smart-contracts?limit=10'),
        api.get('/api/advanced-blockchain/governance/proposals?limit=10'),
        api.get('/api/advanced-blockchain/consensus/validators'),
        api.get('/api/advanced-blockchain/metrics'),
        api.get('/api/advanced-blockchain/health')
      ]);

      setOverview(overviewRes.data);
      setSmartContracts(contractsRes.data);
      setProposals(proposalsRes.data);
      setValidators(validatorsRes.data);
      setMetrics(metricsRes.data);
      setHealth(healthRes.data);
    } catch (error) {
      showError('Erreur lors du chargement des données');
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCompressBlocks = async () => {
    try {
      await api.post('/api/advanced-blockchain/management/compress-blocks');
      showSuccess('Compression des blocs lancée en arrière-plan');
    } catch (error) {
      showError('Erreur lors de la compression');
    }
  };

  const handleArchiveBlocks = async () => {
    try {
      await api.post('/api/advanced-blockchain/management/archive-blocks');
      showSuccess('Archivage des blocs lancé en arrière-plan');
    } catch (error) {
      showError('Erreur lors de l\'archivage');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', name: 'Vue d\'ensemble', icon: ChartBarIcon },
    { id: 'contracts', name: 'Smart Contracts', icon: CubeIcon },
    { id: 'governance', name: 'Gouvernance', icon: ShieldCheckIcon },
    { id: 'consensus', name: 'Consensus', icon: ServerStackIcon },
    { id: 'interop', name: 'Interopérabilité', icon: GlobeAltIcon },
  ];

  const renderOverview = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {/* Métriques de santé */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg shadow-lg p-6"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Santé du Réseau</h3>
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            health?.overall_score > 0.8 ? 'bg-green-100 text-green-800' :
            health?.overall_score > 0.6 ? 'bg-yellow-100 text-yellow-800' :
            'bg-red-100 text-red-800'
          }`}>
            {health?.overall_score ? (health.overall_score * 100).toFixed(1) : 0}%
          </div>
        </div>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Consensus</span>
            <span className="text-sm font-medium">{(health?.consensus_health * 100).toFixed(1)}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Validators</span>
            <span className="text-sm font-medium">{(health?.validator_participation * 100).toFixed(1)}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Transactions</span>
            <span className="text-sm font-medium">{(health?.transaction_success_rate * 100).toFixed(1)}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Uptime</span>
            <span className="text-sm font-medium">{(health?.network_uptime * 100).toFixed(1)}%</span>
          </div>
        </div>
      </motion.div>

      {/* Fonctionnalités avancées */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-lg shadow-lg p-6"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Fonctionnalités Avancées</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{overview?.advanced_features?.smart_contracts}</div>
            <div className="text-sm text-gray-600">Smart Contracts</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{overview?.advanced_features?.active_proposals}</div>
            <div className="text-sm text-gray-600">Propositions Actives</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{overview?.advanced_features?.active_validators}</div>
            <div className="text-sm text-gray-600">Validators</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">{overview?.advanced_features?.cross_chain_bridges}</div>
            <div className="text-sm text-gray-600">Ponts Cross-Chain</div>
          </div>
        </div>
      </motion.div>

      {/* Métriques de performance */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white rounded-lg shadow-lg p-6"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance</h3>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Hash Rate</span>
            <span className="text-sm font-medium">{(metrics?.network_hash_rate / 1000000).toFixed(1)} MH/s</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Temps de Bloc</span>
            <span className="text-sm font-medium">{metrics?.average_block_time.toFixed(1)}s</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">TPS</span>
            <span className="text-sm font-medium">{metrics?.transaction_throughput.toFixed(2)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Décentralisation</span>
            <span className="text-sm font-medium">{(metrics?.network_decentralization_index * 100).toFixed(1)}%</span>
          </div>
        </div>
      </motion.div>

      {/* Gestion des données */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-white rounded-lg shadow-lg p-6 md:col-span-2 lg:col-span-3"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Gestion des Données</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Compression des Blocs</span>
              <ArrowPathIcon className="h-5 w-5 text-blue-600" />
            </div>
            <p className="text-sm text-gray-600 mb-3">
              Compresse automatiquement les anciens blocs pour économiser l'espace
            </p>
            <button
              onClick={handleCompressBlocks}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Lancer la Compression
            </button>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Archivage des Blocs</span>
              <ServerStackIcon className="h-5 w-5 text-green-600" />
            </div>
            <p className="text-sm text-gray-600 mb-3">
              Archive les anciens blocs compressés pour un stockage à long terme
            </p>
            <button
              onClick={handleArchiveBlocks}
              className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors"
            >
              Lancer l'Archivage
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );

  const renderSmartContracts = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">Smart Contracts</h3>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
          Déployer un Contrat
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {smartContracts.map((contract) => (
          <motion.div
            key={contract.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-lg shadow-lg p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-semibold text-gray-900">{contract.name}</h4>
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                contract.status === 'deployed' ? 'bg-green-100 text-green-800' :
                contract.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {contract.status}
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-3">{contract.description}</p>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Adresse:</span>
                <span className="font-mono text-xs">{contract.contract_address?.substring(0, 20)}...</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Version:</span>
                <span>{contract.version}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Gas utilisé:</span>
                <span>{contract.gas_used?.toLocaleString()}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );

  const renderGovernance = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">Gouvernance Décentralisée</h3>
        <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors">
          Créer une Proposition
        </button>
      </div>
      
      <div className="space-y-4">
        {proposals.map((proposal) => (
          <motion.div
            key={proposal.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-lg shadow-lg p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-semibold text-gray-900">{proposal.title}</h4>
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                proposal.status === 'active' ? 'bg-blue-100 text-blue-800' :
                proposal.status === 'passed' ? 'bg-green-100 text-green-800' :
                proposal.status === 'rejected' ? 'bg-red-100 text-red-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {proposal.status}
              </div>
            </div>
            <p className="text-gray-600 mb-4">{proposal.description}</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="text-center">
                <div className="text-sm text-gray-500">Type</div>
                <div className="font-medium">{proposal.proposal_type}</div>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-500">Proposé par</div>
                <div className="font-mono text-xs">{proposal.proposer_address?.substring(0, 20)}...</div>
              </div>
              <div className="text-center">
                <div className="text-sm text-gray-500">Fin du vote</div>
                <div className="font-medium">{new Date(proposal.voting_end).toLocaleDateString()}</div>
              </div>
            </div>
            {proposal.status === 'active' && (
              <div className="flex space-x-2">
                <button className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors">
                  Voter Pour
                </button>
                <button className="flex-1 bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition-colors">
                  Voter Contre
                </button>
                <button className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 transition-colors">
                  S'abstenir
                </button>
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );

  const renderConsensus = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">Consensus Hybride (PoW + PoS)</h3>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">Type:</span>
          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm font-medium">
            {overview?.advanced_features?.consensus_type}
          </span>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Validators Actifs</h4>
          <div className="space-y-3">
            {validators.slice(0, 5).map((validator) => (
              <div key={validator.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-mono text-sm">{validator.address.substring(0, 20)}...</div>
                  <div className="text-xs text-gray-500">
                    Réputation: {validator.reputation_score.toFixed(2)}
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-medium">{validator.stake_amount.toLocaleString()} QS</div>
                  <div className="text-xs text-gray-500">
                    {validator.blocks_validated} blocs validés
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Staking</h4>
          <div className="space-y-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-blue-900">Total Stake</span>
                <span className="text-lg font-bold text-blue-600">{metrics?.total_stake.toLocaleString()} QS</span>
              </div>
              <div className="text-sm text-blue-700">
                {validators.length} validators actifs
              </div>
            </div>
            <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
              Staker des Tokens
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderInteroperability = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-900">Interopérabilité Cross-Chain</h3>
        <button className="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors">
          Nouveau Transfert
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-semibold text-gray-900">Ethereum Bridge</h4>
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Réseau cible:</span>
              <span>Polygon</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Frais:</span>
              <span>0.1%</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Limite quotidienne:</span>
              <span>1M QS</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Tokens supportés:</span>
              <span>QS, ETH, USDT</span>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-semibold text-gray-900">BSC Bridge</h4>
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Réseau cible:</span>
              <span>Avalanche</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Frais:</span>
              <span>0.15%</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Limite quotidienne:</span>
              <span>500K QS</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Tokens supportés:</span>
              <span>QS, BNB, USDC</span>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Transferts Récents</h4>
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <div className="flex-1">
                <div className="text-sm font-medium">500 QS → Polygon</div>
                <div className="text-xs text-gray-500">Confirmé</div>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
              <div className="flex-1">
                <div className="text-sm font-medium">1000 QS → Avalanche</div>
                <div className="text-xs text-gray-500">En cours</div>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <div className="flex-1">
                <div className="text-sm font-medium">250 QS → Polygon</div>
                <div className="text-xs text-gray-500">Confirmé</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverview();
      case 'contracts':
        return renderSmartContracts();
      case 'governance':
        return renderGovernance();
      case 'consensus':
        return renderConsensus();
      case 'interop':
        return renderInteroperability();
      default:
        return renderOverview();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Blockchain Améliorée</h1>
              <p className="mt-1 text-sm text-gray-600">
                Smart contracts, consensus hybride, gouvernance décentralisée et interopérabilité
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <FireIcon className="h-5 w-5 text-orange-500" />
                <span className="text-sm text-gray-600">
                  Consommation: {metrics?.energy_consumption?.toFixed(2)} kWh
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircleIcon className="h-5 w-5 text-green-500" />
                <span className="text-sm text-gray-600">
                  Réseau opérationnel
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation par onglets */}
        <div className="mb-8">
          <nav className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-5 w-5" />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Contenu des onglets */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {renderTabContent()}
        </motion.div>
      </div>
    </div>
  );
};

export default AdvancedBlockchain;