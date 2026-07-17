import { Link, useLocation } from 'react-router-dom';
import { FiGithub, FiMenu, FiX } from 'react-icons/fi';
import { useState } from 'react';

export default function Navbar() {
  const location = useLocation();
  const isLanding = location.pathname === '/';
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 bg-surface-950/80 backdrop-blur-xl border-b border-surface-800/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2.5 text-surface-50 font-bold text-lg">
            <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center">
              <FiGithub className="text-white text-sm" />
            </div>
            GitScope
          </Link>

          {/* Desktop */}
          <div className="hidden md:flex items-center gap-6">
            {isLanding ? (
              <>
                <a href="#features" className="text-sm text-surface-400 hover:text-surface-100 transition-colors">Features</a>
                <a href="#why" className="text-sm text-surface-400 hover:text-surface-100 transition-colors">Why GitScope</a>
              </>
            ) : (
              <Link to="/" className="text-sm text-surface-400 hover:text-surface-100 transition-colors">← Back to Home</Link>
            )}
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-surface-400 hover:text-surface-100 transition-colors"
            >
              <FiGithub className="text-lg" />
            </a>
          </div>

          {/* Mobile toggle */}
          <button onClick={() => setMobileOpen(!mobileOpen)} className="md:hidden text-surface-400">
            {mobileOpen ? <FiX size={22} /> : <FiMenu size={22} />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-surface-800 bg-surface-950 px-4 py-4 space-y-3">
          {isLanding ? (
            <>
              <a href="#features" onClick={() => setMobileOpen(false)} className="block text-sm text-surface-400">Features</a>
              <a href="#why" onClick={() => setMobileOpen(false)} className="block text-sm text-surface-400">Why GitScope</a>
            </>
          ) : (
            <Link to="/" onClick={() => setMobileOpen(false)} className="block text-sm text-surface-400">← Back to Home</Link>
          )}
        </div>
      )}
    </nav>
  );
}
