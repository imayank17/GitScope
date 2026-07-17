import { useQuery } from '@tanstack/react-query';
import { getCommits } from '../services/commitService';

export const useCommits = (owner: string, repo: string, page = 1, perPage = 30) => {
  return useQuery({
    queryKey: ['commits', owner, repo, page, perPage],
    queryFn: () => getCommits(owner, repo, page, perPage),
    enabled: !!owner && !!repo,
  });
};
