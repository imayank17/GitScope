import apiClient from '../api/client';
import type { LanguageBreakdown } from '../types';

export const getLanguages = async (
  owner: string,
  repo: string
): Promise<LanguageBreakdown> => {
  const response = await apiClient.get<LanguageBreakdown>(
    `/repositories/${owner}/${repo}/languages`
  );
  return response.data;
};
