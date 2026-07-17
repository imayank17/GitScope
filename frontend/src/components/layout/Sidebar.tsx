import { NavLink, useParams } from 'react-router-dom';
import {
  FiHome, FiUsers, FiGitCommit, FiAlertCircle,
  FiGitPullRequest, FiRefreshCw, FiChevronLeft, FiChevronRight,
} from 'react-icons/fi';
import { useState } from 'react';

const navItems = [
  { label: 'Overview', icon: FiHome, path: '' },
  { label: 'Contributors', icon: FiUsers, path: '/contributors' },
  { label: 'Commits', icon: FiGitCommit, path: '/commits' },
  { label: 'Issues', icon: FiAlertCircle, path: '/issues' },
  { label: 'Pull Requests', icon: FiGitPullRequest, path: '/pulls' },
  { label: 'Sync', icon: FiRefreshCw, path: '/sync' },
];

export default function Sidebar() {
  const { owner, repo } = useParams();
  const base = `/${owner}/${repo}`;
  const [collapsed, setCollapsed] = useState(false);

  return (
    <>
      {/* Desktop sidebar */}
      <aside
        className={`hidden lg:flex flex-col border-r border-surface-800/50 bg-surface-950 transition-all duration-300 ${
          collapsed ? 'w-16' : 'w-56'
        }`}
      >
        <div className="flex items-center justify-end p-3">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="p-1.5 rounded-md text-surface-400 hover:bg-surface-800 transition-colors"
          >
            {collapsed ? <FiChevronRight size={16} /> : <FiChevronLeft size={16} />}
          </button>
        </div>

        <nav className="flex-1 px-2 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={`${base}${item.path}`}
              end={item.path === ''}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary-600/10 text-primary-400'
                    : 'text-surface-400 hover:bg-surface-800 hover:text-surface-200'
                }`
              }
            >
              <item.icon size={18} className="shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Mobile bottom nav */}
      <nav className="lg:hidden fixed bottom-0 left-0 right-0 z-50 bg-surface-950/95 backdrop-blur border-t border-surface-800/50">
        <div className="flex items-center justify-around py-2">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={`${base}${item.path}`}
              end={item.path === ''}
              className={({ isActive }) =>
                `flex flex-col items-center gap-0.5 px-2 py-1 text-xs transition-colors ${
                  isActive ? 'text-primary-400' : 'text-surface-500'
                }`
              }
            >
              <item.icon size={18} />
              <span className="hidden sm:block">{item.label}</span>
            </NavLink>
          ))}
        </div>
      </nav>
    </>
  );
}
