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
  ServerIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../contexts/ToastContext';

const Sidebar = ({ isOpen, onClose }) => {
  const location = useLocation();
  const { user, logout } = useAuth();
  const { showSuccess } = useToast();

  const handleLogout = async () => {
    await logout();
    showSuccess('Déconnecté avec succès');
    onClose();
  };

  const navigationSections = [
    {
      title: 'Principal',
      items: [
        { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
        { name: 'Devices IoT', href: '/dashboard/devices', icon: CpuChipIcon },
        { name: 'Géolocalisation', href: '/dashboard/geolocation', icon: MapPinIcon },
      ]
    },
    {
      title: 'Sécurité',
      items: [
        { name: 'Cryptographie', href: '/dashboard/cryptography', icon: ShieldCheckIcon },
        { name: 'Crypto Avancée', href: '/dashboard/advanced-cryptography', icon: ShieldCheckIcon },
        { name: 'Gestion Clés', href: '/dashboard/advanced-key-management', icon: KeyIcon },
        { name: 'Sécurité', href: '/dashboard/security', icon: LockClosedIcon },
      ]
    },
    {
      title: 'Blockchain & Économie',
      items: [
        { name: 'Blockchain', href: '/dashboard/blockchain', icon: CubeIcon },
        { name: 'Mining', href: '/dashboard/mining', icon: WrenchScrewdriverIcon },
        { name: 'Tokens $QS', href: '/dashboard/tokens', icon: CurrencyDollarIcon },
      ]
    },
    {
      title: 'Système',
      items: [
        { name: 'API Gateway', href: '/dashboard/api-gateway', icon: ServerIcon },
        { name: 'Profil', href: '/dashboard/profile', icon: UserCircleIcon },
        { name: 'Paramètres', href: '/dashboard/settings', icon: Cog6ToothIcon },
      ]
    }
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
        <nav className="px-6 py-4 flex-1 overflow-y-auto">
          {navigationSections.map((section, sectionIndex) => (
            <div key={section.title} className={sectionIndex > 0 ? 'mt-8' : ''}>
              <h3 className="text-indigo-300 text-xs font-semibold uppercase tracking-wide mb-3">
                {section.title}
              </h3>
              <ul className="space-y-2">
                {section.items.map((item) => {
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
            </div>
          ))}
        </nav>

        {/* Footer avec bouton de déconnexion */}
        <div className="p-6 border-t border-indigo-700">
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center px-4 py-2 bg-indigo-700 hover:bg-indigo-600 text-white rounded-lg font-medium transition-colors duration-200"
          >
            <ArrowRightOnRectangleIcon className="h-5 w-5 mr-2" />
            Déconnexion
          </button>
          
          <div className="mt-4 bg-indigo-700 rounded-lg p-4">
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
