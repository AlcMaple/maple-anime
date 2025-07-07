'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Header } from '@/components/anime/Header';
import { SearchSidebar } from '@/components/anime/SearchSidebar';
import { AnimeSchedule } from '@/components/anime/AnimeSchedule';
import { AnimeCardList } from '@/components/anime/AnimeCardList';
import { pikpakApi } from '@/services/pikpak';
import { AnimeItem } from '@/services/types';

export default function Home() {
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [animeList, setAnimeList] = useState<AnimeItem[]>([]);
  const [showContent, setShowContent] = useState(false);

  const handleSearchClick = () => {
    setIsSearchOpen(true);
  };

  const handleSearchClose = () => {
    setIsSearchOpen(false);
  };

  // 获取动漫数据
  const animeData = async () => {
    try {
      setIsLoading(true);
      const response = await pikpakApi.getAnimeList();

      setAnimeList(response.data || []);

      // 数据加载完成，直接切换状态
      setIsLoading(false);

      // 稍微延迟后显示内容动画
      setTimeout(() => {
        setShowContent(true);
      }, 100);

    } catch (error) {
      console.error('获取动漫数据失败:', error);
      setAnimeList([]);
      setIsLoading(false);
      setTimeout(() => {
        setShowContent(true);
      }, 100);
    }
  };

  useEffect(() => {
    animeData();
  }, []);

  return (
    <div className="relative w-full h-screen overflow-hidden">
      {/* 背景封面图 */}
      <div
        className="absolute inset-0 w-full h-full bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: `url('/images/bg.jpg')`
        }}
      />

      {/* 背景遮罩 - 只在有内容时显示 */}
      <div className={`absolute inset-0 transition-all duration-1000 ${!isLoading ? 'bg-black/40 backdrop-blur-sm' : 'bg-black/0'
        }`}></div>

      {/* 头部导航 */}
      <Header onSearchClick={handleSearchClick} />

      {/* 主要内容区域 */}
      <main className="relative z-10 flex items-center justify-center h-full">
        {/* 加载前的欢迎界面 */}
        {isLoading && (
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
          </div>
        )}

        {/* 数据加载完成后的内容展示 */}
        {!isLoading && (
          <div
            className={`w-full h-full transition-all duration-1000 ease-out ${showContent
              ? 'opacity-100 transform translate-y-0'
              : 'opacity-0 transform translate-y-8'
              }`}
          >
            <div className="w-full h-full flex p-6 gap-6">
              {/* 左栏 - 番剧周期表 */}
              <div className={`w-1/3 transition-all duration-1200 delay-400 ${showContent
                ? 'opacity-100 transform translate-x-0'
                : 'opacity-0 transform -translate-x-12'
                }`}>
                <AnimeSchedule />
              </div>

              {/* 右栏 - 动漫卡片列表 */}
              <div className={`flex-1 transition-all duration-1200 delay-400 ${showContent
                ? 'opacity-100 transform translate-x-0'
                : 'opacity-0 transform translate-x-12'
                }`}>
                <AnimeCardList animeList={animeList} />
              </div>
            </div>
          </div>
        )}
      </main>

      {/* 搜索侧边栏 */}
      <SearchSidebar
        isOpen={isSearchOpen}
        onClose={handleSearchClose}
      />
    </div>
  );
}