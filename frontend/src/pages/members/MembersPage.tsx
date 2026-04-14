import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Plus, Search, Download, UserCheck } from 'lucide-react';
import { membersApi } from '../../api/members';
import { Spinner } from '../../components/ui/Spinner';
import { EmptyState } from '../../components/ui/EmptyState';
import { Pagination } from '../../components/ui/Pagination';
import { Modal } from '../../components/ui/Modal';
import { FideleForm } from '../../components/forms/FideleForm';
import { formatDate, STATUT_FIDELE_COLORS } from '../../utils/format';
import { cn } from '../../utils/cn';

const STATUT_OPTIONS = [
  { value: '', label: 'Tous les statuts' },
  { value: 'actif', label: 'Actif' },
  { value: 'inactif', label: 'Inactif' },
  { value: 'transfere', label: 'Transféré' },
  { value: 'decede', label: 'Décédé' },
];

export const MembersPage = () => {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [statut, setStatut] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [selectedFidele, setSelectedFidele] = useState<any>(null);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery<any>({
    queryKey: ['fideles', page, search, statut],
    queryFn: () => membersApi.getFideles({ page, search, statut }).then(r => r.data),
    placeholderData: (prev: any) => prev,
  });

  const { data: stats } = useQuery({
    queryKey: ['fideles-stats'],
    queryFn: () => membersApi.getStatsFideles().then(r => r.data),
  });

  const downloadCarte = async (id: number, code: string) => {
    const response = await membersApi.getCarteMembre(id);
    const url = URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
    const a = document.createElement('a');
    a.href = url;
    a.download = `carte_membre_${code}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const totalPages = data ? Math.ceil(data.count / 25) : 1;

  return (
    <div className="space-y-6">
      {/* Stats rapides */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: 'Total', value: stats.total, color: 'text-gray-900' },
            { label: 'Actifs', value: stats.actifs, color: 'text-green-700' },
            { label: 'Hommes', value: stats.hommes, color: 'text-blue-700' },
            { label: 'Femmes', value: stats.femmes, color: 'text-purple-700' },
          ].map(s => (
            <div key={s.label} className="card p-4 text-center">
              <p className={`text-2xl font-bold ${s.color}`}>{s.value?.toLocaleString('fr-FR')}</p>
              <p className="text-xs text-gray-500 mt-0.5">{s.label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Barre d'outils */}
      <div className="card">
        <div className="card-header flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <h2 className="font-semibold text-gray-900">Liste des fidèles</h2>
          <button onClick={() => { setSelectedFidele(null); setShowForm(true); }} className="btn-primary btn-sm flex items-center gap-2">
            <Plus size={16} />
            Nouveau fidèle
          </button>
        </div>
        <div className="px-6 py-3 border-b border-gray-100 flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              placeholder="Rechercher par nom, code, téléphone..."
              className="input pl-9"
            />
          </div>
          <select
            value={statut}
            onChange={(e) => { setStatut(e.target.value); setPage(1); }}
            className="input w-auto"
          >
            {STATUT_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-16"><Spinner /></div>
        ) : data?.results?.length === 0 ? (
          <EmptyState icon={UserCheck} title="Aucun fidèle trouvé" description="Commencez par enregistrer votre premier fidèle." action={{ label: 'Ajouter un fidèle', onClick: () => setShowForm(true) }} />
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="table">
                <thead>
                  <tr>
                    <th>Code</th>
                    <th>Nom complet</th>
                    <th>Genre</th>
                    <th>Téléphone</th>
                    <th>Église</th>
                    <th>Statut</th>
                    <th>Inscription</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data?.results?.map((fidele: any) => (
                    <tr key={fidele.id} className="cursor-pointer" onClick={() => setSelectedFidele(fidele)}>
                      <td>
                        <code className="text-xs bg-gray-100 px-2 py-0.5 rounded font-mono text-primary-700">
                          {fidele.code_fidele}
                        </code>
                      </td>
                      <td>
                        <div className="flex items-center gap-3">
                          {fidele.photo ? (
                            <img src={fidele.photo} alt="" className="w-8 h-8 rounded-full object-cover" />
                          ) : (
                            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-400 to-purple-500 flex items-center justify-center text-white text-xs font-semibold">
                              {fidele.prenom?.[0]}{fidele.nom?.[0]}
                            </div>
                          )}
                          <div>
                            <p className="font-medium text-gray-900">{fidele.prenom} {fidele.nom}</p>
                            {fidele.email && <p className="text-xs text-gray-400">{fidele.email}</p>}
                          </div>
                        </div>
                      </td>
                      <td className="text-gray-600">{fidele.genre === 'H' ? 'Homme' : fidele.genre === 'F' ? 'Femme' : 'Autre'}</td>
                      <td className="text-gray-600">{fidele.telephone || '-'}</td>
                      <td className="text-gray-600 text-xs">{fidele.eglise_nom || '-'}</td>
                      <td onClick={(e) => e.stopPropagation()}>
                        <span className={cn('badge', STATUT_FIDELE_COLORS[fidele.statut])}>
                          {fidele.statut}
                        </span>
                      </td>
                      <td className="text-gray-500 text-xs">{formatDate(fidele.date_inscription)}</td>
                      <td onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => downloadCarte(fidele.id, fidele.code_fidele)}
                            className="p-1.5 rounded-lg hover:bg-blue-50 text-blue-600 transition-colors"
                            title="Télécharger la carte de membre"
                          >
                            <Download size={14} />
                          </button>
                        </div>
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

      {/* Modal formulaire fidèle */}
      <Modal
        isOpen={showForm}
        onClose={() => { setShowForm(false); setSelectedFidele(null); }}
        title={selectedFidele ? 'Modifier le fidèle' : 'Nouveau fidèle'}
        size="lg"
      >
        <FideleForm
          fidele={selectedFidele}
          onSuccess={() => {
            setShowForm(false);
            queryClient.invalidateQueries({ queryKey: ['fideles'] });
            queryClient.invalidateQueries({ queryKey: ['fideles-stats'] });
          }}
          onCancel={() => setShowForm(false)}
        />
      </Modal>
    </div>
  );
};
