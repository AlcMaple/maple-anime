// ==================== 通用响应类型 ====================

export interface BackendApiResponse<T = any> {
    code: number;
    msg: string;
    data?: T;
}

// 兼容旧的API响应
export interface ApiResponse<T = any> {
    success: boolean;
    data?: T;
    message?: string;
    error?: string;
}

// 分页数据结构
export interface PaginatedData<T> {
    items: T[];
    total: number;
    page?: number;
    pageSize?: number;
}

// ==================== 动漫类型 ====================

// 动漫搜索请求
export interface AnimeSearchRequest {
    name: string;
}

// 动漫搜索结果
export interface AnimeSearchResult {
    id: string;
    title: string;
    magnet: string;
    episodes?: number;
}

// 动漫详细信息请求
export interface AnimeInfoRequest {
    id: string;
    title: string;
    status: '完结' | '连载';
    summary?: string;
    cover_url?: string;
    username?: string;
    password?: string;
}

// bangumi 动漫信息
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

// bangumi 动漫信息响应
export interface AnimeInfoResponse {
    success: boolean;
    data: BangumiAnimeInfo[];
    total: number;
    keyword: string;
    message: string;
}

// 集数文件
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

// 动漫信息
export interface AnimeItem {
    id: string;
    title: string;
    status: '完结' | '连载';
    summary?: string;
    cover_url?: string;
    updated_at?: string;
    files?: EpisodeFile[];
}

// 动漫分组
export interface AnimeGroup {
    title: string;
    anime_list: AnimeSearchResult[];
}

// ==================== PikPak 相关类型 ====================

// PikPak凭证
export interface PikPakCredentials {
    username: string;
    password: string;
    folder_id?: string;
    file_ids?: string[];
}

// PikPak配置
export interface PikPakConfig extends PikPakCredentials {
    rememberCredentials: boolean;
}

// 下载请求类型
export interface DownloadRequest {
    username: string;
    password: string;
    mode: 'single_season' | 'multiple_seasons';
    title?: string;  // 单季模式使用
    anime_list?: AnimeSearchResult[];  // 单季模式使用
    groups?: AnimeGroup[];  // 多季模式使用
}

// 下载简介
export interface DownloadSummary {
    total_anime: number;
    successful_anime: number;
    total_episodes: number;
    successful_episodes: number;
}

export interface DownloadResult {
    success: boolean;
    message: string;
    summary?: DownloadSummary;
    details?: any[];
}

// 文件删除请求
export interface FileDeleteRequest {
    username: string;
    password: string;
    file_ids: string[];
    folder_id: string;
}

// 文件重命名请求
export interface FileRenameRequest {
    username: string;
    password: string;
    file_id: string;
    new_name: string;
    folder_id: string;
}

// 文件重命名响应
export interface FileRenameResponse extends ApiResponse { }

// 更新动漫请求
export interface UpdateAnimeRequest {
    username: string;
    password: string;
    folder_id: string;
    anime_list: AnimeSearchResult[];
}

// 更新动漫数据
export interface UpdateAnimeData {
    added_count: number;
    failed_count: number;
    folder_id: string;
}

export type UpdateAnimeResponse = ApiResponse<UpdateAnimeData>;

// 删除动漫请求
export interface DeleteAnimeRequest {
    username: string;
    password: string;
    folder_id: string;
}

// 删除动漫数据
export interface DeleteAnimeData {
    folder_id: string;
    anime_title: string;
    synced: boolean;
}

export type DeleteAnimeResponse = ApiResponse<DeleteAnimeData>;

// 文件删除响应
export interface FileDeleteResponse extends ApiResponse {
    deleted_count: number;
    failed_count: number;
}

// ==================== Bangumi 相关类型 ====================

// 动漫图片
export interface AnimeImages {
    large: string;
    medium: string;
    small: string;
}

// 动漫评分
export interface AnimeRating {
    total: number;
    count: Record<string, number>;
    score: number;
}

// 星期
export interface Weekday {
    en: string;
    cn: string;
    ja: string;
    id: number;
}

// 当季动漫
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


// 日历响应数据
export interface CalendarData {
    data: CalendarDay[];
    last_update?: string;
    error?: string;
}

export type CalendarResponse = BackendApiResponse<CalendarData[]>;

// ==================== 客户端 相关类型 ====================

// 动漫列表响应
export type AnimeListResponse = BackendApiResponse<AnimeItem[]>;

// 搜索动漫响应数据
export interface SearchAnimeData {
    anime_list: AnimeItem[];
    total: number;
    keyword: string;
}

// 搜索动漫响应
export type SearchResponse = BackendApiResponse<SearchAnimeData[]>;

export interface EpisodeListRequest {
    folder_id: string;
}

// 集数列表响应
export interface EpisodeListResponse extends ApiResponse {
    data: EpisodeFile[];
    total: number;
}

// 动漫数据响应
export type AnimeDetailResponse = BackendApiResponse<AnimeItem>;

// ==================== 日志系统类型 ====================

// 日志级别类型
export type LogLevel = 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';

// 解析后的日志条目
export interface ParsedLogEntry {
    id?: string;
    timestamp: string;
    level: string;
    logger: string;
    function: string;
    line: string;
    message: string;
    raw: string;
}

// 原始日志条目
export interface LogEntry {
    id?: string;
    timestamp: string;
    level: LogLevel;
    logger: string;
    function: string;
    line: number;
    message: string;
    raw?: string;
}

// 历史日志请求响应类型
export type HistoricalLogResponse = BackendApiResponse<string[]>;

// 日志请求响应类型
export type LogResponse = BackendApiResponse<LogEntry[]>;

// 日志系统状态
export interface LogStatus {
    active_connections: number;
    log_buffer_size: number;
    websocket_connected: boolean;
}

export type LogStatusResponse = BackendApiResponse<LogStatus>;