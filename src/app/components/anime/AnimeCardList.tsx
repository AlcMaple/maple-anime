'use client';

import { useState } from 'react';
import { AnimeItem } from '@/services/types';
import { useRouter } from 'next/navigation';

interface AnimeCardListProps {
    animeList: AnimeItem[];
    className?: string;
}

export const AnimeCardList: React.FC<AnimeCardListProps> = ({
    animeList,
    className = ''
}) => {
    const [imageErrors, setImageErrors] = useState<Set<string>>(new Set());
    const router = useRouter();

    const handleImageError = (animeId: string) => {
        setImageErrors(prev => new Set(prev).add(animeId));
    };

    const handleCardClick = (anime: AnimeItem) => {
        console.log('点击动漫卡片:', anime);
        router.push(`/watch/${anime.id}`);
    };

    // 限制显示数量，只显示前10个
    const displayAnimeList = animeList.slice(0, 10);

    if (animeList.length === 0) {
        return (
            <div className={`h-full p-6 flex items-center justify-center ${className}`}>
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
        <div className={`h-full p-6 ${className}`}>
            {/* 占位符 */}
            <div className="mb-16">
            </div>

            {/* 动漫网格列表 */}
            <div className="overflow-y-auto h-full max-h-[75vh]">
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                    {displayAnimeList.map((anime) => (
                        <div
                            key={anime.id}
                            onClick={() => handleCardClick(anime)}
                            className="group cursor-pointer"
                        >
                            {/* 封面容器 */}
                            <div className="relative aspect-[3/4] mb-3">
                                <div className="w-full h-full bg-white/10 rounded-xl overflow-hidden hover:bg-white/15 transition-all duration-300">
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

                                {/* 状态标签 */}
                                <div className="absolute top-2 right-2">
                                    <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${anime.status === '完结'
                                        ? 'bg-green-500/80 text-white'
                                        : 'bg-blue-500/80 text-white'
                                        }`}>
                                        {anime.status}
                                    </span>
                                </div>

                                {/* hover遮罩 */}
                                <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl flex items-center justify-center">
                                    <div className="bg-white/20 rounded-full p-3">
                                        <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                                            <path d="M8 5v14l11-7z" />
                                        </svg>
                                    </div>
                                </div>
                            </div>

                            {/* 标题 */}
                            <div className="px-1">
                                <h3 className="text-white text-sm font-medium line-clamp-2 group-hover:text-blue-200 transition-colors leading-relaxed">
                                    {anime.title}
                                </h3>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};