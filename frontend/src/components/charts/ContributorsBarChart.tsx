import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import type { Contributor } from '../../types';
import ChartCard from './ChartCard';

interface ContributorsBarChartProps {
  contributors: Contributor[];
}

export default function ContributorsBarChart({ contributors }: ContributorsBarChartProps) {
  const data = contributors
    .slice(0, 10)
    .map((c) => ({ name: c.login, contributions: c.contributions }));

  return (
    <ChartCard title="Top Contributors">
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} layout="vertical" margin={{ left: 20 }}>
          <XAxis type="number" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
          <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} width={80} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', fontSize: '13px' }}
          />
          <Bar dataKey="contributions" fill="#6366f1" radius={[0, 4, 4, 0]} barSize={16} />
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}
