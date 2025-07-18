import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { 
  BuildingStorefrontIcon,
  ChartBarIcon,
  CubeIcon,
  ShieldCheckIcon,
  BanknotesIcon,
  ArrowTrendingUpIcon,
  PlusIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom';
import advancedEconomyService from '../../services/advancedEconomyService';
import { useToast } from '../../contexts/ToastContext';
import Card from '../../components/UI/Card';
import Button from '../../components/UI/Button';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const Economy = () => {
  const { showError } = useToast();

  // Queries
  const { data: dashboard, isLoading: dashboardLoading } = useQuery(
    'economyDashboard',
    advancedEconomyService.getEconomyDashboard,
    {
      onError: () => showError('Erreur lors du chargement du tableau de bord économique')
    }
  );

  const { data: recommendations, isLoading: recommendationsLoading } = useQuery(
    'economyRecommendations',
    advancedEconomyService.getRecommendations,
    {
      onError: () => showError('Erreur lors du chargement des recommandations')
    }
  );

  const { data: healthCheck } = useQuery(
    'economyHealth',
    advancedEconomyService.getHealthCheck,
    {
      refetchInterval: 30000, // Check every 30 seconds
      onError: () => showError('Service économique indisponible')
    }
  );

  const economyFeatures = [
    {
      title: 'Marketplace de Services',
      description: 'Achetez et vendez des services spécialisés',
      icon: BuildingStorefrontIcon,
      color: 'blue',
      stats: dashboard?.dashboard?.marketplace,
      path: '/economy/marketplace'
    },
    {
      title: 'Staking & DeFi',
      description: 'Staking de tokens avec récompenses',
      icon: ChartBarIcon,
      color: 'green',
      stats: dashboard?.dashboard?.staking,
      path: '/economy/staking'
    },
    {
      title: 'Tokenisation d\'Actifs',
      description: 'Transformez vos actifs physiques en tokens',
      icon: CubeIcon,
      color: 'purple',
      stats: dashboard?.dashboard?.tokenization,
      path: '/economy/tokenization'
    },
    {
      title: 'Prêts & Emprunts',
      description: 'Système de prêts décentralisé',
      icon: BanknotesIcon,
      color: 'orange',
      stats: dashboard?.dashboard?.lending,
      path: '/economy/lending'
    },
    {
      title: 'Assurance Décentralisée',
      description: 'Protégez vos actifs avec des smart contracts',
      icon: ShieldCheckIcon,
      color: 'red',
      stats: dashboard?.dashboard?.insurance,
      path: '/economy/insurance'
    },
    {
      title: 'Analytics & Gouvernance',
      description: 'Prendre des décisions éclairées',
      icon: ArrowTrendingUpIcon,
      color: 'indigo',
      stats: { active_proposals: 0 },
      path: '/economy/governance'
    }
  ];

  const getColorClasses = (color) => {
    const colors = {
      blue: 'text-blue-600 bg-blue-50',
      green: 'text-green-600 bg-green-50',
      purple: 'text-purple-600 bg-purple-50',
      orange: 'text-orange-600 bg-orange-50',
      red: 'text-red-600 bg-red-50',
      indigo: 'text-indigo-600 bg-indigo-50'
    };
    return colors[color] || 'text-gray-600 bg-gray-50';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      high: 'text-red-700 bg-red-50 border-red-200',
      medium: 'text-yellow-700 bg-yellow-50 border-yellow-200',
      low: 'text-green-700 bg-green-50 border-green-200'
    };
    return colors[priority] || 'text-gray-700 bg-gray-50 border-gray-200';
  };

  if (dashboardLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Économie Avancée
          </h1>
          <p className="text-gray-600 mt-1">
            Marketplace, DeFi, Tokenisation et plus encore
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            healthCheck?.status === 'healthy' 
              ? 'bg-green-100 text-green-800' 
              : 'bg-red-100 text-red-800'
          }`}>
            {healthCheck?.status === 'healthy' ? 'Service actif' : 'Service indisponible'}
          </div>
        </div>
      </div>

      {/* Global Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <BuildingStorefrontIcon className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Services actifs</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboard?.dashboard?.marketplace?.active_services || 0}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">QS stakés</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboard?.dashboard?.staking?.total_staked?.toLocaleString() || 0}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CubeIcon className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Actifs tokenisés</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboard?.dashboard?.tokenization?.tokenized_assets || 0}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <BanknotesIcon className="h-8 w-8 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Prêts actifs</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboard?.dashboard?.lending?.active_loans || 0}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Features Grid */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Services disponibles
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {economyFeatures.map((feature, index) => {
            const IconComponent = feature.icon;
            return (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className={`p-3 rounded-lg ${getColorClasses(feature.color)}`}>
                      <IconComponent className="h-6 w-6" />
                    </div>
                    <Link to={feature.path}>
                      <Button size="sm" variant="outline">
                        <EyeIcon className="h-4 w-4 mr-1" />
                        Voir
                      </Button>
                    </Link>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600 text-sm mt-1">
                      {feature.description}
                    </p>
                  </div>

                  {feature.stats && (
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        {Object.entries(feature.stats).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="text-gray-500 capitalize">
                              {key.replace(/_/g, ' ')}:
                            </span>
                            <span className="font-medium">{value}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Recommendations */}
      {recommendations?.recommendations?.length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Recommandations personnalisées
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommendations.recommendations.map((rec, index) => (
              <Card key={index} className={`border-l-4 ${getPriorityColor(rec.priority)}`}>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-gray-900">
                      {rec.title}
                    </h3>
                    <span className={`px-2 py-1 text-xs rounded-full font-medium ${getPriorityColor(rec.priority)}`}>
                      {rec.priority}
                    </span>
                  </div>
                  <p className="text-gray-600 text-sm">
                    {rec.description}
                  </p>
                  <div className="flex justify-end">
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => {
                        // Handle recommendation action
                        console.log('Action:', rec.action);
                      }}
                    >
                      Voir plus
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Actions rapides
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link to="/economy/tokenization">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <div className="text-center space-y-2">
                <CubeIcon className="h-8 w-8 text-purple-600 mx-auto" />
                <p className="font-medium text-gray-900">Tokeniser un actif</p>
              </div>
            </Card>
          </Link>
          
          <Link to="/economy/marketplace">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <div className="text-center space-y-2">
                <BuildingStorefrontIcon className="h-8 w-8 text-blue-600 mx-auto" />
                <p className="font-medium text-gray-900">Créer un service</p>
              </div>
            </Card>
          </Link>
          
          <Link to="/economy/staking">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <div className="text-center space-y-2">
                <ChartBarIcon className="h-8 w-8 text-green-600 mx-auto" />
                <p className="font-medium text-gray-900">Staking de tokens</p>
              </div>
            </Card>
          </Link>
          
          <Link to="/economy/lending">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <div className="text-center space-y-2">
                <BanknotesIcon className="h-8 w-8 text-orange-600 mx-auto" />
                <p className="font-medium text-gray-900">Demander un prêt</p>
              </div>
            </Card>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Economy;