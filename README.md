# maple-anime

这是每个人理想的动漫网站

This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

## 开发进度计划

### 核心功能

| 状态 | 阶段 | 任务 | 技术方案 |
|:---:|------|------|----------|
| ⬜ | 基础设施 | 服务器环境搭建 | Docker + MinIO |
| ⬜ | 基础设施 | 安全配置 | HTTPS, CORS, CSP |
| ⬜ | 前端 | 基础框架搭建 | Next.js + Tailwind |
| ⬜ | 前端 | 数据获取层实现 | SWR + 接口封装 |
| ⬜ | 前端 | 视频播放器集成 | Plyr + HLS.js |
| ⬜ | 前端 | 动画效果实现 | framer-motion |
| ⬜ | 后端 | API服务开发 | FastAPI + Pydantic v2 |
| ⬜ | 后端 | 爬虫系统开发 | Scrapy + Splash |
| ⬜ | 后端 | 用户系统 | JWT认证 |
| ⬜ | 数据处理 | 视频转码流水线 | FFmpeg + Celery |
| ⬜ | 数据处理 | HLS格式转换 | FFmpeg HLS配置 |
| ⬜ | 运维 | BunnyCDN配置 | 视频加速分发 |
| ⬜ | 运维 | CI/CD流程 | GitHub Actions |
| ⬜ | 测试 | 基本功能测试 | 手动 + 自动化 |