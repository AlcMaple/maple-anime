'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

import { Search } from '@/ui/Search';
import { CalendarAnime } from '@/services/types';
import { bangumiApi } from '@/services/bangumi';

interface AnimeScheduleProps {
    className?: string;
}

export const AnimeSchedule: React.FC<AnimeScheduleProps> = ({ className = '' }) => {
    const router = useRouter();
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedDay, setSelectedDay] = useState(0); // 0-6 对应周一到周日
    const [calendarList, setCalendarList] = useState<CalendarAnime[]>([]);
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

    // 获取当天是周几
    useEffect(() => {
        const today = new Date().getDay();
        // JavaScript getDay() 返回 0-6，0是周日，1是周一
        const currentDay = today === 0 ? 6 : today - 1; // 转换为 0-6 格式
        setSelectedDay(currentDay);
    }, []);

    // 获取日历数据
    const calendarData = async () => {
        setIsLoading(true);
        try {
            const response = await bangumiApi.get();
            console.log("用户端日历数据：", response.data);

            if (response.data && Array.isArray(response.data)) {
                // selectedDay: 0-6 对应周一到周日
                // API返回的weekday.id: 1-7 对应周一到周日
                const targetWeekdayId = selectedDay + 1;

                // 找到对应星期的数据
                const dayData = response.data.find(item =>
                    item.weekday && item.weekday.id === targetWeekdayId
                );

                if (dayData && dayData.items) {
                    // 转换数据格式匹配CalendarAnime类型
                    const formattedData: CalendarAnime[] = dayData.items.map((item: any) => ({
                        id: item.id,
                        name: item.name || '',
                        name_cn: item.name_cn || item.name || '',
                        summary: item.summary || '',
                        images: {
                            large: item.images?.large || '',
                            medium: item.images?.medium || '',
                            small: item.images?.small || ''
                        },
                        air_date: item.air_date || '',
                        air_weekday: targetWeekdayId,
                        rating: {
                            total: item.rating?.total || 0,
                            count: item.rating?.count || {},
                            score: item.rating?.score || 0
                        }
                    }));

                    setCalendarList(formattedData);
                } else {
                    setCalendarList([]);
                }
            } else {
                setCalendarList([]);
            }
        } catch (error) {
            console.error('获取日历数据失败:', error);
            setCalendarList([]);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        calendarData();
    }, [selectedDay]);

    const handleSearch = () => {
        console.log('搜索番剧:', searchQuery);
        router.push(`/search?q=${searchQuery}`);
    };

    return (
        <div className={`h-full p-6 ${className}`}>
            {/* 搜索栏 */}
            <div className="mb-6">
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
            <div className="mb-6">
                <div className="flex gap-2">
                    {weekdays.map((day) => (
                        <button
                            key={day.id}
                            onClick={() => setSelectedDay(day.id)}
                            className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${selectedDay === day.id
                                ? 'bg-blue-500 text-white shadow-lg'
                                : 'bg-white/15 text-white/80 hover:bg-white/25'
                                }`}
                        >
                            {day.shortName}
                        </button>
                    ))}
                </div>
            </div>

            {/* 番剧列表 */}
            <div className="flex-1 overflow-y-auto max-h-[60vh]">
                <div className="space-y-3">
                    {isLoading ? (
                        <div className="flex items-center justify-center py-8">
                            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                            <span className="ml-2 text-white/80 text-sm">加载中...</span>
                        </div>
                    ) : calendarList.length === 0 ? (
                        <div className="text-center py-8 text-white/60">
                            <svg className="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6 0a4 4 0 01-4-4V7a4 4 0 118 0v1a4 4 0 01-4 4z" />
                            </svg>
                            <p className="text-sm">暂无番剧</p>
                        </div>
                    ) : (
                        calendarList.map((anime) => (
                            <div
                                key={anime.id}
                                className="flex items-center space-x-3 p-3 rounded-lg hover:bg-white/10 transition-all duration-200 cursor-default group"
                            >
                                {/* 封面 */}
                                <div className="flex-shrink-0">
                                    <div className="w-12 h-16 bg-white/10 rounded overflow-hidden">
                                        <img
                                            src={anime.images.small}
                                            alt={anime.name_cn || anime.name}
                                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                                            onError={(e) => {
                                                const target = e.target as HTMLImageElement;
                                                target.src = '';
                                            }}
                                        />
                                    </div>
                                </div>

                                {/* 标题 */}
                                <div className="flex-1 min-w-0">
                                    <h4 className="text-white text-sm font-medium line-clamp-2 group-hover:text-blue-200 transition-colors">
                                        {anime.name_cn || anime.name}
                                    </h4>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};