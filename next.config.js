/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'export',
    trailingSlash: true,
    images: {
        unoptimized: true
    },
    assetPrefix: process.env.NODE_ENV === 'production' ? '' : '',
    basePath: '',
    // 静态导出配置
    exportPathMap: async function () {
        return {
            '/': { page: '/' },
        }
    },
    // 确保API路由正确指向后端
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: '/api/:path*', // 保持原样，由Apache代理
            },
        ]
    },
}

module.exports = nextConfig