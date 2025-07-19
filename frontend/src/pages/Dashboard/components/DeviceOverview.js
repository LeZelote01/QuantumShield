import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { EyeIcon, CpuChipIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import dashboardService from '../../../services/dashboardService';
import Card from '../../../components/UI/Card';
import LoadingSpinner from '../../../components/UI/LoadingSpinner';

const DeviceOverview = () => {
  const { data: devicesOverview, isLoading } = useQuery(
    'devicesOverview',
    dashboardService.getDevicesOverview,
    {
      refetchInterval: 60000, // Refetch every minute
    }
  );

  if (isLoading) {
    return (
      <Card title="Aperçu des devices">
        <div className="flex items-center justify-center py-8">
          <LoadingSpinner />
        </div>
      </Card>
    );
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      case 'compromised':
        return 'bg-red-100 text-red-800';
      case 'maintenance':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'active':
        return 'Actif';
      case 'inactive':
        return 'Inactif';
      case 'compromised':
        return 'Compromis';
      case 'maintenance':
        return 'Maintenance';
      default:
        return 'Inconnu';
    }
  };

  return (
    <Card 
      title="Aperçu des devices" 
      subtitle={`${devicesOverview?.total_devices || 0} devices enregistrés`}
      footer={
        <Link 
          to="/devices" 
          className="text-indigo-600 hover:text-indigo-500 font-medium text-sm"
        >
          Voir tous les devices →
        </Link>
      }
    >
      <div className="space-y-6">
        {/* Statistiques rapides */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center">
              <CpuChipIcon className="h-8 w-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-green-900">Actifs</p>
                <p className="text-2xl font-bold text-green-600">
                  {devicesOverview?.status_distribution?.active || 0}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center">
              <CpuChipIcon className="h-8 w-8 text-gray-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">Inactifs</p>
                <p className="text-2xl font-bold text-gray-600">
                  {devicesOverview?.status_distribution?.inactive || 0}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-red-50 p-4 rounded-lg">
            <div className="flex items-center">
              <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-red-900">Compromis</p>
                <p className="text-2xl font-bold text-red-600">
                  {devicesOverview?.status_distribution?.compromised || 0}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-sm">
                  {Math.round(devicesOverview?.average_uptime || 0)}%
                </span>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-blue-900">Uptime moy.</p>
                <p className="text-2xl font-bold text-blue-600">
                  {Math.round(devicesOverview?.average_uptime || 0)}%
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Types de devices */}
        <div>
          <h4 className="text-sm font-medium text-gray-600 mb-3">Types de devices</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {Object.entries(devicesOverview?.device_types || {}).map(([type, count]) => (
              <div key={type} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-sm font-medium text-gray-900">{type}</span>
                <span className="text-sm text-gray-600">{count} device{count > 1 ? 's' : ''}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Devices récents */}
        <div>
          <h4 className="text-sm font-medium text-gray-600 mb-3">Derniers devices</h4>
          <div className="space-y-3">
            {devicesOverview?.device_metrics?.slice(0, 5).map((device, index) => (
              <div key={device.device_id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-3">
                  <CpuChipIcon className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{device.device_name}</p>
                    <p className="text-xs text-gray-500">{device.device_type}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`
                    px-2 py-1 rounded-full text-xs font-medium
                    ${getStatusColor(device.status)}
                  `}>
                    {getStatusText(device.status)}
                  </span>
                  <Link 
                    to={`/devices/${device.device_id}`}
                    className="text-indigo-600 hover:text-indigo-500"
                  >
                    <EyeIcon className="h-4 w-4" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
};

export default DeviceOverview;