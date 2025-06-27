'use client';

import { useState } from 'react';
import { AnimeItem } from '@/services/types';

interface AnimeCardListProps {
    animeList: AnimeItem[];
    className?: string;
}

export const AnimeCardList: React.FC<AnimeCardListProps> = ({
    animeList,
    className = ''
}) => {
    const [imageErrors, setImageErrors] = useState<Set<string>>(new Set());

    const handleImageError = (animeId: string) => {
        setImageErrors(prev => new Set(prev).add(animeId));
    };

    const handleCardClick = (anime: AnimeItem) => {
        console.log('点击动漫卡片:', anime);
    };

    if (animeList.length === 0) {
        return (
            <div className={`bg-white/10 backdrop-blur-md rounded-lg p-8 h-full flex items-center justify-center ${className}`}>
                <div className="text-center text-white/60">
                    <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2h4a1 1 0 110 2h-1v10a2 2 0 01-2 2H6a2 2 0 01-2-2V6H3a1 1 0 110-2h4zM6 6v10h12V6H6z" />
                    </svg>
                    <p className="text-lg">暂无动漫数据</p>
                    <p className="text-sm mt-2 opacity-75">请稍后再试或联系管理员添加动漫</p>
                </div>
            </div>
        );
    }

    return (
        <div className={`bg-white/10 backdrop-blur-md rounded-lg p-4 h-full ${className}`}>
            {/* 头部标题 */}
            <div className="mb-4">
                <h2 className="text-xl font-semibold text-white mb-2">
                    动漫库 ({animeList.length})
                </h2>
                <div className="w-full h-px bg-white/20"></div>
            </div>

            {/* 动漫卡片列表 */}
            <div className="overflow-y-auto h-full pb-4">
                <div className="grid gap-4">
                    {animeList.map((anime) => (
                        <div
                            key={anime.id}
                            onClick={() => handleCardClick(anime)}
                            className="bg-white/10 rounded-lg p-4 hover:bg-white/20 transition-all duration-300 cursor-pointer group hover:scale-[1.02] hover:shadow-lg"
                        >
                            <div className="flex space-x-4">
                                {/* 封面图 */}
                                <div className="flex-shrink-0">
                                    <div className="w-20 h-28 bg-gray-300/20 rounded-lg overflow-hidden">
                                        {anime.cover_url && !imageErrors.has(anime.id) ? (
                                            <img
                                                src={anime.cover_url}
                                                alt={anime.title}
                                                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                                                onError={() => handleImageError(anime.id)}
                                            />
                                        ) : (
                                            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-400/20 to-gray-600/20">
                                                <svg className="w-8 h-8 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2h4a1 1 0 110 2h-1v10a2 2 0 01-2 2H6a2 2 0 01-2-2V6H3a1 1 0 110-2h4z" />
                                                </svg>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* 动漫信息 */}
                                <div className="flex-1 min-w-0">
                                    {/* 标题和状态 */}
                                    <div className="flex items-start justify-between mb-2">
                                        <h3 className="text-white font-semibold text-lg line-clamp-2 group-hover:text-blue-200 transition-colors">
                                            {anime.title}
                                        </h3>
                                        <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ml-2 flex-shrink-0 ${anime.status === '完结'
                                            ? 'bg-green-500/20 text-green-200 border border-green-500/30'
                                            : 'bg-blue-500/20 text-blue-200 border border-blue-500/30'
                                            }`}>
                                            {anime.status}
                                        </span>
                                    </div>

                                    {/* 简介 */}
                                    {anime.summary && (
                                        <p className="text-white/70 text-sm leading-relaxed line-clamp-3 mb-3">
                                            {anime.summary}
                                        </p>
                                    )}

                                    {/* 底部信息 */}
                                    <div className="flex items-center justify-between">
                                        <div className="text-white/50 text-xs">
                                            {anime.updated_at && (
                                                <span>更新于 {new Date(anime.updated_at).toLocaleDateString()}</span>
                                            )}
                                        </div>

                                        <div className="flex items-center space-x-2">
                                            {/* 播放按钮 */}
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    console.log('播放动漫:', anime);
                                                }}
                                                className="flex items-center space-x-1 px-3 py-1 bg-blue-500/20 hover:bg-blue-500/30 text-blue-200 rounded-full text-xs transition-all duration-200 hover:scale-105"
                                            >
                                                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                                                    <path d="M8 5v14l11-7z" />
                                                </svg>
                                                <span>播放</span>
                                            </button>

                                            {/* 详情按钮 */}
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    console.log('查看详情:', anime);
                                                }}
                                                className="flex items-center space-x-1 px-3 py-1 bg-white/10 hover:bg-white/20 text-white/80 rounded-full text-xs transition-all duration-200 hover:scale-105"
                                            >
                                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                                </svg>
                                                <span>详情</span>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* 悬停时的装饰线 */}
                            <div className="w-0 group-hover:w-full h-0.5 bg-gradient-to-r from-blue-400 to-purple-400 transition-all duration-300 mt-3 rounded-full"></div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};