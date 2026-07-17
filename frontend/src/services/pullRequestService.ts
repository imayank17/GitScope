import apiClient from '../api/client';
import type { PaginatedResponse, PullRequest } from '../types';

export const getPullRequests = async (
  owner: string,
  repo: string,
  state = 'open',
  page = 1,
  perPage = 30
): Promise<PaginatedResponse<PullRequest>> => {
  const response = await apiClient.get<PaginatedResponse<PullRequest>>(
    `/repositories/${owner}/${repo}/pulls`,
    { params: { state, page, per_page: perPage } }
  );
  return response.data;
};
