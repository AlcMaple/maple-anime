import axios from 'axios';
import { message } from '@/ui/Message';

// 获取 Axios 实例类型
type AxiosInstance = ReturnType<typeof axios.create>;

// API 接口响应结构
export interface ApiResponse<T = any> {
    success: boolean;
    data?: T;
    message?: string;
    error?: string;
}

// 创建 axios 实例
const api: AxiosInstance = axios.create({
    baseURL: 'http://localhost:8002',
    timeout: 600000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// 请求拦截器
api.interceptors.request.use(
    (config) => config,
    (error) => {
        console.error('Request Error:', error);
        return Promise.reject(error);
    }
);

// 响应拦截器
api.interceptors.response.use(
    (response) => response,
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

// 封装 HTTP 方法
export const apiClient = {
    get: <T = any>(url: string, config?: Parameters<typeof api.get>[1]) =>
        api.get<T>(url, config).then(res => res.data),

    post: <T = any>(url: string, data?: any, config?: Parameters<typeof api.post>[2]) =>
        api.post<T>(url, data, config).then(res => res.data),

    put: <T = any>(url: string, data?: any, config?: Parameters<typeof api.put>[2]) =>
        api.put<T>(url, data, config).then(res => res.data),

    delete: <T = any>(url: string, config?: Parameters<typeof api.delete>[1]) =>
        api.delete<T>(url, config).then(res => res.data),
};

export default api;
