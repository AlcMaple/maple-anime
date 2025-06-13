import React, { useState, useRef, useEffect } from 'react';

interface Option {
    value: string;
    label: string;
}

interface SelectProps {
    label?: string;
    value: string;
    onChange: (value: string) => void;
    options: Option[];
    placeholder?: string;
    disabled?: boolean;
    className?: string;
}

export const Select: React.FC<SelectProps> = ({
    label,
    value,
    onChange,
    options,
    placeholder = "请选择...",
    disabled = false,
    className = ""
}) => {
    const [isOpen, setIsOpen] = useState(false);
    const selectRef = useRef<HTMLDivElement>(null);

    // 点击外部关闭下拉框
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    // 处理选项选择
    const handleOptionSelect = (optionValue: string) => {
        if (!disabled) {
            onChange(optionValue);
            setIsOpen(false);
        }
    };

    // 处理键盘事件
    const handleKeyDown = (event: React.KeyboardEvent) => {
        if (disabled) return;

        switch (event.key) {
            case 'Enter':
            case ' ':
                event.preventDefault();
                setIsOpen(!isOpen);
                break;
            case 'Escape':
                setIsOpen(false);
                break;
            case 'ArrowDown':
                event.preventDefault();
                if (!isOpen) {
                    setIsOpen(true);
                }
                break;
            case 'ArrowUp':
                event.preventDefault();
                break;
        }
    };

    // 获取当前选中的选项显示文本
    const getSelectedLabel = () => {
        const selectedOption = options.find(option => option.value === value);
        return selectedOption ? selectedOption.label : placeholder;
    };

    return (
        <div className={`mb-4 ${className}`}>
            {label && (
                <label className="block text-sm font-medium text-gray-700 mb-1">
                    {label}
                </label>
            )}

            <div className="relative" ref={selectRef}>
                {/* 选择框主体 */}
                <div
                    onClick={() => !disabled && setIsOpen(!isOpen)}
                    onKeyDown={handleKeyDown}
                    tabIndex={disabled ? -1 : 0}
                    className={`
                        w-full p-3 border-2 rounded-lg my-2 transition-colors duration-300 cursor-pointer
                        flex items-center justify-between
                        ${disabled
                            ? 'bg-gray-100 border-gray-200 text-gray-400 cursor-not-allowed'
                            : isOpen
                                ? 'border-indigo-500 bg-white text-gray-900'
                                : 'border-gray-300 bg-white text-gray-900 hover:border-gray-400'
                        }
                        ${!value && !disabled ? 'text-gray-500' : ''}
                    `}
                >
                    <span className="flex-1 text-left">
                        {getSelectedLabel()}
                    </span>

                    {/* 下拉箭头 */}
                    <svg
                        className={`w-5 h-5 transition-transform duration-200 flex-shrink-0 ml-2 ${isOpen ? 'transform rotate-180' : ''
                            } ${disabled ? 'text-gray-400' : 'text-gray-600'}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                </div>

                {/* 下拉选项列表 */}
                {isOpen && !disabled && (
                    <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                        {options.length === 0 ? (
                            <div className="px-3 py-2 text-sm text-gray-500 text-center">
                                暂无选项
                            </div>
                        ) : (
                            options.map((option, index) => (
                                <div
                                    key={option.value}
                                    onClick={() => handleOptionSelect(option.value)}
                                    className={`
                                        px-3 py-2 text-sm cursor-pointer transition-colors duration-150
                                        ${option.value === value
                                            ? 'bg-indigo-50 text-indigo-900 font-medium'
                                            : 'text-gray-900 hover:bg-gray-50'
                                        }
                                        ${index === 0 ? 'rounded-t-lg' : ''}
                                        ${index === options.length - 1 ? 'rounded-b-lg' : ''}
                                    `}
                                >
                                    {option.label}
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};