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
            <div className={`h-full p-6 flex items-center justify-center ${className}`}>
                <div className="bg-white/15 backdrop-blur-xl rounded-2xl p-8 border border-white/10">
                    <div className="text-center text-white/60">
                        <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2h4a1 1 0 110 2h-1v10a2 2 0 01-2 2H6a2 2 0 01-2-2V6H3a1 1 0 110-2h4zM6 6v10h12V6H6z" />
                        </svg>
                        <p className="text-lg">暂无动漫数据</p>
                        <p className="text-sm mt-2 opacity-75">请稍后再试或联系管理员添加动漫</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className={`h-full p-6 ${className}`}>
            {/* 动漫卡片列表 */}
            <div className="overflow-y-auto h-full pb-4 bg-white/15 backdrop-blur-xl rounded-2xl p-4 border border-white/10">
                <div className="grid gap-4">
                    {animeList.map((anime) => (
                        <div
                            key={anime.id}
                            onClick={() => handleCardClick(anime)}
                            className="bg-white/20 backdrop-blur-sm rounded-2xl p-6 hover:bg-white/30 transition-all duration-500 cursor-pointer group hover:scale-[1.02] hover:shadow-2xl border border-white/10 hover:border-white/20"
                        >
                            <div className="flex space-x-4">
                                {/* 封面图 */}
                                <div className="flex-shrink-0">
                                    <div className="w-20 h-28 bg-gray-300/20 rounded-xl overflow-hidden shadow-lg">
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
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};