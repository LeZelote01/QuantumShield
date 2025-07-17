import api from './api';

class DeviceService {
  async getDevices() {
    try {
      const response = await api.get('/api/devices/');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getDevice(deviceId) {
    try {
      const response = await api.get(`/api/devices/${deviceId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getDeviceById(deviceId) {
    return this.getDevice(deviceId);
  }

  async registerDevice(deviceData) {
    try {
      const response = await api.post('/api/devices/register', deviceData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async updateDevice(deviceId, updateData) {
    try {
      const response = await api.put(`/api/devices/${deviceId}`, updateData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async sendHeartbeat(heartbeatData) {
    try {
      const response = await api.post('/api/devices/heartbeat', heartbeatData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getDeviceMetrics(deviceId) {
    try {
      const response = await api.get(`/api/devices/${deviceId}/metrics`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getDeviceAnomalies(deviceId, limit = 50) {
    try {
      const response = await api.get(`/api/devices/${deviceId}/anomalies?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async updateFirmware(deviceId, firmwareData) {
    try {
      const response = await api.post(`/api/devices/${deviceId}/firmware-update`, firmwareData);
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getOfflineDevices() {
    try {
      const response = await api.get('/api/devices/offline/list');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getDevicesOverview() {
    try {
      const response = await api.get('/api/devices/stats/overview');
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  async getAvailableDeviceTypes() {
    try {
      const response = await api.get('/api/devices/types/available');
      return response.data;
    } catch (error) {
      throw error;
    }
  }
}

export default new DeviceService();