import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { message } from '@/ui/Message';

// API接口
export interface ApiResponse<T = any> {
    success: boolean;
    data?: T;
    message?: string;
    error?: string;
}

// 创建axios实例
const api: AxiosInstance = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// 请求拦截器
api.interceptors.request.use(
    (config) => {
        return config;
    },
    (error) => {
        console.error('Request Error:', error);
        return Promise.reject(error);
    }
);

// 响应拦截器
api.interceptors.response.use(
    (response: AxiosResponse) => {
        return response;
    },
    (error) => {
        // 统一错误处理
        const errorMessage = error.response?.data?.message ||
            error.response?.data?.detail ||
            error.message ||
            '请求失败';

        // 显示错误消息
        message.error(errorMessage);

        return Promise.reject(error);
    }
);

// 封装HTTP方法
export const apiClient = {
    get: <T = any>(url: string, config?: AxiosRequestConfig) =>
        api.get<T>(url, config).then(res => res.data),

    post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
        api.post<T>(url, data, config).then(res => res.data),

    put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
        api.put<T>(url, data, config).then(res => res.data),

    delete: <T = any>(url: string, config?: AxiosRequestConfig) =>
        api.delete<T>(url, config).then(res => res.data),
};

export default api;