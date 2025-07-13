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
    folder_id?: string;
    file_ids?: string[];
}

export interface PikPakConfig extends PikPakCredentials {
    rememberCredentials: boolean;
}

// 集数文件类型
export interface EpisodeFile {
    id: string;
    name: string;
    size?: number;
    kind?: string;
    create_time?: string;
    update_time?: string;
    mime_type?: string;
    play_url?: string;
    hash?: string;
    is_video?: boolean;
    folder_id?: string;
}

// 动漫项目类型
export interface AnimeItem {
    id: string;
    title: string;
    status: '完结' | '连载';
    summary?: string;
    cover_url?: string;
    updated_at?: string;
    files?: EpisodeFile[];
}

// 动漫详细信息类型
export interface AnimeInfoRequest {
    id: string;
    title: string;
    status: '完结' | '连载';
    summary?: string;
    cover_url?: string;
    username?: string;
    password?: string;
}

// 动漫信息响应类型
export interface BangumiAnimeInfo {
    id: number;
    name: string;
    name_cn: string;
    summary: string;
    images: {
        large: string;
        medium: string;
        small: string;
    };
    air_date: string;
    eps_count: number;
    rating: {
        score: number;
        total: number;
    };
    tags: string[];
}

export interface AnimeInfoResponse {
    success: boolean;
    data: BangumiAnimeInfo[];
    total: number;
    keyword: string;
    message: string;
}

export interface AnimeDetailResponse {
    success: boolean;
    data: AnimeItem;
    message: string;
}

// 动漫列表响应类型
export interface AnimeListResponse {
    success: boolean;
    data: AnimeItem[];
    total: number;
    message: string;
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



export interface EpisodeListRequest {
    folder_id: string;
}

export interface FileDeleteRequest {
    username: string;
    password: string;
    file_ids: string[];
    folder_id: string;
}

export interface FileRenameRequest {
    username: string;
    password: string;
    file_id: string;
    new_name: string;
    folder_id: string;
}

export interface UpdateAnimeRequest {
    username: string;
    password: string;
    folder_id: string;
    anime_list: AnimeSearchResult[];
}

export interface UpdateAnimeResponse extends ApiResponse {
    data: {
        added_count: number;
        failed_count: number;
        folder_id: string;
    };
}

export interface DeleteAnimeRequest {
    username: string;
    password: string;
    folder_id: string;
}

export interface DeleteAnimeResponse extends ApiResponse {
    data: {
        folder_id: string;
        anime_title: string;
        synced: boolean;
    };
}

// 客户端：搜索动漫响应
export interface SearchResponse extends AnimeListResponse {
    keyword: string;
}

// 客户端：动漫数据响应
export interface AnimeDetailResponse extends AnimeItem {
    success: boolean;
    message: string;
}

// API响应包装类型
export interface ApiResponse<T = any> {
    success: boolean;
    data?: T;
    message?: string;
    error?: string;
}

// 响应类型
export interface EpisodeListResponse extends ApiResponse {
    data: EpisodeFile[];
    total: number;
}

export interface FileDeleteResponse extends ApiResponse {
    deleted_count: number;
    failed_count: number;
}

export interface FileRenameResponse extends ApiResponse { }