import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  CubeIcon, 
  BanknotesIcon, 
  BuildingOfficeIcon,
  TruckIcon,
  GlobeAmericasIcon,
  SparklesIcon,
  PlusIcon,
  EyeIcon,
  ShoppingCartIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import advancedEconomyService from '../../services/advancedEconomyService';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../contexts/ToastContext';
import Card from '../../components/UI/Card';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';
import Modal from '../../components/UI/Modal';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const AssetTokenization = () => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showBuyModal, setShowBuyModal] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [newAsset, setNewAsset] = useState({
    asset_type: 'real_estate',
    name: '',
    description: '',
    total_value: '',
    total_tokens: '',
    documents: []
  });
  const [buyData, setBuyData] = useState({
    asset_id: '',
    token_count: ''
  });

  const { user } = useAuth();
  const { showSuccess, showError } = useToast();
  const queryClient = useQueryClient();

  // Queries
  const { data: assets, isLoading: assetsLoading } = useQuery(
    'tokenizedAssets',
    () => advancedEconomyService.getTokenizedAssets(),
    {
      onError: () => showError('Erreur lors du chargement des actifs')
    }
  );

  const { data: myOwnerships, isLoading: ownershipsLoading } = useQuery(
    'assetOwnerships',
    () => advancedEconomyService.getAssetOwnerships(user?.id),
    {
      enabled: !!user?.id,
      onError: () => showError('Erreur lors du chargement des propriétés')
    }
  );

  // Mutations
  const tokenizeAssetMutation = useMutation(
    advancedEconomyService.tokenizeAsset,
    {
      onSuccess: (data) => {
        showSuccess('Actif tokenisé avec succès !');
        setShowCreateModal(false);
        setNewAsset({
          asset_type: 'real_estate',
          name: '',
          description: '',
          total_value: '',
          total_tokens: '',
          documents: []
        });
        queryClient.invalidateQueries('tokenizedAssets');
      },
      onError: (error) => {
        showError(`Erreur lors de la tokenisation: ${error.response?.data?.detail || error.message}`);
      }
    }
  );

  const buyTokensMutation = useMutation(
    advancedEconomyService.buyAssetTokens,
    {
      onSuccess: (data) => {
        showSuccess(`Achat réussi ! Vous possédez maintenant ${data.asset_purchase.tokens_purchased} tokens`);
        setShowBuyModal(false);
        setBuyData({ asset_id: '', token_count: '' });
        queryClient.invalidateQueries('tokenizedAssets');
        queryClient.invalidateQueries('assetOwnerships');
      },
      onError: (error) => {
        showError(`Erreur lors de l'achat: ${error.response?.data?.detail || error.message}`);
      }
    }
  );

  const handleTokenizeAsset = () => {
    if (!newAsset.name || !newAsset.total_value || !newAsset.total_tokens) {
      showError('Veuillez remplir tous les champs obligatoires');
      return;
    }

    tokenizeAssetMutation.mutate({
      ...newAsset,
      total_value: parseFloat(newAsset.total_value),
      total_tokens: parseInt(newAsset.total_tokens)
    });
  };

  const handleBuyTokens = () => {
    if (!buyData.asset_id || !buyData.token_count) {
      showError('Veuillez remplir tous les champs');
      return;
    }

    buyTokensMutation.mutate({
      asset_id: buyData.asset_id,
      token_count: parseInt(buyData.token_count)
    });
  };

  const getAssetTypeIcon = (type) => {
    const icons = {
      real_estate: BuildingOfficeIcon,
      equipment: TruckIcon,
      intellectual_property: SparklesIcon,
      renewable_energy: GlobeAmericasIcon,
      carbon_credits: GlobeAmericasIcon,
      commodity: CubeIcon
    };
    return icons[type] || CubeIcon;
  };

  const getAssetTypeLabel = (type) => {
    const labels = {
      real_estate: 'Immobilier',
      equipment: 'Équipement',
      intellectual_property: 'Propriété intellectuelle',
      renewable_energy: 'Énergie renouvelable',
      carbon_credits: 'Crédits carbone',
      commodity: 'Matières premières'
    };
    return labels[type] || type;
  };

  if (assetsLoading) {
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
            Tokenisation d'Actifs
          </h1>
          <p className="text-gray-600 mt-1">
            Transformez vos actifs physiques en tokens numériques
          </p>
        </div>
        <Button 
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 hover:bg-blue-700"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Tokeniser un actif
        </Button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CubeIcon className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Actifs tokenisés</p>
              <p className="text-2xl font-bold text-gray-900">
                {assets?.tokenized_assets?.length || 0}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <BanknotesIcon className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Mes participations</p>
              <p className="text-2xl font-bold text-gray-900">
                {myOwnerships?.ownerships?.length || 0}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CheckCircleIcon className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Valeur totale</p>
              <p className="text-2xl font-bold text-gray-900">
                {assets?.total_value?.toLocaleString() || 0} QS
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <SparklesIcon className="h-8 w-8 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Tokens disponibles</p>
              <p className="text-2xl font-bold text-gray-900">
                {assets?.available_tokens || 0}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Available Assets */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Actifs disponibles
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {assets?.tokenized_assets?.map((asset) => {
            const IconComponent = getAssetTypeIcon(asset.asset_type);
            const availableTokens = asset.total_tokens - asset.tokens_sold;
            const soldPercentage = (asset.tokens_sold / asset.total_tokens) * 100;

            return (
              <Card key={asset.id} className="hover:shadow-lg transition-shadow">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <IconComponent className="h-8 w-8 text-blue-600" />
                      <div className="ml-3">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {asset.name}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {getAssetTypeLabel(asset.asset_type)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedAsset(asset)}
                      >
                        <EyeIcon className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => {
                          setBuyData({ asset_id: asset.id, token_count: '' });
                          setShowBuyModal(true);
                        }}
                        disabled={availableTokens === 0}
                      >
                        <ShoppingCartIcon className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  <p className="text-gray-600 text-sm line-clamp-2">
                    {asset.description}
                  </p>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Prix par token</span>
                      <span className="font-semibold">{asset.token_price} QS</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Tokens disponibles</span>
                      <span className="font-semibold">{availableTokens}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${soldPercentage}%` }}
                      />
                    </div>
                    <div className="text-xs text-gray-500">
                      {soldPercentage.toFixed(1)}% vendu
                    </div>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      </div>

      {/* My Ownerships */}
      {myOwnerships?.ownerships?.length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Mes participations
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {myOwnerships.ownerships.map((ownership) => (
              <Card key={ownership.id}>
                <div className="space-y-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {ownership.asset_name}
                      </h3>
                      <p className="text-sm text-gray-500">
                        {ownership.token_count} tokens
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-500">Valeur actuelle</p>
                      <p className="font-semibold text-green-600">
                        {(ownership.token_count * ownership.current_price).toLocaleString()} QS
                      </p>
                    </div>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Prix d'achat</span>
                    <span>{ownership.purchase_price} QS</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-500">Participation</span>
                    <span className="font-semibold">{ownership.ownership_percentage}%</span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Create Asset Modal */}
      <Modal 
        isOpen={showCreateModal} 
        onClose={() => setShowCreateModal(false)}
        title="Tokeniser un actif"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Type d'actif
            </label>
            <select
              value={newAsset.asset_type}
              onChange={(e) => setNewAsset({...newAsset, asset_type: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
            >
              <option value="real_estate">Immobilier</option>
              <option value="equipment">Équipement</option>
              <option value="intellectual_property">Propriété intellectuelle</option>
              <option value="renewable_energy">Énergie renouvelable</option>
              <option value="carbon_credits">Crédits carbone</option>
              <option value="commodity">Matières premières</option>
            </select>
          </div>

          <Input
            label="Nom de l'actif"
            value={newAsset.name}
            onChange={(e) => setNewAsset({...newAsset, name: e.target.value})}
            placeholder="Nom de votre actif"
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={newAsset.description}
              onChange={(e) => setNewAsset({...newAsset, description: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="Décrivez votre actif..."
            />
          </div>

          <Input
            label="Valeur totale (QS)"
            type="number"
            value={newAsset.total_value}
            onChange={(e) => setNewAsset({...newAsset, total_value: e.target.value})}
            placeholder="100000"
          />

          <Input
            label="Nombre total de tokens"
            type="number"
            value={newAsset.total_tokens}
            onChange={(e) => setNewAsset({...newAsset, total_tokens: e.target.value})}
            placeholder="1000"
          />

          {newAsset.total_value && newAsset.total_tokens && (
            <div className="bg-blue-50 p-3 rounded-md">
              <p className="text-sm text-blue-800">
                Prix par token: {(parseFloat(newAsset.total_value) / parseInt(newAsset.total_tokens)).toFixed(2)} QS
              </p>
            </div>
          )}

          <div className="flex justify-end space-x-3">
            <Button
              variant="outline"
              onClick={() => setShowCreateModal(false)}
            >
              Annuler
            </Button>
            <Button
              onClick={handleTokenizeAsset}
              disabled={tokenizeAssetMutation.isLoading}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {tokenizeAssetMutation.isLoading ? 'Tokenisation...' : 'Tokeniser'}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Buy Tokens Modal */}
      <Modal 
        isOpen={showBuyModal} 
        onClose={() => setShowBuyModal(false)}
        title="Acheter des tokens"
      >
        <div className="space-y-4">
          <Input
            label="Nombre de tokens"
            type="number"
            value={buyData.token_count}
            onChange={(e) => setBuyData({...buyData, token_count: e.target.value})}
            placeholder="10"
          />

          {buyData.token_count && selectedAsset && (
            <div className="bg-green-50 p-3 rounded-md">
              <p className="text-sm text-green-800">
                Coût total: {(parseInt(buyData.token_count) * selectedAsset.token_price).toLocaleString()} QS
              </p>
            </div>
          )}

          <div className="flex justify-end space-x-3">
            <Button
              variant="outline"
              onClick={() => setShowBuyModal(false)}
            >
              Annuler
            </Button>
            <Button
              onClick={handleBuyTokens}
              disabled={buyTokensMutation.isLoading}
              className="bg-green-600 hover:bg-green-700"
            >
              {buyTokensMutation.isLoading ? 'Achat...' : 'Acheter'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default AssetTokenization;