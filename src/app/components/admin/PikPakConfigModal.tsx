'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/ui/Button';
import { Input } from '@/ui/Input';
import { message } from '@/ui/Message';

interface PikPakConfig {
    username: string;
    password: string;
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
    const [rememberCredentials, setRememberCredentials] = useState(false);
    const [isSaving, setIsSaving] = useState(false);

    // 组件挂载时加载保存的配置
    useEffect(() => {
        if (isOpen) {
            loadSavedConfig();
        }
    }, [isOpen]);

    // 从localStorage加载保存的配置
    const loadSavedConfig = () => {
        try {
            const savedUsername = localStorage.getItem('pikpak_username');
            const savedPassword = localStorage.getItem('pikpak_password');
            const savedRemember = localStorage.getItem('pikpak_remember') === 'true';

            if (savedUsername && savedPassword && savedRemember) {
                setUsername(savedUsername);
                setPassword(savedPassword);
                setRememberCredentials(true);
            }
        } catch (error) {
            message.warning('加载PikPak配置失败');
        }
    };

    // 保存配置
    const handleSave = async () => {
        // 验证输入
        if (!username.trim()) {
            message.error('请输入PikPak用户名');
            return;
        }

        if (!password.trim()) {
            message.error('请输入PikPak密码');
            return;
        }

        setIsSaving(true);

        try {
            const config: PikPakConfig = {
                username: username.trim(),
                password: password.trim(),
                rememberCredentials
            };

            if (rememberCredentials) {
                // 记住密码
                localStorage.setItem('pikpak_username', config.username);
                localStorage.setItem('pikpak_password', config.password);
                localStorage.setItem('pikpak_remember', 'true');
            } else {
                localStorage.removeItem('pikpak_username');
                localStorage.removeItem('pikpak_password');
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

    // 清理数据并关闭
    const handleClose = () => {
        setIsSaving(false);
        onClose();
    };

    // 冒泡处理
    const handleModalClick = (e: React.MouseEvent) => {
        e.stopPropagation();
    };

    if (!isOpen) return null;

    return (
        <div
            className="fixed inset-0 bg-white/8 backdrop-blur-[0.3px] flex items-center justify-center z-50 p-4"
            onClick={handleClose}
        >
            <div
                className="bg-white rounded-lg shadow-xl max-w-md w-full overflow-hidden"
                onClick={handleModalClick}
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

                        {/* 保存密码选项 */}
                        <div className="flex items-center space-x-2">
                            <input
                                type="checkbox"
                                id="rememberCredentials"
                                checked={rememberCredentials}
                                onChange={(e) => setRememberCredentials(e.target.checked)}
                                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                            />
                            <label htmlFor="rememberCredentials" className="text-sm text-gray-700">
                                保存账号密码
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