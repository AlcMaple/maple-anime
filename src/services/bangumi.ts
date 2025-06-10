import { apiClient } from '@/utils/api';
import { CalendarResponse } from './types';

export class BangumiService {
    // 获取当季新番日历数据
    static async getCalendar(): Promise<CalendarResponse> {
        return apiClient.get<CalendarResponse>('/api/calendar');
    }

    // 更新当季新番数据
    static async updateCalendar(): Promise<CalendarResponse> {
        return apiClient.get<CalendarResponse>('/api/calendar/update');
    }
}

// 导出实例
export const bangumiApi = {
    get: BangumiService.getCalendar,
    update: BangumiService.updateCalendar,
};