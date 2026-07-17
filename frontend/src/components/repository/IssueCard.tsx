import { motion } from 'framer-motion';
import { FiExternalLink } from 'react-icons/fi';
import type { Issue } from '../../types';
import Badge from '../common/Badge';

interface IssueCardProps {
  issue: Issue;
  index?: number;
}

export default function IssueCard({ issue, index = 0 }: IssueCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04 }}
      className="bg-surface-800/60 border border-surface-700/50 rounded-xl p-4 hover:border-surface-600/60 transition-colors"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs text-surface-500 font-mono">#{issue.number}</span>
            <Badge
              text={issue.state}
              variant={issue.state === 'open' ? 'success' : 'danger'}
            />
          </div>
          <p className="text-sm text-surface-100 font-medium line-clamp-2">{issue.title}</p>
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-2 text-xs text-surface-400">
            <span>{issue.user_login}</span>
            <span>{new Date(issue.created_at).toLocaleDateString()}</span>
            {issue.comments > 0 && <span>{issue.comments} comments</span>}
          </div>
          {issue.labels.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {issue.labels.map((l) => (
                <Badge key={l} text={l} variant="info" />
              ))}
            </div>
          )}
        </div>
        <a
          href={issue.html_url}
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
