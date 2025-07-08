import { apiClient } from '@/utils/api';
import {
    SearchResponse
} from './types';

export class ClientService {
    // 搜索动漫
    static async searchAnime(request: { name: string }): Promise<SearchResponse> {
        return apiClient.post<SearchResponse>('/api/client/search', request);
    }
}

// 导出实例
export const clientApi = {
    clientSearch: ClientService.searchAnime
};