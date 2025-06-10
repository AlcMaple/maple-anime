import { apiClient } from '@/utils/api';
import { PikPakCredentials, DownloadRequest, DownloadResult, AnimeListResponse } from './types';

export class PikPakService {
    // 下载动漫到PikPak
    static async downloadAnime(request: DownloadRequest): Promise<DownloadResult> {
        return apiClient.post<DownloadResult>('/api/download', request);
    }

    // 获取动漫列表
    static async getAnimeList(credentials: PikPakCredentials): Promise<AnimeListResponse> {
        return apiClient.post<AnimeListResponse>('/api/anime/list', credentials);
    }
}

// 导出实例
export const pikpakApi = {
    download: PikPakService.downloadAnime,
    getAnimeList: PikPakService.getAnimeList,
};