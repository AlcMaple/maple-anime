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
    UpdateAnimeRequest,
    UpdateAnimeResponse,
    DeleteAnimeRequest,
    DeleteAnimeResponse,
    ApiResponse
} from './types';

export class PikPakService {
    // 下载动漫到PikPak
    static async downloadAnime(request: DownloadRequest): Promise<DownloadResult> {
        return apiClient.post<DownloadResult>('/api/pikpak/batch-download', request);
    }

    // 获取动漫列表
    static async getAnimeList(): Promise<AnimeListResponse> {
        return apiClient.get<AnimeListResponse>('/api/anime/list');
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

    // 同步数据
    static async syncData(request: PikPakCredentials): Promise<ApiResponse> {
        return apiClient.post<ApiResponse>('/api/pikpak/sync', request);
    }

    // 获取视频连接
    static async getVideoUrl(request: PikPakCredentials): Promise<ApiResponse> {
        return apiClient.post<ApiResponse>('/api/pikpak/update-links', request);
    }

    // 更新动漫
    static async updateAnime(request: UpdateAnimeRequest): Promise<UpdateAnimeResponse> {
        return apiClient.post<UpdateAnimeResponse>('/api/pikpak/update-episode', request);
    }

    // 删除动漫
    static async deleteAnime(request: DeleteAnimeRequest): Promise<DeleteAnimeResponse> {
        return apiClient.post<DeleteAnimeResponse>('/api/pikpak/delete-anime', request);
    }
}

// 导出实例
export const pikpakApi = {
    download: PikPakService.downloadAnime,
    getAnimeList: PikPakService.getAnimeList,
    getEpisodeList: PikPakService.getEpisodeList,
    deleteEpisodes: PikPakService.deleteEpisodes,
    renameEpisode: PikPakService.renameEpisode,
    syncData: PikPakService.syncData,
    getVideoUrl: PikPakService.getVideoUrl,
    updateAnime: PikPakService.updateAnime,
    deleteAnime: PikPakService.deleteAnime,
};