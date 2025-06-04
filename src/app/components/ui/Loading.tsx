import React from 'react';

interface LoadingProps {
    variant?: 'spinner' | 'dots' | 'pulse' | 'bars';
    size?: 'small' | 'medium' | 'large';
    color?: 'primary' | 'white' | 'gray';
    text?: string;
    className?: string;
}

export const Loading: React.FC<LoadingProps> = ({
    variant = 'spinner',
    size = 'medium',
    color = 'primary',
    text,
    className = ''
}) => {
    const getSizeStyles = () => {
        switch (size) {
            case 'small':
                return 'w-4 h-4';
            case 'large':
                return 'w-12 h-12';
            default: // medium
                return 'w-8 h-8';
        }
    };

    const getColorStyles = () => {
        switch (color) {
            case 'white':
                return 'text-white border-white';
            case 'gray':
                return 'text-gray-500 border-gray-500';
            default: // primary
                return 'text-blue-500 border-blue-500';
        }
    };

    const getTextSize = () => {
        switch (size) {
            case 'small':
                return 'text-sm';
            case 'large':
                return 'text-lg';
            default: // medium
                return 'text-base';
        }
    };

    const renderSpinner = () => (
        <div
            className={`${getSizeStyles()} ${getColorStyles()} border-2 border-t-transparent rounded-full animate-spin`}
        />
    );

    const renderDots = () => (
        <div className="flex space-x-1">
            <div className={`${size === 'small' ? 'w-2 h-2' : size === 'large' ? 'w-4 h-4' : 'w-3 h-3'} ${getColorStyles().split(' ')[0]} bg-current rounded-full animate-bounce`} style={{ animationDelay: '0ms' }}></div>
            <div className={`${size === 'small' ? 'w-2 h-2' : size === 'large' ? 'w-4 h-4' : 'w-3 h-3'} ${getColorStyles().split(' ')[0]} bg-current rounded-full animate-bounce`} style={{ animationDelay: '150ms' }}></div>
            <div className={`${size === 'small' ? 'w-2 h-2' : size === 'large' ? 'w-4 h-4' : 'w-3 h-3'} ${getColorStyles().split(' ')[0]} bg-current rounded-full animate-bounce`} style={{ animationDelay: '300ms' }}></div>
        </div>
    );

    const renderPulse = () => (
        <div
            className={`${getSizeStyles()} ${getColorStyles().split(' ')[0]} bg-current rounded-full animate-pulse`}
        />
    );

    const renderBars = () => (
        <div className="flex space-x-1 items-end">
            <div className={`${size === 'small' ? 'w-1 h-4' : size === 'large' ? 'w-2 h-8' : 'w-1 h-6'} ${getColorStyles().split(' ')[0]} bg-current rounded animate-pulse`} style={{ animationDelay: '0ms' }}></div>
            <div className={`${size === 'small' ? 'w-1 h-6' : size === 'large' ? 'w-2 h-12' : 'w-1 h-8'} ${getColorStyles().split(' ')[0]} bg-current rounded animate-pulse`} style={{ animationDelay: '150ms' }}></div>
            <div className={`${size === 'small' ? 'w-1 h-4' : size === 'large' ? 'w-2 h-8' : 'w-1 h-6'} ${getColorStyles().split(' ')[0]} bg-current rounded animate-pulse`} style={{ animationDelay: '300ms' }}></div>
        </div>
    );

    const renderLoadingAnimation = () => {
        switch (variant) {
            case 'dots':
                return renderDots();
            case 'pulse':
                return renderPulse();
            case 'bars':
                return renderBars();
            default: // spinner
                return renderSpinner();
        }
    };

    return (
        <div className={`flex items-center justify-center space-x-3 ${className}`}>
            {renderLoadingAnimation()}
            {text && (
                <span className={`${getTextSize()} ${getColorStyles().split(' ')[0]} font-medium`}>
                    {text}
                </span>
            )}
        </div>
    );
};