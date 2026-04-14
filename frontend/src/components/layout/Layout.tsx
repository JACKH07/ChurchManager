import { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

const PAGE_TITLES: Record<string, string> = {
  '/': 'Tableau de bord',
  '/members': 'Fidèles',
  '/contributions': 'Cotisations',
  '/events': 'Événements',
  '/announcements': 'Annonces',
  '/reports': 'Rapports',
  '/settings': 'Paramètres',
  '/hierarchy/regions': 'Régions',
  '/hierarchy/districts': 'Districts',
  '/hierarchy/paroisses': 'Paroisses',
  '/hierarchy/eglises': 'Églises',
};

export const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const title = PAGE_TITLES[location.pathname] || 'ChurchManager';

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header onMenuClick={() => setSidebarOpen(true)} title={title} />
        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
