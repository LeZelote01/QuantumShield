import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Progress } from '../components/ui/progress';
import { 
  Shield, 
  ShieldCheck, 
  AlertTriangle, 
  Eye, 
  Lock, 
  Unlock,
  Settings,
  Users,
  Activity,
  FileText,
  Download,
  Upload,
  QrCode,
  CheckCircle,
  XCircle,
  AlertCircle,
  TrendingUp,
  Database,
  Bug,
  UserCheck
} from 'lucide-react';

const SecurityAdvanced = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [securityDashboard, setSecurityDashboard] = useState({});
  const [mfaStatus, setMfaStatus] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // États pour MFA
  const [mfaSetup, setMfaSetup] = useState(null);
  const [totpCode, setTotpCode] = useState('');
  const [showMfaSetup, setShowMfaSetup] = useState(false);

  // États pour les honeypots
  const [honeypotReport, setHoneypotReport] = useState({});
  const [honeypotForm, setHoneypotForm] = useState({
    honeypot_type: 'fake_login',
    config: {}
  });

  // États pour les sauvegardes
  const [backupReport, setBackupReport] = useState({});
  const [backupForm, setBackupForm] = useState({
    backup_type: 'security_config',
    data: {}
  });

  // États pour la conformité
  const [complianceReport, setComplianceReport] = useState({});
  const [gdprForm, setGdprForm] = useState({
    user_id: ''
  });

  useEffect(() => {
    fetchSecurityData();
  }, []);

  const fetchSecurityData = async () => {
    try {
      setLoading(true);
      
      // Récupérer le dashboard de sécurité
      const dashboardResponse = await fetch('/api/security/dashboard', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (dashboardResponse.ok) {
        const dashboardData = await dashboardResponse.json();
        setSecurityDashboard(dashboardData.dashboard);
      }

      // Récupérer le statut MFA
      const mfaResponse = await fetch('/api/security/mfa/status', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (mfaResponse.ok) {
        const mfaData = await mfaResponse.json();
        setMfaStatus(mfaData.mfa_status);
      }

      // Récupérer le rapport des honeypots
      const honeypotResponse = await fetch('/api/security/honeypots/report', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (honeypotResponse.ok) {
        const honeypotData = await honeypotResponse.json();
        setHoneypotReport(honeypotData.report);
      }

      // Récupérer le rapport des sauvegardes
      const backupResponse = await fetch('/api/security/backup/report', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (backupResponse.ok) {
        const backupData = await backupResponse.json();
        setBackupReport(backupData.report);
      }

      // Récupérer le rapport de conformité
      const complianceResponse = await fetch('/api/security/compliance/report', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (complianceResponse.ok) {
        const complianceData = await complianceResponse.json();
        setComplianceReport(complianceData.compliance_report);
      }

    } catch (err) {
      setError('Erreur lors du chargement des données de sécurité');
      console.error('Erreur:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleMfaSetup = async () => {
    try {
      const response = await fetch('/api/security/mfa/setup-totp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ service_name: 'QuantumShield' })
      });

      if (response.ok) {
        const data = await response.json();
        setMfaSetup(data.setup_data);
        setShowMfaSetup(true);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Erreur lors de la configuration MFA');
      }
    } catch (err) {
      setError('Erreur lors de la configuration MFA');
      console.error('Erreur:', err);
    }
  };

  const handleMfaVerify = async () => {
    try {
      const response = await fetch('/api/security/mfa/verify-totp-setup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ totp_code: totpCode })
      });

      if (response.ok) {
        setShowMfaSetup(false);
        setMfaSetup(null);
        setTotpCode('');
        fetchSecurityData();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Code TOTP invalide');
      }
    } catch (err) {
      setError('Erreur lors de la vérification MFA');
      console.error('Erreur:', err);
    }
  };

  const handleDisableMfa = async () => {
    try {
      const response = await fetch('/api/security/mfa/disable', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ method: 'totp' })
      });

      if (response.ok) {
        fetchSecurityData();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Erreur lors de la désactivation MFA');
      }
    } catch (err) {
      setError('Erreur lors de la désactivation MFA');
      console.error('Erreur:', err);
    }
  };

  const handleCreateHoneypot = async () => {
    try {
      const response = await fetch('/api/security/honeypots/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(honeypotForm)
      });

      if (response.ok) {
        setHoneypotForm({ honeypot_type: 'fake_login', config: {} });
        fetchSecurityData();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Erreur lors de la création du honeypot');
      }
    } catch (err) {
      setError('Erreur lors de la création du honeypot');
      console.error('Erreur:', err);
    }
  };

  const handleCreateBackup = async () => {
    try {
      const response = await fetch('/api/security/backup/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(backupForm)
      });

      if (response.ok) {
        setBackupForm({ backup_type: 'security_config', data: {} });
        fetchSecurityData();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Erreur lors de la création de la sauvegarde');
      }
    } catch (err) {
      setError('Erreur lors de la création de la sauvegarde');
      console.error('Erreur:', err);
    }
  };

  const handleGenerateGdprReport = async () => {
    try {
      const response = await fetch('/api/security/gdpr/report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(gdprForm)
      });

      if (response.ok) {
        const data = await response.json();
        // Télécharger le rapport
        const blob = new Blob([JSON.stringify(data.gdpr_report, null, 2)], {
          type: 'application/json'
        });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `gdpr_report_${gdprForm.user_id}.json`;
        a.click();
        window.URL.revokeObjectURL(url);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Erreur lors de la génération du rapport GDPR');
      }
    } catch (err) {
      setError('Erreur lors de la génération du rapport GDPR');
      console.error('Erreur:', err);
    }
  };

  const getSecurityLevelColor = (level) => {
    switch (level) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'critical': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement des données de sécurité...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Sécurité Avancée</h1>
          <p className="text-gray-600">Gestion complète de la sécurité QuantumShield</p>
        </div>
        <div className="flex items-center space-x-4">
          <Badge className="bg-blue-100 text-blue-800">
            <Shield className="w-4 h-4 mr-1" />
            Score: {securityDashboard.security_score?.toFixed(1) || '0.0'}
          </Badge>
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
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="mfa">MFA</TabsTrigger>
          <TabsTrigger value="honeypots">Honeypots</TabsTrigger>
          <TabsTrigger value="backups">Sauvegardes</TabsTrigger>
          <TabsTrigger value="compliance">Conformité</TabsTrigger>
        </TabsList>

        {/* Dashboard Tab */}
        <TabsContent value="dashboard" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Événements 24h</CardTitle>
                <Activity className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {securityDashboard.overview?.events_last_24h || 0}
                </div>
                <p className="text-xs text-gray-600">Événements de sécurité</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Alertes Actives</CardTitle>
                <AlertTriangle className="h-4 w-4 text-orange-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {securityDashboard.overview?.active_alerts || 0}
                </div>
                <p className="text-xs text-gray-600">Alertes non résolues</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Utilisateurs MFA</CardTitle>
                <UserCheck className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {securityDashboard.overview?.mfa_enabled_users || 0}
                </div>
                <p className="text-xs text-gray-600">
                  / {securityDashboard.overview?.total_users_with_mfa || 0}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Score Sécurité</CardTitle>
                <TrendingUp className="h-4 w-4 text-purple-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {securityDashboard.security_score?.toFixed(1) || '0.0'}
                </div>
                <p className="text-xs text-gray-600">/ 100</p>
              </CardContent>
            </Card>
          </div>

          {/* Alertes actives */}
          <Card>
            <CardHeader>
              <CardTitle>Alertes de Sécurité Actives</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {securityDashboard.active_alerts?.length > 0 ? (
                  securityDashboard.active_alerts.map((alert, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <AlertTriangle className="h-5 w-5 text-red-600" />
                        <div>
                          <p className="font-medium text-red-800">{alert.alert_type}</p>
                          <p className="text-sm text-red-600">
                            Score de risque: {alert.risk_score?.toFixed(2)}
                          </p>
                        </div>
                      </div>
                      <Badge className="bg-red-100 text-red-800">
                        {new Date(alert.created_at).toLocaleDateString()}
                      </Badge>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <ShieldCheck className="h-12 w-12 mx-auto mb-4 text-green-500" />
                    <p>Aucune alerte active</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* MFA Tab */}
        <TabsContent value="mfa" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Authentification Multi-Facteur (MFA)</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">Statut MFA</h3>
                  <p className="text-sm text-gray-600">
                    {mfaStatus.mfa_enabled ? 'Activé' : 'Désactivé'}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  {mfaStatus.mfa_enabled ? (
                    <CheckCircle className="h-8 w-8 text-green-600" />
                  ) : (
                    <XCircle className="h-8 w-8 text-red-600" />
                  )}
                </div>
              </div>

              {mfaStatus.mfa_enabled ? (
                <div className="space-y-4">
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h4 className="font-medium text-green-800">MFA Activé</h4>
                    <p className="text-sm text-green-700">
                      Votre compte est protégé par l'authentification à deux facteurs
                    </p>
                    <div className="mt-2 space-y-1">
                      {mfaStatus.methods?.map((method, index) => (
                        <div key={index} className="flex items-center space-x-2">
                          <Badge className="bg-green-100 text-green-800">
                            {method.method.toUpperCase()}
                          </Badge>
                          <span className="text-sm text-gray-600">
                            Configuré le {new Date(method.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <Button 
                    onClick={handleDisableMfa}
                    variant="outline"
                    className="text-red-600 border-red-200 hover:bg-red-50"
                  >
                    <Unlock className="w-4 h-4 mr-2" />
                    Désactiver MFA
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="bg-yellow-50 p-4 rounded-lg">
                    <h4 className="font-medium text-yellow-800">MFA Désactivé</h4>
                    <p className="text-sm text-yellow-700">
                      Votre compte n'est pas protégé par l'authentification à deux facteurs
                    </p>
                  </div>
                  
                  <Button 
                    onClick={handleMfaSetup}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    <Lock className="w-4 h-4 mr-2" />
                    Configurer MFA
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Honeypots Tab */}
        <TabsContent value="honeypots" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Honeypots et Pièges</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {honeypotReport.active_honeypots || 0}
                  </div>
                  <div className="text-sm text-gray-600">Honeypots Actifs</div>
                </div>
                <div className="text-center p-4 bg-red-50 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">
                    {honeypotReport.total_interactions || 0}
                  </div>
                  <div className="text-sm text-gray-600">Interactions Total</div>
                </div>
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">
                    {honeypotReport.recent_interactions || 0}
                  </div>
                  <div className="text-sm text-gray-600">Interactions 24h</div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-medium">Créer un Honeypot</h4>
                <div className="flex space-x-4">
                  <select
                    value={honeypotForm.honeypot_type}
                    onChange={(e) => setHoneypotForm({...honeypotForm, honeypot_type: e.target.value})}
                    className="flex-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="fake_login">Faux Login</option>
                    <option value="fake_api">Fausse API</option>
                    <option value="fake_admin">Faux Admin</option>
                  </select>
                  <Button onClick={handleCreateHoneypot} className="bg-red-600 hover:bg-red-700">
                    <Bug className="w-4 h-4 mr-2" />
                    Créer
                  </Button>
                </div>
              </div>

              {honeypotReport.honeypots?.length > 0 && (
                <div className="space-y-3">
                  <h4 className="font-medium">Honeypots Configurés</h4>
                  {honeypotReport.honeypots.map((honeypot, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium">{honeypot.type}</p>
                        <p className="text-sm text-gray-600">
                          {honeypot.interactions} interactions
                        </p>
                      </div>
                      <Badge className={honeypot.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                        {honeypot.active ? 'Actif' : 'Inactif'}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Backups Tab */}
        <TabsContent value="backups" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Sauvegardes Sécurisées</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {backupReport.total_backups || 0}
                  </div>
                  <div className="text-sm text-gray-600">Sauvegardes Total</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {(backupReport.total_size || 0) / 1024 / 1024 < 1 ? 
                      `${Math.round((backupReport.total_size || 0) / 1024)} KB` :
                      `${Math.round((backupReport.total_size || 0) / 1024 / 1024)} MB`
                    }
                  </div>
                  <div className="text-sm text-gray-600">Taille Total</div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-medium">Créer une Sauvegarde</h4>
                <div className="flex space-x-4">
                  <select
                    value={backupForm.backup_type}
                    onChange={(e) => setBackupForm({...backupForm, backup_type: e.target.value})}
                    className="flex-1 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="security_config">Configuration Sécurité</option>
                    <option value="user_data">Données Utilisateur</option>
                    <option value="system_logs">Logs Système</option>
                  </select>
                  <Button onClick={handleCreateBackup} className="bg-green-600 hover:bg-green-700">
                    <Database className="w-4 h-4 mr-2" />
                    Créer
                  </Button>
                </div>
              </div>

              {backupReport.recent_backups?.length > 0 && (
                <div className="space-y-3">
                  <h4 className="font-medium">Sauvegardes Récentes</h4>
                  {backupReport.recent_backups.map((backup, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium">{backup.type}</p>
                        <p className="text-sm text-gray-600">
                          {new Date(backup.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <Badge className="bg-blue-100 text-blue-800">
                        {backup.size < 1024 ? `${backup.size} B` :
                         backup.size < 1024 * 1024 ? `${Math.round(backup.size / 1024)} KB` :
                         `${Math.round(backup.size / 1024 / 1024)} MB`}
                      </Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Compliance Tab */}
        <TabsContent value="compliance" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Conformité Réglementaire</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-blue-800">GDPR</h4>
                  <p className="text-sm text-blue-700">
                    Score: {complianceReport.gdpr_compliance?.compliance_score?.toFixed(1) || '0.0'}%
                  </p>
                  <div className="mt-2 space-y-1">
                    <div className="flex justify-between text-sm">
                      <span>Utilisateurs totaux</span>
                      <span>{complianceReport.gdpr_compliance?.total_users || 0}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Consentements</span>
                      <span>{complianceReport.gdpr_compliance?.consents_given || 0}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Suppressions</span>
                      <span>{complianceReport.gdpr_compliance?.data_deletions || 0}</span>
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-green-50 rounded-lg">
                  <h4 className="font-medium text-green-800">CCPA</h4>
                  <p className="text-sm text-green-700">
                    Conformité: {complianceReport.ccpa_compliance?.data_protection_measures ? 'Oui' : 'Non'}
                  </p>
                  <div className="mt-2 space-y-1">
                    <div className="flex justify-between text-sm">
                      <span>Protection données</span>
                      <span>{complianceReport.ccpa_compliance?.data_protection_measures ? '✓' : '✗'}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Droits utilisateurs</span>
                      <span>{complianceReport.ccpa_compliance?.user_rights_implemented ? '✓' : '✗'}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Politique privacy</span>
                      <span>{complianceReport.ccpa_compliance?.privacy_policy_updated ? '✓' : '✗'}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h4 className="font-medium">Génération Rapport GDPR</h4>
                <div className="flex space-x-4">
                  <Input
                    placeholder="ID Utilisateur"
                    value={gdprForm.user_id}
                    onChange={(e) => setGdprForm({...gdprForm, user_id: e.target.value})}
                    className="flex-1"
                  />
                  <Button onClick={handleGenerateGdprReport} className="bg-purple-600 hover:bg-purple-700">
                    <FileText className="w-4 h-4 mr-2" />
                    Générer Rapport
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Modal MFA Setup */}
      {showMfaSetup && mfaSetup && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Configuration MFA</h3>
            
            <div className="space-y-4">
              <div className="text-center">
                <QrCode className="h-8 w-8 mx-auto mb-2 text-blue-600" />
                <p className="text-sm text-gray-600">
                  Scannez ce QR code avec votre application d'authentification
                </p>
              </div>
              
              <div className="flex justify-center">
                <img 
                  src={`data:image/png;base64,${mfaSetup.qr_code}`} 
                  alt="QR Code MFA" 
                  className="border rounded-lg"
                />
              </div>
              
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  Code de vérification
                </label>
                <Input
                  type="text"
                  value={totpCode}
                  onChange={(e) => setTotpCode(e.target.value)}
                  placeholder="Entrez le code à 6 chiffres"
                  maxLength={6}
                />
              </div>
              
              <div className="flex justify-end space-x-2">
                <Button 
                  variant="outline"
                  onClick={() => setShowMfaSetup(false)}
                >
                  Annuler
                </Button>
                <Button 
                  onClick={handleMfaVerify}
                  disabled={totpCode.length !== 6}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  Vérifier
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SecurityAdvanced;