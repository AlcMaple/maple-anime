'use client';

import React, { useState } from 'react';
import { Button } from '@/ui/Button';
import { message } from '@/ui/Message';
import { pikpakApi } from '@/services/pikpak';
import { AnimeItem } from '@/services/types';

interface DeleteAnimeModalProps {
    isOpen: boolean;
    onClose: () => void;
    onDeleteComplete: () => void;
    anime: AnimeItem | null;
}

export const DeleteAnimeModal: React.FC<DeleteAnimeModalProps> = ({
    isOpen,
    onClose,
    onDeleteComplete,
    anime
}) => {
    const [isDeleting, setIsDeleting] = useState(false);

    // 确认删除
    const handleConfirmDelete = async () => {
        if (!anime) {
            message.error('缺少动漫信息');
            return;
        }

        const pikpakUsername = localStorage.getItem('pikpak_username');
        const pikpakPassword = localStorage.getItem('pikpak_password');

        if (!pikpakUsername || !pikpakPassword) {
            message.error('请先配置PikPak账号信息');
            return;
        }

        setIsDeleting(true);

        try {
            const result = await pikpakApi.deleteAnime({
                username: pikpakUsername,
                password: pikpakPassword,
                folder_id: anime.id,
            });

            if (result.success) {
                message.success(`成功删除动漫: ${anime.title}`);
                onDeleteComplete();
                onClose();
            } else {
                message.error(`删除失败: ${result.message || '未知错误'}`);
            }

        } catch (error) {
            console.error('删除动漫失败:', error);
            message.error('删除动漫失败');
        } finally {
            setIsDeleting(false);
        }
    };

    // 取消删除
    const handleCancel = () => {
        if (!isDeleting) {
            onClose();
        }
    };

    if (!isOpen || !anime) return null;

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full relative">
                {/* 删除中遮罩 */}
                {isDeleting && (
                    <div className="absolute inset-0 bg-white/90 flex items-center justify-center z-10 rounded-lg">
                        <div className="text-center">
                            <div className="flex flex-col items-center gap-4">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600"></div>
                                <div className="text-sm font-medium text-gray-800">正在删除动漫...</div>
                                <div className="text-xs text-gray-600">
                                    正在删除PikPak文件夹并同步数据库
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* 模态框头部 */}
                <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
                            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                        </div>
                        <h2 className="text-xl font-semibold text-gray-900">确认删除动漫</h2>
                    </div>
                    <button
                        onClick={handleCancel}
                        disabled={isDeleting}
                        className="text-gray-400 hover:text-gray-600 text-2xl font-light"
                    >
                        ×
                    </button>
                </div>

                {/* 模态框内容 */}
                <div className="p-6">
                    {/* 警告信息 */}
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                        <div className="flex items-start space-x-3">
                            <svg className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z" />
                            </svg>
                            <div>
                                <h3 className="text-sm font-medium text-red-800 mb-1">
                                    危险操作 - 此操作不可逆
                                </h3>
                                <p className="text-sm text-red-700">
                                    删除动漫将会永久删除PikPak中的所有文件和数据库记录，无法恢复。
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* 动漫信息 */}
                    <div className="mb-6">
                        <h3 className="text-sm font-medium text-gray-900 mb-3">将要删除的动漫：</h3>
                        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                            <div className="space-y-2">
                                <div>
                                    <span className="text-sm font-medium text-gray-700">标题：</span>
                                    <span className="text-sm text-gray-900 ml-2">{anime.title}</span>
                                </div>
                                <div>
                                    <span className="text-sm font-medium text-gray-700">状态：</span>
                                    <span className={`text-sm ml-2 px-2 py-1 rounded-full ${anime.status === '完结'
                                            ? 'bg-gray-100 text-gray-800'
                                            : 'bg-green-100 text-green-800'
                                        }`}>
                                        {anime.status}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* 确认文字 */}
                    <div className="mb-6">
                        <p className="text-sm text-gray-700 mb-2">
                            删除操作将执行以下步骤：
                        </p>
                        <ul className="text-sm text-gray-600 space-y-1 ml-4">
                            <li>• 删除PikPak云盘中的整个动漫文件夹</li>
                            <li>• 同步数据库，移除记录</li>
                            <li>• 所有相关的文件和数据将永久丢失</li>
                        </ul>
                    </div>

                    <div className="text-center mb-6">
                        <p className="text-sm font-medium text-gray-900">
                            请输入动漫标题以确认删除：
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                            输入 "{anime.title}" 确认删除
                        </p>
                    </div>

                    {/* 确认输入 */}
                    <div className="mb-6">
                        <input
                            type="text"
                            placeholder={`请输入：${anime.title}`}
                            className="w-full px-3 py-2 text-gray-900 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                            disabled={isDeleting}
                            id="confirm-input"
                        />
                    </div>
                </div>

                {/* 模态框底部 */}
                <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
                    <Button
                        variant="info"
                        onClick={handleCancel}
                        disabled={isDeleting}
                    >
                        取消
                    </Button>
                    <Button
                        variant="danger"
                        onClick={() => {
                            const input = document.getElementById('confirm-input') as HTMLInputElement;
                            if (input && input.value === anime.title) {
                                handleConfirmDelete();
                            } else {
                                message.warning('请正确输入动漫标题以确认删除');
                                input?.focus();
                            }
                        }}
                        disabled={isDeleting}
                        className="bg-red-600 hover:bg-red-700"
                    >
                        确认删除
                    </Button>
                </div>
            </div>
        </div>
    );
};