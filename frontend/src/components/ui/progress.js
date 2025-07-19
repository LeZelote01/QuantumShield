import React from 'react';

export const Progress = ({ value, className = '' }) => {
  const percentage = Math.min(100, Math.max(0, value || 0));
  
  return (
    <div className={`w-full bg-gray-200 rounded-full h-2 ${className}`}>
      <div 
        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
        style={{ width: `${percentage}%` }}
      ></div>
    </div>
  );
};