import { apiClient } from '@/utils/api';
import {
    PikPakCredentials,
    DownloadRequest,
    DownloadResult,
    AnimeListResponse,
    EpisodeListRequest,
    FileDeleteRequest,
    FileRenameRequest,
    EpisodeListResponse,
    FileDeleteResponse,
    FileRenameResponse,
} from './types';

export class PikPakService {
    // 下载动漫到PikPak
    static async downloadAnime(request: DownloadRequest): Promise<DownloadResult> {
        return apiClient.post<DownloadResult>('/api/download', request);
    }

    // 获取动漫列表
    static async getAnimeList(credentials: PikPakCredentials): Promise<AnimeListResponse> {
        return apiClient.post<AnimeListResponse>('/api/anime/list', credentials);
    }

    // 获取集数列表
    static async getEpisodeList(request: EpisodeListRequest): Promise<EpisodeListResponse> {
        return apiClient.post<EpisodeListResponse>('/api/episodes/list', request);
    }

    // 批量删除文件
    static async deleteEpisodes(request: FileDeleteRequest): Promise<FileDeleteResponse> {
        return apiClient.post<FileDeleteResponse>('/api/episodes/delete', request);
    }

    // 重命名文件
    static async renameEpisode(request: FileRenameRequest): Promise<FileRenameResponse> {
        return apiClient.post<FileRenameResponse>('/api/episodes/rename', request);
    }
}

// 导出实例
export const pikpakApi = {
    download: PikPakService.downloadAnime,
    getAnimeList: PikPakService.getAnimeList,
    getEpisodeList: PikPakService.getEpisodeList,
    deleteEpisodes: PikPakService.deleteEpisodes,
    renameEpisode: PikPakService.renameEpisode,
};