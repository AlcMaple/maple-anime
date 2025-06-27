'use client';

import { use, useEffect, useState } from 'react';
import Link from 'next/link';
import { Header } from '@/components/anime/Header';
import { SearchSidebar } from '@/components/anime/SearchSidebar';

export default function Home() {
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearchClick = () => {
    setIsSearchOpen(true);
  };

  const handleSearchClose = () => {
    setIsSearchOpen(false);
  };

  useEffect(() => {

  }, []);

  return (
    <div className="relative w-full h-screen overflow-hidden">
      {/* 背景封面图 */}
      <div
        className="absolute inset-0 w-full h-full bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: `url('/images/bg.jpg')`
        }}
      >
        {/* 背景遮罩 */}
        <div className="absolute inset-0 bg-black/20"></div>
      </div>

      {/* 头部导航 */}
      <Header onSearchClick={handleSearchClick} />

      {/* 主要内容区域 */}
      <main className="relative z-10 flex items-center justify-center h-full">
        <div className="text-center text-white px-4">
          {/* 主标题 */}
          <h1 className="text-5xl md:text-7xl font-bold mb-6 drop-shadow-lg">
            每个人理想的
            <br />
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              动漫网站
            </span>
          </h1>

          {/* 副标题 */}
          <p className="text-xl md:text-2xl mb-8 text-white/90 drop-shadow-md">
            追番、观看、分享 - 一站式动漫体验
          </p>

          {/* 操作按钮组 */}
          {/* <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/search"
              className="px-8 py-3 bg-blue-500/80 hover:bg-blue-500 backdrop-blur-sm rounded-full text-white font-medium transition-all duration-300 hover:scale-105 hover:shadow-lg"
            >
              开始探索
            </Link>

            <Link
              href="/admin"
              className="px-8 py-3 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-full text-white font-medium border border-white/30 transition-all duration-300 hover:scale-105"
            >
              管理入口
            </Link>
          </div> */}

          {(isLoading && ())}
        </div>
      </main>

      {/* 搜索侧边栏 */}
      <SearchSidebar
        isOpen={isSearchOpen}
        onClose={handleSearchClose}
      />
    </div>
  );
}