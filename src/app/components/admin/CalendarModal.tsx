'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/ui/Button';
import { Loading } from '@/ui/Loading';
import { message } from '@/ui/Message';
import { bangumiApi } from '@/services/bangumi';
import { CalendarDay, CalendarAnime } from '@/services/types';

interface CalendarModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export const CalendarModal: React.FC<CalendarModalProps> = ({
    isOpen,
    onClose
}) => {
    const [calendarData, setCalendarData] = useState<CalendarDay[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isRefreshing, setIsRefreshing] = useState(false);

    // 解析响应数据的通用函数
    const parseCalendarData = (responseData: any): CalendarDay[] => {
        // 获取数据
        if (Array.isArray(responseData)) {
            return responseData;
        }

        // 更新数据
        if (responseData && responseData.data && Array.isArray(responseData.data)) {
            return responseData.data;
        }

        // 其他情况
        return [];
    };

    // 加载当季新番数据
    const loadCalendarData = async () => {
        setIsLoading(true);

        try {
            const response = await bangumiApi.get();
            console.log("加载当季新番数据：", response);

            if (response.code == 200) {
                const parsedData = parseCalendarData(response.data);
                setCalendarData(parsedData);
            } else {
                message.error(`获取数据失败: ${response.msg}`);
            }
        } catch (error) {
            message.error('获取当季新番数据失败');
        } finally {
            setIsLoading(false);
        }
    };

    // 更新当季新番数据
    const updateCalendarData = async () => {
        setIsRefreshing(true);

        try {
            const response = await bangumiApi.update();
            if (response.code == 200) {
                const parsedData = parseCalendarData(response.data);
                console.log("更新后的当季新番数据：", parsedData);

                setCalendarData(parsedData);
                message.success('当季新番数据已更新');
            } else {
                message.error(`刷新数据失败: ${response.msg}`);
            }
        } catch (error) {
            message.error('刷新当季新番数据失败');
        } finally {
            setIsRefreshing(false);
        }
    };

    // 处理刷新
    const handleRefresh = () => {
        updateCalendarData();
    };

    // 组件打开时加载数据
    useEffect(() => {
        if (isOpen && calendarData.length === 0) {
            loadCalendarData();
        }
    }, [isOpen]);

    // 获取默认封面
    const getImageUrl = (anime: CalendarAnime) => {
        return anime.images?.medium || anime.images?.small || anime.images?.large || 'images/placeholder-anime.jpg';
    };

    if (!isOpen) return null;

    return (
        <div
            className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4"
        >
            <div
                className="bg-white rounded-lg shadow-2xl w-full max-w-7xl max-h-[90vh] overflow-hidden"
            >
                {/* 模态框头部 */}
                <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-gradient-to-r from-blue-50 to-indigo-50">
                    <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                        </div>
                        <div>
                            <h2 className="text-xl font-semibold text-gray-900">当季新番</h2>
                        </div>
                    </div>
                    <div className="flex items-center space-x-3">
                        <Button
                            variant="info"
                            onClick={handleRefresh}
                            className="flex items-center space-x-2"
                            disabled={isRefreshing}
                        >
                            <span className="text-sm">刷新</span>
                        </Button>
                        <button
                            onClick={onClose}
                            className="text-gray-400 hover:text-gray-600 text-2xl font-light"
                        >
                            ×
                        </button>
                    </div>
                </div>

                {/* 刷新中遮罩 */}
                {isRefreshing && (
                    <div className="absolute inset-0 bg-white/90 flex items-center justify-center z-10">
                        <Loading
                            variant="spinner"
                            size="large"
                            color="primary"
                            text="刷新当季新番数据中..."
                        />
                    </div>
                )}

                {/* 模态框内容 */}
                <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
                    {isLoading ? (
                        <div className="flex justify-center items-center py-20">
                            <Loading
                                variant="spinner"
                                size="large"
                                color="primary"
                                text="加载当季新番数据中..."
                            />
                        </div>
                    ) : calendarData.length === 0 ? (
                        <div className="text-center py-20 text-gray-500">
                            <div className="text-4xl mb-4">📅</div>
                            <p>暂无当季新番数据</p>
                        </div>
                    ) : (
                        /* 日历表格 */
                        <div className="grid grid-cols-7 gap-4">
                            {calendarData.map((day, dayIndex) => (
                                <div key={dayIndex} className="border border-gray-200 rounded-lg overflow-hidden">
                                    {/* 星期标题 */}
                                    <div className="bg-gray-100 px-3 py-2 text-center">
                                        <div className="font-medium text-gray-900 text-sm">
                                            {day.weekday.cn}
                                        </div>
                                        <div className="text-xs text-gray-600">
                                            {day.weekday.en}
                                        </div>
                                    </div>

                                    {/* 动漫列表 */}
                                    <div className="p-2 space-y-2 min-h-[200px] max-h-[400px] overflow-y-auto anime-list-scroll">
                                        {day.items.length === 0 ? (
                                            <div className="text-center text-gray-400 text-xs py-4">
                                                暂无新番
                                            </div>
                                        ) : (
                                            day.items.map((anime, animeIndex) => (
                                                <div
                                                    key={animeIndex}
                                                    className="relative group cursor-pointer rounded-md overflow-hidden hover:shadow-md transition-all duration-300"
                                                >
                                                    {/* 动漫封面 */}
                                                    <div className="relative aspect-[3/4] bg-gray-200">
                                                        <img
                                                            src={getImageUrl(anime)}
                                                            alt={anime.name_cn || anime.name}
                                                            className="w-full h-full object-cover"
                                                            onError={(e) => {
                                                                e.currentTarget.src = 'images/placeholder-anime.jpg';
                                                            }}
                                                        />

                                                        {/* 标题背景层 */}
                                                        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent p-2">
                                                            <div className="text-white text-xs font-medium leading-tight">
                                                                {anime.name_cn || anime.name}
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            ))
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* 模态框底部 */}
                <div className="px-6 py-4 border-t border-gray-200 flex justify-end items-center">
                    <Button
                        variant="info"
                        onClick={onClose}
                        className="bg-gray-500 hover:bg-gray-600"
                    >
                        关闭
                    </Button>
                </div>
            </div>
        </div>
    );
};