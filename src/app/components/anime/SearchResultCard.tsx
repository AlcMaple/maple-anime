'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { AnimeItem } from '@/services/types';

interface SearchResultCardProps {
    anime: AnimeItem;
}

export const SearchResultCard: React.FC<SearchResultCardProps> = ({ anime }) => {
    const router = useRouter();
    const [imageError, setImageError] = useState(false);
    const [isHovered, setIsHovered] = useState(false);

    const handleCardClick = () => {
        // 跳转到播放页面，传递动漫ID
        router.push(`/watch/${anime.id}`);
    };

    const handleImageError = () => {
        setImageError(true);
    };

    return (
        <div
            className="group cursor-pointer"
            onClick={handleCardClick}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            {/* 主卡片容器 */}
            <div className="relative">

                {/* 卡片主体 */}
                <div className={`relative bg-white/10 backdrop-blur-xl rounded-xl border border-white/20 overflow-hidden transition-all duration-500 ${isHovered ? 'transform scale-[1.02] shadow-2xl shadow-purple-500/20' : 'shadow-lg'
                    }`}>

                    {/* 封面区域 */}
                    <div className="relative aspect-[3/4] overflow-hidden">
                        {/* 封面图片 */}
                        {anime.cover_url && !imageError ? (
                            <img
                                src={anime.cover_url}
                                alt={anime.title}
                                className={`w-full h-full object-cover transition-all duration-700 ${isHovered ? 'scale-110' : 'scale-100'
                                    }`}
                                onError={handleImageError}
                            />
                        ) : (
                            <div className="w-full h-full bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center">
                                <div className="text-center text-white/50">
                                    <svg className="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                    </svg>
                                    <span className="text-xs">暂无封面</span>
                                </div>
                            </div>
                        )}

                        {/* 状态徽章 */}
                        <div className="absolute top-3 right-3">
                            <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium backdrop-blur-md border ${anime.status === '完结'
                                ? 'bg-green-500/80 text-white border-green-400/50'
                                : 'bg-blue-500/80 text-white border-blue-400/50'
                                }`}>
                                {anime.status || '未知'}
                            </span>
                        </div>

                        {/* 悬浮时的播放按钮 */}
                        <div className={`absolute inset-0 flex items-center justify-center transition-all duration-300 ${isHovered ? 'opacity-100' : 'opacity-0'
                            }`}>
                            <div className="bg-white/20 rounded-full p-4 border border-white/30">
                                <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M8 5v14l11-7z" />
                                </svg>
                            </div>
                        </div>

                        {/* 底部渐变遮罩 */}
                        <div className="absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
                    </div>

                    {/* 信息区域 */}
                    <div className="relative p-4">
                        {/* 标题 */}
                        <h3 className="font-bold text-white text-sm md:text-base leading-tight mb-2 line-clamp-2 group-hover:text-blue-300 transition-colors duration-300">
                            {anime.title}
                        </h3>

                        {/* 简介 */}
                        {anime.summary && (
                            <p className="text-white/70 text-xs leading-relaxed line-clamp-3 mb-3">
                                {anime.summary}
                            </p>
                        )}

                        {/* 底部操作区 */}
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                                {/* 播放图标 */}
                                <div className="flex items-center space-x-1 text-white/60 text-xs">
                                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                                        <path d="M8 5v14l11-7z" />
                                    </svg>
                                    <span>立即观看</span>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    );
};