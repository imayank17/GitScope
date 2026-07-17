import LanguagePieChart from '../charts/LanguagePieChart';
import CommitActivityChart from '../charts/CommitActivityChart';
import MetricsHistoryChart from '../charts/MetricsHistoryChart';
import ContributorsBarChart from '../charts/ContributorsBarChart';
import PullRequestTrendChart from '../charts/PullRequestTrendChart';
import IssueTrendChart from '../charts/IssueTrendChart';
import { ChartSkeleton } from '../common/Skeleton';
import type { LanguageBreakdown, Commit, RepositorySnapshot, Contributor, PullRequest, Issue } from '../../types';

interface DashboardChartsProps {
  languages?: LanguageBreakdown;
  commits?: Commit[];
  snapshots?: RepositorySnapshot[];
  contributors?: Contributor[];
  pullRequests?: PullRequest[];
  issues?: Issue[];
  isLoading?: boolean;
}

export default function DashboardCharts({
  languages,
  commits,
  snapshots,
  contributors,
  pullRequests,
  issues,
  isLoading,
}: DashboardChartsProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {Array.from({ length: 6 }).map((_, i) => (
          <ChartSkeleton key={i} />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {languages && Object.keys(languages.percentages).length > 0 && (
        <LanguagePieChart data={languages} />
      )}
      {commits && commits.length > 0 && (
        <CommitActivityChart commits={commits} />
      )}
      {contributors && contributors.length > 0 && (
        <ContributorsBarChart contributors={contributors} />
      )}
      {pullRequests && pullRequests.length > 0 && (
        <PullRequestTrendChart pullRequests={pullRequests} />
      )}
      {issues && issues.length > 0 && (
        <IssueTrendChart issues={issues} />
      )}
      {snapshots && snapshots.length > 0 && (
        <MetricsHistoryChart snapshots={snapshots} />
      )}
    </div>
  );
}
