import apiClient from '../api/client';
import type { RepositorySnapshot } from '../types';

export const getMetricsHistory = async (id: string): Promise<RepositorySnapshot[]> => {
  const response = await apiClient.get<RepositorySnapshot[]>(
    `/repositories/${id}/metrics/history`
  );
  return response.data;
};
