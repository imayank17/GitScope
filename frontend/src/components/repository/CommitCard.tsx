import { motion } from 'framer-motion';
import { FiGitCommit, FiExternalLink } from 'react-icons/fi';
import type { Commit } from '../../types';

interface CommitCardProps {
  commit: Commit;
  index?: number;
}

export default function CommitCard({ commit, index = 0 }: CommitCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04 }}
      className="bg-surface-800/60 border border-surface-700/50 rounded-xl p-4 hover:border-surface-600/60 transition-colors"
    >
      <div className="flex items-start gap-3">
        <FiGitCommit className="text-primary-400 mt-1 shrink-0" />
        <div className="flex-1 min-w-0">
          <p className="text-sm text-surface-100 font-medium line-clamp-2">{commit.message}</p>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-xs text-surface-400">
            <span>{commit.author_name}</span>
            <span>{new Date(commit.author_date).toLocaleDateString()}</span>
            <code className="font-mono text-surface-500 bg-surface-800 px-1.5 py-0.5 rounded">
              {commit.sha.slice(0, 7)}
            </code>
          </div>
        </div>
        <a
          href={commit.html_url}
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
