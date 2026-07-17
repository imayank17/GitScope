import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import DashboardLayout from '../layouts/DashboardLayout';
import LandingPage from '../pages/LandingPage';
import DashboardPage from '../pages/DashboardPage';
import ContributorsPage from '../pages/ContributorsPage';
import CommitsPage from '../pages/CommitsPage';
import IssuesPage from '../pages/IssuesPage';
import PullRequestsPage from '../pages/PullRequestsPage';
import SyncPage from '../pages/SyncPage';
import NotFoundPage from '../pages/NotFoundPage';

const router = createBrowserRouter([
  {
    element: <MainLayout />,
    children: [
      { path: '/', element: <LandingPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
  {
    path: '/:owner/:repo',
    element: <DashboardLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'contributors', element: <ContributorsPage /> },
      { path: 'commits', element: <CommitsPage /> },
      { path: 'issues', element: <IssuesPage /> },
      { path: 'pulls', element: <PullRequestsPage /> },
      { path: 'sync', element: <SyncPage /> },
    ],
  },
]);

export default function AppRouter() {
  return <RouterProvider router={router} />;
}
