'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/ui/Button';
import { Input } from '@/ui/Input';
import { message } from '@/ui/Message';
import { Loading } from '@/ui/Loading';
import { pikpakApi } from '@/services/pikpak';
import { AnimeSearchResult } from '@/services/types';

interface AnimeGroup {
    title: string;
    animes: AnimeSearchResult[];
}

interface DownloadConfigModalProps {
    isOpen: boolean;
    onClose: () => void;
    selectedAnimes: AnimeSearchResult[];
    onConfirm: () => void;
}

export const DownloadConfigModal: React.FC<DownloadConfigModalProps> = ({
    isOpen,
    onClose,
    selectedAnimes,
    onConfirm
}) => {
    const [hasMultipleSeasons, setHasMultipleSeasons] = useState(false);
    const [animeGroups, setAnimeGroups] = useState<AnimeGroup[]>([]);
    const [singleTitle, setSingleTitle] = useState('');
    const [isDownloading, setIsDownloading] = useState(false);

    // 重置状态
    useEffect(() => {
        if (isOpen) {
            setHasMultipleSeasons(false);
            setAnimeGroups([{ title: '', animes: [] }]);
            setSingleTitle('');
            setIsDownloading(false);
        }
    }, [isOpen]);

    // 处理多季切换
    const handleMultipleSeasonChange = (checked: boolean) => {
        setHasMultipleSeasons(checked);
        if (checked) {
            // 初始化一个空的分组
            setAnimeGroups([{ title: '', animes: [] }]);
        }
    };

    // 添加新的动漫分组
    const addAnimeGroup = () => {
        setAnimeGroups([...animeGroups, { title: '', animes: [] }]);
    };

    // 删除动漫分组
    const removeAnimeGroup = (index: number) => {
        if (animeGroups.length > 1) {
            const newGroups = animeGroups.filter((_, i) => i !== index);
            setAnimeGroups(newGroups);
        }
    };

    // 更新分组标题
    const updateGroupTitle = (index: number, title: string) => {
        const newGroups = [...animeGroups];
        newGroups[index].title = title;
        setAnimeGroups(newGroups);
    };

    // 切换动漫归属分组
    const toggleAnimeInGroup = (groupIndex: number, anime: AnimeSearchResult) => {
        const newGroups = [...animeGroups];

        // 先从所有分组中移除这个动漫
        newGroups.forEach(group => {
            group.animes = group.animes.filter(a => a.id !== anime.id);
        });

        // 检查当前分组是否已包含这个动漫
        const currentGroup = newGroups[groupIndex];
        const isAlreadyInGroup = currentGroup.animes.some(a => a.id === anime.id);

        if (!isAlreadyInGroup) {
            // 添加到当前分组
            currentGroup.animes.push(anime);
        }

        setAnimeGroups(newGroups);
    };

    // 检查动漫是否在指定分组中
    const isAnimeInGroup = (groupIndex: number, animeId: string) => {
        return animeGroups[groupIndex]?.animes.some(a => a.id === animeId) || false;
    };

    // 验证配置
    const validateConfig = (): string | null => {
        if (hasMultipleSeasons) {
            // 检查是否有空标题的分组
            for (let i = 0; i < animeGroups.length; i++) {
                if (!animeGroups[i].title.trim()) {
                    return `第 ${i + 1} 个分组的标题不能为空`;
                }
            }

            // 检查是否有动漫未分配到任何分组
            const assignedAnimes = new Set();
            animeGroups.forEach(group => {
                group.animes.forEach(anime => assignedAnimes.add(anime.id));
            });

            const unassignedAnimes = selectedAnimes.filter(anime => !assignedAnimes.has(anime.id));
            if (unassignedAnimes.length > 0) {
                return `还有 ${unassignedAnimes.length} 个动漫未分配到任何分组`;
            }

            // 检查是否有分组没有动漫
            const emptyGroups = animeGroups.filter(group => group.animes.length === 0);
            if (emptyGroups.length > 0) {
                return `有 ${emptyGroups.length} 个分组没有分配任何动漫`;
            }
        } else {
            if (!singleTitle.trim()) {
                return '标题不能为空';
            }
        }

        return null;
    };

    // 处理确认下载
    const handleConfirmDownload = async () => {
        const errorMsg = validateConfig();
        if (errorMsg) {
            message.error(errorMsg);
            return;
        }

        // 获取PikPak配置
        const pikpakUsername = localStorage.getItem('pikpak_username');
        const pikpakPassword = localStorage.getItem('pikpak_password');

        if (!pikpakUsername || !pikpakPassword) {
            message.error('请先配置PikPak账号信息');
            return;
        }

        setIsDownloading(true);

        try {
            let downloadData;

            if (hasMultipleSeasons) {
                // 多季模式：按分组下载
                downloadData = {
                    username: pikpakUsername,
                    password: pikpakPassword,
                    mode: 'multiple_seasons',
                    groups: animeGroups.map(group => ({
                        title: group.title,
                        anime_list: group.animes
                    }))
                };
            } else {
                // 单季模式：所有动漫归到一个标题下
                downloadData = {
                    username: pikpakUsername,
                    password: pikpakPassword,
                    mode: 'single_season',
                    title: singleTitle,
                    anime_list: selectedAnimes
                };
            }

            console.log("将要请求的下载动漫数据：", downloadData);

            const result = await pikpakApi.download(downloadData);

            if (result.success) {
                message.success('下载配置已提交，开始下载任务');
                onConfirm();
                handleClose();
            } else {
                message.error(`下载失败: ${result.message}`);
            }

        } catch (error) {
            console.error('下载失败:', error);
        } finally {
            setIsDownloading(false);
        }
    };

    // 关闭弹窗
    const handleClose = () => {
        if (!isDownloading) {
            onClose();
        }
    };

    // 冒泡处理
    const handleModalClick = (e: React.MouseEvent) => {
        e.stopPropagation();
    };

    if (!isOpen) return null;

    return (
        <div
            className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-[60] p-4"
        >
            <div
                className="bg-white rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden border-2 border-gray-100 transform transition-all duration-300 animate-in zoom-in-95"
            >
                {/* 模态框头部 */}
                <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-gradient-to-r from-blue-50 to-indigo-50">
                    <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
                            </svg>
                        </div>
                        <h2 className="text-xl font-semibold text-gray-900">下载配置</h2>
                    </div>
                    <button
                        onClick={handleClose}
                        className="text-gray-400 hover:text-gray-600 text-2xl font-light"
                        disabled={isDownloading}
                    >
                        ×
                    </button>
                </div>

                {/* 下载中遮罩 */}
                {isDownloading && (
                    <div className="absolute inset-0 bg-white/90 flex items-center justify-center z-10">
                        <div className="text-center">
                            <Loading
                                variant="spinner"
                                size="large"
                                color="primary"
                                text="正在提交下载任务..."
                            />
                        </div>
                    </div>
                )}

                {/* 模态框内容 */}
                <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
                    {/* 基本信息 */}
                    <div className="mb-6">
                        <h3 className="text-lg font-medium text-gray-900 mb-2">
                            已选择 {selectedAnimes.length} 个动漫资源
                        </h3>

                        {/* 多季选项 */}
                        <div className="flex items-center space-x-2 mb-4">
                            <input
                                type="checkbox"
                                id="hasMultipleSeasons"
                                checked={hasMultipleSeasons}
                                onChange={(e) => handleMultipleSeasonChange(e.target.checked)}
                                disabled={isDownloading}
                                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                            />
                            <label htmlFor="hasMultipleSeasons" className="text-sm font-medium text-gray-700">
                                包含多季（需要分组管理）
                            </label>
                        </div>
                    </div>

                    {/* 单季模式 */}
                    {!hasMultipleSeasons && (
                        <div className="space-y-4">
                            <div>
                                <Input
                                    label="动漫标题"
                                    placeholder="请输入动漫标题，例如：药屋少女的呢喃"
                                    value={singleTitle}
                                    onChange={(e) => setSingleTitle(e.target.value)}
                                    disabled={isDownloading}
                                />
                            </div>

                            <div className="bg-gray-50 rounded-lg p-4">
                                <h4 className="font-medium text-gray-900 mb-2">
                                    将要下载的动漫 ({selectedAnimes.length} 个)：
                                </h4>
                                <div className="space-y-2 max-h-40 overflow-y-auto">
                                    {selectedAnimes.map((anime) => (
                                        <div key={anime.id} className="text-sm text-gray-600 bg-white p-2 rounded">
                                            {anime.title}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* 多季模式 */}
                    {hasMultipleSeasons && (
                        <div className="space-y-6">
                            {/* 分组管理 */}
                            {animeGroups.map((group, groupIndex) => (
                                <div key={groupIndex} className="border border-gray-200 rounded-lg p-4">
                                    <div className="flex items-center justify-between mb-4">
                                        <h4 className="font-medium text-gray-900">
                                            分组 {groupIndex + 1}
                                        </h4>
                                        {animeGroups.length > 1 && (
                                            <Button
                                                variant="danger"
                                                className="text-xs px-2 py-1"
                                                onClick={() => removeAnimeGroup(groupIndex)}
                                                disabled={isDownloading}
                                            >
                                                删除分组
                                            </Button>
                                        )}
                                    </div>

                                    <div className="mb-4">
                                        <Input
                                            label="分组标题"
                                            placeholder="例如：药屋少女的呢喃第一季"
                                            value={group.title}
                                            onChange={(e) => updateGroupTitle(groupIndex, e.target.value)}
                                            disabled={isDownloading}
                                        />
                                    </div>

                                    <div className="mb-4">
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            选择归属此分组的动漫 ({group.animes.length} 个已选择)：
                                        </label>
                                        <div className="space-y-2 max-h-48 overflow-y-auto border border-gray-200 rounded p-3">
                                            {selectedAnimes.map((anime) => (
                                                <label
                                                    key={anime.id}
                                                    className="flex items-start space-x-2 cursor-pointer hover:bg-gray-50 p-2 rounded"
                                                >
                                                    <input
                                                        type="checkbox"
                                                        checked={isAnimeInGroup(groupIndex, anime.id)}
                                                        onChange={() => toggleAnimeInGroup(groupIndex, anime)}
                                                        disabled={isDownloading}
                                                        className="mt-1 w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                                                    />
                                                    <span className="text-sm text-gray-700 flex-1">
                                                        {anime.title}
                                                    </span>
                                                </label>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            ))}

                            {/* 添加分组按钮 */}
                            <Button
                                variant="info"
                                onClick={addAnimeGroup}
                                disabled={isDownloading}
                                className="w-full"
                            >
                                + 添加新分组
                            </Button>
                        </div>
                    )}
                </div>

                {/* 模态框底部 */}
                <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
                    <Button
                        variant="info"
                        onClick={handleClose}
                        className="bg-gray-500 hover:bg-gray-600"
                        disabled={isDownloading}
                    >
                        取消
                    </Button>
                    <Button
                        variant="success"
                        onClick={handleConfirmDownload}
                        disabled={isDownloading}
                    >
                        确认下载
                    </Button>
                </div>
            </div>
        </div>
    );
};