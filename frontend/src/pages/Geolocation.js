import React, { useState, useEffect } from 'react';
import { MapPin, Navigation, Target, Activity, AlertTriangle, Map, Plus, Search, Filter, History } from 'lucide-react';
import { useToast } from '../contexts/ToastContext';

const Geolocation = () => {
  const [devices, setDevices] = useState([]);
  const [geofences, setGeofences] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [statistics, setStatistics] = useState({});
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [locationHistory, setLocationHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [newGeofence, setNewGeofence] = useState({
    name: '',
    type: 'polygon',
    coordinates: [{ latitude: 48.8566, longitude: 2.3522 }],
    radius: 1000,
    description: ''
  });
  const [showCreateGeofence, setShowCreateGeofence] = useState(false);
  const [nearbySearch, setNearbySearch] = useState({
    latitude: 48.8566,
    longitude: 2.3522,
    radius: 1.0
  });
  const [nearbyDevices, setNearbyDevices] = useState([]);

  const { showSuccess, showError } = useToast();

  const fetchDevices = async () => {
    try {
      const response = await fetch('/api/devices/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setDevices(data);
      }
    } catch (error) {
      console.error('Erreur récupération devices:', error);
    }
  };

  const fetchGeofences = async () => {
    try {
      const response = await fetch('/api/geolocation/geofences', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setGeofences(data.geofences || []);
      }
    } catch (error) {
      console.error('Erreur récupération geofences:', error);
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await fetch('/api/geolocation/alerts', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setAlerts(data.alerts || []);
      }
    } catch (error) {
      console.error('Erreur récupération alertes:', error);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await fetch('/api/geolocation/statistics', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setStatistics(data.statistics || {});
      }
    } catch (error) {
      console.error('Erreur récupération statistiques:', error);
    }
  };

  const fetchLocationHistory = async (deviceId) => {
    try {
      const response = await fetch(`/api/geolocation/device/${deviceId}/location-history`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setLocationHistory(data.history || []);
      }
    } catch (error) {
      console.error('Erreur récupération historique:', error);
    }
  };

  const updateDeviceLocation = async (deviceId) => {
    try {
      // Obtenir la position actuelle
      const position = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject);
      });

      const response = await fetch('/api/geolocation/update-location', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          device_id: deviceId,
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          altitude: position.coords.altitude,
          source: 'manual'
        })
      });

      if (response.ok) {
        showSuccess('Position mise à jour avec succès');
        fetchDevices();
        fetchStatistics();
      } else {
        showError('Erreur lors de la mise à jour de la position');
      }
    } catch (error) {
      if (error.code === error.PERMISSION_DENIED) {
        showError('Accès à la géolocalisation refusé');
      } else {
        showError('Erreur lors de la récupération de la position');
      }
    }
  };

  const createGeofence = async () => {
    try {
      const response = await fetch('/api/geolocation/geofences', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(newGeofence)
      });

      if (response.ok) {
        showSuccess('Zone géographique créée avec succès');
        setShowCreateGeofence(false);
        setNewGeofence({
          name: '',
          type: 'polygon',
          coordinates: [{ latitude: 48.8566, longitude: 2.3522 }],
          radius: 1000,
          description: ''
        });
        fetchGeofences();
      } else {
        showError('Erreur lors de la création de la zone');
      }
    } catch (error) {
      showError('Erreur lors de la création de la zone');
    }
  };

  const findNearbyDevices = async () => {
    try {
      const response = await fetch('/api/geolocation/nearby-devices', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(nearbySearch)
      });

      if (response.ok) {
        const data = await response.json();
        setNearbyDevices(data.nearby_devices || []);
      }
    } catch (error) {
      console.error('Erreur recherche devices proches:', error);
    }
  };

  const resolveAlert = async (alertId) => {
    try {
      const response = await fetch(`/api/geolocation/alerts/${alertId}/resolve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        showSuccess('Alerte résolue');
        fetchAlerts();
      }
    } catch (error) {
      showError('Erreur lors de la résolution de l\'alerte');
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        await Promise.all([
          fetchDevices(),
          fetchGeofences(),
          fetchAlerts(),
          fetchStatistics()
        ]);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const filteredDevices = devices.filter(device =>
    device.device_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    device.device_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const devicesWithLocation = devices.filter(device => device.current_location);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <MapPin className="h-8 w-8 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">Géolocalisation des Dispositifs</h1>
        </div>
        <button
          onClick={() => setShowCreateGeofence(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>Créer une Zone</span>
        </button>
      </div>

      {/* Statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Devices Localisés</p>
              <p className="text-2xl font-bold text-blue-600">
                {statistics.devices_with_location || 0}
              </p>
            </div>
            <Navigation className="h-8 w-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Zones Géographiques</p>
              <p className="text-2xl font-bold text-green-600">
                {statistics.user_geofence_zones || 0}
              </p>
            </div>
            <Target className="h-8 w-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Alertes Actives</p>
              <p className="text-2xl font-bold text-red-600">
                {statistics.active_alerts || 0}
              </p>
            </div>
            <AlertTriangle className="h-8 w-8 text-red-600" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Qualité Moyenne</p>
              <p className="text-2xl font-bold text-purple-600">
                {(statistics.average_location_quality * 100).toFixed(1)}%
              </p>
            </div>
            <Activity className="h-8 w-8 text-purple-600" />
          </div>
        </div>
      </div>

      {/* Onglets */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { key: 'overview', label: 'Vue d\'ensemble', icon: Map },
              { key: 'devices', label: 'Dispositifs', icon: Navigation },
              { key: 'geofences', label: 'Zones', icon: Target },
              { key: 'alerts', label: 'Alertes', icon: AlertTriangle },
              { key: 'search', label: 'Recherche', icon: Search }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Contenu des onglets */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">Répartition des Sources</h3>
            <div className="space-y-3">
              {Object.entries(statistics.source_distribution || {}).map(([source, count]) => (
                <div key={source} className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700 capitalize">{source}</span>
                  <span className="text-sm text-gray-500">{count}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-4">Couverture Géographique</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Couverture</span>
                <span className="text-sm text-gray-500">
                  {(statistics.location_coverage || 0).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${statistics.location_coverage || 0}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'devices' && (
        <div className="bg-white rounded-lg shadow-md">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Dispositifs avec Localisation</h3>
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  placeholder="Rechercher un dispositif..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
                />
                <Filter className="h-4 w-4 text-gray-400" />
              </div>
            </div>
          </div>
          <div className="divide-y divide-gray-200">
            {filteredDevices.map((device) => (
              <div key={device.device_id} className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`h-3 w-3 rounded-full ${
                      device.current_location ? 'bg-green-500' : 'bg-gray-300'
                    }`}></div>
                    <div>
                      <h4 className="font-medium text-gray-900">{device.device_name}</h4>
                      <p className="text-sm text-gray-600">{device.device_id}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {device.current_location && (
                      <button
                        onClick={() => {
                          setSelectedDevice(device);
                          fetchLocationHistory(device.device_id);
                        }}
                        className="text-blue-600 hover:text-blue-800 text-sm"
                      >
                        <History className="h-4 w-4" />
                      </button>
                    )}
                    <button
                      onClick={() => updateDeviceLocation(device.device_id)}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm"
                    >
                      Mettre à jour
                    </button>
                  </div>
                </div>
                {device.current_location && (
                  <div className="mt-3 text-sm text-gray-600">
                    <p>Lat: {device.current_location.coordinates.latitude.toFixed(6)}</p>
                    <p>Lon: {device.current_location.coordinates.longitude.toFixed(6)}</p>
                    <p>Adresse: {device.current_location.address}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'geofences' && (
        <div className="bg-white rounded-lg shadow-md">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold">Zones Géographiques</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {geofences.map((geofence) => (
              <div key={geofence.id} className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">{geofence.name}</h4>
                    <p className="text-sm text-gray-600">{geofence.description}</p>
                    <p className="text-sm text-gray-500 mt-1">
                      Type: {geofence.zone_type} - 
                      {geofence.zone_type === 'circle' && ` Rayon: ${geofence.radius}m`}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs rounded ${
                      geofence.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {geofence.is_active ? 'Actif' : 'Inactif'}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'alerts' && (
        <div className="bg-white rounded-lg shadow-md">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold">Alertes de Géolocalisation</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {alerts.map((alert) => (
              <div key={alert.id} className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900">{alert.description}</h4>
                    <p className="text-sm text-gray-600">Device: {alert.device_id}</p>
                    <p className="text-sm text-gray-500">
                      {new Date(alert.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs rounded ${
                      alert.alert_type === 'movement_detected' ? 'bg-yellow-100 text-yellow-800' :
                      alert.alert_type === 'zone_entry' ? 'bg-blue-100 text-blue-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {alert.alert_type}
                    </span>
                    {!alert.resolved && (
                      <button
                        onClick={() => resolveAlert(alert.id)}
                        className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm"
                      >
                        Résoudre
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'search' && (
        <div className="bg-white rounded-lg shadow-md">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold">Recherche de Dispositifs Proches</h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <input
                type="number"
                placeholder="Latitude"
                value={nearbySearch.latitude}
                onChange={(e) => setNearbySearch({
                  ...nearbySearch,
                  latitude: parseFloat(e.target.value)
                })}
                className="border border-gray-300 rounded-lg px-3 py-2"
              />
              <input
                type="number"
                placeholder="Longitude"
                value={nearbySearch.longitude}
                onChange={(e) => setNearbySearch({
                  ...nearbySearch,
                  longitude: parseFloat(e.target.value)
                })}
                className="border border-gray-300 rounded-lg px-3 py-2"
              />
              <input
                type="number"
                placeholder="Rayon (km)"
                value={nearbySearch.radius}
                onChange={(e) => setNearbySearch({
                  ...nearbySearch,
                  radius: parseFloat(e.target.value)
                })}
                className="border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
            <button
              onClick={findNearbyDevices}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg mb-4"
            >
              Rechercher
            </button>
            <div className="space-y-3">
              {nearbyDevices.map((item) => (
                <div key={item.device.device_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <h4 className="font-medium">{item.device.device_name}</h4>
                    <p className="text-sm text-gray-600">{item.device.device_id}</p>
                  </div>
                  <div className="text-sm text-gray-500">
                    {item.distance_km.toFixed(2)} km
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Modal de création de géofence */}
      {showCreateGeofence && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Créer une Zone Géographique</h3>
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Nom de la zone"
                value={newGeofence.name}
                onChange={(e) => setNewGeofence({...newGeofence, name: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              />
              <select
                value={newGeofence.type}
                onChange={(e) => setNewGeofence({...newGeofence, type: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              >
                <option value="polygon">Polygone</option>
                <option value="circle">Cercle</option>
                <option value="rectangle">Rectangle</option>
              </select>
              <input
                type="number"
                placeholder="Latitude"
                value={newGeofence.coordinates[0].latitude}
                onChange={(e) => setNewGeofence({
                  ...newGeofence,
                  coordinates: [{ ...newGeofence.coordinates[0], latitude: parseFloat(e.target.value) }]
                })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              />
              <input
                type="number"
                placeholder="Longitude"
                value={newGeofence.coordinates[0].longitude}
                onChange={(e) => setNewGeofence({
                  ...newGeofence,
                  coordinates: [{ ...newGeofence.coordinates[0], longitude: parseFloat(e.target.value) }]
                })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
              />
              {newGeofence.type === 'circle' && (
                <input
                  type="number"
                  placeholder="Rayon (mètres)"
                  value={newGeofence.radius}
                  onChange={(e) => setNewGeofence({...newGeofence, radius: parseInt(e.target.value)})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              )}
              <textarea
                placeholder="Description"
                value={newGeofence.description}
                onChange={(e) => setNewGeofence({...newGeofence, description: e.target.value})}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 h-20"
              />
            </div>
            <div className="flex justify-end space-x-2 mt-6">
              <button
                onClick={() => setShowCreateGeofence(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Annuler
              </button>
              <button
                onClick={createGeofence}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
              >
                Créer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Geolocation;