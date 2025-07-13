import axios from 'axios';

// 根据环境配置API基础URL
const baseURL = process.env.NODE_ENV === 'production'
    ? ''  // 生产环境使用相对路径，由Apache代理
    : 'http://localhost:8002'; // 开发环境直接访问后端

const apiClient = axios.create({
    baseURL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// 请求拦截器
apiClient.interceptors.request.use(
    (config) => {
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 响应拦截器
apiClient.interceptors.response.use(
    (response) => {
        return response.data;
    },
    (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
    }
);

export { apiClient };