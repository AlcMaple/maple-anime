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
        let errorMessage = '请求失败';

        if (error.response?.data?.detail) {
            if (Array.isArray(error.response.data.detail)) {
                errorMessage = error.response.data.detail.map((item: any) =>
                    `${item.loc?.join?.('.') || ''}: ${item.msg || ''}`
                ).join('; ');
            } else {
                errorMessage = String(error.response.data.detail);
            }
        } else if (error.response?.data?.message) {
            errorMessage = String(error.response.data.message);
        } else if (error.message) {
            errorMessage = String(error.message);
        }

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