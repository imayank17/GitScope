import apiClient from '../api/client';
import type { PaginatedResponse, Commit } from '../types';

export const getCommits = async (
  owner: string,
  repo: string,
  page = 1,
  perPage = 30
): Promise<PaginatedResponse<Commit>> => {
  const response = await apiClient.get<PaginatedResponse<Commit>>(
    `/repositories/${owner}/${repo}/commits`,
    { params: { page, per_page: perPage } }
  );
  return response.data;
};
