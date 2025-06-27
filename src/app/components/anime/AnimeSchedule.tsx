'use client';

import { useState, useEffect } from 'react';
import { Search } from '@/ui/Search';
import { CalendarAnime } from '@/services/types';

interface AnimeScheduleProps {
    className?: string;
}

export const AnimeSchedule: React.FC<AnimeScheduleProps> = ({ className = '' }) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedDay, setSelectedDay] = useState(0); // 0-6 对应周一到周日
    const [calendarData, setCalendarData] = useState<CalendarAnime[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    const weekdays = [
        { id: 0, name: '周一', shortName: '一' },
        { id: 1, name: '周二', shortName: '二' },
        { id: 2, name: '周三', shortName: '三' },
        { id: 3, name: '周四', shortName: '四' },
        { id: 4, name: '周五', shortName: '五' },
        { id: 5, name: '周六', shortName: '六' },
        { id: 6, name: '周日', shortName: '日' }
    ];

    // 获取当天是周几，设置默认选中
    useEffect(() => {
        const today = new Date().getDay();
        // JavaScript getDay() 返回 0-6，0是周日，1是周一
        const currentDay = today === 0 ? 6 : today - 1; // 转换为我们的 0-6 格式
        setSelectedDay(currentDay);
    }, []);

    // 获取日历数据
    const fetchCalendarData = async () => {
        setIsLoading(true);
        try {
            // 模拟API延迟
            await new Promise(resolve => setTimeout(resolve, 1000));

            // 模拟数据
            const mockData: CalendarAnime[] = [
                {
                    id: 1,
                    name: "咒术回战",
                    name_cn: "咒术回战",
                    summary: "描述一个充满咒术的世界...",
                    images: {
                        large: "/images/anime1.jpg",
                        medium: "/images/anime1.jpg",
                        small: "/images/anime1.jpg"
                    },
                    air_date: "2024-01-08",
                    air_weekday: selectedDay + 1,
                    rating: {
                        total: 1000,
                        count: {},
                        score: 8.5
                    }
                },
                {
                    id: 2,
                    name: "鬼灭之刃",
                    name_cn: "鬼灭之刃",
                    summary: "讲述了鬼杀队的故事...",
                    images: {
                        large: "/images/anime2.jpg",
                        medium: "/images/anime2.jpg",
                        small: "/images/anime2.jpg"
                    },
                    air_date: "2024-01-08",
                    air_weekday: selectedDay + 1,
                    rating: {
                        total: 1500,
                        count: {},
                        score: 9.0
                    }
                }
            ];

            setCalendarData(mockData);
        } catch (error) {
            console.error('获取日历数据失败:', error);
            setCalendarData([]);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchCalendarData();
    }, [selectedDay]);

    const handleSearch = () => {
        console.log('搜索番剧:', searchQuery);
    };

    const filteredAnime = calendarData.filter(anime =>
        anime.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        anime.name_cn.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className={`bg-white/10 backdrop-blur-md rounded-lg p-4 h-full ${className}`}>
            {/* 搜索栏 */}
            <div className="mb-4">
                <Search
                    placeholder="搜索番剧..."
                    value={searchQuery}
                    onChange={setSearchQuery}
                    onSearch={handleSearch}
                    variant="glassmorphism"
                    className="w-full"
                />
            </div>

            {/* 星期选择 */}
            <div className="mb-4">
                <div className="flex flex-wrap gap-1">
                    {weekdays.map((day) => (
                        <button
                            key={day.id}
                            onClick={() => setSelectedDay(day.id)}
                            className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${selectedDay === day.id
                                ? 'bg-blue-500 text-white shadow-lg'
                                : 'bg-white/20 text-white/80 hover:bg-white/30'
                                }`}
                        >
                            {day.shortName}
                        </button>
                    ))}
                </div>
            </div>

            {/* 当前选中日期标题 */}
            <div className="mb-4">
                <h3 className="text-lg font-semibold text-white">
                    {weekdays[selectedDay].name}新番
                </h3>
                <div className="w-full h-px bg-white/20 mt-2"></div>
            </div>

            {/* 番剧列表 */}
            <div className="flex-1 overflow-y-auto">
                {isLoading ? (
                    <div className="flex items-center justify-center py-8">
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                        <span className="ml-2 text-white/80 text-sm">加载中...</span>
                    </div>
                ) : filteredAnime.length === 0 ? (
                    <div className="text-center py-8 text-white/60">
                        <svg className="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6 0a4 4 0 01-4-4V7a4 4 0 118 0v1a4 4 0 01-4 4z" />
                        </svg>
                        <p className="text-sm">暂无番剧</p>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {filteredAnime.map((anime) => (
                            <div
                                key={anime.id}
                                className="flex items-center space-x-3 p-3 bg-white/10 rounded-lg hover:bg-white/20 transition-all duration-200 cursor-pointer group"
                            >
                                {/* 封面 */}
                                <div className="flex-shrink-0">
                                    <div className="w-12 h-16 bg-gray-300/20 rounded overflow-hidden">
                                        <img
                                            src={anime.images.small}
                                            alt={anime.name_cn || anime.name}
                                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                                            onError={(e) => {
                                                const target = e.target as HTMLImageElement;
                                                target.src = '/images/placeholder-anime.jpg';
                                            }}
                                        />
                                    </div>
                                </div>

                                {/* 标题 */}
                                <div className="flex-1 min-w-0">
                                    <h4 className="text-white font-medium text-sm line-clamp-2 group-hover:text-blue-200 transition-colors">
                                        {anime.name_cn || anime.name}
                                    </h4>
                                    {anime.rating.score > 0 && (
                                        <div className="flex items-center mt-1">
                                            <span className="text-yellow-400 text-xs">★</span>
                                            <span className="text-white/70 text-xs ml-1">{anime.rating.score}</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};