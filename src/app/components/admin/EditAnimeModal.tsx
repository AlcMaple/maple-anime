'use client';

import React, { useState, useEffect } from 'react';

import { Button } from '@/ui/Button';
import { Input } from '@/ui/Input';
import { Search } from '@/ui/Search';
import { message } from '@/ui/Message';
import { Loading } from '@/ui/Loading';
import { Select } from '@/ui/Select';
import { animeApi } from '@/services/anime';
import { AnimeItem } from '@/services/types';

interface BangumiAnimeInfo {
    id: number;
    name: string;
    name_cn: string;
    summary: string;
    images: {
        large: string;
        medium: string;
        small: string;
    };
    air_date: string;
    eps_count: number;
    rating: {
        score: number;
        total: number;
    };
}

interface EditAnimeModalProps {
    isOpen: boolean;
    onClose: () => void;
    anime: AnimeItem | null;
    onSave: () => void;
}

export const EditAnimeModal: React.FC<EditAnimeModalProps> = ({
    isOpen,
    onClose,
    anime,
    onSave
}) => {
    const [formData, setFormData] = useState({
        title: '',
        status: '连载' as '连载' | '完结',
        summary: '',
        cover_url: ''
    });

    const [searchQuery, setSearchQuery] = useState('');
    const [bangumiResults, setBangumiResults] = useState<BangumiAnimeInfo[]>([]);
    const [isSearching, setIsSearching] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [isLoadingAnimeInfo, setIsLoadingAnimeInfo] = useState(false);

    // 当弹窗打开且动漫数据变化时，加载动漫信息
    useEffect(() => {
        if (isOpen && anime) {
            loadAnimeInfo();
        }
    }, [isOpen, anime]);

    // 加载动漫详细信息
    const loadAnimeInfo = async () => {
        if (!anime) return;

        setIsLoadingAnimeInfo(true);
        try {
            const response = await animeApi.getAnimeInfoById({
                id: anime.id,
                title: anime.title,
                status: anime.status,
                summary: '',
                cover_url: '',
                username: '',
                password: ''
            });
            console.log("加载动漫详细信息：", response);


            if (response.data) {
                setFormData({
                    title: response.data.title || anime.title,
                    status: response.data.status || anime.status,
                    summary: response.data.summary || '',
                    cover_url: response.data.cover_url || ''
                });
                setSearchQuery(response.data.title || anime.title);
            } else {
                // 如果没有详细信息，使用基础信息
                setFormData({
                    title: anime.title,
                    status: anime.status,
                    summary: '',
                    cover_url: ''
                });
                setSearchQuery(anime.title);
            }
        } catch (error) {
            message.error('加载动漫信息失败');
            setFormData({
                title: anime.title,
                status: anime.status,
                summary: '',
                cover_url: ''
            });
            setSearchQuery(anime.title);
        } finally {
            setIsLoadingAnimeInfo(false);
        }
    };

    // 搜索Bangumi动漫信息
    const handleSearchBangumi = async () => {
        if (!searchQuery.trim()) {
            message.warning('请输入搜索关键词');
            return;
        }

        setIsSearching(true);
        setBangumiResults([]);

        try {
            const response = await animeApi.getAnimeInfo({ name: searchQuery });
            console.log("搜索Bangumi返回结果：", response);


            if (response.data) {
                setBangumiResults(response.data);
                message.success(`找到 ${response.data.length} 个相关动漫`);
            } else {
                setBangumiResults([]);
                message.info('没有找到相关动漫信息');
            }
        } catch (error) {
            message.error('搜索失败');
        } finally {
            setIsSearching(false);
        }
    };

    // 应用Bangumi信息
    const applyBangumiInfo = (bangumiAnime: BangumiAnimeInfo) => {
        setFormData(prev => ({
            ...prev,
            summary: bangumiAnime.summary || prev.summary,
            cover_url: bangumiAnime.images?.large || bangumiAnime.images?.medium || prev.cover_url
        }));
        message.success('已应用Bangumi信息');
    };

    // 保存动漫信息
    const handleSave = async () => {
        if (!anime) return;

        if (!formData.title.trim()) {
            message.error('动漫标题不能为空');
            return;
        }

        // 获取PikPak配置
        const pikpakUsername = localStorage.getItem('pikpak_username');
        const pikpakPassword = localStorage.getItem('pikpak_password');

        if (!pikpakUsername || !pikpakPassword) {
            message.error('请先配置PikPak账号信息');
            return;
        }

        setIsSaving(true);

        try {
            const response = await animeApi.saveAnimeInfo({
                id: anime.id,
                title: formData.title,
                status: formData.status,
                summary: formData.summary,
                cover_url: formData.cover_url,
                username: pikpakUsername,
                password: pikpakPassword
            });
            console.log("保存动漫信息返回结果：", response);


            if (response.success) {
                message.success(response.message);
                onSave();
                handleClose();
            } else {
                message.error(response.message);
            }
        } catch (error) {
            message.error('保存失败');
        } finally {
            setIsSaving(false);
        }
    };

    // 关闭弹窗
    const handleClose = () => {
        if (!isSaving) {
            setFormData({ title: '', status: '连载', summary: '', cover_url: '' });
            setSearchQuery('');
            setBangumiResults([]);
            setIsSearching(false);
            setIsLoadingAnimeInfo(false);
            onClose();
        }
    };

    // 表单字段更新
    const updateFormField = (field: keyof typeof formData, value: string) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    if (!isOpen || !anime) return null;

    return (
        <div
            className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4"
        >
            <div
                className="bg-white rounded-lg shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
            >
                {/* 模态框头部 */}
                <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-gradient-to-r from-blue-50 to-indigo-50">
                    <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                        </div>
                        <h2 className="text-xl font-semibold text-gray-900">编辑动漫信息</h2>
                    </div>
                    <button
                        onClick={handleClose}
                        className="text-gray-400 hover:text-gray-600 text-2xl font-light"
                        disabled={isSaving}
                    >
                        ×
                    </button>
                </div>

                {/* 保存中遮罩 */}
                {isSaving && (
                    <div className="absolute inset-0 bg-white/90 flex items-center justify-center z-10">
                        <Loading
                            variant="spinner"
                            size="large"
                            color="primary"
                            text="正在保存..."
                        />
                    </div>
                )}

                {/* 模态框内容 */}
                <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
                    {/* 加载动漫信息状态 */}
                    {isLoadingAnimeInfo ? (
                        <div className="flex justify-center items-center py-20">
                            <Loading
                                variant="spinner"
                                size="large"
                                color="primary"
                                text="加载动漫信息中..."
                            />
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {/* 左侧：基本信息编辑 */}
                            <div className="space-y-4">
                                <h3 className="text-lg font-medium text-gray-900 mb-4">基本信息</h3>

                                <Input
                                    label="动漫标题"
                                    value={formData.title}
                                    onChange={(e) => updateFormField('title', e.target.value)}
                                    placeholder="请输入动漫标题"
                                    disabled={isSaving}
                                />

                                <Select
                                    label="状态"
                                    value={formData.status}
                                    onChange={(value) => updateFormField('status', value)}
                                    options={[
                                        { value: "连载", label: "连载" },
                                        { value: "完结", label: "完结" }
                                    ]}
                                    disabled={isSaving}
                                />

                                <Input
                                    label="封面URL"
                                    value={formData.cover_url}
                                    onChange={(e) => updateFormField('cover_url', e.target.value)}
                                    placeholder="请输入封面图片URL"
                                    disabled={isSaving}
                                />

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        简介
                                    </label>
                                    <textarea
                                        value={formData.summary}
                                        onChange={(e) => updateFormField('summary', e.target.value)}
                                        placeholder="请输入动漫简介"
                                        disabled={isSaving}
                                        rows={6}
                                        className="w-full p-3 border-2 border-gray-300 rounded-lg transition-colors duration-300 focus:outline-none focus:border-indigo-500 text-gray-900 bg-white resize-vertical"
                                    />
                                </div>

                                {/* 封面预览 */}
                                {formData.cover_url && (
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            封面预览
                                        </label>
                                        <div className="w-32 h-48 border border-gray-300 rounded-lg overflow-hidden">
                                            <img
                                                src={formData.cover_url}
                                                alt="封面预览"
                                                className="w-full h-full object-cover"
                                                onError={(e) => {
                                                    e.currentTarget.style.display = 'none';
                                                }}
                                            />
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* 右侧：Bangumi信息搜索 */}
                            <div className="space-y-4">
                                <h3 className="text-lg font-medium text-gray-900 mb-4">Bangumi信息</h3>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        搜索Bangumi获取详细信息
                                    </label>
                                    <Search
                                        placeholder="搜索动漫名称..."
                                        value={searchQuery}
                                        onChange={setSearchQuery}
                                        onSearch={handleSearchBangumi}
                                        disabled={isSearching || isSaving}
                                    />
                                </div>

                                {/* 搜索结果 */}
                                {isSearching ? (
                                    <div className="flex justify-center py-8">
                                        <Loading
                                            variant="spinner"
                                            size="medium"
                                            color="primary"
                                            text="搜索中..."
                                        />
                                    </div>
                                ) : bangumiResults.length > 0 ? (
                                    <div className="space-y-3 max-h-96 overflow-y-auto">
                                        <h4 className="font-medium text-gray-900">搜索结果 ({bangumiResults.length} 个)：</h4>
                                        {bangumiResults.map((item, index) => (
                                            <div
                                                key={index}
                                                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
                                            >
                                                <div className="flex items-start space-x-3">
                                                    {/* 封面 */}
                                                    {item.images?.medium && (
                                                        <img
                                                            src={item.images.medium}
                                                            alt={item.name_cn || item.name}
                                                            className="w-16 h-24 object-cover rounded border border-gray-300 flex-shrink-0"
                                                            onError={(e) => {
                                                                e.currentTarget.style.display = 'none';
                                                            }}
                                                        />
                                                    )}

                                                    <div className="flex-1 min-w-0">
                                                        <h5 className="font-medium text-gray-900 mb-1">
                                                            {item.name_cn || item.name}
                                                        </h5>

                                                        {item.name_cn && item.name && (
                                                            <p className="text-sm text-gray-600 mb-2">
                                                                原名: {item.name}
                                                            </p>
                                                        )}

                                                        {/* {item.air_date && (
                                                            <p className="text-sm text-gray-600 mb-2">
                                                                播出日期: {item.air_date}
                                                            </p>
                                                        )}

                                                        {item.rating?.score > 0 && (
                                                            <p className="text-sm text-gray-600 mb-2">
                                                                评分: {item.rating.score}/10 ({item.rating.total}人评价)
                                                            </p>
                                                        )} */}

                                                        {item.summary && (
                                                            <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                                                                {item.summary}
                                                            </p>
                                                        )}

                                                        <Button
                                                            variant="info"
                                                            className="text-xs px-3 py-1"
                                                            onClick={() => applyBangumiInfo(item)}
                                                            disabled={isSaving}
                                                        >
                                                            应用此信息
                                                        </Button>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : null}
                            </div>
                        </div>
                    )}
                </div>

                {/* 模态框底部 */}
                <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
                    <Button
                        variant="info"
                        onClick={handleClose}
                        className="bg-gray-500 hover:bg-gray-600"
                        disabled={isSaving}
                    >
                        取消
                    </Button>
                    <Button
                        variant="success"
                        onClick={handleSave}
                        disabled={isSaving || isLoadingAnimeInfo}
                    >
                        保存
                    </Button>
                </div>
            </div>
        </div>
    );
};