'use client';

import React, { useState } from 'react';
import { Button } from '@/ui/Button';
import { Input } from '@/ui/Input';
import { Search } from '@/ui/Search';
import { message } from '@/ui/Message';
import { Loading } from '@/ui/Loading';
import { animeApi } from '@/services/anime';
import { pikpakApi } from '@/services/pikpak';
import { AnimeSearchResult } from '@/services/types';

interface UpdateAnimeModalProps {
    isOpen: boolean;
    onClose: () => void;
    onUpdateComplete: () => void;
    currentAnime?: { id: string; title: string } | null; // 当前动漫信息，包含folder_id
}

export const UpdateAnimeModal: React.FC<UpdateAnimeModalProps> = ({
    isOpen,
    onClose,
    onUpdateComplete,
    currentAnime
}) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState<AnimeSearchResult[]>([]);
    const [isSearching, setIsSearching] = useState(false);
    const [selectedAnimes, setSelectedAnimes] = useState<Set<string>>(new Set());
    const [isUpdating, setIsUpdating] = useState(false);

    // 分页状态
    const [currentPage, setCurrentPage] = useState(1);
    const pageSize = 24; // 每页显示24个

    // 搜索动漫
    const handleSearch = async () => {
        if (!searchQuery.trim()) {
            message.warning('请输入动漫名称');
            return;
        }

        setIsSearching(true);
        setSearchResults([]);
        setSelectedAnimes(new Set());
        setCurrentPage(1);

        try {
            const data = await animeApi.search({ name: searchQuery });
            setSearchResults(data);

            if (data.length === 0) {
                message.info('没有找到相关动漫资源');
            } else {
                message.success(`找到 ${data.length} 个动漫资源`);
            }
        } catch (error) {
            console.error('搜索失败:', error);
        } finally {
            setIsSearching(false);
        }
    };

    // 分页计算
    const totalPages = Math.ceil(searchResults.length / pageSize);
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const currentPageResults = searchResults.slice(startIndex, endIndex);

    // 选择/取消选择动漫
    const handleToggleAnime = (animeId: string) => {
        const newSelected = new Set(selectedAnimes);
        if (newSelected.has(animeId)) {
            newSelected.delete(animeId);
        } else {
            newSelected.add(animeId);
        }
        setSelectedAnimes(newSelected);
    };

    // 全选当前页
    const handleSelectCurrentPage = () => {
        const currentPageIds = currentPageResults.map(anime => String(anime.id));
        const newSelected = new Set(selectedAnimes);

        const allCurrentPageSelected = currentPageIds.every(id => newSelected.has(id));

        if (allCurrentPageSelected) {
            // 取消选择当前页
            currentPageIds.forEach(id => newSelected.delete(id));
        } else {
            // 选择当前页全部
            currentPageIds.forEach(id => newSelected.add(id));
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

    // 更新动漫
    const handleUpdateAnime = async () => {
        console.log("开始更新动漫", currentAnime);

        if (!currentAnime) {
            message.error('缺少动漫信息');
            return;
        }

        if (selectedAnimes.size === 0) {
            message.warning('请先选择要新增的集数');
            return;
        }

        const pikpakUsername = localStorage.getItem('pikpak_username');
        const pikpakPassword = localStorage.getItem('pikpak_password');

        if (!pikpakUsername || !pikpakPassword) {
            message.error('请先配置PikPak账号信息');
            return;
        }

        setIsUpdating(true);

        try {
            const selectedResults = searchResults.filter(anime => selectedAnimes.has(String(anime.id)));
            const result = await pikpakApi.updateAnime({
                username: pikpakUsername,
                password: pikpakPassword,
                folder_id: currentAnime.id, // 使用当前动漫的ID作为folder_id
                anime_list: selectedResults
            });

            console.log("更新动漫响应：", result);

            if (result.success && result.data) {
                message.success(`成功为"${currentAnime.title}"新增 ${result.data.added_count} 个集数`);
                if (result.data.failed_count > 0) {
                    message.warning(`其中 ${result.data.failed_count} 个集数添加失败`);
                }
                onUpdateComplete();
                handleClose();
            } else {
                message.error(`更新失败: ${result.message || '未知错误'}`);
            }

        } catch (error) {
            console.error('更新失败:', error);
            message.error('更新失败');
        } finally {
            setIsUpdating(false);
        }
    };

    // 清理数据并关闭
    const handleClose = () => {
        if (!isUpdating) {
            setSearchQuery('');
            setSearchResults([]);
            setIsSearching(false);
            setSelectedAnimes(new Set());
            setCurrentPage(1);
            onClose();
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden relative">
                {/* 更新中遮罩 */}
                {isUpdating && (
                    <div className="absolute inset-0 bg-white/90 flex items-start justify-center pt-24 z-50 rounded-lg">
                        <div className="text-center">
                            <div className="flex flex-col items-center gap-4">
                                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                                <div className="text-lg font-medium text-gray-800">正在更新动漫...</div>
                            </div>
                        </div>
                    </div>
                )}

                {/* 模态框头部 */}
                <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                    <div>
                        <h2 className="text-xl font-semibold text-gray-900">更新动漫</h2>
                        {/* {currentAnime && (
                            <p className="text-sm text-gray-600 mt-1">为 "{currentAnime.title}" 添加新集数</p>
                        )} */}
                    </div>
                    <button
                        onClick={handleClose}
                        disabled={isUpdating}
                        className="text-gray-400 hover:text-gray-600 text-2xl font-light"
                    >
                        ×
                    </button>
                </div>

                {/* 模态框内容 */}
                <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
                    {/* 当前动漫信息 */}
                    {currentAnime && (
                        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                            <h3 className="text-lg font-medium text-blue-800 mb-2">要更新的动漫</h3>
                            <p className="text-blue-700">
                                <span className="font-medium">标题：</span>{currentAnime.title}
                            </p>
                            {/* <p className="text-blue-600 text-sm mt-1">
                                <span className="font-medium">文件夹ID：</span>{currentAnime.id}
                            </p> */}
                        </div>
                    )}

                    {/* 搜索区域 */}
                    <div className="mb-6">
                        <Search
                            placeholder="搜索动漫..."
                            value={searchQuery}
                            onChange={(value) => setSearchQuery(value)}
                            onSearch={handleSearch}
                            disabled={isSearching || isUpdating}
                        />
                    </div>

                    {/* 搜索结果区域 */}
                    <div className="space-y-4">
                        {searchResults.length > 0 && (
                            <div>
                                {/* 结果统计和操作栏 */}
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center space-x-4">
                                        <h3 className="text-lg font-medium text-gray-900">
                                            搜索结果 ({searchResults.length} 个)
                                        </h3>
                                        <div className="text-sm text-gray-600">
                                            已选择 {selectedAnimes.size} 个
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <Button
                                            variant="info"
                                            className="text-xs px-3 py-1"
                                            onClick={handleSelectCurrentPage}
                                            disabled={isUpdating}
                                        >
                                            {currentPageResults.every(anime => selectedAnimes.has(String(anime.id))) ? '取消当前页' : '选择当前页'}
                                        </Button>
                                        <Button
                                            variant="info"
                                            className="text-xs px-3 py-1"
                                            onClick={handleSelectAll}
                                            disabled={isUpdating}
                                        >
                                            {selectedAnimes.size === searchResults.length ? '全不选' : '全选'}
                                        </Button>
                                    </div>
                                </div>

                                {/* 动漫列表 */}
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
                                    {currentPageResults.map((anime) => (
                                        <div
                                            key={anime.id}
                                            className={`border rounded-lg p-3 cursor-pointer transition-all duration-200 ${selectedAnimes.has(String(anime.id))
                                                ? 'border-blue-500 bg-blue-50'
                                                : 'border-gray-200 hover:border-gray-300'
                                                }`}
                                            onClick={() => handleToggleAnime(String(anime.id))}
                                        >
                                            <div className="flex items-start space-x-2">
                                                <input
                                                    type="checkbox"
                                                    checked={selectedAnimes.has(String(anime.id))}
                                                    onChange={() => { }}
                                                    className="mt-1 rounded border-gray-300"
                                                />
                                                <div className="flex-1 min-w-0 min-h-[50px]">
                                                    <p className="text-sm font-medium text-gray-900 leading-tight break-words">
                                                        {anime.title}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                {/* 分页 */}
                                {totalPages > 1 && (
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center space-x-2">
                                            <Button
                                                variant="info"
                                                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                                                disabled={currentPage === 1 || isUpdating}
                                                className="text-sm px-3 py-1"
                                            >
                                                上一页
                                            </Button>
                                            <span className="text-sm text-gray-600">
                                                第 {currentPage} 页，共 {totalPages} 页
                                            </span>
                                            <Button
                                                variant="info"
                                                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                                                disabled={currentPage === totalPages || isUpdating}
                                                className="text-sm px-3 py-1"
                                            >
                                                下一页
                                            </Button>
                                        </div>
                                        <div className="flex items-center space-x-2">
                                            <span className="text-sm text-gray-600">跳转到</span>
                                            <input
                                                type="number"
                                                min="1"
                                                max={totalPages}
                                                value={currentPage}
                                                onChange={(e) => {
                                                    const page = parseInt(e.target.value);
                                                    if (page >= 1 && page <= totalPages) {
                                                        setCurrentPage(page);
                                                    }
                                                }}
                                                className="text-gray-900 w-16 px-2 py-1 text-sm border border-gray-300 rounded text-center"
                                                disabled={isUpdating}
                                            />
                                            <span className="text-sm text-gray-600">页</span>
                                        </div>
                                    </div>
                                )}
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
                        {selectedAnimes.size > 0 && `已选择 ${selectedAnimes.size} 个新集数`}
                    </div>
                    <div className="flex space-x-3">
                        <Button
                            variant="info"
                            onClick={handleClose}
                            disabled={isUpdating}
                        >
                            取消
                        </Button>
                        <Button
                            variant="primary"
                            onClick={handleUpdateAnime}
                            disabled={isUpdating}
                        >
                            更新
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
};