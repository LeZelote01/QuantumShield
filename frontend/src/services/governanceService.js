import api from './api';

class GovernanceService {
  // ===== PROPOSAL MANAGEMENT =====
  
  async createProposal(proposalData) {
    try {
      const response = await api.post('/api/governance/proposals/create', proposalData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getProposals(status = null, limit = 50) {
    try {
      const params = new URLSearchParams();
      if (status) params.append('proposal_status', status);
      params.append('limit', limit.toString());
      
      const response = await api.get(`/api/governance/proposals?${params}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getProposalDetails(proposalId) {
    try {
      const response = await api.get(`/api/governance/proposals/${proposalId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getActiveProposals() {
    try {
      const response = await api.get('/api/governance/active-proposals');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async approveProposal(proposalId) {
    try {
      const response = await api.post('/api/governance/proposals/approve', {
        proposal_id: proposalId
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async finalizeProposal(proposalId) {
    try {
      const response = await api.post(`/api/governance/proposals/${proposalId}/finalize`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // ===== VOTING MANAGEMENT =====
  
  async castVote(proposalId, voteType) {
    try {
      const response = await api.post('/api/governance/votes/cast', {
        proposal_id: proposalId,
        vote_type: voteType
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getVotingHistory() {
    try {
      const response = await api.get('/api/governance/votes/history');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getVotingPower() {
    try {
      const response = await api.get('/api/governance/votes/power');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // ===== STATISTICS AND UTILITIES =====
  
  async getGovernanceStats() {
    try {
      const response = await api.get('/api/governance/stats');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getProposalTypes() {
    try {
      const response = await api.get('/api/governance/proposal-types');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getHealthCheck() {
    try {
      const response = await api.get('/api/governance/health');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  // ===== UTILITY METHODS =====
  
  formatProposalType(type) {
    const types = {
      parameter_change: 'Changement de paramètre',
      feature_addition: 'Ajout de fonctionnalité',
      system_upgrade: 'Mise à jour système',
      fund_allocation: 'Allocation de fonds'
    };
    return types[type] || type;
  }

  formatVoteType(type) {
    const types = {
      for: 'Pour',
      against: 'Contre',
      abstain: 'Abstention'
    };
    return types[type] || type;
  }

  formatProposalStatus(status) {
    const statuses = {
      pending: 'En attente',
      active: 'Actif',
      passed: 'Adopté',
      rejected: 'Rejeté',
      executed: 'Exécuté'
    };
    return statuses[status] || status;
  }

  calculateVotingProgress(votesFor, votesAgainst) {
    const total = votesFor + votesAgainst;
    if (total === 0) return { forPercentage: 0, againstPercentage: 0 };
    
    return {
      forPercentage: (votesFor / total) * 100,
      againstPercentage: (votesAgainst / total) * 100
    };
  }

  getDaysRemaining(endDate) {
    const now = new Date();
    const end = new Date(endDate);
    const diffTime = end - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return Math.max(0, diffDays);
  }

  isVotingActive(proposal) {
    return proposal.status === 'active' && new Date() < new Date(proposal.voting_end_date);
  }

  getStatusColor(status) {
    const colors = {
      active: 'bg-blue-100 text-blue-800',
      passed: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      pending: 'bg-yellow-100 text-yellow-800',
      executed: 'bg-purple-100 text-purple-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  }

  getPriorityColor(priority) {
    const colors = {
      high: 'text-red-700 bg-red-50 border-red-200',
      medium: 'text-yellow-700 bg-yellow-50 border-yellow-200',
      low: 'text-green-700 bg-green-50 border-green-200'
    };
    return colors[priority] || 'text-gray-700 bg-gray-50 border-gray-200';
  }
}

export default new GovernanceService();