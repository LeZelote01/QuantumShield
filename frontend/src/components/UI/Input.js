import React from 'react';

const Input = ({ 
  label, 
  error, 
  helperText, 
  required = false, 
  className = '',
  type = 'text',
  ...props 
}) => {
  return (
    <div className={`space-y-1 ${className}`}>
      {label && (
        <label className="block text-sm font-medium text-gray-700">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <input
        type={type}
        className={`
          w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
          ${error ? 'border-red-500' : 'border-gray-300'}
        `}
        {...props}
      />
      
      {error && (
        <p className="text-red-600 text-sm">{error}</p>
      )}
      
      {helperText && !error && (
        <p className="text-gray-500 text-sm">{helperText}</p>
      )}
    </div>
  );
};

export default Input;