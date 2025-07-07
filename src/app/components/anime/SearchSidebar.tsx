'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

import { Search } from '@/ui/Search';

interface SearchSidebarProps {
    isOpen: boolean;
    onClose: () => void;
}

export const SearchSidebar: React.FC<SearchSidebarProps> = ({ isOpen, onClose }) => {
    const router = useRouter();
    const [searchQuery, setSearchQuery] = useState('');

    // 处理搜索
    const handleSearch = () => {
        console.log('搜索:', searchQuery)
        // 关闭侧边栏
        onClose();
        router.push(`/search?q=${searchQuery}`);
    };

    // 热门搜索
    // const handleHotSearchClick = (keyword: string) => {
    //     setSearchQuery(keyword);
    //     handleSearch(keyword);
    // };

    // 阻止背景滚动
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
        }

        return () => {
            document.body.style.overflow = 'unset';
        };
    }, [isOpen]);

    return (
        <>
            {/* 背景遮罩 */}
            <div
                className={`fixed inset-0 bg-black/30 z-40 transition-opacity duration-300 ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
                    }`}
                onClick={onClose}
            />

            {/* 侧边栏 */}
            <div
                className={`fixed top-0 right-0 h-full w-96 max-w-[90vw] bg-white/95 backdrop-blur-md shadow-2xl z-50 transform transition-transform duration-300 ease-out ${isOpen ? 'translate-x-0' : 'translate-x-full'
                    }`}
            >
                {/* 侧边栏头部 */}
                <div className="flex items-center justify-between p-6 border-b border-gray-200/50">
                    <h2 className="text-xl font-semibold text-gray-800">搜索动漫</h2>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-gray-200/50 rounded-full transition-colors duration-200"
                        aria-label="关闭搜索"
                    >
                        <svg
                            className="w-5 h-5 text-gray-600"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M6 18L18 6M6 6l12 12"
                            />
                        </svg>
                    </button>
                </div>

                {/* 搜索内容 */}
                <div className="p-6 space-y-6">

                    {/* 搜索框 */}
                    <Search
                        placeholder="搜索动漫..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e)}
                        onSearch={handleSearch}
                        variant="glassmorphism"
                    />

                    {/* 热门搜索 */}
                    {/* <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-3">热门搜索</h3>
                        <div className="flex flex-wrap gap-2">
                            {[
                                '进击的巨人',
                                '鬼灭之刃',
                                '咒术回战',
                                '间谍过家家',
                                '链锯人',
                                '赛博朋克边缘行者'
                            ].map((keyword) => (
                                <button
                                    key={keyword}
                                    onClick={() => handleHotSearchClick(keyword)}
                                    className="px-3 py-2 bg-gray-100/80 hover:bg-gray-200/80 backdrop-blur-sm rounded-full text-sm text-gray-700 transition-all duration-200 hover:scale-105"
                                >
                                    {keyword}
                                </button>
                            ))}
                        </div>
                    </div> */}

                    {/* 最近搜索 */}
                    {/* <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-3">最近搜索</h3>
                        <div className="space-y-2">
                            {['小市民系列', '葬送的芙莉莲'].map((keyword, index) => (
                                <div
                                    key={index}
                                    className="flex items-center justify-between p-2 hover:bg-gray-100/50 rounded-lg transition-colors duration-200 cursor-pointer"
                                    onClick={() => handleHotSearchClick(keyword)}
                                >
                                    <span className="text-gray-600">{keyword}</span>
                                    <svg
                                        className="w-4 h-4 text-gray-400"
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                    >
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth={2}
                                            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                                        />
                                    </svg>
                                </div>
                            ))}
                        </div>
                    </div> */}
                </div>
            </div>
        </>
    );
};