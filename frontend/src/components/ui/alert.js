import React from 'react';

export const Alert = ({ children, className = '' }) => {
  return (
    <div className={`rounded-md p-4 ${className}`}>
      {children}
    </div>
  );
};

export const AlertDescription = ({ children, className = '' }) => {
  return (
    <div className={`text-sm ${className}`}>
      {children}
    </div>
  );
};