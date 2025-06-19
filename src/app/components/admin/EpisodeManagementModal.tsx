import React, { useState, useEffect, useRef, use } from 'react';
import { Trash2, Edit2, Download, Play, FileVideo, File, RefreshCw } from 'lucide-react';
import { Button } from '@/ui/Button';
import { Table } from '@/ui/Table';
import { Modal } from '@/ui/Modal';
import { message } from '@/ui/Message';
import { Input } from '@/ui/Input';
import { pikpakApi } from '@/services/pikpak';
import { EpisodeFile } from '@/services/types';

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
    // 静态数据
    // const [episodes, setEpisodes] = useState<EpisodeFile[]>([
    //     {
    //         id: '1',
    //         name: '第1集.mkv',
    //         size: 1024 * 1024 * 10,
    //         kind: 'video',
    //         created_time: '2021-10-10T10:10:10Z',
    //         mime_type: 'video/x-matroska',
    //         play_url: 'https://www.bilibili.com/video/BV1inTSzqEYJ/?spm_id_from=333.1007.tianma.1-1-1.click',
    //         hash: '1234567890',
    //         is_video: true
    //     },
    //     {
    //         id: '2',
    //         name: '第2集.mkv',
    //         size: 1024 * 1024 * 10,
    //         kind: 'video',
    //         created_time: '2021-10-10T10:10:10Z',
    //         mime_type: 'video/x-matroska',
    //         play_url: 'https://via.placeholder.com/150',
    //         hash: '1234567890',
    //         is_video: true
    //     },
    //     {
    //         id: '3',
    //         name: '第3集.mkv',
    //         size: 1024 * 1024 * 10,
    //         kind: 'video',
    //         created_time: '2021-10-10T10:10:10Z',
    //         mime_type: 'video/x-matroska',
    //         play_url: 'https://via.placeholder.com/150',
    //         hash: '1234567890',
    //         is_video: true
    //     },
    //     {
    //         id: '4',
    //         name: '第4集.mkv',
    //         size: 1024 * 1024 * 10,
    //         kind: 'video',
    //         created_time: '2021-10-10T10:10:10Z',
    //         mime_type: 'video/x-matroska',
    //         play_url: 'https://via.placeholder.com/150',
    //         hash: '1234567890',
    //         is_video: true
    //     },
    //     {
    //         id: '5',
    //         name: '第5集.mkv',
    //         size: 1024 * 1024 * 10,
    //         kind: 'video',
    //         created_time: '2021-10-10T10:10:10Z',
    //         mime_type: 'video/x-matroska',
    //         play_url: 'https://via.placeholder.com/150',
    //         hash: '1234567890',
    //         is_video: true
    //     }
    // ]);
    const [loading, setLoading] = useState(false);
    const [selectedIds, setSelectedIds] = useState<string[]>([]);
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
    const [isRenameModalOpen, setIsRenameModalOpen] = useState(false);
    const [currentRenameFile, setCurrentRenameFile] = useState<EpisodeFile | null>(null);
    const [newFileName, setNewFileName] = useState('');
    const [lastRequestTime, setLastRequestTime] = useState<number>(0);
    const [cacheInfo, setCacheInfo] = useState<string>('');

    const requestTimeoutRef = useRef<NodeJS.Timeout>();

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

    // 新窗口播放动漫
    const handlePlayAnime = (episode: EpisodeFile) => {
        console.log("将要播放的连接：", episode.play_url);

        if (!episode.play_url) {
            message.warning('暂无播放链接');
            return;
        }
        window.open(episode.play_url, '_blank');
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
        // size: (
        //     <span className="text-sm text-gray-600">
        //         {formatFileSize(episode.size)}
        //     </span>
        // ),
        // time: (
        //     <span className="text-sm text-gray-600">
        //         {formatTime(episode.created_time)}
        //     </span>
        // ),
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
                <div className="p-6">
                    {/* 缓存状态信息 */}
                    {/* <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                        <div className="flex items-center justify-between">
                            <div className="text-sm text-blue-700">
                                <span className="font-medium">数据状态：</span>
                                {cacheInfo} {getCacheStatusInfo()}
                            </div>
                            <div className="text-xs text-blue-600">
                                缓存有效期: 5分钟，防抖间隔: 2秒
                            </div>
                        </div>
                    </div> */}

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
                        {/* <div className="flex items-center space-x-2">
                            <Button
                                variant="primary"
                                onClick={handleForceRefresh}
                                disabled={loading}
                                className="flex items-center space-x-2 text-sm"
                            >
                                <span>刷新</span>
                            </Button>
                        </div> */}
                    </div>

                    {/* 统计信息 */}
                    <div className="bg-gray-50 rounded-lg p-4 mb-4">
                        <div className="grid gap-4 text-center">
                            <div>
                                <div className="text-xl font-bold text-blue-600">{episodes.length}</div>
                                <div className="text-xs text-gray-600">总文件数</div>
                            </div>
                            {/* <div>
                                <div className="text-xl font-bold text-purple-600">
                                    {formatFileSize(episodes.reduce((total, ep) => total + ep.size, 0))}
                                </div>
                                <div className="text-xs text-gray-600">总大小</div>
                            </div> */}
                        </div>
                    </div>

                    {/* 文件列表 */}
                    <div className="border rounded-lg overflow-hidden">
                        <Table
                            columns={columns}
                            data={tableData}
                            loading={loading}
                            emptyText="暂无文件"
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
                            variant="secondary"
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
                            variant="secondary"
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
        </>
    );
};