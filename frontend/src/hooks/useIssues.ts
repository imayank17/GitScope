import { useQuery } from '@tanstack/react-query';
import { getIssues } from '../services/issueService';

export const useIssues = (
  owner: string,
  repo: string,
  state = 'open',
  page = 1,
  perPage = 30
) => {
  return useQuery({
    queryKey: ['issues', owner, repo, state, page, perPage],
    queryFn: () => getIssues(owner, repo, state, page, perPage),
    enabled: !!owner && !!repo,
  });
};
