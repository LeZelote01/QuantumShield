import React from 'react';
import { useQuery } from 'react-query';
import dashboardService from '../../../services/dashboardService';
import Card from '../../../components/UI/Card';
import LoadingSpinner from '../../../components/UI/LoadingSpinner';

const NetworkStatus = () => {
  const { data: networkStatus, isLoading } = useQuery(
    'networkStatus',
    dashboardService.getNetworkStatus,
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  if (isLoading) {
    return (
      <Card title="Statut du réseau">
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner />
        </div>
      </Card>
    );
  }

  const getHealthColor = (health) => {
    switch (health) {
      case 'healthy':
        return 'text-green-600 bg-green-100';
      case 'congested':
        return 'text-yellow-600 bg-yellow-100';
      case 'low_miners':
        return 'text-orange-600 bg-orange-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getHealthText = (health) => {
    switch (health) {
      case 'healthy':
        return 'Réseau en bonne santé';
      case 'congested':
        return 'Réseau congestionné';
      case 'low_miners':
        return 'Peu de mineurs actifs';
      default:
        return 'Statut inconnu';
    }
  };

  return (
    <Card title="Statut du réseau">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Statut général */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-600">Statut général</span>
            <span className={`
              px-3 py-1 rounded-full text-sm font-medium
              ${getHealthColor(networkStatus?.network_health)}
            `}>
              {getHealthText(networkStatus?.network_health)}
            </span>
          </div>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Dernière synchronisation</span>
              <span className="text-sm font-medium text-gray-900">
                {networkStatus?.blockchain?.is_syncing ? 'En cours...' : 'Synchronisé'}
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Blocs totaux</span>
              <span className="text-sm font-medium text-gray-900">
                {networkStatus?.blockchain?.total_blocks?.toLocaleString() || 0}
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Transactions en attente</span>
              <span className="text-sm font-medium text-gray-900">
                {networkStatus?.blockchain?.pending_transactions || 0}
              </span>
            </div>
          </div>
        </div>

        {/* Métriques mining */}
        <div className="space-y-4">
          <h4 className="text-sm font-medium text-gray-600">Mining</h4>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Difficulté actuelle</span>
              <span className="text-sm font-medium text-gray-900">
                {networkStatus?.mining?.difficulty || 0}
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Mineurs actifs</span>
              <span className="text-sm font-medium text-gray-900">
                {networkStatus?.mining?.active_miners || 0}
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Hash rate</span>
              <span className="text-sm font-medium text-gray-900">
                {networkStatus?.mining?.hash_rate || 0} H/s
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Blocs aujourd'hui</span>
              <span className="text-sm font-medium text-gray-900">
                {networkStatus?.mining?.blocks_today || 0}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Tokens metrics */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <h4 className="text-sm font-medium text-gray-600 mb-4">Tokens $QS</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-sm text-gray-600">Offre circulante</p>
            <p className="text-lg font-semibold text-gray-900">
              {networkStatus?.tokens?.circulating_supply?.toLocaleString() || 0}
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600">Offre totale</p>
            <p className="text-lg font-semibold text-gray-900">
              {networkStatus?.tokens?.total_supply?.toLocaleString() || 0}
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600">Détenteurs actifs</p>
            <p className="text-lg font-semibold text-gray-900">
              {networkStatus?.tokens?.active_holders || 0}
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600">Volume transactions</p>
            <p className="text-lg font-semibold text-gray-900">
              {networkStatus?.tokens?.transaction_volume || 0}
            </p>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default NetworkStatus;