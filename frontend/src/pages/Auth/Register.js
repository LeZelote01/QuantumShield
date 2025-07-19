import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShieldCheckIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../contexts/ToastContext';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const { register, isAuthenticated, error, clearError } = useAuth();
  const { showError, showSuccess } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    if (error) {
      showError(error);
      clearError();
    }
  }, [error, showError, clearError]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.username.trim()) {
      newErrors.username = 'Le nom d\'utilisateur est requis';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Le nom d\'utilisateur doit contenir au moins 3 caractères';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'L\'email est requis';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'L\'email n\'est pas valide';
    }

    if (!formData.password) {
      newErrors.password = 'Le mot de passe est requis';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Le mot de passe doit contenir au moins 6 caractères';
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'La confirmation du mot de passe est requise';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Les mots de passe ne correspondent pas';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setLoading(true);
    
    try {
      const result = await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
      });
      
      if (result.success) {
        showSuccess('Inscription réussie ! Bienvenue sur QuantumShield');
        navigate('/dashboard');
      } else {
        showError(result.error || 'Erreur lors de l\'inscription');
      }
    } catch (error) {
      showError('Erreur lors de l\'inscription');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="bg-white rounded-xl shadow-2xl p-8">
          {/* Logo et titre */}
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              <ShieldCheckIcon className="h-12 w-12 text-indigo-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900">Créer un compte</h2>
            <p className="text-gray-600 mt-2">Rejoignez l'écosystème QuantumShield</p>
          </div>

          {/* Formulaire d'inscription */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <Input
              label="Nom d'utilisateur"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              error={errors.username}
              required
              autoComplete="username"
            />

            <Input
              label="Adresse email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleInputChange}
              error={errors.email}
              required
              autoComplete="email"
            />

            <Input
              label="Mot de passe"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleInputChange}
              error={errors.password}
              required
              autoComplete="new-password"
            />

            <Input
              label="Confirmer le mot de passe"
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              error={errors.confirmPassword}
              required
              autoComplete="new-password"
            />

            <Button
              type="submit"
              variant="primary"
              size="large"
              loading={loading}
              className="w-full"
            >
              S'inscrire
            </Button>
          </form>

          {/* Lien de connexion */}
          <div className="text-center mt-6">
            <p className="text-gray-600">
              Déjà un compte ?{' '}
              <Link 
                to="/login" 
                className="text-indigo-600 hover:text-indigo-500 font-medium"
              >
                Se connecter
              </Link>
            </p>
          </div>

          {/* Avantages */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Avantages de l'inscription
            </h3>
            <div className="grid grid-cols-1 gap-3">
              <div className="flex items-center text-sm text-gray-600">
                <ShieldCheckIcon className="h-4 w-4 text-green-500 mr-2" />
                Wallet $QS gratuit
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <ShieldCheckIcon className="h-4 w-4 text-green-500 mr-2" />
                Récompenses pour participation
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <ShieldCheckIcon className="h-4 w-4 text-green-500 mr-2" />
                Enregistrement devices IoT
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <ShieldCheckIcon className="h-4 w-4 text-green-500 mr-2" />
                Accès mining distribué
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;