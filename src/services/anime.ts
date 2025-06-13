import { apiClient } from '@/utils/api';
import {
    AnimeSearchRequest,
    AnimeSearchResult,
    AnimeInfoRequest,
    AnimeInfoResponse,
    AnimeDetailResponse
} from './types';

export class AnimeService {
    // 搜索动漫
    static async searchAnime(request: AnimeSearchRequest): Promise<AnimeSearchResult[]> {
        return apiClient.post<AnimeSearchResult[]>('/api/search', request);
    }

    // 通过名称获取动漫信息（bangumi）
    static async getAnimeInfo(request: { name: string }): Promise<AnimeInfoResponse> {
        return apiClient.post<AnimeInfoResponse>('/api/anime/info', request);
    }

    // 通过ID获取动漫详细信息（数据库）
    static async getAnimeInfoById(request: AnimeInfoRequest): Promise<AnimeDetailResponse> {
        return apiClient.post<AnimeDetailResponse>('/api/anime/info/id', request);
    }

    // 保存/更新动漫信息
    static async saveAnimeInfo(request: AnimeInfoRequest): Promise<{ success: boolean; message: string }> {
        return apiClient.post<{ success: boolean; message: string }>('/api/anime/info/save', request);
    }
}

// 导出实例
export const animeApi = {
    search: AnimeService.searchAnime,
    getAnimeInfo: AnimeService.getAnimeInfo,
    getAnimeInfoById: AnimeService.getAnimeInfoById,
    saveAnimeInfo: AnimeService.saveAnimeInfo,
};