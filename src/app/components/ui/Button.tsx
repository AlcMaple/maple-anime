import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'success' | 'warning' | 'info' | 'small';
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({ 
  variant = 'primary', 
  children, 
  className = '', 
  ...props 
}) => {
  const getVariantStyles = () => {
    const baseStyles = "border-none cursor-pointer transition-all duration-300 font-medium inline-block text-white rounded-full";
    
    switch (variant) {
      case 'success':
        return `${baseStyles} bg-gradient-to-r from-green-500 to-green-600 text-sm px-6 py-3 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-green-400/40`;
      case 'warning':
        return `${baseStyles} bg-gradient-to-r from-orange-500 to-orange-600 text-sm px-6 py-3 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-orange-400/40`;
      case 'info':
        return `${baseStyles} bg-gradient-to-r from-blue-500 to-blue-600 text-sm px-6 py-3 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-blue-400/40`;
      case 'small':
        return `${baseStyles} bg-gradient-to-r from-indigo-500 to-purple-600 text-xs px-4 py-2 mx-1 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-indigo-400/40`;
      default: // primary
        return `${baseStyles} bg-gradient-to-r from-indigo-500 to-purple-600 text-sm px-6 py-3 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-indigo-400/40`;
    }
  };

  return (
    <button
      className={`${getVariantStyles()} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};