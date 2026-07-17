interface SectionHeaderProps {
  title: string;
  subtitle?: string;
}

export default function SectionHeader({ title, subtitle }: SectionHeaderProps) {
  return (
    <div className="mb-6">
      <h2 className="text-xl font-semibold text-surface-50">{title}</h2>
      {subtitle && <p className="text-sm text-surface-400 mt-1">{subtitle}</p>}
    </div>
  );
}
