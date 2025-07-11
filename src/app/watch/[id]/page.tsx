'use client';

import { useState, useEffect, useRef, use } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Header } from '@/components/anime/Header';

import { SearchSidebar } from '@/components/anime/SearchSidebar';
import { clientApi } from '@/services/client';
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
    const [isPlaying, setIsPlaying] = useState(false);
    const [showContent, setShowContent] = useState(false);
    const videoRef = useRef<HTMLVideoElement>(null);
    const [VideoUrl, setVideoUrl] = useState<string | null>(null);

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

            const response = await clientApi.clientAnimeData(animeId);
            console.log("客户端动漫数据：", response);
            if (response.success) {
                setAnimeInfo(response.data);
                setEpisodes(response.data.files);
                setCurrentEpisode(response.data.files[0]);
                setVideoUrl(response.data.files[0].play_url);
                setIsLoading(false);
                setTimeout(() => setShowContent(true), 100);
            } else {
                console.error('客户端获取动漫数据失败:', response.message);
                setIsLoading(false);
            }

        } catch (error) {
            console.error('加载动漫数据失败:', error);
            setIsLoading(false);
        }
    };

    // 选择集数
    const handleEpisodeSelect = (episode: EpisodeFile) => {
        setCurrentEpisode(episode);
        setVideoUrl(episode.play_url);
        setIsPlaying(false);
        if (videoRef.current) {
            videoRef.current.pause();
            videoRef.current.currentTime = 0;
        }
    };

    // 切换播放状态
    const togglePlay = () => {
        if (!videoRef.current) return;

        if (videoRef.current.paused) {
            videoRef.current.play()
                .then(() => setIsPlaying(true))
                .catch(error => {
                    console.error('播放失败:', error);
                });
        } else {
            videoRef.current.pause();
            setIsPlaying(false);
        }
    };

    // 切换到下一集
    const nextEpisode = () => {
        if (!currentEpisode || !episodes.length) return;
        const currentIndex = episodes.findIndex(ep => ep.id === currentEpisode.id);
        if (currentIndex < episodes.length - 1) {
            handleEpisodeSelect(episodes[currentIndex + 1]);
        }
    };

    // 快进/后退
    const seekVideo = (seconds: number) => {
        if (!videoRef.current) return;
        videoRef.current.currentTime += seconds;
    };

    // 调整音量
    const adjustVolume = (delta: number) => {
        if (!videoRef.current) return;
        const newVolume = Math.max(0, Math.min(1, videoRef.current.volume + delta));
        videoRef.current.volume = newVolume;
    };

    // 键盘事件处理
    const handleKeyDown = (e: KeyboardEvent) => {
        // 防止在输入框中触发
        const target = e.target as HTMLElement;
        if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
            return;
        }

        switch (e.key) {
            case ' ':
                e.preventDefault();
                togglePlay();
                break;
            case 'ArrowLeft':
                e.preventDefault();
                seekVideo(-10); // 后退10秒
                break;
            case 'ArrowRight':
                e.preventDefault();
                seekVideo(10); // 快进10秒
                break;
            case 'ArrowUp':
                e.preventDefault();
                adjustVolume(0.1); // 音量+10%
                break;
            case 'ArrowDown':
                e.preventDefault();
                adjustVolume(-0.1); // 音量-10%
                break;
        }
    };

    // 当视频播放结束时
    const handleVideoEnded = () => {
        setIsPlaying(false);
        // 自动播放下一集
        nextEpisode();
    };

    // 键盘事件监听
    useEffect(() => {
        document.addEventListener('keydown', handleKeyDown);
        return () => {
            document.removeEventListener('keydown', handleKeyDown);
        };
    }, [currentEpisode, episodes]); // 依赖当前集数和集数列表

    useEffect(() => {
        loadAnimeData();
    }, [animeId]);

    return (
        <div className="relative w-full min-h-screen overflow-hidden">
            {/* 背景 */}
            <div className="absolute inset-0 w-full h-full">
                {/* 渐变 */}
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/30 via-purple-900/20 to-pink-900/30"></div>

                {/* 几何图形 */}
                <div className="absolute inset-0 overflow-hidden">
                    <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
                    <div className="absolute top-1/2 -left-20 w-60 h-60 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
                    <div className="absolute bottom-20 right-1/3 w-40 h-40 bg-pink-500/10 rounded-full blur-3xl animate-pulse delay-2000"></div>
                </div>

                {/* 网格 */}
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
                        {/* 动漫标题区域 */}
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
                            {/* 视频播放区域 */}
                            <div className="lg:col-span-3">
                                <div className="relative">
                                    {/* 播放器背景 */}
                                    <div className="absolute -inset-2 bg-gradient-to-br from-white/10 to-white/5 rounded-2xl blur-sm"></div>

                                    {/* 播放器容器 */}
                                    <div className="relative backdrop-blur-md bg-black/30 border border-white/20 rounded-xl overflow-hidden">
                                        <div className="aspect-video flex items-center justify-center bg-black/40">
                                            {currentEpisode ? (
                                                <>
                                                    <video
                                                        ref={videoRef}
                                                        className="w-full h-full"
                                                        src={VideoUrl} // 视频URL
                                                        onClick={(e) => {
                                                            e.stopPropagation(); // 阻止事件冒泡
                                                            togglePlay();
                                                        }}
                                                        onEnded={handleVideoEnded}
                                                        controls={isPlaying} // 播放控制条
                                                    />
                                                    {!isPlaying && (
                                                        <div className="absolute inset-0 flex items-center justify-center cursor-default" onClick={togglePlay}>
                                                            <div className="text-center text-white">
                                                                <div className="text-8xl mb-4">▶</div>
                                                            </div>
                                                        </div>
                                                    )}
                                                </>
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
                                    {/* 集数列表背景 */}
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