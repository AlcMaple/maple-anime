import React, { useState, useEffect, useRef, use } from 'react';
import { Trash2, Edit2, Download, Play, FileVideo, File, RefreshCw, Link } from 'lucide-react';

import { Button } from '@/ui/Button';
import { Table } from '@/ui/Table';
import { Modal } from '@/ui/Modal';
import { message } from '@/ui/Message';
import { Input } from '@/ui/Input';
import { Loading } from '@/ui/Loading';

import { pikpakApi } from '@/services/pikpak';
import { EpisodeFile } from '@/services/types';

import { ConfirmModal } from '@/components/admin/ConfirmModal';

interface EpisodeManagementModalProps {
    isOpen: boolean;
    onClose: () => void;
    animeId: string;
    animeTitle: string;
}

// 缓存接口
interface CacheItem {
    data: EpisodeFile[];
    timestamp: number;
    loading?: boolean;
}

// 缓存对象
const episodeCache = new Map<string, CacheItem>();
// 请求防抖
const REQUEST_DEBOUNCE_TIME = 2000;

export const EpisodeManagementModal: React.FC<EpisodeManagementModalProps> = ({
    isOpen,
    onClose,
    animeId,
    animeTitle
}) => {
    const [episodes, setEpisodes] = useState<EpisodeFile[]>([]);
    const [loading, setLoading] = useState(false);
    const [selectedIds, setSelectedIds] = useState<string[]>([]);
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
    const [isRenameModalOpen, setIsRenameModalOpen] = useState(false);
    const [currentRenameFile, setCurrentRenameFile] = useState<EpisodeFile | null>(null);
    const [newFileName, setNewFileName] = useState('');
    const [lastRequestTime, setLastRequestTime] = useState<number>(0);
    const [cacheInfo, setCacheInfo] = useState<string>('');
    const [isUpdateConfirmOpen, setIsUpdateConfirmOpen] = useState(false);

    // const requestTimeoutRef = useRef<NodeJS.Timeout>();

    // 从缓存获取数据
    const getFromCache = (animeId: string): CacheItem | null => {
        return episodeCache.get(animeId) || null;
    };

    // 设置缓存
    const setCache = (animeId: string, data: EpisodeFile[]) => {
        episodeCache.set(animeId, {
            data,
            timestamp: Date.now()
        });
    };

    // 清除缓存
    const clearCache = (animeId: string) => {
        episodeCache.delete(animeId);
    };

    // 检查请求频率
    const canMakeRequest = (): boolean => {
        const now = Date.now();
        return (now - lastRequestTime) >= REQUEST_DEBOUNCE_TIME;
    };

    // 加载集数列表
    const loadEpisodes = async (forceRefresh: boolean = false) => {
        // if (!isOpen || !animeId) return;

        // // 检查缓存
        // if (!forceRefresh) {
        //     const cached = getFromCache(animeId);
        //     if (cached) {
        //         setEpisodes(cached.data);
        //         setCacheInfo('数据来自缓存');
        //         message.success(`从缓存加载 ${cached.data.length} 个文件`);
        //         return;
        //     }
        // }

        // // 检查请求频率
        // if (!canMakeRequest()) {
        //     const remainingTime = Math.ceil((REQUEST_DEBOUNCE_TIME - (Date.now() - lastRequestTime)) / 1000);
        //     message.warning(`请求过于频繁，请等待 ${remainingTime} 秒后再试`);
        //     return;
        // }

        const pikpakUsername = localStorage.getItem('pikpak_username');
        const pikpakPassword = localStorage.getItem('pikpak_password');

        if (!pikpakUsername || !pikpakPassword) {
            message.error('请先配置PikPak账号信息');
            return;
        }

        // setLoading(true);
        // setLastRequestTime(Date.now());
        // setCacheInfo('正在从服务器获取数据...');

        try {
            const response = await pikpakApi.getEpisodeList({
                folder_id: animeId
            });

            if (response.success) {
                setEpisodes(response.data);
                // setCache(animeId, response.data); // 设置缓存
                // setCacheInfo('数据已更新并缓存');
                message.success(`成功加载 ${response.data.length} 个文件`);
            } else {
                message.error(response.message || '加载失败');
            }
        } catch (error) {
            console.error('加载集数失败:', error);
            const errorMessage = error instanceof Error ? error.message : '加载集数失败';

            // if (errorMessage.includes('too frequent')) {
            //     message.error('请求过于频繁，请稍后再试。建议使用缓存数据。');
            //     // 尝试从缓存获取数据（即使过期）
            //     const cached = episodeCache.get(animeId);
            //     if (cached) {
            //         setEpisodes(cached.data);
            //         setCacheInfo('使用过期缓存数据');
            //         message.info('使用缓存数据，请稍后刷新');
            //     }
            // } else {
            //     message.error(errorMessage);
            // }
            message.error(errorMessage)
        } finally {
            setLoading(false);
        }
    };

    // 刷新
    const handleForceRefresh = () => {
        clearCache(animeId);
        loadEpisodes(true);
    };

    // 当模态框打开时加载数据
    useEffect(() => {
        if (isOpen) {
            //     // 清除之前的定时器
            //     if (requestTimeoutRef.current) {
            //         clearTimeout(requestTimeoutRef.current);
            //     }

            //     // 延迟加载，避免快速切换
            //     requestTimeoutRef.current = setTimeout(() => {
            loadEpisodes(false);
            //         setSelectedIds([]);
            //     }, 100);
        }

        // return () => {
        //     if (requestTimeoutRef.current) {
        //         clearTimeout(requestTimeoutRef.current);
        //     }
        // };
    }, [isOpen, animeId]);

    // 格式化文件大小
    const formatFileSize = (bytes: number): string => {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    };

    // 格式化时间
    const formatTime = (timeStr: string): string => {
        return new Date(timeStr).toLocaleString('zh-CN');
    };

    // 全选/取消全选
    const handleSelectAll = (checked: boolean) => {
        if (checked) {
            setSelectedIds(episodes.map(ep => ep.id));
        } else {
            setSelectedIds([]);
        }
    };

    // 单选
    const handleSelectOne = (id: string, checked: boolean) => {
        if (checked) {
            setSelectedIds([...selectedIds, id]);
        } else {
            setSelectedIds(selectedIds.filter(selectedId => selectedId !== id));
        }
    };

    // 更新视频连接处理函数
    const handleUpdateVideoLink = async (episodeId: string) => {
        const episode = episodes.find(ep => ep.id === episodeId);
        if (!episode) {
            message.error('未找到对应的集数文件');
            return;
        }

        setLoading(true);
        try {
            const pikpakUsername = localStorage.getItem('pikpak_username');
            const pikpakPassword = localStorage.getItem('pikpak_password');

            message.info(`正在更新 "${episode.name}" 的视频连接...`);

            // 调用 API 更新视频连接
            const response = await pikpakApi.getVideoUrl({
                username: pikpakUsername || '',
                password: pikpakPassword || '',
                file_ids: [episodeId],
                folder_id: animeId
            });

            if (response.success && response.data) {
                const result = response.data.results[0];
                if (result.success) {
                    // 更新数据
                    const updatedEpisodes = episodes.map(ep => {
                        if (ep.id === episodeId) {
                            return {
                                ...ep,
                                play_url: result.play_url,
                                updated_time: result.updated_time
                            };
                        }
                        return ep;
                    });
                    setEpisodes(updatedEpisodes);
                    message.success(`"${episode.name}" 视频连接更新成功`);
                } else {
                    message.error(result.message || '更新失败');
                }
            }
            else {
                message.error(response.message || '更新失败');
            }
            message.success(`"${episode.name}" 视频连接更新成功`);
        } catch (error) {
            console.error('更新视频连接失败:', error);
            message.error(`更新 "${episode.name}" 视频连接失败`);
        } finally {
            setLoading(false);
        }
    };

    const [batchUpdateLoading, setBatchUpdateLoading] = useState(false);
    // 批量更新视频链接
    const confirmUpdateAllVideoLinks = async () => {
        if (episodes.length === 0) {
            message.warning('没有可更新的视频文件');
            return;
        }

        const pikpakUsername = localStorage.getItem('pikpak_username');
        const pikpakPassword = localStorage.getItem('pikpak_password');

        if (!pikpakUsername || !pikpakPassword) {
            message.error('请先配置PikPak账号信息');
            return;
        }

        setBatchUpdateLoading(true);
        try {
            message.info(`正在批量更新 ${episodes.length} 个视频连接...`);

            const allFileIds = episodes.map(ep => ep.id);

            // 调用 API 批量更新视频连接
            const response = await pikpakApi.getVideoUrl({
                username: pikpakUsername,
                password: pikpakPassword,
                file_ids: allFileIds,
                folder_id: animeId
            });

            if (response.success && response.data) {
                const { success_count, failed_count, results } = response.data;

                // 更新成功的视频数据
                const updatedEpisodes = episodes.map(ep => {
                    const result = (results as any[]).find(r => r.file_id === ep.id);
                    if (result && result.success) {
                        return {
                            ...ep,
                            play_url: result.play_url,
                            updated_time: result.updated_time
                        };
                    }
                    return ep;
                });

                setEpisodes(updatedEpisodes);

                // 显示结果消息
                if (success_count > 0 && failed_count > 0) {
                    message.success(`成功更新 ${success_count} 个视频连接，${failed_count} 个失败`);
                } else if (success_count > 0) {
                    message.success(`成功更新 ${success_count} 个视频连接`);
                } else {
                    message.error(`更新失败，${failed_count} 个视频连接更新失败`);
                }

                // 更新缓存
                setCache(animeId, updatedEpisodes);
            } else {
                message.error(response.message || '批量更新失败');
            }
        } catch (error) {
            console.error('批量更新视频连接失败:', error);
            message.error('批量更新视频连接失败');
        } finally {
            setBatchUpdateLoading(false);
        }
    };

    const handleUpdateAllVideoLinks = () => {
        setIsUpdateConfirmOpen(true);
    };

    const confirmBatchUpdate = () => {
        setIsUpdateConfirmOpen(false);
        confirmUpdateAllVideoLinks();
    };

    // 批量删除
    const handleBatchDelete = async () => {
        if (selectedIds.length === 0) {
            message.warning('请选择要删除的文件');
            return;
        }

        const pikpakUsername = localStorage.getItem('pikpak_username');
        const pikpakPassword = localStorage.getItem('pikpak_password');

        if (!pikpakUsername || !pikpakPassword) {
            message.error('请先配置PikPak账号信息');
            return;
        }

        setLoading(true);
        try {
            const response = await pikpakApi.deleteEpisodes({
                username: pikpakUsername,
                password: pikpakPassword,
                file_ids: selectedIds,
                folder_id: animeId
            });

            if (response.success) {
                message.success(`成功删除 ${response.deleted_count} 个文件`);
                setSelectedIds([]);
                setIsDeleteModalOpen(false);
                // // 清除缓存并重新加载
                // clearCache(animeId);
                loadEpisodes(true);
            } else {
                message.error(response.message || '删除失败');
            }
        } catch (error) {
            console.error('删除文件失败:', error);
            message.error('删除文件失败');
        } finally {
            setLoading(false);
        }
    };

    // 分离文件名和扩展名
    const getFileNameParts = (fileName: string) => {
        const lastDotIndex = fileName.lastIndexOf('.');
        if (lastDotIndex === -1) {
            return { name: fileName, extension: '' };
        }
        return {
            name: fileName.substring(0, lastDotIndex),
            extension: fileName.substring(lastDotIndex)
        };
    };

    // 重命名文件
    const handleRename = async () => {
        if (!currentRenameFile || !newFileName.trim()) {
            message.warning('请输入新文件名');
            return;
        }

        const pikpakUsername = localStorage.getItem('pikpak_username');
        const pikpakPassword = localStorage.getItem('pikpak_password');

        if (!pikpakUsername || !pikpakPassword) {
            message.error('请先配置PikPak账号信息');
            return;
        }

        setLoading(true);
        try {
            // 组合完整的文件名
            const { extension } = getFileNameParts(currentRenameFile.name);
            const fullFileName = newFileName.trim() + extension;
            const response = await pikpakApi.renameEpisode({
                username: pikpakUsername,
                password: pikpakPassword,
                file_id: currentRenameFile.id,
                new_name: fullFileName,
                folder_id: animeId
            });

            if (response.success) {
                message.success('文件重命名成功');
                setIsRenameModalOpen(false);
                setCurrentRenameFile(null);
                setNewFileName('');
                // 清除缓存并重新加载
                // clearCache(animeId);
                loadEpisodes(true);
            } else {
                message.error(response.message || '重命名失败');
            }
        } catch (error) {
            console.error('重命名失败:', error);
            message.error('重命名失败');
        } finally {
            setLoading(false);
        }
    };

    // 打开重命名模态框
    const openRenameModal = (file: EpisodeFile) => {
        setCurrentRenameFile(file);
        setNewFileName('');
        setIsRenameModalOpen(true);
    };

    // 获取缓存状态信息
    const getCacheStatusInfo = (): string => {
        const cached = episodeCache.get(animeId);
        if (cached) {
            const cacheTime = new Date(cached.timestamp).toLocaleString('zh-CN');
            return `缓存时间: ${cacheTime}`;
        }
        return '无缓存';
    };

    const [isPlayerModalOpen, setIsPlayerModalOpen] = useState(false);
    const [playerEpisode, setPlayerEpisode] = useState<EpisodeFile | null>(null);

    // 播放动漫
    const handlePlayAnime = (episode: EpisodeFile) => {
        console.log("将要播放的连接：", episode.play_url);

        if (!episode.play_url) {
            message.warning('暂无播放链接');
            return;
        }

        // 播放器模态框
        setPlayerEpisode(episode);
        setIsPlayerModalOpen(true);
    };

    // 表格列定义
    const columns = [
        {
            key: 'select',
            title: (
                <input
                    type="checkbox"
                    checked={episodes.length > 0 && selectedIds.length === episodes.length}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    className="rounded border-gray-300"
                />
            ),
            width: '8%'
        },
        { key: 'name', title: '文件名', width: '40%' },
        // { key: 'size', title: '文件大小', width: '12%' },
        // { key: 'time', title: '创建时间', width: '15%' },
        { key: 'updated_time', title: '更新时间', width: '12%' },
        { key: 'actions', title: '操作', width: '15%' }
    ];

    // 表格数据
    const tableData = episodes.map(episode => ({
        select: (
            <input
                type="checkbox"
                checked={selectedIds.includes(episode.id)}
                onChange={(e) => handleSelectOne(episode.id, e.target.checked)}
                className="rounded border-gray-300"
            />
        ),
        name: (
            <div className="flex items-center space-x-2">
                {episode.is_video ? (
                    <FileVideo className="w-4 h-4 text-blue-500" />
                ) : (
                    <File className="w-4 h-4 text-gray-400" />
                )}
                <span className="text-sm font-medium text-gray-900 truncate" title={episode.name}>
                    {episode.name}
                </span>
            </div>
        ),
        updated_time: (
            <span className="text-sm text-gray-600">
                {formatTime(episode.update_time || '')}
            </span>
        ),
        actions: (
            <div className="flex space-x-1">
                <Button
                    variant="info"
                    className="text-xs px-2 py-1"
                    onClick={() => openRenameModal(episode)}
                >
                    <Edit2 className="w-3 h-3" />
                </Button>
                {episode.play_url && (
                    <Button
                        variant="success"
                        className="text-xs px-2 py-1"
                        onClick={() => handlePlayAnime(episode)}
                    >
                        <Play className="w-3 h-3" />
                    </Button>
                )}
                <Button
                    variant="warning"
                    className="text-xs px-2 py-1"
                    onClick={() => handleUpdateVideoLink(episode.id)}
                    disabled={loading}
                    title="更新视频连接"
                >
                    <Link className="w-3 h-3" />
                </Button>
            </div>
        )
    }));

    return (
        <>
            <Modal
                isOpen={isOpen}
                onClose={onClose}
                title={`${animeTitle}`}
                size="xl"
            >
                <div className="p-6 relative">
                    {batchUpdateLoading && (
                        <div className="absolute inset-0 bg-white/90 flex items-start pt-24 justify-center z-50 rounded-lg">
                            <div className="text-center">
                                <div className="flex flex-col items-center gap-4">
                                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                                    <div className="text-lg font-medium text-gray-800">正在批量更新视频链接</div>
                                    <div className="text-sm text-gray-600 max-w-md">
                                        此过程可能需要几分钟时间，系统会每处理3个文件延时8秒以保护服务器，请耐心等待...
                                    </div>
                                    <div className="text-xs text-gray-500">
                                        更新进度会在控制台显示，请勿关闭此窗口
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* 操作栏 */}
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                            <Button
                                variant="danger"
                                onClick={() => setIsDeleteModalOpen(true)}
                                disabled={selectedIds.length === 0}
                                className="flex items-center space-x-2 text-sm"
                            >
                                <span>删除 ({selectedIds.length})</span>
                            </Button>
                        </div>
                        <div className="flex items-center space-x-2">
                            <Button
                                variant="primary"
                                onClick={handleUpdateAllVideoLinks}
                                disabled={episodes.length === 0 || loading || batchUpdateLoading}
                            >
                                更新
                            </Button>
                        </div>
                    </div>

                    {/* 统计信息 */}
                    <div className="bg-gray-50 rounded-lg p-4 mb-4">
                        <div className="grid gap-4 text-center">
                            <div>
                                <div className="text-xl font-bold text-blue-600">{episodes.length}</div>
                                <div className="text-xs text-gray-600">总文件数</div>
                            </div>
                        </div>
                    </div>

                    {/* 文件列表 */}
                    <div className="border rounded-lg overflow-hidden">
                        <Table
                            columns={columns}
                            data={tableData}
                            loading={loading}
                        />
                    </div>
                </div>
            </Modal>

            {/* 删除确认模态框 */}
            <Modal
                isOpen={isDeleteModalOpen}
                onClose={() => setIsDeleteModalOpen(false)}
                title="确认删除"
                size="md"
            >
                <div className="p-6">
                    <p className="text-gray-700 mb-4">
                        确定要删除选中的 {selectedIds.length} 个文件吗？此操作不可恢复。
                    </p>
                    <div className="flex justify-end space-x-3">
                        <Button
                            variant="info"
                            onClick={() => setIsDeleteModalOpen(false)}
                        >
                            取消
                        </Button>
                        <Button
                            variant="danger"
                            onClick={handleBatchDelete}
                            disabled={loading}
                        >
                            确定
                        </Button>
                    </div>
                </div>
            </Modal>

            {/* 重命名模态框 */}
            <Modal
                isOpen={isRenameModalOpen}
                onClose={() => setIsRenameModalOpen(false)}
                title="重命名文件"
                size="md"
            >
                <div className="p-6">
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            原文件名
                        </label>
                        <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                            {currentRenameFile?.name}
                        </div>
                    </div>
                    <div className="mb-6">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            新文件名
                        </label>
                        <div className="relative">
                            <div className="flex items-stretch w-full border border-gray-300 rounded-md focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500">
                                <input
                                    type="text"
                                    value={newFileName}
                                    onChange={(e) => setNewFileName(e.target.value)}
                                    placeholder="请输入新文件名"
                                    className="flex-1 px-3 py-2 text-gray-900 text-sm border-0 rounded-l-md focus:outline-none focus:ring-0 bg-white"
                                />
                                <div className="px-3 py-2 bg-gray-50 text-gray-500 text-sm rounded-r-md border-l border-gray-200 flex items-center">
                                    {currentRenameFile ? getFileNameParts(currentRenameFile.name).extension : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="flex justify-end space-x-3">
                        <Button
                            variant="info"
                            onClick={() => setIsRenameModalOpen(false)}
                        >
                            取消
                        </Button>
                        <Button
                            variant="primary"
                            onClick={handleRename}
                            disabled={loading || !newFileName.trim()}
                        >
                            确定
                        </Button>
                    </div>
                </div>
            </Modal>

            {/* 播放器模态框 */}
            <Modal
                isOpen={isPlayerModalOpen}
                onClose={() => setIsPlayerModalOpen(false)}
                title={`播放: ${playerEpisode?.name}`}
                size="xl"
            >
                <div className="p-6">
                    {playerEpisode && (
                        <div className="space-y-4">
                            {/* 视频播放器 */}
                            <div className="bg-black rounded-lg overflow-hidden">
                                <video
                                    className="w-full h-96"
                                    controls
                                    autoPlay
                                    preload="metadata"
                                    onError={(e) => {
                                        console.error('视频播放错误:', e);
                                        message.error('视频播放失败，可能链接已过期');
                                    }}
                                    onLoadStart={() => {
                                        console.log('开始加载视频');
                                    }}
                                    onCanPlay={() => {
                                        console.log('视频可以播放');
                                    }}
                                >
                                    <source src={playerEpisode.play_url} type="video/mp4" />
                                    <source src={playerEpisode.play_url} type="video/webm" />
                                    <source src={playerEpisode.play_url} type="video/x-matroska" />
                                    您的浏览器不支持视频播放
                                </video>
                            </div>
                        </div>
                    )}
                </div>
            </Modal>

            {/* 批量更新确认弹窗 */}
            <ConfirmModal
                isOpen={isUpdateConfirmOpen}
                onClose={() => setIsUpdateConfirmOpen(false)}
                onConfirm={confirmBatchUpdate}
                title="确认批量更新视频链接"
                content={`即将批量更新 ${episodes.length} 个视频文件的播放链接，此过程可能需要几分钟时间，系统会每处理3个文件延时8秒以保护服务器。确定要继续吗？`}
                confirmText="开始更新"
                confirmVariant="warning"
                isLoading={batchUpdateLoading}
            />
        </>
    );
};