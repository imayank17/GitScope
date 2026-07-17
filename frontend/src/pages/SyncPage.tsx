import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useRepository } from '../hooks/useRepository';
import { useSyncStatus, useRefreshRepository } from '../hooks/useSync';
import SyncStatusCard from '../components/repository/SyncStatusCard';
import SectionHeader from '../components/common/SectionHeader';
import ErrorState from '../components/common/ErrorState';
import { CardSkeleton } from '../components/common/Skeleton';

export default function SyncPage() {
  const { owner, repo } = useParams<{ owner: string; repo: string }>();
  const repoQuery = useRepository(owner!, repo!);
  const repoId = repoQuery.data?.id ?? null;
  const [polling, setPolling] = useState(false);
  const syncQuery = useSyncStatus(repoId, polling);
  const refreshMutation = useRefreshRepository();

  // Stop polling once sync completes
  if (polling && syncQuery.data && syncQuery.data.status !== 'SYNCING') {
    setPolling(false);
  }

  const handleRefresh = () => {
    if (!repoId) return;
    setPolling(true);
    refreshMutation.mutate(repoId);
  };

  if (repoQuery.isError) return <ErrorState message={repoQuery.error?.message} onRetry={() => repoQuery.refetch()} />;

  return (
    <div className="space-y-6 max-w-2xl">
      <SectionHeader title="Synchronization" subtitle="Manage data freshness for this repository" />

      {repoQuery.isLoading ? (
        <CardSkeleton />
      ) : (
        <SyncStatusCard
          syncStatus={syncQuery.data}
          onRefresh={handleRefresh}
          isRefreshing={refreshMutation.isPending || polling}
        />
      )}

      {refreshMutation.isError && (
        <p className="text-sm text-red-400">
          {refreshMutation.error instanceof Error ? refreshMutation.error.message : 'Refresh failed'}
        </p>
      )}
    </div>
  );
}
