import { useParams } from 'react-router-dom';
import { useRepository } from '../hooks/useRepository';
import { useLanguages } from '../hooks/useLanguages';
import { useCommits } from '../hooks/useCommits';
import { useContributors } from '../hooks/useContributors';
import { usePullRequests } from '../hooks/usePullRequests';
import { useIssues } from '../hooks/useIssues';
import { useMetricsHistory } from '../hooks/useMetrics';
import DashboardStats from '../components/dashboard/DashboardStats';
import DashboardCharts from '../components/dashboard/DashboardCharts';
import RepositoryCard from '../components/repository/RepositoryCard';
import SectionHeader from '../components/common/SectionHeader';
import ErrorState from '../components/common/ErrorState';
import { CardSkeleton } from '../components/common/Skeleton';

export default function DashboardPage() {
  const { owner, repo } = useParams<{ owner: string; repo: string }>();
  const repoQuery = useRepository(owner!, repo!);
  const langQuery = useLanguages(owner!, repo!);
  const commitsQuery = useCommits(owner!, repo!, 1, 100);
  const contribQuery = useContributors(owner!, repo!, 1, 30);
  const prQuery = usePullRequests(owner!, repo!, 'all', 1, 100);
  const issuesQuery = useIssues(owner!, repo!, 'all', 1, 100);
  const metricsQuery = useMetricsHistory(repoQuery.data?.id ?? null);

  if (repoQuery.isError) {
    return <ErrorState message={repoQuery.error?.message} onRetry={() => repoQuery.refetch()} />;
  }

  const isLoading = repoQuery.isLoading;

  return (
    <div className="space-y-8 max-w-6xl">
      <SectionHeader title={repoQuery.data?.full_name || 'Repository Dashboard'} subtitle="Overview and analytics" />

      {/* Stats */}
      {isLoading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {Array.from({ length: 5 }).map((_, i) => <CardSkeleton key={i} />)}
        </div>
      ) : repoQuery.data ? (
        <DashboardStats repo={repoQuery.data} />
      ) : null}

      {/* Repo info card */}
      {repoQuery.data && <RepositoryCard repo={repoQuery.data} />}

      {/* Charts */}
      <SectionHeader title="Analytics" subtitle="Visual breakdown of repository activity" />
      <DashboardCharts
        languages={langQuery.data}
        commits={commitsQuery.data?.items}
        snapshots={metricsQuery.data}
        contributors={contribQuery.data?.items}
        pullRequests={prQuery.data?.items}
        issues={issuesQuery.data?.items}
        isLoading={langQuery.isLoading && commitsQuery.isLoading}
      />
    </div>
  );
}
