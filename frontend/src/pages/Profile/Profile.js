import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { authService } from '../../services/authService';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../contexts/ToastContext';
import { 
  UserCircleIcon, 
  KeyIcon, 
  ShieldCheckIcon, 
  CurrencyDollarIcon,
  DocumentTextIcon,
  PencilIcon
} from '@heroicons/react/24/outline';

const Profile = () => {
  const { user } = useAuth();
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    company: user?.company || '',
    bio: user?.bio || ''
  });

  // Fetch user profile
  const { data: profile, isLoading } = useQuery(
    ['user-profile'],
    () => authService.getProfile(),
    {
      onError: (error) => {
        showToast('Erreur lors du chargement du profil', 'error');
      }
    }
  );

  // Update profile mutation
  const updateProfileMutation = useMutation(
    (data) => authService.updateProfile(data),
    {
      onSuccess: () => {
        showToast('Profil mis à jour avec succès', 'success');
        setIsEditing(false);
        queryClient.invalidateQueries(['user-profile']);
      },
      onError: () => {
        showToast('Erreur lors de la mise à jour du profil', 'error');
      }
    }
  );

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    updateProfileMutation.mutate(formData);
  };

  const handleCancel = () => {
    setFormData({
      name: user?.name || '',
      email: user?.email || '',
      phone: user?.phone || '',
      company: user?.company || '',
      bio: user?.bio || ''
    });
    setIsEditing(false);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Mon Profil</h1>
        <p className="text-gray-500 mt-1">Gérez vos informations personnelles et paramètres de sécurité</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Profile Information */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-medium text-gray-900">Informations personnelles</h2>
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="inline-flex items-center text-sm text-blue-600 hover:text-blue-700"
              >
                <PencilIcon className="h-4 w-4 mr-1" />
                {isEditing ? 'Annuler' : 'Modifier'}
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nom complet
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Téléphone
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Entreprise
                  </label>
                  <input
                    type="text"
                    name="company"
                    value={formData.company}
                    onChange={handleInputChange}
                    disabled={!isEditing}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Biographie
                </label>
                <textarea
                  name="bio"
                  value={formData.bio}
                  onChange={handleInputChange}
                  disabled={!isEditing}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50"
                />
              </div>

              {isEditing && (
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={handleCancel}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                  >
                    Annuler
                  </button>
                  <button
                    type="submit"
                    disabled={updateProfileMutation.isLoading}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    {updateProfileMutation.isLoading ? 'Sauvegarde...' : 'Sauvegarder'}
                  </button>
                </div>
              )}
            </form>
          </div>

          {/* Security Settings */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Paramètres de sécurité</h2>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <KeyIcon className="h-5 w-5 text-gray-400 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Mot de passe</p>
                    <p className="text-sm text-gray-500">Dernière modification il y a 30 jours</p>
                  </div>
                </div>
                <button className="text-sm text-blue-600 hover:text-blue-700">
                  Changer
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <ShieldCheckIcon className="h-5 w-5 text-green-500 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Authentification à deux facteurs</p>
                    <p className="text-sm text-gray-500">Activée</p>
                  </div>
                </div>
                <button className="text-sm text-blue-600 hover:text-blue-700">
                  Gérer
                </button>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <DocumentTextIcon className="h-5 w-5 text-gray-400 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Clés API</p>
                    <p className="text-sm text-gray-500">2 clés actives</p>
                  </div>
                </div>
                <button className="text-sm text-blue-600 hover:text-blue-700">
                  Gérer
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Avatar */}
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <div className="mx-auto w-24 h-24 bg-gray-300 rounded-full flex items-center justify-center mb-4">
              <UserCircleIcon className="h-16 w-16 text-gray-600" />
            </div>
            <h3 className="text-lg font-medium text-gray-900">{user?.name || 'Utilisateur'}</h3>
            <p className="text-sm text-gray-500">{user?.email}</p>
            <button className="mt-3 text-sm text-blue-600 hover:text-blue-700">
              Changer la photo
            </button>
          </div>

          {/* Wallet Info */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Wallet QuantumShield</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Adresse</span>
                <code className="text-xs bg-gray-100 px-2 py-1 rounded">
                  {user?.wallet_address ? `${user.wallet_address.substring(0, 6)}...${user.wallet_address.substring(-4)}` : 'N/A'}
                </code>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Solde QS</span>
                <div className="flex items-center">
                  <CurrencyDollarIcon className="h-4 w-4 text-yellow-500 mr-1" />
                  <span className="text-sm font-medium">50.00 QS</span>
                </div>
              </div>
            </div>
          </div>

          {/* Account Stats */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Statistiques</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">Devices enregistrés</span>
                <span className="text-sm font-medium">0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">Tokens gagnés</span>
                <span className="text-sm font-medium">50 QS</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-500">Membre depuis</span>
                <span className="text-sm font-medium">
                  {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;