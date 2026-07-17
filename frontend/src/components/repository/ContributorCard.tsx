import { motion } from 'framer-motion';
import { FiExternalLink } from 'react-icons/fi';
import type { Contributor } from '../../types';

interface ContributorCardProps {
  contributor: Contributor;
  index?: number;
}

export default function ContributorCard({ contributor, index = 0 }: ContributorCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04 }}
      className="bg-surface-800/60 border border-surface-700/50 rounded-xl p-4 flex items-center gap-4 hover:border-surface-600/60 transition-colors"
    >
      <img
        src={contributor.avatar_url}
        alt={contributor.login}
        className="w-10 h-10 rounded-full ring-2 ring-surface-700"
      />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-surface-100 truncate">{contributor.login}</p>
        <p className="text-xs text-surface-400">{contributor.contributions} contributions</p>
      </div>
      <a
        href={contributor.html_url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-surface-400 hover:text-primary-400 transition-colors shrink-0"
      >
        <FiExternalLink size={16} />
      </a>
    </motion.div>
  );
}
