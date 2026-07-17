import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import type { RepositorySnapshot } from '../../types';
import ChartCard from './ChartCard';

interface MetricsHistoryChartProps {
  snapshots: RepositorySnapshot[];
}

export default function MetricsHistoryChart({ snapshots }: MetricsHistoryChartProps) {
  const data = snapshots.map((s) => ({
    date: new Date(s.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    stars: s.stars,
    forks: s.forks,
    issues: s.open_issues,
    watchers: s.watchers,
  }));

  return (
    <ChartCard title="Metrics History" className="col-span-full">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', fontSize: '13px' }}
          />
          <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
          <Line type="monotone" dataKey="stars" stroke="#f59e0b" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="forks" stroke="#06b6d4" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="issues" stroke="#ef4444" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="watchers" stroke="#10b981" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
