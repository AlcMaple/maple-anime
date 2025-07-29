import { apiClient } from '@/utils/api';
import { HistoricalLogResponse, LogStatusResponse, ParsedLogEntry } from './types';

export class LogService {
    /**
     * 获取历史日志
     */
    static async getHistoricalLogs(): Promise<HistoricalLogResponse> {
        return apiClient.get<HistoricalLogResponse>('/api/log');
    }

    /**
     * 获取日志系统状态
     */
    static async getLogStatus(): Promise<LogStatusResponse> {
        return apiClient.get<LogStatusResponse>('/api/log/status');
    }

    /**
     * 创建WebSocket连接获取实时日志
     */
    static createWebSocketConnection(): WebSocket | null {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.host;
            const wsUrl = `${protocol}//${host}/api/log/ws`;

            return new WebSocket(wsUrl);
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            return null;
        }
    }

    /**
     * 解析日志条目
     * 格式: "2024-01-01 12:00:00 | INFO     | module:function:123 - message"
     */
    static parseLogEntry(rawLog: string): ParsedLogEntry | null {
        try {
            // 匹配日志格式
            const logPattern = /^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*\|\s*(\w+)\s*\|\s*([^:]+):([^:]+):(\d+)\s*-\s*(.+)$/;
            const match = rawLog.match(logPattern);

            if (match) {
                return {
                    timestamp: match[1],
                    level: match[2].trim(),
                    logger: match[3],
                    function: match[4],
                    line: match[5],
                    message: match[6],
                    raw: rawLog
                };
            }

            // 如果不匹配标准格式，返回简单格式
            return {
                timestamp: new Date().toISOString().slice(0, 19).replace('T', ' '),
                level: 'INFO',
                logger: 'system',
                function: 'unknown',
                line: '0',
                message: rawLog,
                raw: rawLog
            };
        } catch (error) {
            console.error('Failed to parse log entry:', error);
            return null;
        }
    }

    /**
     * 获取日志级别颜色
     */
    static getLogLevelColor(level: string): string {
        switch (level.toUpperCase()) {
            case 'DEBUG':
                return 'text-gray-500';
            case 'INFO':
                return 'text-blue-500';
            case 'WARNING':
                return 'text-yellow-500';
            case 'ERROR':
                return 'text-red-500';
            case 'CRITICAL':
                return 'text-red-700';
            case 'SUCCESS':
                return 'text-green-500';
            default:
                return 'text-gray-600';
        }
    }

    /**
     * 获取日志级别背景色
     */
    static getLogLevelBgColor(level: string): string {
        switch (level.toUpperCase()) {
            case 'DEBUG':
                return 'bg-gray-100';
            case 'INFO':
                return 'bg-blue-50';
            case 'WARNING':
                return 'bg-yellow-50';
            case 'ERROR':
                return 'bg-red-50';
            case 'CRITICAL':
                return 'bg-red-100';
            case 'SUCCESS':
                return 'bg-green-50';
            default:
                return 'bg-gray-50';
        }
    }
}

// 导出实例
export const logApi = {
    getHistoricalLogs: LogService.getHistoricalLogs,
    getLogStatus: LogService.getLogStatus,
    createWebSocketConnection: LogService.createWebSocketConnection,
    parseLogEntry: LogService.parseLogEntry,
    getLogLevelColor: LogService.getLogLevelColor,
    getLogLevelBgColor: LogService.getLogLevelBgColor,
};