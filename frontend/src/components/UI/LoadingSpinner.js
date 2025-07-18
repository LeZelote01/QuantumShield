import React from 'react';

const LoadingSpinner = ({ size = 'medium', color = 'indigo' }) => {
  const sizeClasses = {
    small: 'h-4 w-4',
    medium: 'h-8 w-8',
    large: 'h-12 w-12',
  };

  const colorClasses = {
    indigo: 'text-indigo-600',
    white: 'text-white',
    gray: 'text-gray-600',
  };

  return (
    <div className="flex items-center justify-center">
      <div className={`animate-spin rounded-full border-b-2 border-current ${sizeClasses[size]} ${colorClasses[color]}`}>
        <span className="sr-only">Chargement...</span>
      </div>
    </div>
  );
};

export default LoadingSpinner;