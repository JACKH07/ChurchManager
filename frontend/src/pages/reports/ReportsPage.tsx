import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Users, CreditCard } from 'lucide-react';
import { dashboardApi } from '../../api/dashboard';
import { formatMontant, MOIS_LABELS } from '../../utils/format';
import { Spinner } from '../../components/ui/Spinner';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';

export const ReportsPage = () => {
  const now = new Date();
  const [mois, setMois] = useState(now.getMonth() + 1);
  const [annee, setAnnee] = useState(now.getFullYear());

  const { data: financeData, isLoading: financeLoading } = useQuery({
    queryKey: ['rapport-financier', mois, annee],
    queryFn: () => dashboardApi.getRapportFinancier({ mois, annee }).then(r => r.data),
  });

  const { data: fidelesData } = useQuery({
    queryKey: ['rapport-fideles'],
    queryFn: () => dashboardApi.getRapportFideles({ statut: 'actif' }).then(r => r.data),
  });

  const YEARS = [annee - 2, annee - 1, annee, annee + 1].filter(y => y >= 2020);

  return (
    <div className="space-y-6">
      {/* Filtres */}
      <div className="card p-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Mois :</label>
            <select value={mois} onChange={e => setMois(Number(e.target.value))} className="input w-auto">
              {MOIS_LABELS.map((m, i) => <option key={i + 1} value={i + 1}>{m}</option>)}
            </select>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Année :</label>
            <select value={annee} onChange={e => setAnnee(Number(e.target.value))} className="input w-auto">
              {YEARS.map(y => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>
        </div>
      </div>

      {/* Rapport financier */}
      <div className="card">
        <div className="card-header flex items-center justify-between">
          <h3 className="font-semibold text-gray-900 flex items-center gap-2">
            <CreditCard size={18} className="text-primary-600" />
            Rapport financier — {MOIS_LABELS[mois - 1]} {annee}
          </h3>
        </div>
        <div className="card-body">
          {financeLoading ? <Spinner /> : financeData ? (
            <div className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="bg-green-50 rounded-xl p-4">
                  <p className="text-sm text-green-700 font-medium">Total collecté</p>
                  <p className="text-3xl font-bold text-green-800 mt-1">{formatMontant(financeData.total_collecte)}</p>
                </div>
                <div className="bg-blue-50 rounded-xl p-4">
                  <p className="text-sm text-blue-700 font-medium">Nombre de transactions</p>
                  <p className="text-3xl font-bold text-blue-800 mt-1">{financeData.nombre_transactions}</p>
                </div>
              </div>
              {Object.keys(financeData.par_type || {}).length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-3">Répartition par type</p>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={Object.entries(financeData.par_type).map(([k, v]) => ({ type: k.replace('_', ' '), montant: v }))}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey="type" tick={{ fontSize: 11 }} />
                      <YAxis tick={{ fontSize: 11 }} tickFormatter={v => `${(v as number / 1000).toFixed(0)}k`} />
                      <Tooltip formatter={(v: any) => [formatMontant(v), 'Montant']} />
                      <Bar dataKey="montant" fill="#1d4ed8" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          ) : (
            <p className="text-gray-400 text-center py-8">Aucune donnée disponible</p>
          )}
        </div>
      </div>

      {/* Rapport fidèles */}
      <div className="card">
        <div className="card-header flex items-center justify-between">
          <h3 className="font-semibold text-gray-900 flex items-center gap-2">
            <Users size={18} className="text-primary-600" />
            Rapport des fidèles actifs
          </h3>
        </div>
        <div className="card-body">
          {fidelesData ? (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-xl">
                <p className="text-2xl font-bold text-blue-800">{fidelesData.total}</p>
                <p className="text-xs text-blue-600 mt-1">Total fidèles actifs</p>
              </div>
            </div>
          ) : (
            <Spinner />
          )}
        </div>
      </div>
    </div>
  );
};
