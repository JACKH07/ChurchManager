import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Users, CreditCard, Building2, Calendar,
  Bell, BarChart3, Settings, ChevronDown, Church, LogOut, X,
} from 'lucide-react';
import { useState } from 'react';
import { cn } from '../../utils/cn';
import { useAuthStore, hasMinRole } from '../../store/authStore';

interface SidebarProps { isOpen: boolean; onClose: () => void; }

interface NavItem {
  icon: React.ElementType;
  label: string;
  to?: string;
  children?: { label: string; to: string }[];
  minRole?: string;
}

const NAV_ITEMS: NavItem[] = [
  { icon: LayoutDashboard, label: 'Tableau de bord', to: '/' },
  {
    icon: Building2, label: 'Hiérarchie', minRole: 'chef_paroisse',
    children: [
      { label: 'Régions', to: '/hierarchy/regions' },
      { label: 'Districts', to: '/hierarchy/districts' },
      { label: 'Paroisses', to: '/hierarchy/paroisses' },
      { label: 'Églises', to: '/hierarchy/eglises' },
    ],
  },
  { icon: Users, label: 'Fidèles', to: '/members' },
  { icon: CreditCard, label: 'Cotisations', to: '/contributions', minRole: 'pasteur_local' },
  { icon: Calendar, label: 'Événements', to: '/events' },
  { icon: Bell, label: 'Annonces', to: '/announcements' },
  { icon: BarChart3, label: 'Rapports', to: '/reports', minRole: 'chef_paroisse' },
  { icon: Settings, label: 'Paramètres', to: '/settings', minRole: 'admin_national' },
];

const NavItemComponent = ({ item }: { item: NavItem }) => {
  const [expanded, setExpanded] = useState(false);
  const location = useLocation();

  if (item.children) {
    const isActive = item.children.some(c => location.pathname.startsWith(c.to));
    return (
      <div>
        <button
          onClick={() => setExpanded(!expanded)}
          className={cn('sidebar-link w-full justify-between', isActive && 'active')}
        >
          <span className="flex items-center gap-3">
            <item.icon size={18} />
            {item.label}
          </span>
          <ChevronDown size={14} className={cn('transition-transform', expanded && 'rotate-180')} />
        </button>
        {expanded && (
          <div className="ml-7 mt-1 space-y-0.5">
            {item.children.map((child) => (
              <NavLink key={child.to} to={child.to}
                className={({ isActive }) => cn('block px-3 py-2 rounded-lg text-sm transition-colors',
                  isActive ? 'text-primary-700 font-semibold bg-primary-50' : 'text-gray-500 hover:text-gray-800 hover:bg-gray-50'
                )}>
                {child.label}
              </NavLink>
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <NavLink to={item.to!}
      className={({ isActive }) => cn('sidebar-link', isActive && 'active')}
    >
      <item.icon size={18} />
      {item.label}
    </NavLink>
  );
};

export const Sidebar = ({ isOpen, onClose }: SidebarProps) => {
  const { user, logout } = useAuthStore();

  const visibleItems = NAV_ITEMS;

  return (
    <>
      {/* Overlay mobile */}
      {isOpen && (
        <div className="fixed inset-0 bg-black/40 z-40 lg:hidden" onClick={onClose} />
      )}

      {/* Sidebar */}
      <aside className={cn(
        'fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 flex flex-col transition-transform duration-300',
        'lg:translate-x-0 lg:static lg:z-auto',
        isOpen ? 'translate-x-0' : '-translate-x-full'
      )}>
        {/* Logo */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-700 to-purple-600 flex items-center justify-center">
              <Church size={18} className="text-white" />
            </div>
            <div>
              <p className="font-bold text-gray-900 text-sm leading-tight">ChurchManager</p>
              <p className="text-xs text-gray-400">Gestion ecclésicastique</p>
            </div>
          </div>
          <button onClick={onClose} className="lg:hidden p-1 rounded-lg hover:bg-gray-100">
            <X size={18} className="text-gray-400" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          {visibleItems.map((item) => (
            <NavItemComponent key={item.label} item={item} />
          ))}
        </nav>

        {/* Utilisateur */}
        <div className="px-3 py-4 border-t border-gray-100">
          <div className="flex items-center gap-3 px-3 py-2 rounded-xl bg-gray-50">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary-500 to-purple-500 flex items-center justify-center text-white font-semibold text-sm flex-shrink-0">
              {user?.first_name?.[0]}{user?.last_name?.[0]}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{user?.full_name}</p>
              <p className="text-xs text-gray-400 truncate capitalize">{user?.role?.replace('_', ' ')}</p>
            </div>
            <button onClick={logout} className="p-1.5 rounded-lg hover:bg-gray-200 text-gray-400 hover:text-red-500 transition-colors" title="Déconnexion">
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};
