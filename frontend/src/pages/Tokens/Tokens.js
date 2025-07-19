import React, { useState } from 'react';
import { useQuery, useMutation } from 'react-query';
import { 
  CurrencyDollarIcon, 
  TrophyIcon, 
  ArrowUpIcon,
  ArrowDownIcon,
  GiftIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import tokenService from '../../services/tokenService';
import { useToast } from '../../contexts/ToastContext';
import Card from '../../components/UI/Card';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import Modal from '../../components/UI/Modal';

const Tokens = () => {
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [transferData, setTransferData] = useState({ to_user: '', amount: '', description: '' });
  const { showSuccess, showError } = useToast();

  // Queries
  const { data: portfolio, isLoading } = useQuery('tokenPortfolio', tokenService.getPortfolio);
  const { data: balance } = useQuery('tokenBalance', tokenService.getBalance);
  const { data: transactions } = useQuery('tokenTransactions', tokenService.getTransactions);
  const { data: rewards } = useQuery('tokenRewards', tokenService.getRewards);
  const { data: leaderboard } = useQuery('tokenLeaderboard', tokenService.getLeaderboard);
  const { data: marketInfo } = useQuery('tokenMarketInfo', tokenService.getMarketInfo);

  // Mutations
  const transferMutation = useMutation(tokenService.transferTokens, {
    onSuccess: () => {
      showSuccess('Transfert effectué avec succès !');
      setShowTransferModal(false);
      setTransferData({ to_user: '', amount: '', description: '' });
    },
    onError: () => showError('Erreur lors du transfert')
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tokens $QS</h1>
          <p className="text-gray-600">
            Gérez vos tokens QuantumShield et participez à l'écosystème
          </p>
        </div>
        <Button onClick={() => setShowTransferModal(true)}>
          Transférer des tokens
        </Button>
      </div>

      {/* Portfolio principal */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Solde principal */}
        <Card className="lg:col-span-2">
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-6 rounded-lg text-white">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-indigo-100">Solde total</p>
                <p className="text-3xl font-bold">
                  {balance?.balance?.toLocaleString() || 0} QS
                </p>
                <p className="text-indigo-200 text-sm">
                  ≈ ${(balance?.balance * 0.1 || 0).toLocaleString()} USD
                </p>
              </div>
              <CurrencyDollarIcon className="h-12 w-12 text-indigo-200" />
            </div>
            
            <div className="grid grid-cols-2 gap-4 mt-6">
              <div className="bg-white bg-opacity-20 p-3 rounded">
                <p className="text-indigo-100 text-sm">Devices actifs</p>
                <p className="text-xl font-bold">{portfolio?.active_devices || 0}</p>
              </div>
              <div className="bg-white bg-opacity-20 p-3 rounded">
                <p className="text-indigo-100 text-sm">Récompenses totales</p>
                <p className="text-xl font-bold">{portfolio?.total_rewards_earned?.toFixed(1) || 0}</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Score de réputation */}
        <Card title="Score de réputation">
          <div className="text-center">
            <div className="w-20 h-20 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <TrophyIcon className="h-10 w-10 text-yellow-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">
              {portfolio?.score?.total_score?.toFixed(0) || 0}
            </p>
            <p className="text-sm text-gray-600">
              Niveau {portfolio?.score?.level || 1}
            </p>
            <div className="mt-4 bg-gray-200 rounded-full h-2">
              <div 
                className="bg-yellow-600 h-2 rounded-full" 
                style={{ width: `${Math.min(100, (portfolio?.score?.total_score || 0) % 100)}%` }}
              />
            </div>
          </div>
        </Card>
      </div>

      {/* Statistiques du marché */}
      <Card title="Informations du marché $QS">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-sm text-gray-600">Offre circulante</p>
            <p className="text-xl font-bold text-gray-900">
              {marketInfo?.supply_info?.circulating_supply?.toLocaleString() || 0}
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600">Offre totale</p>
            <p className="text-xl font-bold text-gray-900">
              {marketInfo?.supply_info?.total_supply?.toLocaleString() || 0}
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600">Détenteurs actifs</p>
            <p className="text-xl font-bold text-gray-900">
              {marketInfo?.network_stats?.active_users || 0}
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600">Transactions</p>
            <p className="text-xl font-bold text-gray-900">
              {marketInfo?.network_stats?.total_transactions || 0}
            </p>
          </div>
        </div>
      </Card>

      {/* Contenu principal */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Transactions récentes */}
        <Card title="Transactions récentes">
          <div className="space-y-3">
            {transactions?.slice(0, 10).map((tx, index) => (
              <div key={tx.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`
                    p-2 rounded-full
                    ${tx.from_user === portfolio?.user_id ? 'bg-red-100' : 'bg-green-100'}
                  `}>
                    {tx.from_user === portfolio?.user_id ? (
                      <ArrowUpIcon className="h-4 w-4 text-red-600" />
                    ) : (
                      <ArrowDownIcon className="h-4 w-4 text-green-600" />
                    )}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {tx.from_user === portfolio?.user_id ? 'Envoyé' : 'Reçu'}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(tx.timestamp).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className={`
                  text-sm font-medium
                  ${tx.from_user === portfolio?.user_id ? 'text-red-600' : 'text-green-600'}
                `}>
                  {tx.from_user === portfolio?.user_id ? '-' : '+'}
                  {tx.amount} QS
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Récompenses récentes */}
        <Card title="Récompenses récentes">
          <div className="space-y-3">
            {rewards?.slice(0, 10).map((reward, index) => (
              <div key={reward.id} className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-green-100 rounded-full">
                    <GiftIcon className="h-4 w-4 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {reward.reward_type.replace('_', ' ')}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(reward.timestamp).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="text-sm font-medium text-green-600">
                  +{reward.amount} QS
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Classement */}
      <Card title="Classement des détenteurs">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rang
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Utilisateur
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Solde
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Devices
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {leaderboard?.slice(0, 10).map((user, index) => (
                <tr key={user.user_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className={`
                        inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium
                        ${index < 3 ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800'}
                      `}>
                        {user.rank}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {user.user_id}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {user.balance.toLocaleString()} QS
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {user.reputation_score.toFixed(0)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {user.device_count}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Modal de transfert */}
      <Modal
        isOpen={showTransferModal}
        onClose={() => setShowTransferModal(false)}
        title="Transférer des tokens"
      >
        <div className="space-y-4">
          <Input
            label="ID utilisateur destinataire"
            value={transferData.to_user}
            onChange={(e) => setTransferData({...transferData, to_user: e.target.value})}
            placeholder="Entrez l'ID utilisateur..."
          />
          
          <Input
            label="Montant (QS)"
            type="number"
            value={transferData.amount}
            onChange={(e) => setTransferData({...transferData, amount: e.target.value})}
            placeholder="0.00"
          />
          
          <Input
            label="Description (optionnel)"
            value={transferData.description}
            onChange={(e) => setTransferData({...transferData, description: e.target.value})}
            placeholder="Motif du transfert..."
          />
          
          <div className="flex justify-end space-x-3">
            <Button
              variant="secondary"
              onClick={() => setShowTransferModal(false)}
            >
              Annuler
            </Button>
            <Button
              onClick={() => transferMutation.mutate(transferData)}
              loading={transferMutation.isLoading}
              disabled={!transferData.to_user || !transferData.amount}
            >
              Transférer
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default Tokens;