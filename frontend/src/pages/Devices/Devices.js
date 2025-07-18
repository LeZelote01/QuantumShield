import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { 
  PlusIcon, 
  CpuChipIcon, 
  EyeIcon, 
  PencilIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import deviceService from '../../services/deviceService';
import { useToast } from '../../contexts/ToastContext';
import Card from '../../components/UI/Card';
import Button from '../../components/UI/Button';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import Modal from '../../components/UI/Modal';
import DeviceRegistrationForm from './components/DeviceRegistrationForm';

const Devices = () => {
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const { showSuccess, showError } = useToast();

  const { data: devices, isLoading, refetch } = useQuery(
    'devices',
    deviceService.getDevices,
    {
      onError: (error) => {
        showError('Erreur lors du chargement des devices');
      },
    }
  );

  const { data: deviceTypes } = useQuery(
    'deviceTypes',
    deviceService.getAvailableDeviceTypes
  );

  const handleDeviceRegistered = () => {
    setShowRegisterModal(false);
    refetch();
    showSuccess('Device enregistré avec succès !');
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'inactive':
        return <XCircleIcon className="h-5 w-5 text-gray-500" />;
      case 'compromised':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      case 'maintenance':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
      default:
        return <CpuChipIcon className="h-5 w-5 text-gray-500" />;
    }
  };

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
          <h1 className="text-2xl font-bold text-gray-900">Devices IoT</h1>
          <p className="text-gray-600">
            Gérez vos dispositifs IoT sécurisés avec cryptographie post-quantique
          </p>
        </div>
        <Button
          onClick={() => setShowRegisterModal(true)}
          className="flex items-center space-x-2"
        >
          <PlusIcon className="h-5 w-5" />
          <span>Enregistrer un device</span>
        </Button>
      </div>

      {/* Statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <CpuChipIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Total devices</p>
              <p className="text-2xl font-bold text-gray-900">{devices?.length || 0}</p>
            </div>
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <CheckCircleIcon className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Actifs</p>
              <p className="text-2xl font-bold text-gray-900">
                {devices?.filter(d => d.status === 'active').length || 0}
              </p>
            </div>
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-red-100 rounded-lg">
              <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Compromis</p>
              <p className="text-2xl font-bold text-gray-900">
                {devices?.filter(d => d.status === 'compromised').length || 0}
              </p>
            </div>
          </div>
        </Card>
        
        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Maintenance</p>
              <p className="text-2xl font-bold text-gray-900">
                {devices?.filter(d => d.status === 'maintenance').length || 0}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Liste des devices */}
      <Card title="Mes devices">
        {devices && devices.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Device
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Statut
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Dernière activité
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {devices.map((device) => (
                  <tr key={device.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="p-2 bg-gray-100 rounded-lg">
                          <CpuChipIcon className="h-5 w-5 text-gray-600" />
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {device.device_name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {device.device_id}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{device.device_type}</div>
                      <div className="text-sm text-gray-500">
                        {device.capabilities?.join(', ')}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`
                        inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                        ${getStatusColor(device.status)}
                      `}>
                        {getStatusIcon(device.status)}
                        <span className="ml-1">{getStatusText(device.status)}</span>
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(device.last_heartbeat).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex items-center space-x-2">
                        <Link
                          to={`/devices/${device.device_id}`}
                          className="text-indigo-600 hover:text-indigo-900"
                        >
                          <EyeIcon className="h-4 w-4" />
                        </Link>
                        <button
                          onClick={() => setSelectedDevice(device)}
                          className="text-gray-600 hover:text-gray-900"
                        >
                          <PencilIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8">
            <CpuChipIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 mb-4">Aucun device enregistré</p>
            <Button onClick={() => setShowRegisterModal(true)}>
              Enregistrer votre premier device
            </Button>
          </div>
        )}
      </Card>

      {/* Modal d'enregistrement */}
      <Modal
        isOpen={showRegisterModal}
        onClose={() => setShowRegisterModal(false)}
        title="Enregistrer un nouveau device"
        size="large"
      >
        <DeviceRegistrationForm
          deviceTypes={deviceTypes?.device_types || []}
          onSuccess={handleDeviceRegistered}
          onCancel={() => setShowRegisterModal(false)}
        />
      </Modal>
    </div>
  );
};

export default Devices;