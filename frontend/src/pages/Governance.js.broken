import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Progress } from '../components/ui/progress';
import { 
  Scale, 
  Vote, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Users,
  TrendingUp,
  FileText,
  Plus,
  Eye,
  Calendar,
  DollarSign
} from 'lucide-react';

const Governance = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [proposals, setProposals] = useState([]);
  const [governanceDashboard, setGovernanceDashboard] = useState({});
  const [votingPower, setVotingPower] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // États pour la création de proposition
  const [showCreateProposal, setShowCreateProposal] = useState(false);
  const [proposalForm, setProposalForm] = useState({
    proposal_type: 'general',
    title: '',
    description: '',
    voting_power_required: 0.1,
    execution_delay_hours: 24,
    voting_duration_hours: 168,
    parameters: {}
  });

  const [voteForm, setVoteForm] = useState({
    proposal_id: '',
    vote_option: 'yes',
    voting_power: null
  });

  const [selectedProposal, setSelectedProposal] = useState(null);

  useEffect(() => {
    fetchGovernanceData();
  }, []);

  const fetchGovernanceData = async () => {
    try {
      setLoading(true);
      
      // Récupérer le dashboard de gouvernance
      const dashboardResponse = await fetch('/api/advanced-economy/governance/dashboard', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (dashboardResponse.ok) {
        const dashboardData = await dashboardResponse.json();
        setGovernanceDashboard(dashboardData.dashboard);
      }

      // Récupérer les propositions
      const proposalsResponse = await fetch('/api/advanced-economy/governance/proposals', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (proposalsResponse.ok) {
        const proposalsData = await proposalsResponse.json();
        setProposals(proposalsData.proposals || []);
      }

      // Récupérer le pouvoir de vote de l'utilisateur
      const userResponse = await fetch('/api/auth/profile', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (userResponse.ok) {
        const userData = await userResponse.json();
        const votingPowerResponse = await fetch(`/api/advanced-economy/governance/user/${userData.user.id}/voting-power`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        
        if (votingPowerResponse.ok) {
          const votingPowerData = await votingPowerResponse.json();
          setVotingPower(votingPowerData.voting_power_breakdown);
        }
      }

    } catch (err) {
      setError('Erreur lors du chargement des données de gouvernance');
      console.error('Erreur:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProposal = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/advanced-economy/governance/proposals/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(proposalForm)
      });

      if (response.ok) {
        setShowCreateProposal(false);
        setProposalForm({
          proposal_type: 'general',
          title: '',
          description: '',
          voting_power_required: 0.1,
          execution_delay_hours: 24,
          voting_duration_hours: 168,
          parameters: {}
        });
        fetchGovernanceData();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Erreur lors de la création de la proposition');
      }
    } catch (err) {
      setError('Erreur lors de la création de la proposition');
      console.error('Erreur:', err);
    }
  };

  const handleVote = async (proposalId, voteOption) => {
    try {
      const response = await fetch('/api/advanced-economy/governance/proposals/vote', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          proposal_id: proposalId,
          vote_option: voteOption,
          voting_power: voteForm.voting_power
        })
      });

      if (response.ok) {
        fetchGovernanceData();
        setVoteForm({ proposal_id: '', vote_option: 'yes', voting_power: null });
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Erreur lors du vote');
      }
    } catch (err) {
      setError('Erreur lors du vote');
      console.error('Erreur:', err);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-blue-100 text-blue-800';
      case 'passed': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'executed': return 'bg-purple-100 text-purple-800';
      case 'expired': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <Clock className="w-4 h-4" />;
      case 'passed': return <CheckCircle className="w-4 h-4" />;
      case 'rejected': return <XCircle className="w-4 h-4" />;
      case 'executed': return <CheckCircle className="w-4 h-4" />;
      case 'expired': return <AlertCircle className="w-4 h-4" />;
      default: return <AlertCircle className="w-4 h-4" />;
    }
  };

  const calculateVotingProgress = (proposal) => {
    const totalVotes = proposal.votes_yes + proposal.votes_no + proposal.votes_abstain;
    const yesPercentage = totalVotes > 0 ? (proposal.votes_yes / totalVotes) * 100 : 0;
    const noPercentage = totalVotes > 0 ? (proposal.votes_no / totalVotes) * 100 : 0;
    return { yesPercentage, noPercentage, totalVotes };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement des données de gouvernance...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gouvernance Décentralisée</h1>
          <p className="text-gray-600">Participez aux décisions de l'écosystème QuantumShield</p>
        </div>
        <div className="flex space-x-4">
          <Button 
            onClick={() => setShowCreateProposal(true)}
            className="bg-blue-600 hover:bg-blue-700"
            disabled={!votingPower.total || votingPower.total < 1000}
          >
            <Plus className="w-4 h-4 mr-2" />
            Créer une Proposition
          </Button>
        </div>
      </div>

      {error && (
        <Alert className="bg-red-50 border-red-200">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="proposals">Propositions</TabsTrigger>
          <TabsTrigger value="voting-power">Mon Pouvoir de Vote</TabsTrigger>
        </TabsList>

        {/* Dashboard Tab */}
        <TabsContent value="dashboard" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Propositions Actives</CardTitle>
                <Vote className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {governanceDashboard.governance_stats?.active_proposals || 0}
                </div>
                <p className="text-xs text-gray-600">En cours de vote</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Propositions</CardTitle>
                <FileText className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {governanceDashboard.governance_stats?.total_proposals || 0}
                </div>
                <p className="text-xs text-gray-600">Depuis le début</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Mes Votes</CardTitle>
                <Users className="h-4 w-4 text-purple-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {governanceDashboard.user_stats?.votes_cast || 0}
                </div>
                <p className="text-xs text-gray-600">Votes exprimés</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Pouvoir de Vote</CardTitle>
                <TrendingUp className="h-4 w-4 text-orange-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {votingPower.total?.toFixed(2) || '0.00'}
                </div>
                <p className="text-xs text-gray-600">QS tokens</p>
              </CardContent>
            </Card>
          </div>

          {/* Propositions récentes */}
          <Card>
            <CardHeader>
              <CardTitle>Propositions Récentes</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {proposals.slice(0, 5).map((proposal) => {
                  const { yesPercentage, noPercentage, totalVotes } = calculateVotingProgress(proposal);
                  
                  return (
                    <div key={proposal.id} className="border rounded-lg p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <Badge className={getStatusColor(proposal.status)}>
                            {getStatusIcon(proposal.status)}
                            <span className="ml-1 capitalize">{proposal.status}</span>
                          </Badge>
                          <span className="text-sm text-gray-500 capitalize">{proposal.proposal_type}</span>
                        </div>
                        <div className="text-sm text-gray-500">
                          {totalVotes} votes
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="font-semibold text-gray-900">{proposal.title}</h4>
                        <p className="text-sm text-gray-600 mt-1">{proposal.description}</p>
                      </div>

                      {proposal.status === 'active' && (
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span>Oui: {yesPercentage.toFixed(1)}%</span>
                            <span>Non: {noPercentage.toFixed(1)}%</span>
                          </div>
                          <div className="flex space-x-1">
                            <div className="h-2 bg-green-500 rounded-l" style={{ width: `${yesPercentage}%` }}></div>
                            <div className="h-2 bg-red-500 rounded-r" style={{ width: `${noPercentage}%` }}></div>
                            <div className="h-2 bg-gray-200 rounded-r flex-1"></div>
                          </div>
                          <div className="text-xs text-gray-500">
                            Fin du vote: {new Date(proposal.voting_ends).toLocaleDateString()}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Propositions Tab */}
        <TabsContent value="proposals" className="space-y-6">
          <div className="space-y-4">
            {proposals.map((proposal) => {
              const { yesPercentage, noPercentage, totalVotes } = calculateVotingProgress(proposal);
              
              return (
                <Card key={proposal.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <Badge className={getStatusColor(proposal.status)}>
                          {getStatusIcon(proposal.status)}
                          <span className="ml-1 capitalize">{proposal.status}</span>
                        </Badge>
                        <span className="text-sm text-gray-500 capitalize">{proposal.proposal_type}</span>
                      </div>
                      <div className="text-sm text-gray-500">
                        Par {proposal.proposer.username}
                      </div>
                    </div>
                    <CardTitle className="text-xl">{proposal.title}</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-gray-700">{proposal.description}</p>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">{proposal.votes_yes}</div>
                        <div className="text-sm text-gray-500">Votes Oui</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-red-600">{proposal.votes_no}</div>
                        <div className="text-sm text-gray-500">Votes Non</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-gray-600">{proposal.votes_abstain}</div>
                        <div className="text-sm text-gray-500">Abstentions</div>
                      </div>
                    </div>

                    {proposal.status === 'active' && (
                      <div className="space-y-4">
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span>Oui: {yesPercentage.toFixed(1)}%</span>
                            <span>Non: {noPercentage.toFixed(1)}%</span>
                          </div>
                          <Progress value={yesPercentage} className="h-2" />
                          <div className="text-xs text-gray-500">
                            Fin du vote: {new Date(proposal.voting_ends).toLocaleDateString()}
                          </div>
                        </div>

                        <div className="flex space-x-2">
                          <Button 
                            onClick={() => handleVote(proposal.id, 'yes')}
                            className="bg-green-600 hover:bg-green-700"
                            disabled={!votingPower.total || votingPower.total <= 0}
                          >
                            <CheckCircle className="w-4 h-4 mr-2" />
                            Voter Oui
                          </Button>
                          <Button 
                            onClick={() => handleVote(proposal.id, 'no')}
                            className="bg-red-600 hover:bg-red-700"
                            disabled={!votingPower.total || votingPower.total <= 0}
                          >
                            <XCircle className="w-4 h-4 mr-2" />
                            Voter Non
                          </Button>
                          <Button 
                            onClick={() => handleVote(proposal.id, 'abstain')}
                            variant="outline"
                            disabled={!votingPower.total || votingPower.total <= 0}
                          >
                            <AlertCircle className="w-4 h-4 mr-2" />
                            S'abstenir
                          </Button>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* Voting Power Tab */}
        <TabsContent value="voting-power" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Mon Pouvoir de Vote</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center">
                <div className="text-4xl font-bold text-blue-600 mb-2">
                  {votingPower.total?.toFixed(2) || '0.00'}
                </div>
                <p className="text-gray-600">Total QS tokens</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {votingPower.token_balance?.toFixed(2) || '0.00'}
                  </div>
                  <div className="text-sm text-gray-600">Solde Tokens</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {votingPower.staked_tokens?.toFixed(2) || '0.00'}
                  </div>
                  <div className="text-sm text-gray-600">Tokens Stakés</div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">
                    {votingPower.asset_tokens?.toFixed(2) || '0.00'}
                  </div>
                  <div className="text-sm text-gray-600">Tokens d'Actifs</div>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-2">Droits de Gouvernance</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Peut proposer</span>
                    <span className={votingPower.total >= 1000 ? 'text-green-600' : 'text-red-600'}>
                      {votingPower.total >= 1000 ? '✓' : '✗'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Peut voter</span>
                    <span className={votingPower.total > 0 ? 'text-green-600' : 'text-red-600'}>
                      {votingPower.total > 0 ? '✓' : '✗'}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600">
                    Minimum 1000 QS requis pour créer une proposition
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Modal de création de proposition */}
      {showCreateProposal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">Créer une Proposition</h3>
            
            <form onSubmit={handleCreateProposal} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Type de Proposition
                </label>
                <select
                  value={proposalForm.proposal_type}
                  onChange={(e) => setProposalForm({...proposalForm, proposal_type: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="general">Général</option>
                  <option value="parameter_change">Changement de Paramètres</option>
                  <option value="tokenomics">Tokenomics</option>
                  <option value="governance">Gouvernance</option>
                  <option value="feature_request">Demande de Fonctionnalité</option>
                  <option value="emergency">Urgence</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Titre
                </label>
                <Input
                  value={proposalForm.title}
                  onChange={(e) => setProposalForm({...proposalForm, title: e.target.value})}
                  placeholder="Titre de la proposition"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <Textarea
                  value={proposalForm.description}
                  onChange={(e) => setProposalForm({...proposalForm, description: e.target.value})}
                  placeholder="Décrivez votre proposition en détail..."
                  rows={4}
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Seuil de Vote Requis (%)
                  </label>
                  <Input
                    type="number"
                    value={proposalForm.voting_power_required * 100}
                    onChange={(e) => setProposalForm({...proposalForm, voting_power_required: e.target.value / 100})}
                    min="1"
                    max="100"
                    step="0.1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Durée de Vote (heures)
                  </label>
                  <Input
                    type="number"
                    value={proposalForm.voting_duration_hours}
                    onChange={(e) => setProposalForm({...proposalForm, voting_duration_hours: parseInt(e.target.value)})}
                    min="1"
                    max="720"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-2">
                <Button 
                  type="button"
                  variant="outline"
                  onClick={() => setShowCreateProposal(false)}
                >
                  Annuler
                </Button>
                <Button 
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  Créer la Proposition
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Governance;