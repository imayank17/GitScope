import { FiGithub } from 'react-icons/fi';

export default function Footer() {
  return (
    <footer className="border-t border-surface-800/50 bg-surface-950">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-surface-400 text-sm">
            <FiGithub />
            <span>GitScope — GitHub Repository Analytics</span>
          </div>
          <p className="text-xs text-surface-500">
            Built with React, TypeScript & FastAPI
          </p>
        </div>
      </div>
    </footer>
  );
}
