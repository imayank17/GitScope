import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useContributors } from '../hooks/useContributors';
import ContributorCard from '../components/repository/ContributorCard';
import SectionHeader from '../components/common/SectionHeader';
import SearchBar from '../components/common/SearchBar';
import Pagination from '../components/common/Pagination';
import ErrorState from '../components/common/ErrorState';
import EmptyState from '../components/common/EmptyState';
import { ListSkeleton } from '../components/common/Skeleton';

export default function ContributorsPage() {
  const { owner, repo } = useParams<{ owner: string; repo: string }>();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const { data, isLoading, isError, error, refetch } = useContributors(owner!, repo!, page, 30);

  if (isError) return <ErrorState message={error?.message} onRetry={refetch} />;

  const filtered = data?.items.filter((c) =>
    c.login.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-4xl">
      <SectionHeader title="Contributors" subtitle={`People who have contributed to ${owner}/${repo}`} />
      <SearchBar value={search} onChange={setSearch} placeholder="Search contributors..." />

      {isLoading ? (
        <ListSkeleton count={6} />
      ) : filtered && filtered.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {filtered.map((c, i) => (
            <ContributorCard key={c.login} contributor={c} index={i} />
          ))}
        </div>
      ) : (
        <EmptyState message="No contributors found" />
      )}

      {data && <Pagination page={page} totalPages={data.total_pages} onPageChange={setPage} />}
    </div>
  );
}
