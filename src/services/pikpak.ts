import { apiClient } from '@/utils/api';
import { PikPakCredentials, DownloadRequest, DownloadResult } from './types';

export class PikPakService {
    // 下载动漫到PikPak
    static async downloadAnime(request: DownloadRequest): Promise<DownloadResult> {
        return apiClient.post<DownloadResult>('/api/download', request);
    }
}

// 导出实例
export const pikpakApi = {
    download: PikPakService.downloadAnime,
};