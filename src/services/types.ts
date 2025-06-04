// 动漫搜索相关类型
export interface AnimeSearchRequest {
    name: string;
}

export interface AnimeSearchResult {
    id: string;
    title: string;
    magnet: string;
    episodes?: number;
}

// PikPak相关类型
export interface PikPakCredentials {
    username: string;
    password: string;
}

export interface PikPakConfig extends PikPakCredentials {
    rememberCredentials: boolean;
}

export interface DownloadRequest {
    username: string;
    password: string;
    anime_list: AnimeSearchResult[];
}

export interface DownloadResult {
    success: boolean;
    message: string;
    summary?: {
        total_anime: number;
        successful_anime: number;
        total_episodes: number;
        successful_episodes: number;
    };
    details?: any[];
}

// API响应包装类型
export interface ApiResponse<T = any> {
    success: boolean;
    data?: T;
    message?: string;
    error?: string;
}