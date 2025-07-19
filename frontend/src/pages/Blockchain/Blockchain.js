import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { 
  CubeIcon, 
  DocumentTextIcon, 
  ShieldCheckIcon,
  ClockIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import blockchainService from '../../services/blockchainService';
import Card from '../../components/UI/Card';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const Blockchain = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('explorer');

  // Queries
  const { data: blockchainStats, isLoading } = useQuery(
    'blockchainStats',
    blockchainService.getBlockchainStats,
    { refetchInterval: 30000 }
  );

  const { data: recentBlocks } = useQuery(
    'recentBlocks',
    () => blockchainService.getRecentBlocks(10),
    { refetchInterval: 30000 }
  );

  const { data: recentTransactions } = useQuery(
    'recentTransactions',
    () => blockchainService.getRecentTransactions(20),
    { refetchInterval: 30000 }
  );

  const { data: explorer } = useQuery(
    'blockchainExplorer',
    blockchainService.getBlockchainExplorer,
    { refetchInterval: 30000 }
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  const tabs = [
    { id: 'explorer', label: 'Explorateur' },
    { id: 'blocks', label: 'Blocs' },
    { id: 'transactions', label: 'Transactions' },
    { id: 'stats', label: 'Statistiques' },
  ];

  const getTransactionTypeColor = (type) => {
    switch (type) {
      case 'reward':
        return 'bg-green-100 text-green-800';
      case 'firmware_update':
        return 'bg-blue-100 text-blue-800';
      case 'device_registration':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Blockchain QuantumShield</h1>
          <p className="text-gray-600">
            Blockchain privée pour la confiance matérielle et l'intégrité des données
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-600">Réseau actif</span>
          </div>
        </div>
      </div>

      {/* Statistiques principales */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <CubeIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Blocs totaux</p>
              <p className="text-2xl font-bold text-gray-900">
                {blockchainStats?.total_blocks?.toLocaleString() || 0}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <DocumentTextIcon className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Transactions</p>
              <p className="text-2xl font-bold text-gray-900">
                {blockchainStats?.total_transactions?.toLocaleString() || 0}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <ClockIcon className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">En attente</p>
              <p className="text-2xl font-bold text-gray-900">
                {blockchainStats?.pending_transactions || 0}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-lg">
              <ShieldCheckIcon className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Difficulté</p>
              <p className="text-2xl font-bold text-gray-900">
                {blockchainStats?.current_difficulty || 0}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Barre de recherche */}
      <Card>
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <Input
              placeholder="Rechercher par hash de bloc, transaction ou adresse..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <Button>Rechercher</Button>
        </div>
      </Card>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm
                ${activeTab === tab.id 
                  ? 'border-indigo-500 text-indigo-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Contenu des tabs */}
      <div>
        {activeTab === 'explorer' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Derniers blocs */}
            <Card title="Derniers blocs">
              <div className="space-y-3">
                {recentBlocks?.slice(0, 5).map((block) => (
                  <div key={block.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-blue-100 rounded-lg">
                        <CubeIcon className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          Bloc #{block.block_number}
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(block.timestamp).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">
                        {block.transactions?.length || 0} tx
                      </p>
                      <p className="text-xs text-gray-500">
                        {block.hash.slice(0, 10)}...
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Dernières transactions */}
            <Card title="Dernières transactions">
              <div className="space-y-3">
                {recentTransactions?.slice(0, 5).map((tx) => (
                  <div key={tx.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-green-100 rounded-lg">
                        <DocumentTextIcon className="h-5 w-5 text-green-600" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {tx.hash.slice(0, 16)}...
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(tx.timestamp).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`
                        px-2 py-1 rounded-full text-xs font-medium
                        ${getTransactionTypeColor(tx.transaction_type)}
                      `}>
                        {tx.transaction_type}
                      </span>
                      <p className="text-xs text-gray-500 mt-1">
                        {tx.amount} QS
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'blocks' && (
          <Card title="Blocs récents">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Numéro
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Hash
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Transactions
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Mineur
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Timestamp
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {recentBlocks?.map((block) => (
                    <tr key={block.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          #{block.block_number}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900 font-mono">
                          {block.hash.slice(0, 16)}...
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {block.transactions?.length || 0}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900 font-mono">
                          {block.miner_address.slice(0, 10)}...
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {new Date(block.timestamp).toLocaleString()}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Button size="small" variant="outline">
                          <EyeIcon className="h-4 w-4" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {activeTab === 'transactions' && (
          <Card title="Transactions récentes">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Hash
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      De
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Vers
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Montant
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Timestamp
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {recentTransactions?.map((tx) => (
                    <tr key={tx.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900 font-mono">
                          {tx.hash.slice(0, 16)}...
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`
                          px-2 py-1 rounded-full text-xs font-medium
                          ${getTransactionTypeColor(tx.transaction_type)}
                        `}>
                          {tx.transaction_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900 font-mono">
                          {tx.from_address.slice(0, 10)}...
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900 font-mono">
                          {tx.to_address.slice(0, 10)}...
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {tx.amount} QS
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {new Date(tx.timestamp).toLocaleString()}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {activeTab === 'stats' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card title="Statistiques réseau">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Type de réseau</span>
                  <span className="text-sm font-medium">Blockchain privée</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Consensus</span>
                  <span className="text-sm font-medium">Proof of Work</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Temps de bloc moyen</span>
                  <span className="text-sm font-medium">5 minutes</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Statut réseau</span>
                  <span className="text-sm font-medium text-green-600">Actif</span>
                </div>
              </div>
            </Card>

            <Card title="Intégrité de la chaîne">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Validation</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-sm font-medium text-green-600">Valide</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Dernière vérification</span>
                  <span className="text-sm font-medium">
                    {new Date(blockchainStats?.last_block_time).toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Hash du dernier bloc</span>
                  <span className="text-sm font-medium font-mono">
                    {explorer?.recent_blocks?.[0]?.hash.slice(0, 10)}...
                  </span>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default Blockchain;