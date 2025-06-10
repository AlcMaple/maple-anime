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

// 动漫分组类型
export interface AnimeGroup {
    title: string;
    anime_list: AnimeSearchResult[];
}

export interface DownloadRequest {
    username: string;
    password: string;
    mode: 'single_season' | 'multiple_seasons';
    title?: string;  // 单季模式使用
    anime_list?: AnimeSearchResult[];  // 单季模式使用
    groups?: AnimeGroup[];  // 多季模式使用
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

// 当季新番类型定义
export interface AnimeImages {
    large: string;
    medium: string;
    small: string;
}

export interface AnimeRating {
    total: number;
    count: Record<string, number>;
    score: number;
}

export interface Weekday {
    en: string;
    cn: string;
    ja: string;
    id: number;
}

export interface CalendarAnime {
    id: number;
    name: string;
    name_cn: string;
    summary: string;
    images: AnimeImages;
    air_date: string;
    air_weekday: number;
    rating: AnimeRating;
}

export interface CalendarDay {
    weekday: Weekday;
    items: CalendarAnime[];
}

export interface CalendarResponse {
    success: boolean;
    data: CalendarDay[];
    updated_at?: string;
    error?: string;
}

// API响应包装类型
export interface ApiResponse<T = any> {
    success: boolean;
    data?: T;
    message?: string;
    error?: string;
}