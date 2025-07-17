import React from 'react';
import { 
  CpuChipIcon, 
  CurrencyDollarIcon, 
  CubeIcon, 
  WrenchScrewdriverIcon,
  ShieldCheckIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';
import Card from '../../../components/UI/Card';

const DashboardStats = ({ overview }) => {
  const stats = [
    {
      name: 'Devices actifs',
      value: overview?.device_stats?.active_devices || 0,
      total: overview?.device_stats?.total_devices || 0,
      icon: CpuChipIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      change: '+2.5%',
      changeType: 'positive'
    },
    {
      name: 'Solde $QS',
      value: overview?.token_stats?.balance || 0,
      icon: CurrencyDollarIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      change: `+${overview?.token_stats?.recent_rewards || 0}`,
      changeType: 'positive'
    },
    {
      name: 'Blocs minés',
      value: overview?.network_stats?.total_blocks || 0,
      icon: CubeIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
      change: '+1.2%',
      changeType: 'positive'
    },
    {
      name: 'Score réputation',
      value: overview?.user_info?.reputation_score || 0,
      icon: ShieldCheckIcon,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-100',
      change: `Niveau ${overview?.user_info?.level || 1}`,
      changeType: 'neutral'
    },
    {
      name: 'Difficulté mining',
      value: overview?.network_stats?.mining_difficulty || 0,
      icon: WrenchScrewdriverIcon,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
      change: 'Stable',
      changeType: 'neutral'
    },
    {
      name: 'Transactions',
      value: overview?.network_stats?.total_transactions || 0,
      icon: ChartBarIcon,
      color: 'text-pink-600',
      bgColor: 'bg-pink-100',
      change: '+5.4%',
      changeType: 'positive'
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      {stats.map((stat, index) => (
        <Card key={index} className="hover:shadow-lg transition-shadow duration-200">
          <div className="flex items-center">
            <div className={`p-3 rounded-lg ${stat.bgColor}`}>
              <stat.icon className={`h-6 w-6 ${stat.color}`} />
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-600">{stat.name}</p>
              <p className="text-2xl font-bold text-gray-900">
                {typeof stat.value === 'number' && stat.value > 1000 
                  ? (stat.value / 1000).toFixed(1) + 'K' 
                  : stat.value}
                {stat.total && (
                  <span className="text-sm font-normal text-gray-500">
                    /{stat.total}
                  </span>
                )}
              </p>
              <p className={`text-xs ${
                stat.changeType === 'positive' ? 'text-green-600' : 
                stat.changeType === 'negative' ? 'text-red-600' : 'text-gray-500'
              }`}>
                {stat.change}
              </p>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
};

export default DashboardStats;