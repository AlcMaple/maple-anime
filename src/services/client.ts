import { apiClient } from '@/utils/api';
import {
    SearchResponse, AnimeDetailResponse
} from './types';

export class ClientService {
    // 搜索动漫
    static async searchAnime(request: { name: string }): Promise<SearchResponse> {
        return apiClient.post<SearchResponse>('/api/client/search', request);
    }

    // 获取动漫数据
    static async getAnimeDetail(id: string): Promise<AnimeDetailResponse> {
        return apiClient.get<AnimeDetailResponse>(`/api/client/anime/${id}`);
    }
}

// 导出实例
export const clientApi = {
    clientSearch: ClientService.searchAnime,
    clientAnimeData: ClientService.getAnimeDetail
};