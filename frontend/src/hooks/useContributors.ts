import { useQuery } from '@tanstack/react-query';
import { getContributors } from '../services/contributorService';

export const useContributors = (owner: string, repo: string, page = 1, perPage = 30) => {
  return useQuery({
    queryKey: ['contributors', owner, repo, page, perPage],
    queryFn: () => getContributors(owner, repo, page, perPage),
    enabled: !!owner && !!repo,
  });
};
