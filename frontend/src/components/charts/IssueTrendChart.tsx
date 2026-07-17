import { useMemo } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import type { Issue } from '../../types';
import ChartCard from './ChartCard';

interface IssueTrendChartProps {
  issues: Issue[];
}

export default function IssueTrendChart({ issues }: IssueTrendChartProps) {
  const data = useMemo(() => {
    const buckets: Record<string, { open: number; closed: number }> = {};
    issues.forEach((issue) => {
      const date = new Date(issue.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      if (!buckets[date]) buckets[date] = { open: 0, closed: 0 };
      if (issue.state === 'open') buckets[date].open++;
      else buckets[date].closed++;
    });
    return Object.entries(buckets)
      .map(([date, v]) => ({ date, ...v }))
      .reverse();
  }, [issues]);

  return (
    <ChartCard title="Issue Trend">
      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={data}>
          <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} allowDecimals={false} />
          <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', fontSize: '13px' }} />
          <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
          <Area type="monotone" dataKey="open" stroke="#10b981" fill="#10b981" fillOpacity={0.15} strokeWidth={2} />
          <Area type="monotone" dataKey="closed" stroke="#ef4444" fill="#ef4444" fillOpacity={0.15} strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
