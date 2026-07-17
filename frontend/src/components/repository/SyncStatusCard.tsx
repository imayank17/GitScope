import { motion } from 'framer-motion';
import { FiRefreshCw, FiCheck, FiAlertTriangle, FiClock } from 'react-icons/fi';
import type { SyncStatus } from '../../types';
import Button from '../common/Button';

interface SyncStatusCardProps {
  syncStatus: SyncStatus | undefined;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export default function SyncStatusCard({ syncStatus, onRefresh, isRefreshing }: SyncStatusCardProps) {
  const status = syncStatus?.status || 'UNKNOWN';
  const isSyncing = status === 'SYNCING' || isRefreshing;

  const statusConfig: Record<string, { icon: typeof FiCheck; color: string; label: string }> = {
    COMPLETED: { icon: FiCheck, color: 'text-emerald-400', label: 'Synced' },
    SYNCING: { icon: FiRefreshCw, color: 'text-amber-400', label: 'Syncing...' },
    FAILED: { icon: FiAlertTriangle, color: 'text-red-400', label: 'Failed' },
    PENDING: { icon: FiClock, color: 'text-surface-400', label: 'Pending' },
  };

  const cfg = statusConfig[status] || statusConfig.PENDING;
  const StatusIcon = cfg.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-surface-800/60 border border-surface-700/50 rounded-xl p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-surface-300">Synchronization</h3>
        <div className={`flex items-center gap-2 ${cfg.color}`}>
          <StatusIcon className={isSyncing ? 'animate-spin' : ''} size={16} />
          <span className="text-sm font-medium">{cfg.label}</span>
        </div>
      </div>

      {syncStatus?.last_synced_at && (
        <p className="text-xs text-surface-400 mb-1">
          Last synced: {new Date(syncStatus.last_synced_at).toLocaleString()}
        </p>
      )}

      {syncStatus?.error && (
        <p className="text-xs text-red-400 mb-3 bg-red-500/10 p-2 rounded-lg">{syncStatus.error}</p>
      )}

      <Button
        variant="secondary"
        size="sm"
        onClick={onRefresh}
        isLoading={isSyncing}
        disabled={isSyncing}
        className="mt-3"
      >
        <FiRefreshCw size={14} />
        {isSyncing ? 'Syncing...' : 'Refresh Now'}
      </Button>
    </motion.div>
  );
}
