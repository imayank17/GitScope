import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useIssues } from '../hooks/useIssues';
import IssueCard from '../components/repository/IssueCard';
import SectionHeader from '../components/common/SectionHeader';
import Pagination from '../components/common/Pagination';
import ErrorState from '../components/common/ErrorState';
import EmptyState from '../components/common/EmptyState';
import { ListSkeleton } from '../components/common/Skeleton';

const TABS = ['open', 'closed', 'all'] as const;

export default function IssuesPage() {
  const { owner, repo } = useParams<{ owner: string; repo: string }>();
  const [state, setState] = useState<string>('open');
  const [page, setPage] = useState(1);
  const { data, isLoading, isError, error, refetch } = useIssues(owner!, repo!, state, page, 20);

  if (isError) return <ErrorState message={error?.message} onRetry={refetch} />;

  return (
    <div className="space-y-6 max-w-4xl">
      <SectionHeader title="Issues" subtitle="Track bugs and feature requests" />

      {/* State tabs */}
      <div className="flex gap-1 bg-surface-800/60 rounded-lg p-1 w-fit">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => { setState(t); setPage(1); }}
            className={`px-4 py-1.5 rounded-md text-sm font-medium capitalize transition-colors ${
              state === t ? 'bg-primary-600 text-white' : 'text-surface-400 hover:text-surface-200'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {isLoading ? (
        <ListSkeleton count={6} />
      ) : data && data.items.length > 0 ? (
        <div className="space-y-3">
          {data.items.map((issue, i) => (
            <IssueCard key={issue.number} issue={issue} index={i} />
          ))}
        </div>
      ) : (
        <EmptyState message={`No ${state} issues found`} />
      )}

      {data && <Pagination page={page} totalPages={data.total_pages} onPageChange={setPage} />}
    </div>
  );
}
