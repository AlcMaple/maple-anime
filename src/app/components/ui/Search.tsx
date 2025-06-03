import React from 'react';

interface SearchProps {
    placeholder?: string;
    value: string;
    onChange: (value: string) => void;
    onSearch: () => void;
    className?: string;
    disabled?: boolean;
}

export const Search: React.FC<SearchProps> = ({
    placeholder = "搜索...",
    value,
    onChange,
    onSearch,
    className = "",
    disabled = false
}) => {
    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !disabled) {
            onSearch();
        }
    };

    return (
        <div className={`flex items-center ${className}`}>
            <div className="flex items-center bg-gray-100 rounded-full">
                <input
                    type="text"
                    placeholder={placeholder}
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    onKeyPress={handleKeyPress}
                    disabled={disabled}
                    className="w-64 px-4 py-3 bg-transparent outline-none text-gray-900 placeholder-gray-500 rounded-l-full disabled:opacity-50"
                />
                <button
                    onClick={onSearch}
                    disabled={disabled}
                    className="bg-gradient-to-r from-pink-400 to-pink-500 text-white px-6 py-3 rounded-full hover:from-pink-500 hover:to-pink-600 transition-all duration-300 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                </button>
            </div>
        </div>
    );
};