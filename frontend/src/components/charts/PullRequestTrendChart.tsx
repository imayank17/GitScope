import { useMemo } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import type { PullRequest } from '../../types';
import ChartCard from './ChartCard';

interface PullRequestTrendChartProps {
  pullRequests: PullRequest[];
}

export default function PullRequestTrendChart({ pullRequests }: PullRequestTrendChartProps) {
  const data = useMemo(() => {
    const buckets: Record<string, { open: number; merged: number; closed: number }> = {};
    pullRequests.forEach((pr) => {
      const date = new Date(pr.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      if (!buckets[date]) buckets[date] = { open: 0, merged: 0, closed: 0 };
      if (pr.merged_at) buckets[date].merged++;
      else if (pr.state === 'closed') buckets[date].closed++;
      else buckets[date].open++;
    });
    return Object.entries(buckets)
      .map(([date, v]) => ({ date, ...v }))
      .reverse();
  }, [pullRequests]);

  return (
    <ChartCard title="Pull Request Trend">
      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={data}>
          <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} allowDecimals={false} />
          <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', fontSize: '13px' }} />
          <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
          <Area type="monotone" dataKey="open" stackId="1" stroke="#10b981" fill="#10b981" fillOpacity={0.15} strokeWidth={2} />
          <Area type="monotone" dataKey="merged" stackId="1" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.15} strokeWidth={2} />
          <Area type="monotone" dataKey="closed" stackId="1" stroke="#ef4444" fill="#ef4444" fillOpacity={0.15} strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
