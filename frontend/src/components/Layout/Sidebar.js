import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  HomeIcon, 
  CpuChipIcon, 
  CubeIcon, 
  ShieldCheckIcon,
  CurrencyDollarIcon,
  WrenchScrewdriverIcon,
  UserCircleIcon,
  Cog6ToothIcon,
  XMarkIcon,
  KeyIcon,
  LockClosedIcon,
  MapPinIcon,
  ServerIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../../contexts/AuthContext';

const Sidebar = ({ isOpen, onClose }) => {
  const location = useLocation();
  const { user } = useAuth();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'Devices IoT', href: '/devices', icon: CpuChipIcon },
    { name: 'Géolocalisation', href: '/geolocation', icon: MapPinIcon },
    { name: 'Cryptographie', href: '/cryptography', icon: ShieldCheckIcon },
    { name: 'Crypto Avancée', href: '/advanced-cryptography', icon: ShieldCheckIcon },
    { name: 'Gestion Clés', href: '/advanced-key-management', icon: KeyIcon },
    { name: 'Blockchain', href: '/blockchain', icon: CubeIcon },
    { name: 'Mining', href: '/mining', icon: WrenchScrewdriverIcon },
    { name: 'Tokens $QS', href: '/tokens', icon: CurrencyDollarIcon },
    { name: 'Sécurité', href: '/security', icon: LockClosedIcon },
    { name: 'Profil', href: '/profile', icon: UserCircleIcon },
    { name: 'Paramètres', href: '/settings', icon: Cog6ToothIcon },
  ];

  return (
    <>
      {/* Mobile sidebar overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-gradient-to-b from-indigo-800 to-indigo-900 
        transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center">
            <ShieldCheckIcon className="h-8 w-8 text-white" />
            <span className="ml-2 text-xl font-bold text-white">QuantumShield</span>
          </div>
          <button
            onClick={onClose}
            className="lg:hidden text-white hover:text-gray-300"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {/* User info */}
        <div className="px-6 py-4 border-b border-indigo-700">
          <div className="flex items-center">
            <div className="h-10 w-10 bg-indigo-600 rounded-full flex items-center justify-center">
              <span className="text-white font-medium">
                {user?.username?.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="ml-3">
              <p className="text-white font-medium">{user?.username}</p>
              <p className="text-indigo-300 text-sm">{user?.email}</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="px-6 py-4">
          <ul className="space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    onClick={onClose}
                    className={`
                      flex items-center px-3 py-2 rounded-lg text-sm font-medium
                      transition-colors duration-200
                      ${isActive 
                        ? 'bg-indigo-700 text-white' 
                        : 'text-indigo-200 hover:bg-indigo-700 hover:text-white'
                      }
                    `}
                  >
                    <item.icon className="h-5 w-5 mr-3" />
                    {item.name}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-6">
          <div className="bg-indigo-700 rounded-lg p-4">
            <p className="text-indigo-200 text-sm">Version 1.0.0</p>
            <p className="text-indigo-300 text-xs mt-1">
              Cryptographie post-quantique pour l'IoT
            </p>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;