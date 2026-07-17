import { motion } from 'framer-motion';
import { FiExternalLink, FiGitBranch, FiCalendar } from 'react-icons/fi';
import type { Repository } from '../../types';
import Badge from '../common/Badge';

interface RepositoryCardProps {
  repo: Repository;
}

export default function RepositoryCard({ repo }: RepositoryCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-surface-800/60 border border-surface-700/50 rounded-xl p-6"
    >
      <div className="flex items-start gap-4 mb-4">
        <img
          src={repo.owner_avatar_url}
          alt={repo.owner_login}
          className="w-12 h-12 rounded-full ring-2 ring-surface-700"
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="text-lg font-semibold text-surface-50 truncate">{repo.full_name}</h3>
            <Badge text={repo.visibility} variant="info" />
          </div>
          <p className="text-sm text-surface-400 mt-1 line-clamp-2">{repo.description || 'No description'}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
        <div className="flex items-center gap-2 text-surface-400">
          <FiGitBranch className="shrink-0" />
          <span>{repo.default_branch}</span>
        </div>
        <div className="flex items-center gap-2 text-surface-400">
          <FiCalendar className="shrink-0" />
          <span>{new Date(repo.created_at).toLocaleDateString()}</span>
        </div>
        {repo.language && (
          <div className="flex items-center gap-2 text-surface-400">
            <span className="w-2.5 h-2.5 rounded-full bg-primary-500 shrink-0" />
            <span>{repo.language}</span>
          </div>
        )}
      </div>

      {repo.topics.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-4">
          {repo.topics.slice(0, 8).map((t) => (
            <Badge key={t} text={t} />
          ))}
        </div>
      )}

      <a
        href={repo.html_url}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-1.5 text-sm text-primary-400 hover:text-primary-300 mt-4 transition-colors"
      >
        View on GitHub <FiExternalLink size={14} />
      </a>
    </motion.div>
  );
}
