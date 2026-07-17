import apiClient from '../api/client';
import type { PaginatedResponse, Contributor } from '../types';

export const getContributors = async (
  owner: string,
  repo: string,
  page = 1,
  perPage = 30
): Promise<PaginatedResponse<Contributor>> => {
  const response = await apiClient.get<PaginatedResponse<Contributor>>(
    `/repositories/${owner}/${repo}/contributors`,
    { params: { page, per_page: perPage } }
  );
  return response.data;
};
