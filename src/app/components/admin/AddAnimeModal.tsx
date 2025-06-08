'use client';

import React, { useState } from 'react';
import { Button } from '@/ui/Button';
import { Input } from '@/ui/Input';
import { Search } from '@/ui/Search';
import { message } from '@/ui/Message';
import { Loading } from '@/ui/Loading';
import { animeApi } from '@/services/anime';
import { DownloadConfigModal } from './DownloadConfigModal';
import { AnimeSearchResult } from '@/services/types';

interface AddAnimeModalProps {
    isOpen: boolean;
    onClose: () => void;
    onAddAnime: (anime: AnimeSearchResult) => void;
}

export const AddAnimeModal: React.FC<AddAnimeModalProps> = ({
    isOpen,
    onClose,
    onAddAnime
}) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState<AnimeSearchResult[]>([]);
    const [isSearching, setIsSearching] = useState(false);
    const [selectedAnimes, setSelectedAnimes] = useState<Set<string>>(new Set());

    // 新增下载配置弹窗状态
    const [isDownloadConfigOpen, setIsDownloadConfigOpen] = useState(false);
    const [selectedAnimesForDownload, setSelectedAnimesForDownload] = useState<AnimeSearchResult[]>([]);

    // 搜索动漫
    const handleSearch = async () => {
        if (!searchQuery.trim()) {
            message.warning('请输入动漫名称');
            return;
        }

        setIsSearching(true);
        setSearchResults([]);
        setSelectedAnimes(new Set()); // 清空之前的选择

        try {
            const data = await animeApi.search({ name: searchQuery });
            setSearchResults(data);

            if (data.length === 0) {
                message.info('没有找到相关动漫资源');
            }
        } catch (error) {
            console.error('搜索失败:', error);
        } finally {
            setIsSearching(false);
        }
    };

    // 处理复选框变化
    const handleCheckboxChange = (animeId: string) => {
        const newSelected = new Set(selectedAnimes);
        if (newSelected.has(animeId)) {
            newSelected.delete(animeId);
        } else {
            newSelected.add(animeId);
        }
        setSelectedAnimes(newSelected);
    };

    // 全选/全不选
    const handleSelectAll = () => {
        if (selectedAnimes.size === searchResults.length) {
            setSelectedAnimes(new Set());
        } else {
            setSelectedAnimes(new Set(searchResults.map(anime => String(anime.id))));
        }
    };

    // 打开下载配置弹窗
    const handleDownloadSelected = () => {
        if (selectedAnimes.size === 0) {
            message.warning('请先选择要下载的动漫');
            return;
        }

        // 获取PikPak配置
        const pikpakUsername = localStorage.getItem('pikpak_username');
        const pikpakPassword = localStorage.getItem('pikpak_password');

        if (!pikpakUsername || !pikpakPassword) {
            message.error('请先配置PikPak账号信息');
            return;
        }

        // 准备选中的动漫数据
        const selectedResults = searchResults.filter(anime => selectedAnimes.has(String(anime.id)));
        setSelectedAnimesForDownload(selectedResults);
        setIsDownloadConfigOpen(true);
    };

    // 下载配置完成
    const handleDownloadConfirm = () => {
        // 重置选择状态
        setSelectedAnimes(new Set());
        setSelectedAnimesForDownload([]);
        handleClose();
    };

    // 清理数据
    const handleClose = () => {
        setSearchQuery('');
        setSearchResults([]);
        setIsSearching(false);
        setSelectedAnimes(new Set());
        setIsDownloadConfigOpen(false);
        setSelectedAnimesForDownload([]);
        onClose();
    };

    // 冒泡处理
    const handleModalClick = (e: React.MouseEvent) => {
        e.stopPropagation();
    };

    if (!isOpen) return null;

    return (
        <>
            <div
                className={`fixed inset-0 bg-white/8 backdrop-blur-[0.3px] flex items-center justify-center z-50 p-4 transition-all duration-300 ${isDownloadConfigOpen ? 'opacity-30 pointer-events-none' : 'opacity-100'
                    }`}
                onClick={handleClose}
            >
                <div
                    className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
                    onClick={handleModalClick}
                >
                    {/* 模态框头部 */}
                    <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                        <h2 className="text-xl font-semibold text-gray-900">添加动漫</h2>
                        <button
                            onClick={handleClose}
                            className="text-gray-400 hover:text-gray-600 text-2xl font-light"
                        >
                            ×
                        </button>
                    </div>

                    {/* 模态框内容 */}
                    <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
                        {/* 搜索区域 */}
                        <div className="mb-6">
                            <h3 className="text-lg font-medium text-gray-900 mb-4">搜索动漫资源</h3>
                            <Search
                                placeholder="搜索动漫..."
                                value={searchQuery}
                                onChange={(value) => {
                                    setSearchQuery(value);
                                }}
                                onSearch={handleSearch}
                                disabled={isSearching}
                            />
                        </div>

                        {/* 搜索结果区域 */}
                        <div className="space-y-4">
                            {searchResults.length > 0 && (
                                <div>
                                    <div className="flex items-center justify-between mb-4">
                                        <h3 className="text-lg font-medium text-gray-900">
                                            搜索结果 ({searchResults.length} 个)
                                        </h3>
                                        <div className="flex items-center space-x-4">
                                            <span className="text-sm text-gray-600">
                                                已选择 {selectedAnimes.size} 个
                                            </span>
                                            <button
                                                onClick={handleSelectAll}
                                                className="text-sm text-blue-600 hover:text-blue-800"
                                            >
                                                {selectedAnimes.size === searchResults.length ? '全不选' : '全选'}
                                            </button>
                                        </div>
                                    </div>

                                    <div className="space-y-3 max-h-96 overflow-y-auto">
                                        {searchResults.map((anime, index) => (
                                            <div
                                                key={anime.id}
                                                className={`border rounded-lg p-4 transition-colors ${selectedAnimes.has(String(anime.id))
                                                    ? 'bg-blue-50 border-blue-200'
                                                    : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                                                    }`}
                                            >
                                                <div className="flex items-start space-x-3">
                                                    <input
                                                        type="checkbox"
                                                        checked={selectedAnimes.has(String(anime.id))}
                                                        onChange={() => handleCheckboxChange(String(anime.id))}
                                                        className="mt-1 w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                                                    />
                                                    <div className="flex-1">
                                                        <h4 className="font-medium text-gray-900 mb-2">
                                                            {anime.title}
                                                        </h4>
                                                        <p className="text-xs text-gray-500 break-all">
                                                            磁力链接: {anime.magnet.substring(0, 80)}...
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* 搜索中状态 */}
                            {isSearching && (
                                <div className="text-center py-12 text-gray-500">
                                    <div className="text-4xl mb-4">⏳</div>
                                    <p>正在搜索动漫资源...</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* 模态框底部 */}
                    <div className="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
                        <div className="text-sm text-gray-600">
                            {selectedAnimes.size > 0 && `已选择 ${selectedAnimes.size} 个动漫`}
                        </div>
                        <div className="flex space-x-3">
                            <Button
                                variant="info"
                                onClick={handleClose}
                                className="bg-gray-500 hover:bg-gray-600"
                            >
                                关闭
                            </Button>
                            <Button
                                variant="success"
                                onClick={handleDownloadSelected}
                                disabled={selectedAnimes.size === 0}
                                className=""
                            >
                                下载配置
                            </Button>
                        </div>
                    </div>
                </div>
            </div>

            {/* 下载配置弹窗 */}
            <DownloadConfigModal
                isOpen={isDownloadConfigOpen}
                onClose={() => setIsDownloadConfigOpen(false)}
                selectedAnimes={selectedAnimesForDownload}
                onConfirm={handleDownloadConfirm}
            />
        </>
    );
};