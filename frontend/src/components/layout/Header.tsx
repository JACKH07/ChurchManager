import { Menu, Bell } from 'lucide-react';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { notificationsApi } from '../../api/dashboard';
import { formatRelative } from '../../utils/format';
import { cn } from '../../utils/cn';

interface HeaderProps { onMenuClick: () => void; title?: string; }

export const Header = ({ onMenuClick, title }: HeaderProps) => {
  const [showNotifs, setShowNotifs] = useState(false);

  const { data: notifData } = useQuery({
    queryKey: ['notifications-non-lues'],
    queryFn: () => notificationsApi.getNonLues().then(r => r.data),
    refetchInterval: 60000,
  });

  const count = notifData?.count || 0;
  const notifs = notifData?.notifications || [];

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 lg:px-6 flex-shrink-0">
      <div className="flex items-center gap-4">
        <button onClick={onMenuClick} className="lg:hidden p-2 rounded-lg hover:bg-gray-100">
          <Menu size={20} className="text-gray-600" />
        </button>
        {title && <h1 className="text-base font-semibold text-gray-900 hidden sm:block">{title}</h1>}
      </div>

      <div className="flex items-center gap-2">
        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setShowNotifs(!showNotifs)}
            className="relative p-2 rounded-lg hover:bg-gray-100 text-gray-600 transition-colors"
          >
            <Bell size={20} />
            {count > 0 && (
              <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-bold">
                {count > 9 ? '9+' : count}
              </span>
            )}
          </button>

          {showNotifs && (
            <div className="absolute right-0 top-12 w-80 bg-white border border-gray-200 rounded-xl shadow-xl z-50">
              <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                <span className="font-semibold text-sm text-gray-900">Notifications</span>
                {count > 0 && <span className="badge-red badge">{count} non lue(s)</span>}
              </div>
              <div className="max-h-80 overflow-y-auto">
                {notifs.length === 0 ? (
                  <p className="text-center text-gray-400 text-sm py-8">Aucune notification</p>
                ) : (
                  notifs.map((n: any) => (
                    <div key={n.id} className={cn(
                      'px-4 py-3 border-b border-gray-50 hover:bg-gray-50 cursor-pointer',
                      !n.est_lue && 'bg-blue-50/40'
                    )}>
                      <p className="text-sm font-medium text-gray-900">{n.titre}</p>
                      <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{n.message}</p>
                      <p className="text-xs text-gray-400 mt-1">{formatRelative(n.created_at)}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
