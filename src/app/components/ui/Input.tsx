import React, { useState } from 'react';

interface RightButtonConfig {
  text: string;
  countdownText?: (count: number) => string;
  onClick: () => void;
  disabled?: boolean;
  countdown?: number;
  title?: string;
}

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  showPasswordToggle?: boolean;
  rightButton?: RightButtonConfig;
}

export const Input: React.FC<InputProps> = ({
  label,
  className = '',
  showPasswordToggle = false,
  rightButton,
  type,
  ...props
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const [inputType, setInputType] = useState(type);

  // 处理密码显示切换
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
    setInputType(showPassword ? 'password' : 'text');
  };

  // 判断是否为密码输入框
  const isPasswordInput = type === 'password' && showPasswordToggle;

  // 判断是否有右侧按钮
  const hasRightButton = !!rightButton;

  // 获取右侧按钮显示文本
  const getRightButtonText = () => {
    if (!rightButton) return '';

    if (rightButton.countdown && rightButton.countdown > 0 && rightButton.countdownText) {
      return rightButton.countdownText(rightButton.countdown);
    }

    return rightButton.text;
  };

  // 获取右侧按钮样式
  const getRightButtonClassName = () => {
    if (!rightButton) return '';

    const baseClass = 'text-sm cursor-pointer select-none transition-colors';

    if (rightButton.disabled || (rightButton.countdown && rightButton.countdown > 0)) {
      return `${baseClass} text-gray-400 cursor-not-allowed`;
    }

    return `${baseClass} text-blue-500 hover:text-blue-700`;
  };

  // 处理右侧按钮点击
  const handleRightButtonClick = () => {
    if (!rightButton || rightButton.disabled ||
      (rightButton.countdown && rightButton.countdown > 0)) {
      return;
    }
    rightButton.onClick();
  };

  return (
    <div className="mb-4">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}

      <div className="flex items-center border-2 border-gray-300 rounded-lg my-2 transition-colors duration-300 focus-within:border-indigo-500 bg-white">
        <input
          type={inputType}
          className={`flex-1 p-3 text-gray-900 placeholder-gray-500 bg-transparent border-none outline-none ${className}`}
          {...props}
        />

        {/* 右侧按钮区域 */}
        <div className="flex items-center space-x-2 px-3">
          {/* 右侧功能按钮 */}
          {hasRightButton && (
            <div
              onClick={handleRightButtonClick}
              className={getRightButtonClassName()}
              title={rightButton.title}
            >
              {getRightButtonText()}
            </div>
          )}

          {/* 密码显示/隐藏按钮 */}
          {isPasswordInput && (
            <button
              type="button"
              onClick={togglePasswordVisibility}
              className="text-gray-500 hover:text-gray-700 focus:outline-none"
              tabIndex={-1}
            >
              {showPassword ? (
                // 隐藏密码图标
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                </svg>
              ) : (
                // 显示密码图标
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};