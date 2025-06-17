'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/ui/Button';
import { Input } from '@/ui/Input';
import { message } from '@/ui/Message';

interface PikPakConfig {
    username: string;
    password: string;
    key: string;
    rememberCredentials: boolean;
}

interface PikPakConfigModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSave: (config: PikPakConfig) => void;
}

export const PikPakConfigModal: React.FC<PikPakConfigModalProps> = ({
    isOpen,
    onClose,
    onSave
}) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [key, setKey] = useState('');
    const [rememberCredentials, setRememberCredentials] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [isGettingKey, setIsGettingKey] = useState(false);
    const [getKeyCountdown, setGetKeyCountdown] = useState(0);

    // 组件挂载时加载保存的配置
    useEffect(() => {
        if (isOpen) {
            loadSavedConfig();
        }
    }, [isOpen]);

    // 倒计时
    useEffect(() => {
        let timer: NodeJS.Timeout;
        if (getKeyCountdown > 0) {
            timer = setTimeout(() => {
                setGetKeyCountdown(prev => prev - 1);
            }, 1000);
        }
        return () => {
            if (timer) clearTimeout(timer);
        };
    }, [getKeyCountdown]);

    // 从localStorage加载保存的配置
    const loadSavedConfig = () => {
        try {
            const savedUsername = localStorage.getItem('pikpak_username');
            const savedPassword = localStorage.getItem('pikpak_password');
            const savedKey = localStorage.getItem('pikpak_key');
            const savedRemember = localStorage.getItem('pikpak_remember') === 'true';

            if (savedRemember) {
                setUsername(savedUsername || '');
                setPassword(savedPassword || '');
                setKey(savedKey || '');
                setRememberCredentials(true);
            }
        } catch (error) {
            message.warning('加载PikPak配置失败');
        }
    };

    // 验证输入
    const validateInput = () => {
        const hasKey = key.trim();
        const hasCredentials = username.trim() && password.trim();

        if (!hasKey && !hasCredentials) {
            message.error('请输入Key或者用户名和密码');
            return false;
        }

        return true;
    };

    // 保存配置
    const handleSave = async () => {
        // 验证输入
        if (!validateInput()) {
            return;
        }

        setIsSaving(true);

        try {
            const config: PikPakConfig = {
                username: username.trim(),
                password: password.trim(),
                key: key.trim(),
                rememberCredentials
            };

            if (rememberCredentials) {
                // 记住密码
                localStorage.setItem('pikpak_username', config.username);
                localStorage.setItem('pikpak_password', config.password);
                localStorage.setItem('pikpak_key', config.key);
                localStorage.setItem('pikpak_remember', 'true');
            } else {
                localStorage.removeItem('pikpak_username');
                localStorage.removeItem('pikpak_password');
                localStorage.removeItem('pikpak_key');
                localStorage.removeItem('pikpak_remember');
            }

            // 调用父组件的保存回调
            onSave(config);

            // 显示成功消息
            message.success('PikPak配置保存成功！');
            handleClose();

        } catch (error) {
            const errorMsg = error instanceof Error ? error.message : '保存失败';
            message.error(`pikpak配置保存失败: ${errorMsg}`);
        } finally {
            setIsSaving(false);
        }
    };

    // 获取Key
    const handleGetKey = async () => {
        // 验证用户名密码是否已填写
        if (!username.trim() || !password.trim()) {
            message.error('请先填写用户名和密码才能获取Key');
            return;
        }

        // 检查是否在倒计时中
        if (getKeyCountdown > 0) {
            message.warning(`请等待 ${getKeyCountdown} 秒后重试`);
            return;
        }

        setIsGettingKey(true);

        try {
            // // 获取Key
            // const testResult = await pikpakApi.testConnection({
            //     username: username.trim(),
            //     password: password.trim(),
            //     key: ''
            // });

            // if (testResult.success && testResult.new_key) {
            //     // 获取成功，自动填入Key
            //     setKey(testResult.new_key);
            //     message.success('Key获取成功！已自动填入');

            //     // 如果开启了记住配置，立即保存key到localStorage
            //     if (rememberCredentials) {
            //         localStorage.setItem('pikpak_key', testResult.new_key);
            //     }

            //     // 开始60秒倒计时
            //     setGetKeyCountdown(60);
            // } else {
            //     // 获取失败
            //     message.error(testResult.message || '获取Key失败，请检查用户名密码');
            //     // 失败也开始倒计时，防止频繁请求
            //     setGetKeyCountdown(60);
            // }
        } catch (error) {
            const errorMsg = error instanceof Error ? error.message : '获取Key失败';
            message.error(errorMsg);
            setGetKeyCountdown(60);
        } finally {
            setIsGettingKey(false);
        }
    };

    // 清理数据并关闭
    const handleClose = () => {
        setIsSaving(false);
        setIsGettingKey(false);
        setGetKeyCountdown(0);
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div
            className="fixed inset-0 bg-white/8 backdrop-blur-[0.3px] flex items-center justify-center z-50 p-4"
        >
            <div
                className="bg-white rounded-lg shadow-xl max-w-md w-full overflow-hidden"
            >
                {/* 模态框头部 */}
                <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                    <h2 className="text-xl font-semibold text-gray-900">PikPak 配置</h2>
                    <button
                        onClick={handleClose}
                        className="text-gray-400 hover:text-gray-600 text-2xl font-light"
                    >
                        ×
                    </button>
                </div>

                {/* 模态框内容 */}
                <div className="p-6">
                    <div className="space-y-4">

                        {/* 用户名输入 */}
                        <div>
                            <Input
                                label="用户名"
                                type="text"
                                placeholder="请输入PikPak用户名（邮箱或手机号）"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                            />
                        </div>

                        {/* 密码输入 */}
                        <div>
                            <Input
                                label="密码"
                                type="password"
                                placeholder="请输入PikPak密码"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                showPasswordToggle={true}
                            />
                        </div>

                        {/* Key输入框 */}
                        <Input
                            label="Key"
                            type="text"
                            placeholder="请输入PikPak API Key"
                            value={key}
                            onChange={(e) => setKey(e.target.value)}
                            rightButton={{
                                text: '获取key',
                                countdownText: (count) => `${count}s后重试`,
                                onClick: handleGetKey,
                                disabled: !username.trim() || !password.trim(),
                                countdown: getKeyCountdown,
                                title: getKeyCountdown > 0
                                    ? `请等待 ${getKeyCountdown} 秒后重试`
                                    : '获取Key'
                            }}
                        />

                        {/* 记住选项 */}
                        <div className="flex items-center space-x-2">
                            <input
                                type="checkbox"
                                id="rememberCredentials"
                                checked={rememberCredentials}
                                onChange={(e) => setRememberCredentials(e.target.checked)}
                                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                            />
                            <label htmlFor="rememberCredentials" className="text-sm text-gray-700">
                                记住
                            </label>
                        </div>
                    </div>
                </div>

                {/* 模态框底部 */}
                <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
                    <Button
                        variant="info"
                        onClick={handleClose}
                        className="bg-gray-500 hover:bg-gray-600"
                    >
                        关闭
                    </Button>
                    <Button
                        variant="primary"
                        onClick={handleSave}
                        className="px-6"
                    >
                        保存
                    </Button>
                </div>
            </div>
        </div>
    );
};