'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/ui/Button';
import { Card } from '@/ui/Card';
import { Loading } from '@/ui/Loading';
import { message } from '@/ui/Message';
import { logApi } from '@/services/log';

interface ParsedLogEntry {
    id: string;
    timestamp: string;
    level: string;
    logger: string;
    function: string;
    line: string;
    message: string;
    raw: string;
}

export default function LogPage() {
    const [logs, setLogs] = useState<ParsedLogEntry[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isConnected, setIsConnected] = useState(false);
    const [autoScroll, setAutoScroll] = useState(true);
    const [logStatus, setLogStatus] = useState({
        websocket_enabled: false,
        active_connections: 0,
        log_buffer_size: 0
    });

    const logContainerRef = useRef<HTMLDivElement>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const logIdCounter = useRef(0);
    const router = useRouter();
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loginTime, setLoginTime] = useState<string>('');

    // 自动滚动到底部
    const scrollToBottom = useCallback(() => {
        if (autoScroll && logContainerRef.current) {
            logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
        }
    }, [autoScroll]);

    // 添加日志条目
    const addLogEntry = useCallback((rawLog: string) => {
        const parsed = logApi.parseLogEntry(rawLog);
        if (parsed) {
            const entry: ParsedLogEntry = {
                id: `log-${logIdCounter.current++}-${Date.now()}`,
                ...parsed
            };

            setLogs(prev => {
                const newLogs = [...prev, entry];
                // 限制日志数量，避免内存溢出
                return newLogs.slice(-500);
            });
        }
    }, []);

    // 获取历史日志
    const loadHistoricalLogs = useCallback(async () => {
        try {
            const response = await logApi.getHistoricalLogs();
            if (response.code === 200 && Array.isArray(response.data)) {
                const parsedLogs = response.data
                    .map((rawLog: string) => {
                        const parsed = logApi.parseLogEntry(rawLog);
                        if (parsed) {
                            return {
                                id: `history-${logIdCounter.current++}`,
                                ...parsed
                            };
                        }
                        return null;
                    })
                    .filter((log): log is ParsedLogEntry => log !== null);

                setLogs(parsedLogs);
            }
        } catch (error) {
            console.error('Failed to load historical logs:', error);
            message.error('加载历史日志失败');
        }
    }, []);

    // 获取日志系统状态
    const loadLogStatus = useCallback(async () => {
        try {
            const response = await logApi.getLogStatus();
            if (response.code === 200 && response.data) {
                setLogStatus(response.data);
            }
        } catch (error) {
            console.error('Failed to load log status:', error);
        }
    }, []);

    // 建立WebSocket连接
    const connectWebSocket = useCallback(() => {
        if (wsRef.current) {
            wsRef.current.close();
        }

        const ws = logApi.createWebSocketConnection();
        if (!ws) {
            message.error('无法创建WebSocket连接');
            return;
        }

        wsRef.current = ws;

        ws.onopen = () => {
            setIsConnected(true);
            message.success('实时日志连接已建立');
        };

        ws.onmessage = (event) => {
            addLogEntry(event.data);
        };

        ws.onclose = (event) => {
            setIsConnected(false);
            if (event.code !== 1000) {
                message.warning('WebSocket连接已断开');
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            setIsConnected(false);
            message.error('WebSocket连接发生错误');
        };
    }, [addLogEntry]);

    // 断开WebSocket连接
    const disconnectWebSocket = useCallback(() => {
        if (wsRef.current) {
            wsRef.current.close(1000, 'User disconnected');
        }
    }, []);

    // 清空日志
    const clearLogs = useCallback(() => {
        setLogs([]);
        message.success('日志已清空');
    }, []);

    // 组件挂载时加载数据
    useEffect(() => {
        const initializeLogPage = async () => {
            setIsLoading(true);
            try {
                await Promise.all([
                    loadHistoricalLogs(),
                    loadLogStatus()
                ]);
            } finally {
                setIsLoading(false);
            }
        };

        initializeLogPage();
    }, [loadHistoricalLogs, loadLogStatus]);

    // 自动滚动效果
    useEffect(() => {
        scrollToBottom();
    }, [logs, scrollToBottom]);

    // 组件卸载时清理WebSocket
    useEffect(() => {
        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, []);

    // 检查登录状态
    useEffect(() => {
        const checkAuth = () => {
            const authStatus = localStorage.getItem('adminAuth');
            const loginTimeStr = localStorage.getItem('adminLoginTime');

            if (authStatus === 'true' && loginTimeStr) {
                const loginDate = new Date(loginTimeStr);
                const now = new Date();
                const daysDiff = (now.getTime() - loginDate.getTime()) / (1000 * 3600 * 24);

                if (daysDiff < 7) {
                    setIsAuthenticated(true);
                    setLoginTime(loginDate.toLocaleString());
                } else {
                    localStorage.removeItem('adminAuth');
                    localStorage.removeItem('adminLoginTime');
                    router.push('/admin/login');
                }
            } else {
                router.push('/admin/login');
            }
            setIsLoading(false);
        };

        checkAuth();
    }, [router]);

    // 渲染单条日志
    const renderLogEntry = (log: ParsedLogEntry) => {
        const levelColor = logApi.getLogLevelColor(log.level);
        const levelBgColor = logApi.getLogLevelBgColor(log.level);

        return (
            <div
                key={log.id}
                className={`px-3 py-1 hover:bg-gray-50 transition-colors duration-150 border-l-2 border-transparent hover:border-blue-200 ${levelBgColor}`}
            >
                <div className="flex items-start font-mono text-sm leading-relaxed">
                    {/* 时间戳 */}
                    <span className="text-green-600 whitespace-nowrap mr-1">
                        {log.timestamp}
                    </span>

                    {/* 分隔符 - 使用特殊字符确保连贯 */}
                    <span className="text-gray-400 mx-1 select-none">│</span>

                    {/* 日志级别 */}
                    <span className={`${levelColor} font-medium whitespace-nowrap min-w-[70px] mr-1`}>
                        {log.level.padEnd(8)}
                    </span>

                    {/* 分隔符 */}
                    <span className="text-gray-400 mx-1 select-none">│</span>

                    {/* 模块信息 */}
                    <span className="text-cyan-600 whitespace-nowrap mr-1">
                        {log.logger}:{log.function}:{log.line}
                    </span>

                    {/* 分隔符 */}
                    <span className="text-gray-400 mx-1 select-none">-</span>

                    {/* 日志消息 */}
                    <span className={`${levelColor} flex-1 break-words`}>
                        {log.message}
                    </span>
                </div>
            </div>
        );
    };

    if (isLoading) {
        return (
            <div className="p-6">
                <Loading text="加载日志数据中..." />
            </div>
        );
    }

    return (
        <div className="p-6 max-w-full">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900 mb-2">系统日志管理</h1>
                <p className="text-gray-600">实时查看系统运行日志，监控应用状态</p>
            </div>

            {/* 状态栏 */}
            <Card className="mb-6">
                <div className="flex items-center justify-between p-4">
                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-2">
                            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                            <span className="text-sm font-medium">
                                {isConnected ? '实时连接已建立' : '实时连接已断开'}
                            </span>
                        </div>

                        <div className="text-sm text-gray-600">
                            <span>活跃连接: {logStatus.active_connections}</span>
                            <span className="mx-2">|</span>
                            <span>缓冲区大小: {logStatus.log_buffer_size}</span>
                            <span className="mx-2">|</span>
                            <span>当前日志: {logs.length}</span>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <label className="flex items-center gap-2 text-sm">
                            <input
                                type="checkbox"
                                checked={autoScroll}
                                onChange={(e) => setAutoScroll(e.target.checked)}
                                className="rounded"
                            />
                            自动滚动
                        </label>

                        {isConnected ? (
                            <Button variant="danger" onClick={disconnectWebSocket}>
                                断开连接
                            </Button>
                        ) : (
                            <Button variant="primary" onClick={connectWebSocket}>
                                连接实时日志
                            </Button>
                        )}

                        <Button variant="warning" onClick={clearLogs}>
                            清空日志
                        </Button>

                        <Button variant="success" onClick={loadHistoricalLogs}>
                            刷新历史日志
                        </Button>
                    </div>
                </div>
            </Card>

            {/* 日志显示区域 */}
            <Card>
                <div className="bg-gray-900 text-white">
                    <div className="px-4 py-3 border-b border-gray-700">
                        <h3 className="text-sm font-medium">系统日志输出</h3>
                    </div>

                    <div
                        ref={logContainerRef}
                        className="h-[600px] overflow-y-auto bg-white text-black scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100"
                        style={{
                            fontFamily: 'Monaco, Menlo, "Ubuntu Mono", "Roboto Mono", "Courier New", monospace',
                            fontSize: '13px',
                            lineHeight: '1.4'
                        }}
                    >
                        {logs.length === 0 ? (
                            <div className="flex items-center justify-center h-full text-gray-500">
                                <div className="text-center">
                                    <div className="text-6xl mb-4">📋</div>
                                    <div className="text-lg font-medium mb-2">暂无日志数据</div>
                                    <div className="text-sm">点击"连接实时日志"开始监控系统日志</div>
                                </div>
                            </div>
                        ) : (
                            logs.map(renderLogEntry)
                        )}
                    </div>
                </div>
            </Card>
        </div>
    );
}