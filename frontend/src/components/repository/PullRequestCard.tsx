import { motion } from 'framer-motion';
import { FiExternalLink, FiGitMerge } from 'react-icons/fi';
import type { PullRequest } from '../../types';
import Badge from '../common/Badge';

interface PullRequestCardProps {
  pr: PullRequest;
  index?: number;
}

export default function PullRequestCard({ pr, index = 0 }: PullRequestCardProps) {
  const isMerged = !!pr.merged_at;
  const stateVariant = isMerged ? 'info' : pr.state === 'open' ? 'success' : 'danger';
  const stateText = isMerged ? 'merged' : pr.state;

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04 }}
      className="bg-surface-800/60 border border-surface-700/50 rounded-xl p-4 hover:border-surface-600/60 transition-colors"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="text-xs text-surface-500 font-mono">#{pr.number}</span>
            <Badge text={stateText} variant={stateVariant} />
            {pr.draft && <Badge text="draft" variant="warning" />}
            {isMerged && <FiGitMerge className="text-cyan-400" size={14} />}
          </div>
          <p className="text-sm text-surface-100 font-medium line-clamp-2">{pr.title}</p>
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-2 text-xs text-surface-400">
            <span>{pr.user_login}</span>
            <span>{new Date(pr.created_at).toLocaleDateString()}</span>
          </div>
          {pr.labels.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {pr.labels.map((l) => (
                <Badge key={l} text={l} variant="info" />
              ))}
            </div>
          )}
        </div>
        <a
          href={pr.html_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-surface-400 hover:text-primary-400 transition-colors shrink-0"
        >
          <FiExternalLink size={15} />
        </a>
      </div>
    </motion.div>
  );
}
