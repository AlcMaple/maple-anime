import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export const Input: React.FC<InputProps> = ({ 
  label,
  className = '', 
  ...props 
}) => {
  return (
    <div className="mb-4">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}
      <input
        className={`w-full p-3 border-2 border-gray-300 rounded-lg my-2 transition-colors duration-300 focus:outline-none focus:border-indigo-500 text-gray-900 placeholder-gray-500 bg-white ${className}`}
        {...props}
      />
    </div>
  );
};