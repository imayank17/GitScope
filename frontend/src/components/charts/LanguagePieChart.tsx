import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import type { LanguageBreakdown } from '../../types';
import ChartCard from './ChartCard';

const COLORS = [
  '#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#ef4444',
  '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#64748b',
];

interface LanguagePieChartProps {
  data: LanguageBreakdown;
}

export default function LanguagePieChart({ data }: LanguagePieChartProps) {
  const chartData = Object.entries(data.percentages)
    .map(([name, value]) => ({ name, value: Math.round(value * 100) / 100 }))
    .sort((a, b) => b.value - a.value);

  return (
    <ChartCard title="Languages">
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={90}
            paddingAngle={2}
            dataKey="value"
          >
            {chartData.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '8px',
              fontSize: '13px',
            }}
            formatter={(value) => [`${value}%`, 'Share']}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="flex flex-wrap gap-x-4 gap-y-1.5 mt-2">
        {chartData.slice(0, 6).map((item, i) => (
          <div key={item.name} className="flex items-center gap-1.5 text-xs text-surface-400">
            <span
              className="w-2.5 h-2.5 rounded-full shrink-0"
              style={{ backgroundColor: COLORS[i % COLORS.length] }}
            />
            {item.name} ({item.value}%)
          </div>
        ))}
      </div>
    </ChartCard>
  );
}
