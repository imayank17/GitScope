import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { refreshRepository, getSyncStatus } from '../services/syncService';

export const useSyncStatus = (id: string | null, polling = false) => {
  return useQuery({
    queryKey: ['syncStatus', id],
    queryFn: () => getSyncStatus(id!),
    enabled: !!id,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return polling || status === 'SYNCING' ? 3000 : false;
    },
  });
};

export const useRefreshRepository = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => refreshRepository(id),
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: ['syncStatus', id] });
    },
  });
};
