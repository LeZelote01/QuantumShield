import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { CurrencyDollarIcon, TrophyIcon, ChartBarIcon } from '@heroicons/react/24/outline';
import tokenService from '../../../services/tokenService';
import Card from '../../../components/UI/Card';
import LoadingSpinner from '../../../components/UI/LoadingSpinner';

const TokenPortfolio = () => {
  const { data: portfolio, isLoading } = useQuery(
    'tokenPortfolio',
    tokenService.getPortfolio,
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  const { data: userScore } = useQuery(
    'userScore',
    tokenService.getUserScore
  );

  if (isLoading) {
    return (
      <Card title="Portfolio $QS">
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner />
        </div>
      </Card>
    );
  }

  return (
    <Card 
      title="Portfolio $QS" 
      subtitle={`Wallet: ${portfolio?.wallet_address?.slice(0, 10)}...`}
      footer={
        <Link 
          to="/tokens" 
          className="text-indigo-600 hover:text-indigo-500 font-medium text-sm"
        >
          Voir le portfolio complet →
        </Link>
      }
    >
      <div className="space-y-6">
        {/* Solde principal */}
        <div className="bg-gradient-to-r from-indigo-500 to-purple-600 p-6 rounded-lg text-white">
          <div className="flex items-center justify-between mb-4">
            <CurrencyDollarIcon className="h-8 w-8" />
            <span className="text-sm opacity-90">Solde actuel</span>
          </div>
          <div className="text-3xl font-bold">
            {portfolio?.balance?.toLocaleString() || 0} QS
          </div>
          <div className="text-sm opacity-90 mt-2">
            ≈ ${(portfolio?.balance * 0.1 || 0).toLocaleString()} USD
          </div>
        </div>

        {/* Score de réputation */}
        <div className="bg-yellow-50 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <TrophyIcon className="h-6 w-6 text-yellow-600" />
              <div>
                <p className="text-sm font-medium text-yellow-900">Score de réputation</p>
                <p className="text-xs text-yellow-600">
                  Niveau {userScore?.level || 1}
                </p>
              </div>
            </div>
            <div className="text-2xl font-bold text-yellow-600">
              {Math.round(userScore?.total_score || 0)}
            </div>
          </div>
        </div>

        {/* Statistiques rapides */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center">
              <ChartBarIcon className="h-6 w-6 text-green-600" />
              <div className="ml-3">
                <p className="text-xs text-green-600">Devices actifs</p>
                <p className="text-lg font-bold text-green-900">
                  {portfolio?.active_devices || 0}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center">
              <CurrencyDollarIcon className="h-6 w-6 text-blue-600" />
              <div className="ml-3">
                <p className="text-xs text-blue-600">Récompenses</p>
                <p className="text-lg font-bold text-blue-900">
                  {portfolio?.total_rewards_earned?.toFixed(1) || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Transactions récentes */}
        <div>
          <h4 className="text-sm font-medium text-gray-600 mb-3">Transactions récentes</h4>
          <div className="space-y-2">
            {portfolio?.recent_transactions?.slice(0, 3).map((tx, index) => (
              <div key={tx.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <div className="flex-1">
                  <p className="text-xs font-medium text-gray-900">
                    {tx.transaction_type === 'reward' ? 'Récompense' : 'Transfert'}
                  </p>
                  <p className="text-xs text-gray-500">
                    {new Date(tx.timestamp).toLocaleDateString()}
                  </p>
                </div>
                <div className={`text-xs font-medium ${
                  tx.from_user === portfolio?.user_id ? 'text-red-600' : 'text-green-600'
                }`}>
                  {tx.from_user === portfolio?.user_id ? '-' : '+'}
                  {tx.amount} QS
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Récompenses récentes */}
        <div>
          <h4 className="text-sm font-medium text-gray-600 mb-3">Récompenses récentes</h4>
          <div className="space-y-2">
            {portfolio?.recent_rewards?.slice(0, 3).map((reward, index) => (
              <div key={reward.id} className="flex items-center justify-between p-2 bg-green-50 rounded">
                <div className="flex-1">
                  <p className="text-xs font-medium text-green-900">
                    {reward.reward_type.replace('_', ' ')}
                  </p>
                  <p className="text-xs text-green-600">
                    {new Date(reward.timestamp).toLocaleDateString()}
                  </p>
                </div>
                <div className="text-xs font-medium text-green-600">
                  +{reward.amount} QS
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
};

export default TokenPortfolio;