interface SkeletonProps {
  className?: string;
}

function Skeleton({ className = '' }: SkeletonProps) {
  return <div className={`animate-pulse bg-surface-700/50 rounded-lg ${className}`} />;
}

export function CardSkeleton() {
  return (
    <div className="bg-surface-800/60 border border-surface-700/50 rounded-xl p-5 space-y-3">
      <Skeleton className="h-4 w-24" />
      <Skeleton className="h-8 w-16" />
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="bg-surface-800/60 border border-surface-700/50 rounded-xl p-6 space-y-4">
      <Skeleton className="h-5 w-32" />
      <Skeleton className="h-56 w-full" />
    </div>
  );
}

export function ListSkeleton({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="bg-surface-800/60 border border-surface-700/50 rounded-xl p-4 space-y-2">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
        </div>
      ))}
    </div>
  );
}

export default Skeleton;
