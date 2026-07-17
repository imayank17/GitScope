import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiSearch, FiBarChart2, FiGitPullRequest, FiUsers, FiRefreshCw, FiTrendingUp } from 'react-icons/fi';
import { useAnalyzeRepository } from '../hooks/useRepository';
import Button from '../components/common/Button';

export default function LandingPage() {
  const [input, setInput] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const analyze = useAnalyzeRepository();

  const handleAnalyze = () => {
    setError('');
    const trimmed = input.trim();
    if (!trimmed) { setError('Please enter a repository'); return; }

    // Parse owner/repo from various formats
    let repoUrl = trimmed;
    const ghMatch = trimmed.match(/github\.com\/([^/]+)\/([^/\s?#]+)/);
    if (ghMatch) {
      repoUrl = `${ghMatch[1]}/${ghMatch[2]}`;
    }

    analyze.mutate(
      { repo_url: repoUrl },
      {
        onSuccess: (data) => navigate(`/${data.full_name}`),
        onError: (err) => setError(err instanceof Error ? err.message : 'Failed to analyze repository'),
      }
    );
  };

  const features = [
    { icon: FiBarChart2, title: 'Rich Analytics', desc: 'Detailed metrics, language breakdown, and historical trends at a glance.' },
    { icon: FiUsers, title: 'Contributor Insights', desc: 'See who drives the project with contributor rankings and activity data.' },
    { icon: FiGitPullRequest, title: 'PR & Issue Tracking', desc: 'Visualize pull request and issue trends to understand project health.' },
    { icon: FiRefreshCw, title: 'Live Sync', desc: 'Background synchronization keeps your data fresh automatically.' },
    { icon: FiTrendingUp, title: 'Historical Metrics', desc: 'Track stars, forks, and issues over time with snapshot history.' },
    { icon: FiSearch, title: 'Instant Search', desc: 'Paste a URL or type owner/repo — analysis starts immediately.' },
  ];

  return (
    <div className="relative">
      {/* Background gradient */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-primary-600/8 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-cyan-500/5 rounded-full blur-3xl" />
      </div>

      {/* Hero */}
      <section className="max-w-4xl mx-auto px-4 pt-20 pb-16 sm:pt-28 sm:pb-24 text-center">
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-surface-50 mb-4">
            Understand any
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-cyan-400"> GitHub repo </span>
            in seconds
          </h1>
          <p className="text-lg text-surface-400 max-w-2xl mx-auto mb-10">
            GitScope gives you a clean analytics dashboard for any public repository.
            Paste a link, get insights.
          </p>
        </motion.div>

        {/* Search card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.5 }}
          className="max-w-xl mx-auto bg-surface-800/70 border border-surface-700/50 rounded-2xl p-6 backdrop-blur"
        >
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <FiSearch className="absolute left-3.5 top-1/2 -translate-y-1/2 text-surface-400" />
              <input
                type="text"
                value={input}
                onChange={(e) => { setInput(e.target.value); setError(''); }}
                onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
                placeholder="https://github.com/vercel/next.js"
                className="w-full bg-surface-900/80 border border-surface-700 rounded-xl pl-10 pr-4 py-3 text-sm text-surface-100 placeholder-surface-500 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500/30 transition-colors"
              />
            </div>
            <Button
              onClick={handleAnalyze}
              isLoading={analyze.isPending}
              size="lg"
              className="sm:w-auto"
            >
              Analyze
            </Button>
          </div>
          {error && <p className="text-xs text-red-400 mt-3 text-left">{error}</p>}
          <p className="text-xs text-surface-500 mt-3">
            Try: 
            <button onClick={() => setInput('vercel/next.js')} className="text-primary-400 hover:underline cursor-pointer">vercel/next.js</button>
            {' · '}
            <button onClick={() => setInput('microsoft/vscode')} className="text-primary-400 hover:underline cursor-pointer">microsoft/vscode</button>
          </p>
        </motion.div>
      </section>

      {/* Features */}
      <section id="features" className="max-w-6xl mx-auto px-4 py-16">
        <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
          <h2 className="text-2xl font-bold text-surface-50 text-center mb-3">What you get</h2>
          <p className="text-surface-400 text-center mb-12 max-w-lg mx-auto">
            A full picture of any repository, powered by the GitHub API and delivered with a clean interface.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08 }}
              className="bg-surface-800/40 border border-surface-700/40 rounded-xl p-6 hover:border-surface-600/50 transition-colors"
            >
              <f.icon className="text-primary-400 text-xl mb-3" />
              <h3 className="text-sm font-semibold text-surface-100 mb-1">{f.title}</h3>
              <p className="text-xs text-surface-400 leading-relaxed">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Why GitScope */}
      <section id="why" className="max-w-4xl mx-auto px-4 py-16 text-center">
        <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
          <h2 className="text-2xl font-bold text-surface-50 mb-3">Why GitScope?</h2>
          <p className="text-surface-400 max-w-2xl mx-auto leading-relaxed">
            GitHub provides raw data — GitScope turns it into clarity. Whether you're evaluating a dependency,
            reviewing an open-source project before contributing, or just curious about a repo's trajectory,
            GitScope delivers the signal without the noise.
          </p>
        </motion.div>
      </section>
    </div>
  );
}
