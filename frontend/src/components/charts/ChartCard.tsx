import type { ReactNode } from 'react';
import { motion } from 'framer-motion';

interface ChartCardProps {
  title: string;
  children: ReactNode;
  className?: string;
}

export default function ChartCard({ title, children, className = '' }: ChartCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`bg-surface-800/60 border border-surface-700/50 rounded-xl p-6 ${className}`}
    >
      <h3 className="text-sm font-medium text-surface-300 mb-4">{title}</h3>
      {children}
    </motion.div>
  );
}
