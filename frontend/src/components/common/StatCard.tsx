import { motion } from 'framer-motion';
import type { IconType } from 'react-icons';

interface StatCardProps {
  label: string;
  value: string | number;
  icon: IconType;
  color?: string;
  index?: number;
}

export default function StatCard({ label, value, icon: Icon, color = 'text-primary-400', index = 0 }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, duration: 0.4 }}
      className="bg-surface-800/60 border border-surface-700/50 rounded-xl p-5 hover:border-surface-600/60 transition-colors"
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-surface-400 uppercase tracking-wider">{label}</span>
        <Icon className={`text-lg ${color}`} />
      </div>
      <p className="text-2xl font-bold text-surface-50">
        {typeof value === 'number' ? value.toLocaleString() : value}
      </p>
    </motion.div>
  );
}
