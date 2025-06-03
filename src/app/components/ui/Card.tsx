import React from 'react';

interface CardProps {
    title?: string;
    children: React.ReactNode;
    className?: string;
    variant?: 'section' | 'sidebar' | 'result';
}

export const Card: React.FC<CardProps> = ({
    title,
    children,
    className = '',
    variant = 'section'
}) => {
    const getVariantStyles = () => {
        const baseStyles = "p-6 rounded-2xl shadow-lg transition-transform duration-300";

        switch (variant) {
            case 'sidebar':
                return `${baseStyles} bg-white/95 backdrop-blur-sm`;
            case 'result':
                return `${baseStyles} bg-white border border-gray-200 max-h-96 overflow-y-auto`;
            default: // section
                return `${baseStyles} bg-white/95 backdrop-blur-sm hover:-translate-y-1`;
        }
    };

    return (
        <div className={`${getVariantStyles()} ${className}`}>
            {title && (
                <h3 className="mb-4 text-gray-700 text-xl font-medium">
                    {title}
                </h3>
            )}
            {children}
        </div>
    );
};