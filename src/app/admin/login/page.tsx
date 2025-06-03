'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';
import { Card } from '../../components/ui/Card';

const ADMIN_PASSWORD = '2333';

export default function LoginPage() {
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const router = useRouter();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        // 模拟登录验证
        setTimeout(() => {
            if (password === ADMIN_PASSWORD) {
                // 保存登录状态到localStorage
                localStorage.setItem('adminAuth', 'true');
                localStorage.setItem('adminLoginTime', new Date().toISOString());

                // 跳转到管理端主页
                router.push('/admin');
            } else {
                setError('密码错误，请重试');
            }
            setIsLoading(false);
        }, 500);
    };

    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-5">
            <div className="w-full max-w-md">
                {/* 页面标题 */}
                <div className="text-center mb-8 font-bold">
                    <p className="text-lg opacity-90">
                        Maple Anime 管理后台
                    </p>
                </div>

                {/* 登录表单 */}
                <Card variant="section" className="w-full">
                    <form onSubmit={handleLogin} className="space-y-6">

                        <Input
                            label="管理员密码"
                            type="password"
                            placeholder="请输入管理员密码"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            className={error ? 'border-red-500 focus:border-red-500' : ''}
                        />

                        {error && (
                            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                                <div className="flex items-center">
                                    <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                                    <span className="text-sm text-red-700">❌ {error}</span>
                                </div>
                            </div>
                        )}

                        <Button
                            type="submit"
                            variant="primary"
                            className="w-full py-4 text-base"
                            disabled={isLoading || !password.trim()}
                        >
                            {isLoading ? '🔄 验证中...' : '登录'}
                        </Button>
                    </form>

                </Card>

                {/* 底部信息 */}
                <div className="mt-6 text-center text-sm opacity-75">
                    <p className="text-sm">
                        🌸 Maple Anime Management System
                    </p>
                </div>
            </div>
        </div>
    );
}