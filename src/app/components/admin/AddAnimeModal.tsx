'use client';

import React, { useState } from 'react';
import { Button } from '@/ui/Button';
import { Search } from '@/ui/Search';
import { message } from '@/ui/Message';
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

    // 分页状态
    const [currentPage, setCurrentPage] = useState(1);
    const pageSize = 24; // 每页显示24个

    // 下载配置弹窗状态
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
        setSelectedAnimes(new Set());
        setCurrentPage(1); // 重置到第一页

        try {
            const response = await animeApi.search({ name: searchQuery });
            const data = response.data || [];
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

    // 生成分页按钮
    const generatePageNumbers = () => {
        const pages = [];
        const maxVisible = 7; // 最多显示7个页码按钮

        if (totalPages <= maxVisible) {
            // 总页数不多，显示全部
            for (let i = 1; i <= totalPages; i++) {
                pages.push(i);
            }
        } else {
            // 总页数较多，智能显示
            if (currentPage <= 4) {
                // 当前页在前面
                for (let i = 1; i <= 5; i++) pages.push(i);
                pages.push('...');
                pages.push(totalPages);
            } else if (currentPage >= totalPages - 3) {
                // 当前页在后面
                pages.push(1);
                pages.push('...');
                for (let i = totalPages - 4; i <= totalPages; i++) pages.push(i);
            } else {
                // 当前页在中间
                pages.push(1);
                pages.push('...');
                for (let i = currentPage - 1; i <= currentPage + 1; i++) pages.push(i);
                pages.push('...');
                pages.push(totalPages);
            }
        }
        return pages;
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

    // 当前页全选/全不选
    const handleSelectAllCurrentPage = () => {
        const currentPageIds = currentPageResults.map(anime => String(anime.id));
        const newSelected = new Set(selectedAnimes);

        // 检查当前页是否全部已选
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

    // 全局全选/全不选
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

        const pikpakUsername = localStorage.getItem('pikpak_username');
        const pikpakPassword = localStorage.getItem('pikpak_password');

        if (!pikpakUsername || !pikpakPassword) {
            message.error('请先配置PikPak账号信息');
            return;
        }

        const selectedResults = searchResults.filter(anime => selectedAnimes.has(String(anime.id)));
        setSelectedAnimesForDownload(selectedResults);
        setIsDownloadConfigOpen(true);
    };

    // 下载配置完成
    const handleDownloadConfirm = () => {
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
        setCurrentPage(1);
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
            >
                <div
                    className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden"
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
                    <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
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
                                    {/* 结果统计和操作栏 */}
                                    <div className="flex items-center justify-between mb-4">
                                        <div className="flex items-center space-x-4">
                                            <h3 className="text-lg font-medium text-gray-900">
                                                搜索结果 ({searchResults.length} 个)
                                            </h3>
                                            <span className="text-sm text-gray-600">
                                                第 {currentPage} 页，共 {totalPages} 页
                                            </span>
                                        </div>
                                        <div className="flex items-center space-x-4">
                                            <span className="text-sm text-gray-600">
                                                已选择 {selectedAnimes.size} 个
                                            </span>
                                            <button
                                                onClick={handleSelectAllCurrentPage}
                                                className="text-sm text-blue-600 hover:text-blue-800"
                                            >
                                                {currentPageResults.every(anime => selectedAnimes.has(String(anime.id)))
                                                    ? '取消当前页' : '选择当前页'}
                                            </button>
                                            <button
                                                onClick={handleSelectAll}
                                                className="text-sm text-blue-600 hover:text-blue-800"
                                            >
                                                {selectedAnimes.size === searchResults.length ? '全不选' : '全选'}
                                            </button>
                                        </div>
                                    </div>

                                    {/* 结果列表 */}
                                    <div className="space-y-3 mb-6">
                                        {currentPageResults.map((anime) => (
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
                                                        className="mt-1 w-4 h-4 text-blue-600 rounded focus:ring-blue-500 flex-shrink-0"
                                                    />
                                                    <div className="flex-1 min-w-0">
                                                        {/* 标题 */}
                                                        <h4 className="font-medium text-gray-900 mb-3 text-sm leading-5 break-words">
                                                            {anime.title}
                                                        </h4>
                                                        {/* 磁力链接预览 */}
                                                        <div className="bg-gray-100 rounded p-2">
                                                            <p className="text-xs text-gray-600 font-mono break-all">
                                                                磁力: {anime.magnet.substring(0, 100)}...
                                                            </p>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>

                                    {/* 分页控件 */}
                                    {totalPages > 1 && (
                                        <div className="flex items-center justify-center space-x-2">
                                            {/* 上一页 */}
                                            <button
                                                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                                                disabled={currentPage === 1}
                                                className="text-gray-900 px-3 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                                            >
                                                上一页
                                            </button>

                                            {/* 页码按钮 */}
                                            {generatePageNumbers().map((page, index) => (
                                                <button
                                                    key={index}
                                                    onClick={() => typeof page === 'number' && setCurrentPage(page)}
                                                    disabled={page === '...'}
                                                    className={`px-3 py-2 text-sm border rounded ${page === currentPage
                                                        ? 'bg-blue-500 text-white border-blue-500'
                                                        : page === '...'
                                                            ? 'text-gray-900 border-transparent cursor-default'
                                                            : 'text-gray-900 border-gray-300 hover:bg-gray-50'
                                                        }`}
                                                >
                                                    {page}
                                                </button>
                                            ))}

                                            {/* 下一页 */}
                                            <button
                                                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                                                disabled={currentPage === totalPages}
                                                className="text-gray-900 px-3 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                                            >
                                                下一页
                                            </button>

                                            {/* 跳转 */}
                                            <div className="flex items-center space-x-2 ml-4">
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