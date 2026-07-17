import apiClient from '../api/client';
import type { Repository, RepositoryAnalyzeRequest } from '../types';

export const analyzeRepository = async (data: RepositoryAnalyzeRequest): Promise<Repository> => {
  const response = await apiClient.post<Repository>('/repositories/analyze', data);
  return response.data;
};

export const getRepository = async (owner: string, repo: string): Promise<Repository> => {
  const response = await apiClient.get<Repository>(`/github/${owner}/${repo}`);
  return response.data;
};
