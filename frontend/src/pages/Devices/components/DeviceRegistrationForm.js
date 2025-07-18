import React, { useState } from 'react';
import { useMutation } from 'react-query';
import deviceService from '../../../services/deviceService';
import { useToast } from '../../../contexts/ToastContext';
import Button from '../../../components/UI/Button';
import Input from '../../../components/UI/Input';

const DeviceRegistrationForm = ({ deviceTypes, onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    device_id: '',
    device_name: '',
    device_type: '',
    location: '',
    capabilities: [],
  });
  const [errors, setErrors] = useState({});
  const { showError } = useToast();

  const registerMutation = useMutation(
    deviceService.registerDevice,
    {
      onSuccess: () => {
        onSuccess();
      },
      onError: (error) => {
        showError(error.response?.data?.detail || 'Erreur lors de l\'enregistrement');
      },
    }
  );

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleCapabilityChange = (e) => {
    const { value, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      capabilities: checked 
        ? [...prev.capabilities, value]
        : prev.capabilities.filter(cap => cap !== value)
    }));
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.device_id.trim()) {
      newErrors.device_id = 'L\'ID du device est requis';
    }

    if (!formData.device_name.trim()) {
      newErrors.device_name = 'Le nom du device est requis';
    }

    if (!formData.device_type) {
      newErrors.device_type = 'Le type de device est requis';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    registerMutation.mutate(formData);
  };

  const selectedDeviceType = deviceTypes.find(type => type.name === formData.device_type);

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Input
          label="ID du device"
          name="device_id"
          value={formData.device_id}
          onChange={handleInputChange}
          error={errors.device_id}
          required
          placeholder="ex: DEVICE001"
        />

        <Input
          label="Nom du device"
          name="device_name"
          value={formData.device_name}
          onChange={handleInputChange}
          error={errors.device_name}
          required
          placeholder="ex: Capteur Bureau"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Type de device *
        </label>
        <select
          name="device_type"
          value={formData.device_type}
          onChange={handleInputChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          required
        >
          <option value="">Sélectionner un type</option>
          {deviceTypes.map((type) => (
            <option key={type.name} value={type.name}>
              {type.name}
            </option>
          ))}
        </select>
        {errors.device_type && (
          <p className="text-red-600 text-sm mt-1">{errors.device_type}</p>
        )}
      </div>

      <Input
        label="Localisation"
        name="location"
        value={formData.location}
        onChange={handleInputChange}
        placeholder="ex: Bureau, Salon, Entrepôt A"
      />

      {selectedDeviceType && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Capacités disponibles
          </label>
          <p className="text-sm text-gray-600 mb-3">
            {selectedDeviceType.description}
          </p>
          <div className="grid grid-cols-2 gap-3">
            {selectedDeviceType.capabilities.map((capability) => (
              <label key={capability} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  value={capability}
                  checked={formData.capabilities.includes(capability)}
                  onChange={handleCapabilityChange}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-700">{capability}</span>
              </label>
            ))}
          </div>
        </div>
      )}

      <div className="flex justify-end space-x-3">
        <Button
          type="button"
          variant="secondary"
          onClick={onCancel}
        >
          Annuler
        </Button>
        <Button
          type="submit"
          loading={registerMutation.isLoading}
        >
          Enregistrer le device
        </Button>
      </div>
    </form>
  );
};

export default DeviceRegistrationForm;