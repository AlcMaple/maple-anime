'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Header } from '@/components/anime/Header';

import { SearchSidebar } from '@/components/anime/SearchSidebar';
import { pikpakApi } from '@/services/pikpak';
import { AnimeItem, EpisodeFile } from '@/services/types';

export default function WatchPage() {
    const params = useParams();
    const router = useRouter();
    const animeId = params?.id as string;

    // 状态管理
    const [animeInfo, setAnimeInfo] = useState<AnimeItem | null>(null);
    const [episodes, setEpisodes] = useState<EpisodeFile[]>([]);
    const [currentEpisode, setCurrentEpisode] = useState<EpisodeFile | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isSearchOpen, setIsSearchOpen] = useState(false);
    const [showContent, setShowContent] = useState(false);

    // 搜索功能
    const handleSearchClick = () => {
        setIsSearchOpen(true);
    };

    const handleSearchClose = () => {
        setIsSearchOpen(false);
    };

    // 加载动漫信息和集数列表
    const loadAnimeData = async () => {
        if (!animeId) return;

        try {
            setIsLoading(true);

            // 模拟数据，实际应该从API获取
            const mockAnime: AnimeItem = {
                id: animeId,
                title: '药屋少女的独白',
                status: '连载'
            };

            const mockEpisodes: EpisodeFile[] = [
                { id: '1', name: '第01集 - 猫猫', play_url: '' },
                { id: '2', name: '第02集 - 解毒', play_url: '' },
                { id: '3', name: '第03集 - 幽灵', play_url: '' },
                { id: '4', name: '第04集 - 恩赏', play_url: '' },
                { id: '5', name: '第05集 - 里树', play_url: '' },
                { id: '6', name: '第06集 - 园游会', play_url: '' },
                { id: '7', name: '第07集 - 里宫', play_url: '' },
                { id: '8', name: '第08集 - 麦稈', play_url: '' },
                { id: '9', name: '第09集 - 天国', play_url: '' },
                { id: '10', name: '第10集 - 结尾', play_url: '' }
            ];

            setAnimeInfo(mockAnime);
            setEpisodes(mockEpisodes);
            setCurrentEpisode(mockEpisodes[0]);

            setIsLoading(false);
            setTimeout(() => setShowContent(true), 100);

        } catch (error) {
            console.error('加载动漫数据失败:', error);
            setIsLoading(false);
        }
    };

    // 选择集数
    const handleEpisodeSelect = (episode: EpisodeFile) => {
        setCurrentEpisode(episode);
    };

    useEffect(() => {
        loadAnimeData();
    }, [animeId]);

    return (
        <div className="relative w-full min-h-screen overflow-hidden">
            {/* 动态背景 */}
            <div className="absolute inset-0 w-full h-full">
                {/* 渐变背景 */}
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/30 via-purple-900/20 to-pink-900/30"></div>

                {/* 动态几何图形 */}
                <div className="absolute inset-0 overflow-hidden">
                    <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
                    <div className="absolute top-1/2 -left-20 w-60 h-60 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
                    <div className="absolute bottom-20 right-1/3 w-40 h-40 bg-pink-500/10 rounded-full blur-3xl animate-pulse delay-2000"></div>
                </div>

                {/* 网格背景 */}
                <div className="absolute inset-0 opacity-5">
                    <div className="w-full h-full" style={{
                        backgroundImage: `
                            linear-gradient(rgba(255,255,255,.1) 1px, transparent 1px),
                            linear-gradient(90deg, rgba(255,255,255,.1) 1px, transparent 1px)
                        `,
                        backgroundSize: '50px 50px'
                    }}></div>
                </div>
            </div>

            {/* 背景模糊遮罩 */}
            <div className="absolute inset-0 bg-black/20 backdrop-blur-sm"></div>

            {/* 头部导航 */}
            <Header onSearchClick={handleSearchClick} />

            {/* 主要内容区域 */}
            <main className="relative z-10 p-6 pt-4">
                {isLoading ? (
                    <div className="flex items-center justify-center h-96">
                        <div className="text-center text-white">
                            <div className="inline-block w-8 h-8 border-4 border-white/20 border-t-white rounded-full animate-spin mb-4"></div>
                            <p className="text-lg">加载中...</p>
                        </div>
                    </div>
                ) : (
                    <div className={`transition-all duration-1000 ease-out ${showContent ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
                        }`}>
                        {/* 动漫标题区域 - 独特的悬浮设计 */}
                        <div className="mb-8">
                            <div className="relative max-w-4xl mx-auto">
                                {/* 标题容器 */}
                                <div className="relative rounded-xl p-6 text-center">
                                    <h1 className="text-4xl md:text-5xl font-bold text-white mb-2 tracking-wide">
                                        {animeInfo?.title}
                                    </h1>
                                </div>
                            </div>
                        </div>

                        {/* 视频播放和集数选择区域 */}
                        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-4 gap-6">
                            {/* 视频播放器区域 */}
                            <div className="lg:col-span-3">
                                <div className="relative">
                                    {/* 播放器装饰背景 */}
                                    <div className="absolute -inset-2 bg-gradient-to-br from-white/10 to-white/5 rounded-2xl blur-sm"></div>

                                    {/* 播放器容器 */}
                                    <div className="relative backdrop-blur-md bg-black/30 border border-white/20 rounded-xl overflow-hidden">
                                        <div className="aspect-video flex items-center justify-center bg-black/40">
                                            {currentEpisode ? (
                                                <div className="text-center text-white">
                                                    <div className="text-8xl mb-4">▶</div>
                                                    <p className="text-xl mb-2">{currentEpisode.name}</p>
                                                    <p className="text-white/60">点击播放</p>
                                                </div>
                                            ) : (
                                                <div className="text-white/60">
                                                    <p>请选择集数</p>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* 集数选择区域 */}
                            <div className="lg:col-span-1">
                                <div className="relative">
                                    {/* 集数列表装饰背景 */}
                                    <div className="absolute -inset-2 bg-gradient-to-b from-white/10 to-white/5 rounded-2xl blur-sm"></div>

                                    {/* 集数列表容器 */}
                                    <div className="relative backdrop-blur-md bg-white/5 border border-white/10 rounded-xl p-4">
                                        <h3 className="text-white font-semibold mb-4 text-center">选集播放</h3>

                                        <div className="space-y-2 max-h-116 overflow-y-auto pr-2 anime-list-scroll">
                                            {episodes.map((episode) => (
                                                <button
                                                    key={episode.id}
                                                    onClick={() => handleEpisodeSelect(episode)}
                                                    className={`w-full p-3 rounded-lg text-left transition-all duration-300 group ${currentEpisode?.id === episode.id
                                                        ? 'bg-white/20 border-white/30 text-white shadow-lg'
                                                        : 'bg-white/5 border-white/10 text-white/80 hover:bg-white/10 hover:border-white/20'
                                                        } border backdrop-blur-sm`}
                                                >
                                                    <div className="flex items-center justify-between">
                                                        <span className="font-medium truncate">
                                                            {episode.name}
                                                        </span>
                                                        {currentEpisode?.id === episode.id && (
                                                            <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse flex-shrink-0 ml-2"></div>
                                                        )}
                                                    </div>
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                </div>
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