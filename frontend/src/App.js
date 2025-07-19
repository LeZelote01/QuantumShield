import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';

// Components
import Layout from './components/Layout/Layout';
import ProtectedRoute from './components/Auth/ProtectedRoute';
import Toast from './components/UI/Toast';

// Pages
import Home from './pages/Home/Home';
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';
import Dashboard from './pages/Dashboard/Dashboard';
import Devices from './pages/Devices/Devices';
import DeviceDetails from './pages/Devices/DeviceDetails';
import Cryptography from './pages/Cryptography/Cryptography';
import AdvancedCryptography from './pages/Cryptography/AdvancedCryptography';
import AdvancedKeyManagement from './pages/Cryptography/AdvancedKeyManagement';
import Blockchain from './pages/Blockchain/Blockchain';
import AdvancedBlockchain from './pages/Blockchain/AdvancedBlockchain';
import Mining from './pages/Mining/Mining';
import Tokens from './pages/Tokens/Tokens';
import Profile from './pages/Profile/Profile';
import Settings from './pages/Settings/Settings';
import Geolocation from './pages/Geolocation';

// Security Pages
import SecurityDashboard from './pages/Security/SecurityDashboard';
import AdvancedSecurity from './pages/Security/AdvancedSecurity';

// New Pages
// import Governance from './pages/Governance';
// import SecurityAdvanced from './pages/SecurityAdvanced';
import APIGateway from './pages/APIGateway';

import './App.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ToastProvider>
          <Router>
            <div className="App">
              <Toast />
              <Routes>
                {/* Public Routes */}
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                
                {/* Protected Routes */}
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <Layout />
                    </ProtectedRoute>
                  }
                >
                  <Route index element={<Dashboard />} />
                  <Route path="devices" element={<Devices />} />
                  <Route path="devices/:deviceId" element={<DeviceDetails />} />
                  <Route path="cryptography" element={<Cryptography />} />
                  <Route path="advanced-cryptography" element={<AdvancedCryptography />} />
                  <Route path="advanced-key-management" element={<AdvancedKeyManagement />} />
                  <Route path="blockchain" element={<Blockchain />} />
                  <Route path="advanced-blockchain" element={<AdvancedBlockchain />} />
                  <Route path="mining" element={<Mining />} />
                  <Route path="tokens" element={<Tokens />} />
                  <Route path="geolocation" element={<Geolocation />} />
                  <Route path="security" element={<SecurityDashboard />} />
                  <Route path="security/advanced" element={<AdvancedSecurity />} />
                  {/* <Route path="security-advanced" element={<SecurityAdvanced />} />
                  <Route path="governance" element={<Governance />} /> */}
                  <Route path="api-gateway" element={<APIGateway />} />
                  <Route path="profile" element={<Profile />} />
                  <Route path="settings" element={<Settings />} />
                </Route>
                
                {/* Catch all - redirect to home */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </div>
          </Router>
        </ToastProvider>
      </AuthProvider>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;