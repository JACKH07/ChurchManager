import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, CheckCircle, XCircle, TrendingUp, CreditCard } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { contributionsApi } from '../../api/contributions';
import { Spinner } from '../../components/ui/Spinner';
import { EmptyState } from '../../components/ui/EmptyState';
import { Pagination } from '../../components/ui/Pagination';
import { Modal } from '../../components/ui/Modal';
import { CotisationForm } from '../../components/forms/CotisationForm';
import { formatDate, formatMontant, STATUT_COTISATION_COLORS, MOIS_LABELS } from '../../utils/format';
import { cn } from '../../utils/cn';

const TYPE_LABELS: Record<string, string> = {
  mensuelle_membre: 'Cotisation membre',
  dime: 'Dîme',
  offrande: 'Offrande',
  contribution_paroisse: 'Contribution Paroisse',
  don_special: 'Don spécial',
};

export const ContributionsPage = () => {
  const [page, setPage] = useState(1);
  const [statut, setStatut] = useState('');
  const [type, setType] = useState('');
  const [showForm, setShowForm] = useState(false);
  const queryClient = useQueryClient();
  const now = new Date();

  const { data, isLoading } = useQuery<any>({
    queryKey: ['cotisations', page, statut, type],
    queryFn: () => contributionsApi.getCotisations({ page, statut, type_cotisation: type }).then(r => r.data),
    placeholderData: (prev: any) => prev,
  });

  const { data: resume } = useQuery({
    queryKey: ['cotisations-resume'],
    queryFn: () => contributionsApi.getResume({ statut: 'valide', periode_mois: now.getMonth() + 1, periode_annee: now.getFullYear() }).then(r => r.data),
  });

  const { data: evolution } = useQuery({
    queryKey: ['evolution-mensuelle'],
    queryFn: () => contributionsApi.getEvolutionMensuelle().then(r => r.data),
  });

  const validerMutation = useMutation({
    mutationFn: (id: number) => contributionsApi.validerCotisation(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['cotisations'] }),
  });

  const rejeterMutation = useMutation({
    mutationFn: (id: number) => contributionsApi.rejeterCotisation(id, 'Refusé'),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['cotisations'] }),
  });

  const totalPages = data ? Math.ceil(data.count / 25) : 1;

  return (
    <div className="space-y-6">
      {/* Résumé financier */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="card p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-green-100 flex items-center justify-center">
              <CreditCard size={18} className="text-green-700" />
            </div>
            <p className="text-sm text-gray-500">Total collecté (mois)</p>
          </div>
          <p className="text-2xl font-bold text-gray-900">{formatMontant(resume?.total_collecte || 0)}</p>
          <p className="text-xs text-gray-400 mt-1">{resume?.nombre_cotisations || 0} paiements</p>
        </div>
        <div className="card p-5 sm:col-span-2">
          <p className="text-sm font-medium text-gray-700 mb-3">Par type de cotisation</p>
          <div className="flex flex-wrap gap-2">
            {Object.entries(resume?.par_type || {}).map(([type, montant]: [string, any]) => (
              <div key={type} className="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-1.5">
                <span className="text-xs text-gray-500">{TYPE_LABELS[type] || type}</span>
                <span className="text-xs font-semibold text-gray-900">{formatMontant(montant)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Graphique évolution */}
      {evolution && (
        <div className="card">
          <div className="card-header">
            <h3 className="font-semibold text-gray-900 flex items-center gap-2">
              <TrendingUp size={18} className="text-primary-600" />
              Évolution mensuelle des cotisations
            </h3>
          </div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={evolution}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="mois" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
                <Tooltip formatter={(v: any) => [formatMontant(v), 'Montant']} />
                <Bar dataKey="montant" fill="#1d4ed8" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Liste cotisations */}
      <div className="card">
        <div className="card-header flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <h2 className="font-semibold text-gray-900">Cotisations et paiements</h2>
          <button onClick={() => setShowForm(true)} className="btn-primary btn-sm flex items-center gap-2">
            <Plus size={16} />
            Enregistrer un paiement
          </button>
        </div>
        <div className="px-6 py-3 border-b border-gray-100 flex flex-col sm:flex-row gap-3">
          <select value={statut} onChange={(e) => { setStatut(e.target.value); setPage(1); }} className="input w-auto">
            <option value="">Tous les statuts</option>
            <option value="en_attente">En attente</option>
            <option value="valide">Validé</option>
            <option value="rejete">Rejeté</option>
          </select>
          <select value={type} onChange={(e) => { setType(e.target.value); setPage(1); }} className="input w-auto">
            <option value="">Tous les types</option>
            <option value="mensuelle_membre">Cotisation membre</option>
            <option value="dime">Dîme</option>
            <option value="offrande">Offrande</option>
            <option value="don_special">Don spécial</option>
          </select>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-16"><Spinner /></div>
        ) : data?.results?.length === 0 ? (
          <EmptyState icon={CreditCard} title="Aucune cotisation" description="Enregistrez le premier paiement." action={{ label: 'Enregistrer un paiement', onClick: () => setShowForm(true) }} />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="table">
                <thead>
                  <tr>
                    <th>Référence</th>
                    <th>Fidèle</th>
                    <th>Type</th>
                    <th>Montant</th>
                    <th>Mode</th>
                    <th>Période</th>
                    <th>Statut</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data?.results?.map((c: any) => (
                    <tr key={c.id}>
                      <td>
                        <code className="text-xs bg-gray-100 px-2 py-0.5 rounded font-mono">{c.reference}</code>
                      </td>
                      <td className="font-medium text-gray-900">{c.fidele_nom || '-'}</td>
                      <td className="text-gray-600 text-xs">{c.type_cotisation_display || TYPE_LABELS[c.type_cotisation] || c.type_cotisation}</td>
                      <td className="font-semibold text-gray-900">{formatMontant(c.montant)}</td>
                      <td className="text-gray-500 text-xs capitalize">{c.mode_paiement?.replace('_', ' ')}</td>
                      <td className="text-gray-500 text-xs">
                        {c.periode_mois ? `${MOIS_LABELS[c.periode_mois - 1]} ${c.periode_annee}` : formatDate(c.date_paiement)}
                      </td>
                      <td>
                        <span className={cn('badge', STATUT_COTISATION_COLORS[c.statut])}>
                          {c.statut}
                        </span>
                      </td>
                      <td>
                        {c.statut === 'en_attente' && (
                          <div className="flex items-center gap-1">
                            <button
                              onClick={() => validerMutation.mutate(c.id)}
                              className="p-1.5 rounded-lg hover:bg-green-50 text-green-600 transition-colors"
                              title="Valider"
                            >
                              <CheckCircle size={16} />
                            </button>
                            <button
                              onClick={() => rejeterMutation.mutate(c.id)}
                              className="p-1.5 rounded-lg hover:bg-red-50 text-red-600 transition-colors"
                              title="Rejeter"
                            >
                              <XCircle size={16} />
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pagination currentPage={page} totalPages={totalPages} onPageChange={setPage} totalItems={data?.count} />
          </>
        )}
      </div>

      <Modal isOpen={showForm} onClose={() => setShowForm(false)} title="Enregistrer un paiement" size="md">
        <CotisationForm
          onSuccess={() => { setShowForm(false); queryClient.invalidateQueries({ queryKey: ['cotisations'] }); }}
          onCancel={() => setShowForm(false)}
        />
      </Modal>
    </div>
  );
};
