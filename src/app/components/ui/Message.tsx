'use client';

import React, { useEffect, useState } from 'react';

export type MessageType = 'success' | 'error' | 'warning' | 'info';

interface MessageItem {
    id: string;
    type: MessageType;
    content: string;
    duration: number;
}

// 全局消息状态
let messages: MessageItem[] = [];
let setMessagesCallback: ((messages: MessageItem[]) => void) | null = null;

// 消息管理函数
const updateMessages = () => {
    if (setMessagesCallback) {
        setMessagesCallback([...messages]);
    }
};

const addMessage = (type: MessageType, content: string, duration = 3000) => {
    const id = Date.now().toString() + Math.random().toString(36).substr(2, 9);
    const newMessage: MessageItem = { id, type, content, duration };

    messages.push(newMessage);
    updateMessages();

    // 自动移除
    setTimeout(() => {
        removeMessage(id);
    }, duration);
};

const removeMessage = (id: string) => {
    messages = messages.filter(msg => msg.id !== id);
    updateMessages();
};

// 导出消息函数
export const message = {
    success: (content: string, duration?: number) => addMessage('success', content, duration),
    error: (content: string, duration?: number) => addMessage('error', content, duration),
    warning: (content: string, duration?: number) => addMessage('warning', content, duration),
    info: (content: string, duration?: number) => addMessage('info', content, duration),
};

// 单个消息组件
const MessageItem: React.FC<{
    message: MessageItem;
    onRemove: (id: string) => void
}> = ({ message: msg, onRemove }) => {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        setTimeout(() => setIsVisible(true), 50);
    }, []);

    const handleRemove = () => {
        setIsVisible(false);
        setTimeout(() => onRemove(msg.id), 300);
    };

    const getTypeStyles = () => {
        switch (msg.type) {
            case 'success':
                return 'bg-green-500 border-green-600';
            case 'error':
                return 'bg-red-500 border-red-600';
            case 'warning':
                return 'bg-yellow-500 border-yellow-600';
            case 'info':
                return 'bg-blue-500 border-blue-600';
            default:
                return 'bg-gray-500 border-gray-600';
        }
    };

    const getIcon = () => {
        switch (msg.type) {
            case 'success': return '✅';
            case 'error': return '❌';
            case 'warning': return '⚠️';
            case 'info': return 'ℹ️';
            default: return 'ℹ️';
        }
    };

    return (
        <div
            className={`
        transform transition-all duration-300 ease-in-out
        ${isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}
        ${getTypeStyles()}
        text-white px-4 py-3 rounded-lg shadow-lg border-l-4 mb-2
        min-w-80 max-w-md flex items-center space-x-3
      `}
        >
            <span className="text-lg">{getIcon()}</span>
            <span className="flex-1 text-sm font-medium">{msg.content}</span>
            <button
                onClick={handleRemove}
                className="text-white hover:text-gray-200 text-lg font-light ml-2"
            >
                ×
            </button>
        </div>
    );
};

// 消息容器组件
export const Message: React.FC = () => {
    const [currentMessages, setCurrentMessages] = useState<MessageItem[]>([]);

    useEffect(() => {
        setMessagesCallback = setCurrentMessages;
        return () => {
            setMessagesCallback = null;
        };
    }, []);

    if (currentMessages.length === 0) return null;

    return (
        <div className="fixed top-5 right-5 z-[9999] space-y-2">
            {currentMessages.map((msg) => (
                <MessageItem
                    key={msg.id}
                    message={msg}
                    onRemove={removeMessage}
                />
            ))}
        </div>
    );
};