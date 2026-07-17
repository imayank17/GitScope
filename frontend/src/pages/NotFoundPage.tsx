import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import Button from '../components/common/Button';

export default function NotFoundPage() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center"
      >
        <p className="text-7xl font-bold text-surface-700 mb-4">404</p>
        <h1 className="text-xl font-semibold text-surface-200 mb-2">Page not found</h1>
        <p className="text-sm text-surface-400 mb-8">The page you're looking for doesn't exist or has been moved.</p>
        <Link to="/">
          <Button variant="primary">Go Home</Button>
        </Link>
      </motion.div>
    </div>
  );
}
