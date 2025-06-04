import { apiClient } from '@/utils/api';
import { AnimeSearchRequest, AnimeSearchResult } from './types';

export class AnimeService {
    // 搜索动漫
    static async searchAnime(request: AnimeSearchRequest): Promise<AnimeSearchResult[]> {
        return apiClient.post<AnimeSearchResult[]>('/api/search', request);
    }
}

// 导出实例
export const animeApi = {
    search: AnimeService.searchAnime,
};