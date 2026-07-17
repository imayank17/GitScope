import { useQuery } from '@tanstack/react-query';
import { getPullRequests } from '../services/pullRequestService';

export const usePullRequests = (
  owner: string,
  repo: string,
  state = 'open',
  page = 1,
  perPage = 30
) => {
  return useQuery({
    queryKey: ['pullRequests', owner, repo, state, page, perPage],
    queryFn: () => getPullRequests(owner, repo, state, page, perPage),
    enabled: !!owner && !!repo,
  });
};
