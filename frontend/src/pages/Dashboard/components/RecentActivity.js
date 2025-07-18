import React from 'react';
import { useQuery } from 'react-query';
import { 
  CpuChipIcon, 
  CurrencyDollarIcon, 
  ExclamationTriangleIcon,
  WrenchScrewdriverIcon 
} from '@heroicons/react/24/outline';
import dashboardService from '../../../services/dashboardService';
import Card from '../../../components/UI/Card';
import LoadingSpinner from '../../../components/UI/LoadingSpinner';

const RecentActivity = () => {
  const { data: recentActivity, isLoading } = useQuery(
    'recentActivity',
    () => dashboardService.getRecentActivity(10),
    {
      refetchInterval: 60000, // Refetch every minute
    }
  );

  if (isLoading) {
    return (
      <Card title="Activité récente">
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner />
        </div>
      </Card>
    );
  }

  const getActivityIcon = (type) => {
    switch (type) {
      case 'reward':
        return <CurrencyDollarIcon className="h-5 w-5 text-green-600" />;
      case 'transaction':
        return <CurrencyDollarIcon className="h-5 w-5 text-blue-600" />;
      case 'device_activity':
        return <CpuChipIcon className="h-5 w-5 text-indigo-600" />;
      case 'anomaly':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />;
      case 'mining':
        return <WrenchScrewdriverIcon className="h-5 w-5 text-purple-600" />;
      default:
        return <CpuChipIcon className="h-5 w-5 text-gray-600" />;
    }
  };

  const getActivityColor = (type) => {
    switch (type) {
      case 'reward':
        return 'bg-green-100 border-green-200';
      case 'transaction':
        return 'bg-blue-100 border-blue-200';
      case 'device_activity':
        return 'bg-indigo-100 border-indigo-200';
      case 'anomaly':
        return 'bg-red-100 border-red-200';
      case 'mining':
        return 'bg-purple-100 border-purple-200';
      default:
        return 'bg-gray-100 border-gray-200';
    }
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const activityTime = new Date(timestamp);
    const diffInMinutes = Math.floor((now - activityTime) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'À l\'instant';
    if (diffInMinutes < 60) return `${diffInMinutes} min`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} h`;
    return `${Math.floor(diffInMinutes / 1440)} j`;
  };

  return (
    <Card title="Activité récente" subtitle={`${recentActivity?.total_count || 0} activités`}>
      <div className="space-y-4">
        {recentActivity?.activities?.length > 0 ? (
          recentActivity.activities.map((activity, index) => (
            <div 
              key={index} 
              className={`
                flex items-start space-x-3 p-3 border rounded-lg
                ${getActivityColor(activity.type)}
              `}
            >
              <div className="flex-shrink-0 mt-1">
                {getActivityIcon(activity.type)}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">
                  {activity.description}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {formatTimeAgo(activity.timestamp)}
                </p>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-8">
            <CpuChipIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">Aucune activité récente</p>
          </div>
        )}
      </div>
    </Card>
  );
};

export default RecentActivity;