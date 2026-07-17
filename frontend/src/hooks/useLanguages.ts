import { useQuery } from '@tanstack/react-query';
import { getLanguages } from '../services/languageService';

export const useLanguages = (owner: string, repo: string) => {
  return useQuery({
    queryKey: ['languages', owner, repo],
    queryFn: () => getLanguages(owner, repo),
    enabled: !!owner && !!repo,
  });
};
