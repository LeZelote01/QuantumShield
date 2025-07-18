import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../contexts/ToastContext';
import { 
  CogIcon, 
  BellIcon, 
  ShieldCheckIcon, 
  MoonIcon, 
  GlobeAltIcon,
  KeyIcon,
  TrashIcon
} from '@heroicons/react/24/outline';

const Settings = () => {
  const { user } = useAuth();
  const { showToast } = useToast();
  
  const [settings, setSettings] = useState({
    notifications: {
      email: true,
      push: true,
      mining: true,
      devices: true,
      security: true
    },
    privacy: {
      publicProfile: false,
      shareAnalytics: true,
      allowTracking: false
    },
    appearance: {
      theme: 'light',
      language: 'fr'
    },
    security: {
      twoFactor: true,
      sessionTimeout: 30,
      autoLogout: true
    }
  });

  const handleSettingChange = (category, setting, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [setting]: value
      }
    }));
    showToast('Paramètre mis à jour', 'success');
  };

  const handleExportData = () => {
    showToast('Export des données en cours...', 'info');
    // Simulate export
    setTimeout(() => {
      showToast('Données exportées avec succès', 'success');
    }, 2000);
  };

  const handleDeleteAccount = () => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer votre compte ? Cette action est irréversible.')) {
      showToast('Suppression du compte en cours...', 'error');
      // Simulate account deletion
      setTimeout(() => {
        showToast('Compte supprimé avec succès', 'success');
      }, 2000);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Paramètres</h1>
        <p className="text-gray-500 mt-1">Gérez vos préférences et paramètres de compte</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar Navigation */}
        <div className="lg:col-span-1">
          <nav className="space-y-1">
            <a href="#notifications" className="bg-gray-100 text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
              <BellIcon className="text-gray-500 mr-3 h-5 w-5" />
              Notifications
            </a>
            <a href="#privacy" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
              <ShieldCheckIcon className="text-gray-400 group-hover:text-gray-500 mr-3 h-5 w-5" />
              Confidentialité
            </a>
            <a href="#appearance" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
              <MoonIcon className="text-gray-400 group-hover:text-gray-500 mr-3 h-5 w-5" />
              Apparence
            </a>
            <a href="#security" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
              <KeyIcon className="text-gray-400 group-hover:text-gray-500 mr-3 h-5 w-5" />
              Sécurité
            </a>
          </nav>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3 space-y-6">
          {/* Notifications */}
          <div id="notifications" className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <BellIcon className="h-5 w-5 mr-2" />
              Notifications
            </h2>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">Notifications email</p>
                  <p className="text-sm text-gray-500">Recevoir des notifications par email</p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.notifications.email}
                  onChange={(e) => handleSettingChange('notifications', 'email', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">Notifications push</p>
                  <p className="text-sm text-gray-500">Recevoir des notifications push</p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.notifications.push}
                  onChange={(e) => handleSettingChange('notifications', 'push', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">Notifications mining</p>
                  <p className="text-sm text-gray-500">Alertes sur les activités de mining</p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.notifications.mining}
                  onChange={(e) => handleSettingChange('notifications', 'mining', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">Notifications devices</p>
                  <p className="text-sm text-gray-500">Alertes sur les dispositifs IoT</p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.notifications.devices}
                  onChange={(e) => handleSettingChange('notifications', 'devices', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">Notifications sécurité</p>
                  <p className="text-sm text-gray-500">Alertes de sécurité importantes</p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.notifications.security}
                  onChange={(e) => handleSettingChange('notifications', 'security', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
              </div>
            </div>
          </div>

          {/* Privacy */}
          <div id="privacy" className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <ShieldCheckIcon className="h-5 w-5 mr-2" />
              Confidentialité
            </h2>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">Profil public</p>
                  <p className="text-sm text-gray-500">Permettre aux autres utilisateurs de voir votre profil</p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.privacy.publicProfile}
                  onChange={(e) => handleSettingChange('privacy', 'publicProfile', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">Partage d'analytics</p>
                  <p className="text-sm text-gray-500">Aider à améliorer QuantumShield</p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.privacy.shareAnalytics}
                  onChange={(e) => handleSettingChange('privacy', 'shareAnalytics', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">Autoriser le tracking</p>
                  <p className="text-sm text-gray-500">Permettre le suivi pour la publicité</p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.privacy.allowTracking}
                  onChange={(e) => handleSettingChange('privacy', 'allowTracking', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
              </div>
            </div>
          </div>

          {/* Appearance */}
          <div id="appearance" className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <MoonIcon className="h-5 w-5 mr-2" />
              Apparence
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Thème
                </label>
                <select
                  value={settings.appearance.theme}
                  onChange={(e) => handleSettingChange('appearance', 'theme', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="light">Clair</option>
                  <option value="dark">Sombre</option>
                  <option value="auto">Automatique</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Langue
                </label>
                <select
                  value={settings.appearance.language}
                  onChange={(e) => handleSettingChange('appearance', 'language', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="fr">Français</option>
                  <option value="en">English</option>
                  <option value="es">Español</option>
                </select>
              </div>
            </div>
          </div>

          {/* Security */}
          <div id="security" className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <KeyIcon className="h-5 w-5 mr-2" />
              Sécurité
            </h2>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">Authentification à deux facteurs</p>
                  <p className="text-sm text-gray-500">Sécurité supplémentaire pour votre compte</p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.security.twoFactor}
                  onChange={(e) => handleSettingChange('security', 'twoFactor', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Timeout de session (minutes)
                </label>
                <input
                  type="number"
                  value={settings.security.sessionTimeout}
                  onChange={(e) => handleSettingChange('security', 'sessionTimeout', parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  min="5"
                  max="120"
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">Déconnexion automatique</p>
                  <p className="text-sm text-gray-500">Se déconnecter après inactivité</p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.security.autoLogout}
                  onChange={(e) => handleSettingChange('security', 'autoLogout', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
              </div>
            </div>
          </div>

          {/* Data Management */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Gestion des données</h2>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">Exporter mes données</p>
                  <p className="text-sm text-gray-500">Télécharger toutes vos données</p>
                </div>
                <button
                  onClick={handleExportData}
                  className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100"
                >
                  Exporter
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">Supprimer mon compte</p>
                  <p className="text-sm text-gray-500">Supprimer définitivement votre compte</p>
                </div>
                <button
                  onClick={handleDeleteAccount}
                  className="px-4 py-2 text-sm font-medium text-red-600 bg-red-50 rounded-md hover:bg-red-100 flex items-center"
                >
                  <TrashIcon className="h-4 w-4 mr-1" />
                  Supprimer
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;