import { FiStar, FiGitBranch, FiEye, FiAlertCircle, FiCode } from 'react-icons/fi';
import type { Repository } from '../../types';
import StatCard from '../common/StatCard';

interface DashboardStatsProps {
  repo: Repository;
}

export default function DashboardStats({ repo }: DashboardStatsProps) {
  const stats = [
    { label: 'Stars', value: repo.stars, icon: FiStar, color: 'text-amber-400' },
    { label: 'Forks', value: repo.forks, icon: FiGitBranch, color: 'text-cyan-400' },
    { label: 'Watchers', value: repo.watchers, icon: FiEye, color: 'text-emerald-400' },
    { label: 'Open Issues', value: repo.open_issues, icon: FiAlertCircle, color: 'text-red-400' },
    { label: 'Language', value: repo.language || '—', icon: FiCode, color: 'text-primary-400' },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
      {stats.map((s, i) => (
        <StatCard key={s.label} {...s} index={i} />
      ))}
    </div>
  );
}
