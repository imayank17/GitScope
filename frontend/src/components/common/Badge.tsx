interface BadgeProps {
  text: string;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
}

const colors = {
  default: 'bg-surface-700 text-surface-300',
  success: 'bg-emerald-500/15 text-emerald-400',
  warning: 'bg-amber-500/15 text-amber-400',
  danger: 'bg-red-500/15 text-red-400',
  info: 'bg-cyan-500/15 text-cyan-400',
};

export default function Badge({ text, variant = 'default' }: BadgeProps) {
  return (
    <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[variant]}`}>
      {text}
    </span>
  );
}
