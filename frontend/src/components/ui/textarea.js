import React from 'react';

export const Textarea = ({ 
  value, 
  onChange, 
  placeholder, 
  className = '',
  disabled = false,
  rows = 4,
  required = false
}) => {
  return (
    <textarea
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      disabled={disabled}
      rows={rows}
      required={required}
      className={`flex min-h-[80px] w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
    />
  );
};