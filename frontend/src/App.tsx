import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/layout/Layout';
import { LoginPage } from './pages/auth/LoginPage';
import { DashboardPage } from './pages/dashboard/DashboardPage';
import { MembersPage } from './pages/members/MembersPage';
import { ContributionsPage } from './pages/contributions/ContributionsPage';
import { HierarchyPage } from './pages/hierarchy/HierarchyPage';
import { EventsPage } from './pages/events/EventsPage';
import { ReportsPage } from './pages/reports/ReportsPage';
import { useAuthStore } from './store/authStore';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30000,
      refetchOnWindowFocus: false,
    },
  },
});

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  return <>{children}</>;
};

const PublicRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore();
  return !isAuthenticated ? <>{children}</> : <Navigate to="/" replace />;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
          <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
            <Route index element={<DashboardPage />} />
            <Route path="members" element={<MembersPage />} />
            <Route path="contributions" element={<ContributionsPage />} />
            <Route path="hierarchy/regions" element={<HierarchyPage type="regions" />} />
            <Route path="hierarchy/districts" element={<HierarchyPage type="districts" />} />
            <Route path="hierarchy/paroisses" element={<HierarchyPage type="paroisses" />} />
            <Route path="hierarchy/eglises" element={<HierarchyPage type="eglises" />} />
            <Route path="events" element={<EventsPage />} />
            <Route path="announcements" element={<EventsPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="settings" element={<DashboardPage />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
