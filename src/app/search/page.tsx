'use client';

import { useState, useEffect, Suspense } from 'react'; // Import Suspense
import { useSearchParams } from 'next/navigation';

import { Header } from '@/components/anime/Header';
import { SearchResultCard } from '@/components/anime/SearchResultCard';
import { SearchSidebar } from '@/components/anime/SearchSidebar';
import { AnimeItem } from '@/services/types';
import { clientApi } from '@/services/client'

function SearchContent() {
    const searchParams = useSearchParams();
    const query = searchParams?.get('q') || '';

    const [isSearchOpen, setIsSearchOpen] = useState(false);
    const [searchResults, setSearchResults] = useState<AnimeItem[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [showContent, setShowContent] = useState(false);

    const handleSearchClick = () => {
        setIsSearchOpen(true);
    };

    const handleSearchClose = () => {
        setIsSearchOpen(false);
    };

    const performSearch = async (searchQuery: string) => {
        if (!searchQuery.trim()) return;

        try {
            setIsLoading(true);
            setShowContent(false);

            const response = await clientApi.clientSearch({ name: searchQuery });
            console.log("搜索动漫响应数据:", response.data);
            setSearchResults(response.data);

            setTimeout(() => {
                setShowContent(true);
            }, 200);

        } catch (error) {
            console.error('搜索失败:', error);
            setSearchResults([]);
        } finally {
            setIsLoading(false);
        }
    };

    // 监听URL参数变化，执行搜索
    useEffect(() => {
        if (query) {
            performSearch(query);
        }
    }, [query]);

    return (
        <div className="relative w-full min-h-screen">
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
            <main className="relative z-10 pt-30 pb-10">
                <div className="container mx-auto px-6">

                    {/* 加载状态 */}
                    {isLoading && (
                        <div className="flex justify-center items-center py-20">
                            <div className="relative">
                                <div className="w-16 h-16 border-4 border-white/20 border-t-white rounded-full animate-spin" />
                                <div className="absolute inset-0 w-16 h-16 border-4 border-transparent border-t-blue-400 rounded-full animate-spin"
                                    style={{ animationDirection: 'reverse', animationDuration: '0.8s' }} />
                            </div>
                        </div>
                    )}

                    {/* 搜索结果内容 */}
                    {!isLoading && (
                        <div className={`transition-all duration-800 ease-out ${showContent ? 'opacity-100 transform translate-y-0' : 'opacity-0 transform translate-y-8'
                            }`}>

                            {/* 无结果状态 */}
                            {searchResults.length === 0 && query && (
                                <div className="text-center py-20">
                                    <div className="inline-flex items-center justify-center w-24 h-24 bg-white/10 backdrop-blur-md rounded-full mb-6">
                                        <svg className="w-12 h-12 text-white/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.291-1.007-5.691-2.6m11.382 0A7.962 7.962 0 0012 15c2.34 0 4.291-1.007 5.691-2.6M6 12a6 6 0 1112 0v3.172a1 1 0 01-.293.707l-3.414 3.414A1 1 0 0113.586 20H10.414a1 1 0 01-.707-.293L6.293 16.293A1 1 0 016 15.586V12z" />
                                        </svg>
                                    </div>
                                    <h3 className="text-xl font-semibold text-white mb-2">未找到相关结果</h3>
                                    <p className="text-white/60">尝试使用不同的关键词或检查拼写</p>
                                </div>
                            )}

                            {/* 搜索结果卡片横向滚动 */}
                            {searchResults.length > 0 && (
                                <div className="relative -mx-6">
                                    {/* 滚动容器 */}
                                    <div
                                        className="overflow-x-auto overflow-y-hidden pb-6 px-6 hide-scrollbar"
                                        style={{
                                            scrollbarWidth: 'none',
                                            msOverflowStyle: 'none',
                                        }}
                                    >
                                        <div className="flex gap-6" style={{ width: 'max-content' }}>
                                            {searchResults.map((anime, index) => (
                                                <div
                                                    key={anime.id}
                                                    className={`flex-shrink-0 transition-all duration-600 ${showContent
                                                        ? 'opacity-100 transform translate-y-0'
                                                        : 'opacity-0 transform translate-y-12'
                                                        }`}
                                                    style={{
                                                        width: '280px',
                                                        transitionDelay: `${index * 100}ms`
                                                    }}
                                                >
                                                    <SearchResultCard anime={anime} />
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
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

export default function SearchPage() {
    return (
        <Suspense fallback={
            <div className="flex justify-center items-center min-h-screen bg-black/40 backdrop-blur-sm text-white">
                <div className="relative">
                    <div className="w-16 h-16 border-4 border-white/20 border-t-white rounded-full animate-spin" />
                    <div className="absolute inset-0 w-16 h-16 border-4 border-transparent border-t-blue-400 rounded-full animate-spin"
                        style={{ animationDirection: 'reverse', animationDuration: '0.8s' }} />
                </div>
            </div>
        }>
            <SearchContent />
        </Suspense>
    );
}
