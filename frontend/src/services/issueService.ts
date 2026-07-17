import apiClient from '../api/client';
import type { PaginatedResponse, Issue } from '../types';

export const getIssues = async (
  owner: string,
  repo: string,
  state = 'open',
  page = 1,
  perPage = 30
): Promise<PaginatedResponse<Issue>> => {
  const response = await apiClient.get<PaginatedResponse<Issue>>(
    `/repositories/${owner}/${repo}/issues`,
    { params: { state, page, per_page: perPage } }
  );
  return response.data;
};
