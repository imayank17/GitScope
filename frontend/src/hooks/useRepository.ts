import { useQuery, useMutation } from '@tanstack/react-query';
import { analyzeRepository, getRepository } from '../services/repositoryService';
import type { RepositoryAnalyzeRequest } from '../types';

export const useRepository = (owner: string, repo: string) => {
  return useQuery({
    queryKey: ['repository', owner, repo],
    queryFn: () => getRepository(owner, repo),
    enabled: !!owner && !!repo,
    staleTime: 5 * 60 * 1000,
  });
};

export const useAnalyzeRepository = () => {
  return useMutation({
    mutationFn: (data: RepositoryAnalyzeRequest) => analyzeRepository(data),
  });
};
