import { FiInbox } from 'react-icons/fi';

interface EmptyStateProps {
  message?: string;
  icon?: React.ReactNode;
}

export default function EmptyState({ message = 'No data found', icon }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-surface-400">
      {icon || <FiInbox className="text-4xl mb-3" />}
      <p className="text-sm">{message}</p>
    </div>
  );
}
