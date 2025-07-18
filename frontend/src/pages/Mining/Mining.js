import React, { useState } from 'react';
import { useQuery, useMutation } from 'react-query';
import { 
  WrenchScrewdriverIcon, 
  CpuChipIcon, 
  TrophyIcon,
  ChartBarIcon,
  PlayIcon,
  PauseIcon
} from '@heroicons/react/24/outline';
import miningService from '../../services/miningService';
import { useToast } from '../../contexts/ToastContext';
import Card from '../../components/UI/Card';
import Button from '../../components/UI/Button';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const Mining = () => {
  const [isMining, setIsMining] = useState(false);
  const [hashRate, setHashRate] = useState(1000);
  const { showSuccess, showError } = useToast();

  // Queries
  const { data: miningStats, isLoading } = useQuery(
    'miningStats', 
    miningService.getMiningStats,
    { refetchInterval: 10000 }
  );

  const { data: miningHistory } = useQuery('miningHistory', miningService.getMiningHistory);
  const { data: poolInfo } = useQuery('poolInfo', miningService.getMiningPoolInfo);
  const { data: rewards } = useQuery('miningRewards', miningService.getMiningRewards);
  const { data: leaderboard } = useQuery('miningLeaderboard', miningService.getMiningLeaderboard);
  const { data: calculator } = useQuery(
    ['miningCalculator', hashRate], 
    () => miningService.getMiningCalculator(hashRate),
    { enabled: hashRate > 0 }
  );

  // Mutations
  const registerMinerMutation = useMutation(miningService.registerMiner, {
    onSuccess: () => showSuccess('Mineur enregistré avec succès !'),
    onError: () => showError('Erreur lors de l\'enregistrement')
  });

  const startMining = async () => {
    try {
      // Enregistrer le mineur s'il n'est pas déjà enregistré
      await registerMinerMutation.mutateAsync({ hardware_specs: { hash_rate: hashRate } });
      setIsMining(true);
      showSuccess('Mining démarré !');
    } catch (error) {
      showError('Erreur lors du démarrage du mining');
    }
  };

  const stopMining = () => {
    setIsMining(false);
    showSuccess('Mining arrêté !');
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
          <h1 className="text-2xl font-bold text-gray-900">Mining QuantumShield</h1>
          <p className="text-gray-600">
            Participez au consensus distribué et gagnez des tokens $QS
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className={`
            px-3 py-1 rounded-full text-sm font-medium
            ${isMining ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}
          `}>
            {isMining ? 'En cours' : 'Arrêté'}
          </div>
          <Button
            onClick={isMining ? stopMining : startMining}
            variant={isMining ? 'danger' : 'primary'}
            className="flex items-center space-x-2"
          >
            {isMining ? (
              <>
                <PauseIcon className="h-4 w-4" />
                <span>Arrêter</span>
              </>
            ) : (
              <>
                <PlayIcon className="h-4 w-4" />
                <span>Démarrer</span>
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Statistiques principales */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-lg">
              <WrenchScrewdriverIcon className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Difficulté</p>
              <p className="text-2xl font-bold text-gray-900">
                {miningStats?.current_difficulty || 0}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <CpuChipIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Hash Rate</p>
              <p className="text-2xl font-bold text-gray-900">
                {miningStats?.estimated_hash_rate || 0} H/s
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <TrophyIcon className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Mineurs actifs</p>
              <p className="text-2xl font-bold text-gray-900">
                {miningStats?.active_miners || 0}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <ChartBarIcon className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Blocs minés</p>
              <p className="text-2xl font-bold text-gray-900">
                {miningStats?.total_blocks_mined || 0}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Contenu principal */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Calculateur de rentabilité */}
        <Card title="Calculateur de rentabilité">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Hash Rate (H/s)
              </label>
              <input
                type="number"
                value={hashRate}
                onChange={(e) => setHashRate(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                min="1"
              />
            </div>

            {calculator && (
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Part du réseau</span>
                  <span className="text-sm font-medium">
                    {calculator.user_network_share?.toFixed(2)}%
                  </span>
                </div>
                
                <div className="border-t pt-3">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Gains estimés</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Quotidien</span>
                      <span className="text-sm font-medium text-green-600">
                        {calculator.estimated_earnings?.daily?.toFixed(2)} QS
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Hebdomadaire</span>
                      <span className="text-sm font-medium text-green-600">
                        {calculator.estimated_earnings?.weekly?.toFixed(2)} QS
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Mensuel</span>
                      <span className="text-sm font-medium text-green-600">
                        {calculator.estimated_earnings?.monthly?.toFixed(2)} QS
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Informations du pool */}
        <Card title="Informations du pool">
          <div className="space-y-4">
            <div className="bg-gradient-to-r from-indigo-500 to-purple-600 p-4 rounded-lg text-white">
              <h3 className="font-semibold mb-2">QuantumShield Mining Pool</h3>
              <p className="text-sm opacity-90">Pool de mining distribué</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Frais du pool</p>
                <p className="text-lg font-semibold text-green-600">0%</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Paiement minimum</p>
                <p className="text-lg font-semibold">0.1 QS</p>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Total mineurs</span>
                <span className="text-sm font-medium">{poolInfo?.total_miners || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Taux de succès</span>
                <span className="text-sm font-medium">{poolInfo?.success_rate?.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Blocs trouvés</span>
                <span className="text-sm font-medium">{poolInfo?.blocks_found || 0}</span>
              </div>
            </div>
          </div>
        </Card>

        {/* Historique de mining */}
        <Card title="Mon historique">
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-blue-50 p-3 rounded-lg">
                <p className="text-sm text-blue-600">Blocs minés</p>
                <p className="text-xl font-bold text-blue-900">
                  {miningHistory?.stats?.blocks_mined || 0}
                </p>
              </div>
              <div className="bg-green-50 p-3 rounded-lg">
                <p className="text-sm text-green-600">Récompenses</p>
                <p className="text-xl font-bold text-green-900">
                  {miningHistory?.stats?.total_rewards?.toFixed(1) || 0} QS
                </p>
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-900">Tâches récentes</h4>
              {miningHistory?.stats?.recent_tasks?.slice(0, 5).map((task, index) => (
                <div key={task.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <div>
                    <p className="text-sm font-medium">Tâche #{task.id.slice(-6)}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(task.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <div className={`
                    px-2 py-1 rounded text-xs font-medium
                    ${task.completed ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}
                  `}>
                    {task.completed ? 'Complété' : 'En cours'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>

        {/* Classement des mineurs */}
        <Card title="Classement des mineurs">
          <div className="space-y-3">
            {leaderboard?.leaderboard?.slice(0, 10).map((miner, index) => (
              <div key={miner.miner_address} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`
                    w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                    ${index < 3 ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800'}
                  `}>
                    {miner.rank}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {miner.miner_address.slice(0, 10)}...
                    </p>
                    <p className="text-xs text-gray-500">
                      {miner.blocks_mined} blocs minés
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">
                    {miner.total_rewards?.toFixed(1)} QS
                  </p>
                  <p className="text-xs text-gray-500">
                    {miner.hash_rate} H/s
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Mining;