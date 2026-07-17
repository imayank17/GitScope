import apiClient from '../api/client';
import type { SyncStatus, RefreshResponse } from '../types';

export const refreshRepository = async (id: string): Promise<RefreshResponse> => {
  const response = await apiClient.post<RefreshResponse>(`/repositories/${id}/refresh`);
  return response.data;
};

export const getSyncStatus = async (id: string): Promise<SyncStatus> => {
  const response = await apiClient.get<SyncStatus>(`/repositories/${id}/sync-status`);
  return response.data;
};
