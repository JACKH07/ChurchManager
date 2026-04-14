import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Plus, Edit, Building2, MapPin, type LucideIcon } from 'lucide-react';
import { hierarchyApi } from '../../api/hierarchy';
import { Spinner } from '../../components/ui/Spinner';
import { EmptyState } from '../../components/ui/EmptyState';
import { Modal } from '../../components/ui/Modal';

type EntityType = 'regions' | 'districts' | 'paroisses' | 'eglises';

interface HierarchyPageProps { type: EntityType; }

const ENTITY_CONFIG: Record<EntityType, { label: string; singulier: string; icon: LucideIcon }> = {
  regions: { label: 'Régions', singulier: 'Région', icon: MapPin },
  districts: { label: 'Districts', singulier: 'District', icon: Building2 },
  paroisses: { label: 'Paroisses', singulier: 'Paroisse', icon: Building2 },
  eglises: { label: 'Églises Locales', singulier: 'Église Locale', icon: Building2 },
};

const fetchFns: Record<EntityType, (p?: object) => Promise<any>> = {
  regions: (p) => hierarchyApi.getRegions(p).then(r => r.data),
  districts: (p) => hierarchyApi.getDistricts(p).then(r => r.data),
  paroisses: (p) => hierarchyApi.getParoisses(p).then(r => r.data),
  eglises: (p) => hierarchyApi.getEglises(p).then(r => r.data),
};

const EntityForm = ({ type, entity, onSuccess, onCancel }: any) => {
  const [formData, setFormData] = useState({
    nom: entity?.nom || '',
    code: entity?.code || '',
    description: entity?.description || '',
    region: entity?.region?.toString() || '',
    district: entity?.district?.toString() || '',
    paroisse: entity?.paroisse?.toString() || '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const { data: nationalData } = useQuery({
    queryKey: ['national-all'],
    queryFn: () => hierarchyApi.getNational({ page_size: 10 }).then(r => r.data),
    enabled: type === 'regions',
  });

  const { data: regionsData } = useQuery({
    queryKey: ['regions-all'],
    queryFn: () => hierarchyApi.getRegions({ page_size: 500 }).then(r => r.data),
    enabled: type === 'districts',
  });

  const { data: districtsData } = useQuery({
    queryKey: ['districts-all'],
    queryFn: () => hierarchyApi.getDistricts({ page_size: 500 }).then(r => r.data),
    enabled: type === 'paroisses',
  });

  const { data: paroissesData } = useQuery({
    queryKey: ['paroisses-all'],
    queryFn: () => hierarchyApi.getParoisses({ page_size: 500 }).then(r => r.data),
    enabled: type === 'eglises',
  });

  // Présélectionner le premier national automatiquement
  const nationaux = nationalData?.results || [];
  const premierNational = nationaux[0];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      const payload: any = {
        nom: formData.nom,
        code: formData.code,
        description: formData.description,
      };
      // Associer automatiquement au national disponible pour les régions
      if (type === 'regions' && premierNational) {
        payload.national = premierNational.id;
      }
      if (type === 'districts' && formData.region) payload.region = parseInt(formData.region);
      if (type === 'paroisses' && formData.district) payload.district = parseInt(formData.district);
      if (type === 'eglises' && formData.paroisse) payload.paroisse = parseInt(formData.paroisse);

      const entityType = type as EntityType;
      const updateFns: Record<EntityType, (id: number, data: object) => Promise<any>> = {
        regions: hierarchyApi.updateRegion,
        districts: hierarchyApi.updateDistrict,
        paroisses: hierarchyApi.updateParoisse,
        eglises: hierarchyApi.updateEglise,
      };
      const createFns: Record<EntityType, (data: object) => Promise<any>> = {
        regions: hierarchyApi.createRegion,
        districts: hierarchyApi.createDistrict,
        paroisses: hierarchyApi.createParoisse,
        eglises: hierarchyApi.createEglise,
      };
      if (entity) {
        await updateFns[entityType](entity.id, payload);
      } else {
        await createFns[entityType](payload);
      }
      onSuccess();
    } catch (err: any) {
      const detail = err.response?.data;
      if (typeof detail === 'object') {
        setError(Object.entries(detail).map(([k, v]) => `${k} : ${v}`).join(' | '));
      } else {
        setError('Une erreur est survenue. Vérifiez les champs.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}
      {type === 'regions' && premierNational && (
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-blue-700 text-sm flex items-center gap-2">
          <span className="font-medium">Organisation :</span> {premierNational.nom}
        </div>
      )}
      {type === 'regions' && !premierNational && nationaux.length === 0 && (
        <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-700 text-sm">
          ⚠️ Aucune organisation nationale trouvée. Contactez l'administrateur système.
        </div>
      )}
      {type === 'districts' && (
        <div>
          <label className="label">Région *</label>
          <select value={formData.region} onChange={e => setFormData({ ...formData, region: e.target.value })} className="input" required>
            <option value="">-- Sélectionner --</option>
            {regionsData?.results?.map((r: any) => <option key={r.id} value={r.id}>{r.nom}</option>)}
          </select>
        </div>
      )}
      {type === 'paroisses' && (
        <div>
          <label className="label">District *</label>
          <select value={formData.district} onChange={e => setFormData({ ...formData, district: e.target.value })} className="input" required>
            <option value="">-- Sélectionner --</option>
            {districtsData?.results?.map((d: any) => <option key={d.id} value={d.id}>{d.nom}</option>)}
          </select>
        </div>
      )}
      {type === 'eglises' && (
        <div>
          <label className="label">Paroisse *</label>
          <select value={formData.paroisse} onChange={e => setFormData({ ...formData, paroisse: e.target.value })} className="input" required>
            <option value="">-- Sélectionner --</option>
            {paroissesData?.results?.map((p: any) => <option key={p.id} value={p.id}>{p.nom}</option>)}
          </select>
        </div>
      )}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="label">Code *</label>
          <input value={formData.code} onChange={e => setFormData({ ...formData, code: e.target.value })} className="input" placeholder="AB" maxLength={3} required />
        </div>
        <div>
          <label className="label">Nom *</label>
          <input value={formData.nom} onChange={e => setFormData({ ...formData, nom: e.target.value })} className="input" placeholder="Nom de l'entité" required />
        </div>
      </div>
      <div>
        <label className="label">Description</label>
        <textarea value={formData.description} onChange={e => setFormData({ ...formData, description: e.target.value })} className="input" rows={2} />
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <button type="button" onClick={onCancel} className="btn-secondary">Annuler</button>
        <button type="submit" disabled={submitting} className="btn-primary flex items-center gap-2">
          {submitting ? <><Spinner size="sm" /> Enregistrement...</> : (entity ? 'Mettre à jour' : 'Créer')}
        </button>
      </div>
    </form>
  );
};

export const HierarchyPage = ({ type }: HierarchyPageProps) => {
  const config = ENTITY_CONFIG[type];
  const [showForm, setShowForm] = useState(false);
  const [selected, setSelected] = useState<any>(null);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: [type],
    queryFn: () => fetchFns[type]({ page_size: 100 }),
  });

  const items = data?.results || [];

  return (
    <div className="space-y-4">
      <div className="card">
        <div className="card-header flex items-center justify-between">
          <h2 className="font-semibold text-gray-900 flex items-center gap-2">
            <config.icon size={18} className="text-primary-600" />
            {config.label} ({data?.count || 0})
          </h2>
          <button onClick={() => { setSelected(null); setShowForm(true); }} className="btn-primary btn-sm flex items-center gap-2">
            <Plus size={16} />
            Nouvelle {config.singulier}
          </button>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-16"><Spinner /></div>
        ) : items.length === 0 ? (
          <EmptyState icon={config.icon} title={`Aucune ${config.singulier.toLowerCase()}`} description={`Commencez par créer votre première ${config.singulier.toLowerCase()}.`} action={{ label: `Créer`, onClick: () => setShowForm(true) }} />
        ) : (
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Nom</th>
                  {type === 'regions' && <><th>Responsable</th><th>Districts</th></>}
                  {type === 'districts' && <><th>Région</th><th>Superviseur</th><th>Paroisses</th></>}
                  {type === 'paroisses' && <><th>District</th><th>Chef</th><th>Églises</th></>}
                  {type === 'eglises' && <><th>Paroisse</th><th>Pasteur</th><th>Fidèles actifs</th></>}
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item: any) => (
                  <tr key={item.id}>
                    <td><code className="text-xs bg-gray-100 px-2 py-0.5 rounded font-mono text-primary-700">{item.code_complet || item.code}</code></td>
                    <td className="font-medium text-gray-900">{item.nom}</td>
                    {type === 'regions' && <><td className="text-gray-500 text-sm">{item.responsable_nom || '-'}</td><td>{item.total_districts || 0}</td></>}
                    {type === 'districts' && <><td className="text-gray-500 text-sm">{item.region_nom}</td><td className="text-gray-500 text-sm">{item.superviseur_nom || '-'}</td><td>{item.total_paroisses || 0}</td></>}
                    {type === 'paroisses' && <><td className="text-gray-500 text-sm">{item.district_nom}</td><td className="text-gray-500 text-sm">{item.chef_nom || '-'}</td><td>{item.total_eglises || 0}</td></>}
                    {type === 'eglises' && <><td className="text-gray-500 text-sm">{item.paroisse_nom}</td><td className="text-gray-500 text-sm">{item.pasteur_nom || '-'}</td><td className="text-green-700 font-medium">{item.total_fideles || 0}</td></>}
                    <td>
                      <button onClick={() => { setSelected(item); setShowForm(true); }} className="p-1.5 rounded-lg hover:bg-blue-50 text-blue-600 transition-colors">
                        <Edit size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <Modal isOpen={showForm} onClose={() => { setShowForm(false); setSelected(null); }} title={selected ? `Modifier ${config.singulier}` : `Nouvelle ${config.singulier}`} size="md">
        <EntityForm
          type={type}
          entity={selected}
          onSuccess={() => { setShowForm(false); setSelected(null); queryClient.invalidateQueries({ queryKey: [type] }); }}
          onCancel={() => { setShowForm(false); setSelected(null); }}
        />
      </Modal>
    </div>
  );
};
