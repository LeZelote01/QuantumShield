import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  ChartBarIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  UserGroupIcon,
  PlusIcon,
  EyeIcon,
  HandRaisedIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../contexts/ToastContext';
import Card from '../../components/UI/Card';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';
import Modal from '../../components/UI/Modal';
import LoadingSpinner from '../../components/UI/LoadingSpinner';

const Governance = () => {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showVoteModal, setShowVoteModal] = useState(false);
  const [selectedProposal, setSelectedProposal] = useState(null);
  const [newProposal, setNewProposal] = useState({
    title: '',
    description: '',
    proposal_type: 'parameter_change',
    voting_period_days: 7,
    required_quorum: 0.1,
    parameters: {}
  });

  const { user } = useAuth();
  const { showSuccess, showError } = useToast();
  const queryClient = useQueryClient();

  // Mock data for governance (since backend implementation is needed)
  const mockProposals = [
    {
      id: '1',
      title: 'Réduction des frais de marketplace',
      description: 'Proposition de réduire les frais de marketplace de 2.5% à 2.0% pour stimuler l\'adoption',
      proposal_type: 'parameter_change',
      status: 'active',
      proposer: 'user123',
      created_at: '2025-01-15T10:00:00Z',
      voting_end_date: '2025-01-22T10:00:00Z',
      votes_for: 15000,
      votes_against: 5000,
      total_votes: 20000,
      required_quorum: 0.1,
      current_quorum: 0.15,
      parameters: {
        marketplace_fee: {
          current: 0.025,
          proposed: 0.020
        }
      }
    },
    {
      id: '2',
      title: 'Nouveau pool de staking pour validators',
      description: 'Création d\'un pool de staking spécialisé pour les validateurs avec 35% APY',
      proposal_type: 'feature_addition',
      status: 'passed',
      proposer: 'user456',
      created_at: '2025-01-10T14:30:00Z',
      voting_end_date: '2025-01-17T14:30:00Z',
      votes_for: 25000,
      votes_against: 8000,
      total_votes: 33000,
      required_quorum: 0.1,
      current_quorum: 0.22,
      parameters: {
        validator_pool_apy: {
          current: 0.30,
          proposed: 0.35
        }
      }
    },
    {
      id: '3',
      title: 'Mise à jour du système de gouvernance',
      description: 'Amélioration du système de vote avec délégation et vote pondéré',
      proposal_type: 'system_upgrade',
      status: 'rejected',
      proposer: 'user789',
      created_at: '2025-01-05T09:15:00Z',
      voting_end_date: '2025-01-12T09:15:00Z',
      votes_for: 8000,
      votes_against: 22000,
      total_votes: 30000,
      required_quorum: 0.1,
      current_quorum: 0.18,
      parameters: {}
    }
  ];

  const mockGovernanceStats = {
    total_proposals: 15,
    active_proposals: 3,
    passed_proposals: 8,
    rejected_proposals: 4,
    total_voters: 450,
    total_voting_power: 150000,
    user_voting_power: 1250
  };

  const getStatusColor = (status) => {
    const colors = {
      active: 'bg-blue-100 text-blue-800',
      passed: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      pending: 'bg-yellow-100 text-yellow-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getStatusIcon = (status) => {
    const icons = {
      active: ClockIcon,
      passed: CheckCircleIcon,
      rejected: XCircleIcon,
      pending: ClockIcon
    };
    const IconComponent = icons[status] || ClockIcon;
    return <IconComponent className="h-5 w-5" />;
  };

  const getProposalTypeLabel = (type) => {
    const labels = {
      parameter_change: 'Changement de paramètre',
      feature_addition: 'Ajout de fonctionnalité',
      system_upgrade: 'Mise à jour système',
      fund_allocation: 'Allocation de fonds'
    };
    return labels[type] || type;
  };

  const calculateVotingProgress = (votesFor, votesAgainst) => {
    const total = votesFor + votesAgainst;
    if (total === 0) return { forPercentage: 0, againstPercentage: 0 };
    
    return {
      forPercentage: (votesFor / total) * 100,
      againstPercentage: (votesAgainst / total) * 100
    };
  };

  const handleCreateProposal = () => {
    if (!newProposal.title || !newProposal.description) {
      showError('Veuillez remplir tous les champs obligatoires');
      return;
    }

    // Mock success
    showSuccess('Proposition créée avec succès !');
    setShowCreateModal(false);
    setNewProposal({
      title: '',
      description: '',
      proposal_type: 'parameter_change',
      voting_period_days: 7,
      required_quorum: 0.1,
      parameters: {}
    });
  };

  const handleVote = (proposalId, voteType) => {
    // Mock voting
    showSuccess(`Vote "${voteType}" enregistré avec succès !`);
    setShowVoteModal(false);
    setSelectedProposal(null);
  };

  const isVotingActive = (proposal) => {
    return proposal.status === 'active' && new Date() < new Date(proposal.voting_end_date);
  };

  const getDaysRemaining = (endDate) => {
    const now = new Date();
    const end = new Date(endDate);
    const diffTime = end - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return Math.max(0, diffDays);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Gouvernance Décentralisée
          </h1>
          <p className="text-gray-600 mt-1">
            Participez aux décisions de la communauté QuantumShield
          </p>
        </div>
        <Button 
          onClick={() => setShowCreateModal(true)}
          className="bg-indigo-600 hover:bg-indigo-700"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Nouvelle proposition
        </Button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <DocumentTextIcon className="h-8 w-8 text-indigo-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Propositions actives</p>
              <p className="text-2xl font-bold text-gray-900">
                {mockGovernanceStats.active_proposals}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CheckCircleIcon className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Propositions adoptées</p>
              <p className="text-2xl font-bold text-gray-900">
                {mockGovernanceStats.passed_proposals}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <UserGroupIcon className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Votants actifs</p>
              <p className="text-2xl font-bold text-gray-900">
                {mockGovernanceStats.total_voters}
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <HandRaisedIcon className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Votre pouvoir de vote</p>
              <p className="text-2xl font-bold text-gray-900">
                {mockGovernanceStats.user_voting_power.toLocaleString()}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Active Proposals */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Propositions actives
        </h2>
        <div className="space-y-4">
          {mockProposals.filter(p => p.status === 'active').map((proposal) => {
            const votingProgress = calculateVotingProgress(proposal.votes_for, proposal.votes_against);
            const daysRemaining = getDaysRemaining(proposal.voting_end_date);
            
            return (
              <Card key={proposal.id} className="border-l-4 border-blue-500">
                <div className="space-y-4">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {proposal.title}
                        </h3>
                        <span className={`px-2 py-1 text-xs rounded-full font-medium ${getStatusColor(proposal.status)}`}>
                          {getStatusIcon(proposal.status)}
                          <span className="ml-1">{proposal.status}</span>
                        </span>
                        <span className="text-sm text-gray-500">
                          {getProposalTypeLabel(proposal.proposal_type)}
                        </span>
                      </div>
                      <p className="text-gray-600 mb-3">
                        {proposal.description}
                      </p>
                      
                      {/* Voting Progress */}
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">
                            Pour: {proposal.votes_for.toLocaleString()} QS ({votingProgress.forPercentage.toFixed(1)}%)
                          </span>
                          <span className="text-gray-600">
                            Contre: {proposal.votes_against.toLocaleString()} QS ({votingProgress.againstPercentage.toFixed(1)}%)
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-green-500 h-2 rounded-l-full"
                            style={{ width: `${votingProgress.forPercentage}%` }}
                          />
                        </div>
                        <div className="flex justify-between text-sm text-gray-500">
                          <span>Quorum: {(proposal.current_quorum * 100).toFixed(1)}% (requis: {(proposal.required_quorum * 100).toFixed(1)}%)</span>
                          <span>{daysRemaining} jour(s) restant(s)</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex space-x-2 ml-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedProposal(proposal)}
                      >
                        <EyeIcon className="h-4 w-4" />
                      </Button>
                      {isVotingActive(proposal) && (
                        <Button
                          size="sm"
                          onClick={() => {
                            setSelectedProposal(proposal);
                            setShowVoteModal(true);
                          }}
                          className="bg-indigo-600 hover:bg-indigo-700"
                        >
                          <HandRaisedIcon className="h-4 w-4 mr-1" />
                          Voter
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Recent Proposals */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Propositions récentes
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {mockProposals.filter(p => p.status !== 'active').map((proposal) => {
            const votingProgress = calculateVotingProgress(proposal.votes_for, proposal.votes_against);
            
            return (
              <Card key={proposal.id} className="hover:shadow-lg transition-shadow">
                <div className="space-y-3">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h3 className="font-semibold text-gray-900">
                          {proposal.title}
                        </h3>
                        <span className={`px-2 py-1 text-xs rounded-full font-medium ${getStatusColor(proposal.status)}`}>
                          {getStatusIcon(proposal.status)}
                          <span className="ml-1">{proposal.status}</span>
                        </span>
                      </div>
                      <p className="text-gray-600 text-sm mb-2">
                        {proposal.description}
                      </p>
                      
                      <div className="flex justify-between text-sm text-gray-500">
                        <span>Pour: {votingProgress.forPercentage.toFixed(1)}%</span>
                        <span>Contre: {votingProgress.againstPercentage.toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-1">
                        <div 
                          className={`h-1 rounded-l-full ${
                            proposal.status === 'passed' ? 'bg-green-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${votingProgress.forPercentage}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Create Proposal Modal */}
      <Modal 
        isOpen={showCreateModal} 
        onClose={() => setShowCreateModal(false)}
        title="Créer une nouvelle proposition"
      >
        <div className="space-y-4">
          <Input
            label="Titre de la proposition"
            value={newProposal.title}
            onChange={(e) => setNewProposal({...newProposal, title: e.target.value})}
            placeholder="Ex: Réduction des frais de marketplace"
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Type de proposition
            </label>
            <select
              value={newProposal.proposal_type}
              onChange={(e) => setNewProposal({...newProposal, proposal_type: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
            >
              <option value="parameter_change">Changement de paramètre</option>
              <option value="feature_addition">Ajout de fonctionnalité</option>
              <option value="system_upgrade">Mise à jour système</option>
              <option value="fund_allocation">Allocation de fonds</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description détaillée
            </label>
            <textarea
              value={newProposal.description}
              onChange={(e) => setNewProposal({...newProposal, description: e.target.value})}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500"
              rows={4}
              placeholder="Décrivez en détail votre proposition..."
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Durée de vote (jours)"
              type="number"
              value={newProposal.voting_period_days}
              onChange={(e) => setNewProposal({...newProposal, voting_period_days: parseInt(e.target.value)})}
              min="1"
              max="30"
            />

            <Input
              label="Quorum requis (%)"
              type="number"
              value={newProposal.required_quorum * 100}
              onChange={(e) => setNewProposal({...newProposal, required_quorum: parseFloat(e.target.value) / 100})}
              min="5"
              max="50"
              step="0.1"
            />
          </div>

          <div className="bg-blue-50 p-3 rounded-md">
            <p className="text-sm text-blue-800">
              <strong>Note:</strong> Une fois créée, la proposition sera soumise à examen par la communauté avant d'être mise au vote.
            </p>
          </div>

          <div className="flex justify-end space-x-3">
            <Button
              variant="outline"
              onClick={() => setShowCreateModal(false)}
            >
              Annuler
            </Button>
            <Button
              onClick={handleCreateProposal}
              className="bg-indigo-600 hover:bg-indigo-700"
            >
              Créer la proposition
            </Button>
          </div>
        </div>
      </Modal>

      {/* Vote Modal */}
      <Modal 
        isOpen={showVoteModal} 
        onClose={() => setShowVoteModal(false)}
        title="Voter sur la proposition"
      >
        {selectedProposal && (
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                {selectedProposal.title}
              </h3>
              <p className="text-gray-600 mt-2">
                {selectedProposal.description}
              </p>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-700">
                <strong>Votre pouvoir de vote:</strong> {mockGovernanceStats.user_voting_power.toLocaleString()} QS
              </p>
              <p className="text-sm text-gray-700">
                <strong>Temps restant:</strong> {getDaysRemaining(selectedProposal.voting_end_date)} jour(s)
              </p>
            </div>

            <div className="flex justify-end space-x-3">
              <Button
                variant="outline"
                onClick={() => setShowVoteModal(false)}
              >
                Annuler
              </Button>
              <Button
                onClick={() => handleVote(selectedProposal.id, 'against')}
                className="bg-red-600 hover:bg-red-700"
              >
                <XCircleIcon className="h-4 w-4 mr-1" />
                Voter Contre
              </Button>
              <Button
                onClick={() => handleVote(selectedProposal.id, 'for')}
                className="bg-green-600 hover:bg-green-700"
              >
                <CheckCircleIcon className="h-4 w-4 mr-1" />
                Voter Pour
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Governance;