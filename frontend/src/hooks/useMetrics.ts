import { useQuery } from '@tanstack/react-query';
import { getMetricsHistory } from '../services/metricsService';

export const useMetricsHistory = (id: string | null) => {
  return useQuery({
    queryKey: ['metricsHistory', id],
    queryFn: () => getMetricsHistory(id!),
    enabled: !!id,
  });
};
