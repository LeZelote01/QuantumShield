import React from 'react';

export const Badge = ({ children, className = '' }) => {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${className}`}>
      {children}
    </span>
  );
};

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

export const Progress = ({ value, className = '' }) => {
  return (
    <div className={`w-full bg-gray-200 rounded-full h-2 ${className}`}>
      <div 
        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      ></div>
    </div>
  );
};

export const Tabs = ({ children, value, onValueChange, className = '' }) => {
  return (
    <div className={`w-full ${className}`}>
      <div data-tabs-value={value} data-tabs-change={onValueChange}>
        {children}
      </div>
    </div>
  );
};

export const TabsList = ({ children, className = '' }) => {
  return (
    <div className={`inline-flex h-10 items-center justify-center rounded-md bg-gray-100 p-1 text-gray-500 ${className}`}>
      {children}
    </div>
  );
};

export const TabsTrigger = ({ children, value, className = '' }) => {
  return (
    <button
      className={`inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-white transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-white data-[state=active]:text-gray-950 data-[state=active]:shadow-sm ${className}`}
      data-tabs-trigger={value}
    >
      {children}
    </button>
  );
};

export const TabsContent = ({ children, value, className = '' }) => {
  return (
    <div className={`mt-2 ring-offset-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 ${className}`}>
      {children}
    </div>
  );
};

export const Card = ({ children, className = '' }) => {
  return (
    <div className={`rounded-lg border border-gray-200 bg-white shadow-sm ${className}`}>
      {children}
    </div>
  );
};

export const CardHeader = ({ children, className = '' }) => {
  return (
    <div className={`flex flex-col space-y-1.5 p-6 ${className}`}>
      {children}
    </div>
  );
};

export const CardTitle = ({ children, className = '' }) => {
  return (
    <h3 className={`text-2xl font-semibold leading-none tracking-tight ${className}`}>
      {children}
    </h3>
  );
};

export const CardContent = ({ children, className = '' }) => {
  return (
    <div className={`p-6 pt-0 ${className}`}>
      {children}
    </div>
  );
};

export const Button = ({ 
  children, 
  onClick, 
  disabled = false, 
  variant = 'default',
  className = '',
  type = 'button'
}) => {
  const baseClasses = 'inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 h-10 px-4 py-2';
  
  const variants = {
    default: 'bg-blue-600 text-white hover:bg-blue-700',
    outline: 'border border-gray-300 bg-white hover:bg-gray-50 hover:text-gray-900',
    secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200'
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseClasses} ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  );
};

export const Input = ({ 
  value, 
  onChange, 
  placeholder, 
  type = 'text',
  className = '',
  disabled = false,
  maxLength,
  min,
  max,
  step
}) => {
  return (
    <input
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      disabled={disabled}
      maxLength={maxLength}
      min={min}
      max={max}
      step={step}
      className={`flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-white file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
    />
  );
};

export const Textarea = ({ 
  value, 
  onChange, 
  placeholder, 
  className = '',
  disabled = false,
  rows = 4
}) => {
  return (
    <textarea
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      disabled={disabled}
      rows={rows}
      className={`flex min-h-[80px] w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
    />
  );
};