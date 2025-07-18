import React from 'react';
import { useQuery } from 'react-query';
import dashboardService from '../../services/dashboardService';
import { useToast } from '../../contexts/ToastContext';
import Card from '../../components/UI/Card';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import DashboardStats from './components/DashboardStats';
import NetworkStatus from './components/NetworkStatus';
import RecentActivity from './components/RecentActivity';
import DeviceOverview from './components/DeviceOverview';
import TokenPortfolio from './components/TokenPortfolio';

const Dashboard = () => {
  const { showError } = useToast();

  const { data: overview, isLoading: overviewLoading } = useQuery(
    'dashboardOverview',
    dashboardService.getDashboardOverview,
    {
      onError: (error) => {
        showError('Erreur lors du chargement du dashboard');
      },
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  const { data: alerts } = useQuery(
    'dashboardAlerts',
    dashboardService.getAlerts,
    {
      onError: (error) => {
        console.error('Erreur lors du chargement des alertes:', error);
      },
    }
  );

  if (overviewLoading) {
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
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">
            Bienvenue {overview?.user_info?.username} ! Voici l'état de votre écosystème QuantumShield.
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
            Réseau actif
          </div>
          {alerts?.unread_count > 0 && (
            <div className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-medium">
              {alerts.unread_count} alerte{alerts.unread_count > 1 ? 's' : ''}
            </div>
          )}
        </div>
      </div>

      {/* Stats rapides */}
      <DashboardStats overview={overview} />

      {/* Contenu principal */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Colonne gauche */}
        <div className="lg:col-span-2 space-y-6">
          {/* Aperçu des devices */}
          <DeviceOverview />
          
          {/* Statut du réseau */}
          <NetworkStatus />
          
          {/* Activité récente */}
          <RecentActivity />
        </div>

        {/* Colonne droite */}
        <div className="space-y-6">
          {/* Portfolio tokens */}
          <TokenPortfolio />
          
          {/* Alertes */}
          {alerts && alerts.alerts.length > 0 && (
            <Card title="Alertes" className="border-l-4 border-l-red-500">
              <div className="space-y-3">
                {alerts.alerts.slice(0, 5).map((alert, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className={`
                      w-2 h-2 rounded-full mt-2 flex-shrink-0
                      ${alert.type === 'error' ? 'bg-red-500' : 
                        alert.type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'}
                    `} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900">{alert.title}</p>
                      <p className="text-xs text-gray-500 truncate">{alert.message}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Métriques de performance */}
          <Card title="Performance">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Uptime réseau</span>
                <span className="text-sm font-medium text-green-600">99.9%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Latence moyenne</span>
                <span className="text-sm font-medium text-green-600">&lt; 100ms</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Transactions/s</span>
                <span className="text-sm font-medium text-blue-600">
                  {overview?.network_stats?.total_transactions || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Mineurs actifs</span>
                <span className="text-sm font-medium text-purple-600">
                  {overview?.network_stats?.active_miners || 0}
                </span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;