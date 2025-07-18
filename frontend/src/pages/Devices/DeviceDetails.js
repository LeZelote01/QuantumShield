import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { deviceService } from '../../services/deviceService';
import { cryptoService } from '../../services/cryptoService';
import { useToast } from '../../contexts/ToastContext';
import { ArrowLeftIcon, ShieldCheckIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

const DeviceDetails = () => {
  const { deviceId } = useParams();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  
  const [activeTab, setActiveTab] = useState('overview');
  const [showEncryptForm, setShowEncryptForm] = useState(false);
  const [encryptData, setEncryptData] = useState('');
  const [decryptData, setDecryptData] = useState('');

  // Fetch device details
  const { data: device, isLoading, error } = useQuery(
    ['device', deviceId],
    () => deviceService.getDeviceById(deviceId),
    {
      onError: (error) => {
        showToast('Erreur lors du chargement du device', 'error');
      }
    }
  );

  // Fetch device metrics
  const { data: metrics } = useQuery(
    ['device-metrics', deviceId],
    () => deviceService.getDeviceMetrics(deviceId),
    {
      refetchInterval: 30000, // Refetch every 30 seconds
      enabled: !!device
    }
  );

  // Encrypt data mutation
  const encryptMutation = useMutation(
    (data) => cryptoService.encryptData(data, device?.public_key),
    {
      onSuccess: (result) => {
        showToast('Données chiffrées avec succès', 'success');
        setEncryptData(result.encrypted_data);
      },
      onError: () => {
        showToast('Erreur lors du chiffrement', 'error');
      }
    }
  );

  // Update device heartbeat
  const heartbeatMutation = useMutation(
    (data) => deviceService.updateHeartbeat(deviceId, data),
    {
      onSuccess: () => {
        showToast('Heartbeat mis à jour', 'success');
        queryClient.invalidateQueries(['device', deviceId]);
      },
      onError: () => {
        showToast('Erreur lors de la mise à jour du heartbeat', 'error');
      }
    }
  );

  const handleEncrypt = () => {
    if (!encryptData.trim()) {
      showToast('Veuillez entrer des données à chiffrer', 'error');
      return;
    }
    encryptMutation.mutate(encryptData);
  };

  const handleHeartbeat = () => {
    heartbeatMutation.mutate({
      status: 'active',
      timestamp: new Date().toISOString(),
      sensor_data: {
        temperature: 22.5,
        humidity: 45,
        battery: 87
      }
    });
  };

  const tabs = [
    { id: 'overview', label: 'Aperçu' },
    { id: 'security', label: 'Sécurité' },
    { id: 'metrics', label: 'Métriques' },
    { id: 'logs', label: 'Logs' }
  ];

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !device) {
    return (
      <div className="text-center py-12">
        <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Device non trouvé</h3>
        <p className="text-gray-500 mb-4">Le device demandé n'existe pas ou n'est plus disponible.</p>
        <button
          onClick={() => navigate('/devices')}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          <ArrowLeftIcon className="h-4 w-4 mr-2" />
          Retour aux devices
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <button
          onClick={() => navigate('/devices')}
          className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700 mb-4"
        >
          <ArrowLeftIcon className="h-4 w-4 mr-1" />
          Retour aux devices
        </button>
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{device.name}</h1>
            <p className="text-gray-500 mt-1">{device.device_type} • {device.device_id}</p>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              device.status === 'active' 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {device.status === 'active' ? 'Actif' : 'Inactif'}
            </span>
            <ShieldCheckIcon className="h-5 w-5 text-green-500" />
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Informations générales</h3>
              <dl className="space-y-3">
                <div>
                  <dt className="text-sm font-medium text-gray-500">ID Device</dt>
                  <dd className="text-sm text-gray-900">{device.device_id}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Type</dt>
                  <dd className="text-sm text-gray-900">{device.device_type}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Status</dt>
                  <dd className="text-sm text-gray-900">{device.status}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Dernière activité</dt>
                  <dd className="text-sm text-gray-900">
                    {device.last_seen ? new Date(device.last_seen).toLocaleString() : 'N/A'}
                  </dd>
                </div>
              </dl>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Actions</h3>
              <div className="space-y-3">
                <button
                  onClick={handleHeartbeat}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 text-sm"
                >
                  Envoyer Heartbeat
                </button>
                <button
                  onClick={() => setShowEncryptForm(true)}
                  className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 text-sm"
                >
                  Test Chiffrement
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'security' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Paramètres de sécurité</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Clé publique NTRU++
                </label>
                <textarea
                  value={device.public_key || ''}
                  readOnly
                  className="w-full h-32 p-3 border border-gray-300 rounded-md bg-gray-50 text-xs font-mono"
                />
              </div>
              
              {showEncryptForm && (
                <div className="border-t pt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Test de chiffrement
                  </label>
                  <div className="space-y-3">
                    <textarea
                      value={encryptData}
                      onChange={(e) => setEncryptData(e.target.value)}
                      placeholder="Entrez les données à chiffrer..."
                      className="w-full h-24 p-3 border border-gray-300 rounded-md"
                    />
                    <button
                      onClick={handleEncrypt}
                      disabled={encryptMutation.isLoading}
                      className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
                    >
                      {encryptMutation.isLoading ? 'Chiffrement...' : 'Chiffrer'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'metrics' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Métriques en temps réel</h3>
            {metrics ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {metrics.uptime || '0h'}
                  </div>
                  <div className="text-sm text-gray-500">Uptime</div>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {metrics.cpu_usage || '0%'}
                  </div>
                  <div className="text-sm text-gray-500">CPU Usage</div>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">
                    {metrics.memory_usage || '0%'}
                  </div>
                  <div className="text-sm text-gray-500">Mémoire</div>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">Aucune métrique disponible</p>
            )}
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Logs d'activité</h3>
            <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm h-64 overflow-y-auto">
              <div>2024-01-15 10:30:22 - Device connected</div>
              <div>2024-01-15 10:30:25 - NTRU++ keys generated</div>
              <div>2024-01-15 10:30:30 - Heartbeat sent</div>
              <div>2024-01-15 10:31:00 - Sensor data collected</div>
              <div>2024-01-15 10:31:30 - Heartbeat sent</div>
              <div>2024-01-15 10:32:00 - Encryption test performed</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DeviceDetails;