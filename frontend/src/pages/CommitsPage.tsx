import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useCommits } from '../hooks/useCommits';
import CommitCard from '../components/repository/CommitCard';
import SectionHeader from '../components/common/SectionHeader';
import Pagination from '../components/common/Pagination';
import ErrorState from '../components/common/ErrorState';
import EmptyState from '../components/common/EmptyState';
import { ListSkeleton } from '../components/common/Skeleton';

export default function CommitsPage() {
  const { owner, repo } = useParams<{ owner: string; repo: string }>();
  const [page, setPage] = useState(1);
  const { data, isLoading, isError, error, refetch } = useCommits(owner!, repo!, page, 20);

  if (isError) return <ErrorState message={error?.message} onRetry={refetch} />;

  return (
    <div className="space-y-6 max-w-4xl">
      <SectionHeader title="Commits" subtitle="Recent commit history" />

      {isLoading ? (
        <ListSkeleton count={6} />
      ) : data && data.items.length > 0 ? (
        <div className="space-y-3">
          {data.items.map((c, i) => (
            <CommitCard key={c.sha} commit={c} index={i} />
          ))}
        </div>
      ) : (
        <EmptyState message="No commits found" />
      )}

      {data && <Pagination page={page} totalPages={data.total_pages} onPageChange={setPage} />}
    </div>
  );
}
