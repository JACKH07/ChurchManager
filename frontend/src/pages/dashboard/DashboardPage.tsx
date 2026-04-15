import { useQuery } from '@tanstack/react-query';
import {
  Users, Building2, TrendingUp, CreditCard, AlertTriangle,
  Calendar, MapPin, Activity, Church,
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell,
} from 'recharts';
import { dashboardApi } from '../../api/dashboard';
import { Spinner } from '../../components/ui/Spinner';
import { formatMontant } from '../../utils/format';
import { useAuthStore } from '../../store/authStore';

const COLORS = ['#1d4ed8', '#7c3aed', '#059669', '#d97706', '#dc2626', '#0891b2'];

const StatCard = ({ icon: Icon, label, value, sub, color = 'blue' }: any) => {
  const colorMap: Record<string, string> = {
    blue: 'bg-blue-100 text-blue-700',
    purple: 'bg-purple-100 text-purple-700',
    green: 'bg-green-100 text-green-700',
    gold: 'bg-amber-100 text-amber-700',
  };
  return (
    <div className="card p-5 flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${colorMap[color]}`}>
        <Icon size={22} />
      </div>
      <div>
        <p className="text-sm text-gray-500 mb-0.5">{label}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
};

export const DashboardPage = () => {
  const { user } = useAuthStore();
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => dashboardApi.getStats().then(r => r.data),
    refetchInterval: 300000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Bienvenue */}
      <div className="card p-6 bg-gradient-to-br from-primary-700 to-purple-700 text-white border-0">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold">Bonjour, {user?.first_name}</h2>
            <p className="text-blue-200 text-sm mt-1">
              {new Date().toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
            </p>
          </div>
          <div className="w-16 h-16 rounded-2xl bg-white/20 flex items-center justify-center">
            <Church size={30} className="text-white" />
          </div>
        </div>
        {stats?.alertes?.length > 0 && (
          <div className="mt-4 flex items-center gap-2 bg-white/20 rounded-xl px-4 py-2.5">
            <AlertTriangle size={16} className="text-yellow-300" />
            <p className="text-sm text-yellow-100">{stats.alertes[0].message}</p>
          </div>
        )}
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Users} label="Total Fidèles" value={stats?.total_fideles?.toLocaleString('fr-FR') || 0} sub={`+${stats?.nouveaux_fideles_mois || 0} ce mois`} color="blue" />
        <StatCard icon={Building2} label="Régions" value={stats?.total_regions || 0} sub={`${stats?.total_districts || 0} districts`} color="purple" />
        <StatCard icon={CreditCard} label="Recettes ce mois" value={formatMontant(stats?.recettes_mois || 0)} sub={`${stats?.nombre_paiements_mois || 0} paiements`} color="green" />
        <StatCard icon={Activity} label="Taux de cotisation" value={`${stats?.taux_cotisation_mois || 0}%`} sub={`${stats?.evenements_a_venir || 0} événements à venir`} color="gold" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Évolution des cotisations */}
        <div className="card">
          <div className="card-header">
            <h3 className="font-semibold text-gray-900 flex items-center gap-2">
              <TrendingUp size={18} className="text-primary-600" />
              Évolution des cotisations (6 mois)
            </h3>
          </div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={stats?.evolution_cotisations || []}>
                <defs>
                  <linearGradient id="colorMontant" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#1d4ed8" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#1d4ed8" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="mois" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                <Tooltip formatter={(v: any) => [formatMontant(v), 'Montant']} />
                <Area type="monotone" dataKey="montant" stroke="#1d4ed8" strokeWidth={2} fill="url(#colorMontant)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Répartition par région */}
        <div className="card">
          <div className="card-header">
            <h3 className="font-semibold text-gray-900 flex items-center gap-2">
              <MapPin size={18} className="text-primary-600" />
              Fidèles par région
            </h3>
          </div>
          <div className="card-body">
            {stats?.repartition_regions?.length > 0 ? (
              <div className="flex items-center gap-4">
                <ResponsiveContainer width="50%" height={180}>
                  <PieChart>
                    <Pie
                      data={stats.repartition_regions}
                      dataKey="total"
                      nameKey="region"
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                    >
                      {stats.repartition_regions.map((_: any, i: number) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(v: any) => [v, 'Fidèles']} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="flex-1 space-y-2">
                  {stats.repartition_regions.slice(0, 6).map((r: any, i: number) => (
                    <div key={r.code} className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                        <span className="text-gray-700 truncate max-w-[120px]">{r.region}</span>
                      </div>
                      <span className="font-semibold text-gray-900">{r.total.toLocaleString('fr-FR')}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-40 text-gray-400 text-sm">
                Aucune donnée disponible
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Statistiques secondaires */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="card p-5 text-center">
          <p className="text-3xl font-bold text-primary-700">{stats?.total_paroisses || 0}</p>
          <p className="text-sm text-gray-500 mt-1">Paroisses</p>
        </div>
        <div className="card p-5 text-center">
          <p className="text-3xl font-bold text-purple-700">{stats?.total_eglises || 0}</p>
          <p className="text-sm text-gray-500 mt-1">Églises locales</p>
        </div>
        <div className="card p-5 text-center">
          <div className="flex items-center justify-center gap-1">
            <Calendar size={18} className="text-amber-600" />
            <p className="text-3xl font-bold text-amber-700">{stats?.evenements_a_venir || 0}</p>
          </div>
          <p className="text-sm text-gray-500 mt-1">Événements à venir</p>
        </div>
      </div>
    </div>
  );
};
