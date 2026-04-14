import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Plus, Calendar, MapPin, Users, Clock } from 'lucide-react';
import { eventsApi } from '../../api/dashboard';
import { Spinner } from '../../components/ui/Spinner';
import { EmptyState } from '../../components/ui/EmptyState';
import { Modal } from '../../components/ui/Modal';
import { formatDateTime } from '../../utils/format';
import { cn } from '../../utils/cn';

const TYPE_COLORS: Record<string, string> = {
  convention: 'badge-blue',
  conference: 'badge-purple',
  retraite: 'badge-green',
  culte_special: 'badge-yellow',
  formation: 'badge-blue',
  reunion: 'badge-gray',
};

const EventCard = ({ event, onClick }: { event: any; onClick: () => void }) => (
  <div onClick={onClick} className="card p-5 hover:shadow-md transition-all cursor-pointer hover:-translate-y-0.5">
    <div className="flex items-start justify-between mb-3">
      <span className={cn('badge', TYPE_COLORS[event.type_evenement] || 'badge-gray')}>
        {event.type_evenement?.replace('_', ' ')}
      </span>
      {event.est_passe && <span className="badge badge-gray">Passé</span>}
    </div>
    <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">{event.titre}</h3>
    <div className="space-y-1.5 text-sm text-gray-500">
      <div className="flex items-center gap-2">
        <Clock size={14} className="flex-shrink-0" />
        <span>{formatDateTime(event.date_debut)}</span>
      </div>
      {event.lieu && (
        <div className="flex items-center gap-2">
          <MapPin size={14} className="flex-shrink-0" />
          <span className="truncate">{event.lieu}</span>
        </div>
      )}
      <div className="flex items-center gap-2">
        <Users size={14} className="flex-shrink-0" />
        <span>{event.total_inscrits} inscrits{event.capacite_max ? ` / ${event.capacite_max}` : ''}</span>
      </div>
    </div>
  </div>
);

const EventForm = ({ onSuccess, onCancel }: { onSuccess: () => void; onCancel: () => void }) => {
  const [formData, setFormData] = useState({
    titre: '', description: '', type_evenement: 'reunion',
    date_debut: '', date_fin: '', lieu: '', capacite_max: '',
    niveau_visibilite: 'eglise', inscription_requise: false,
  });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await eventsApi.createEvenement(formData);
      onSuccess();
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="label">Titre *</label>
        <input value={formData.titre} onChange={e => setFormData({ ...formData, titre: e.target.value })} className="input" required />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="label">Type</label>
          <select value={formData.type_evenement} onChange={e => setFormData({ ...formData, type_evenement: e.target.value })} className="input">
            <option value="convention">Convention</option>
            <option value="conference">Conférence</option>
            <option value="retraite">Retraite</option>
            <option value="culte_special">Culte spécial</option>
            <option value="formation">Formation</option>
            <option value="reunion">Réunion</option>
          </select>
        </div>
        <div>
          <label className="label">Visibilité</label>
          <select value={formData.niveau_visibilite} onChange={e => setFormData({ ...formData, niveau_visibilite: e.target.value })} className="input">
            <option value="eglise">Église locale</option>
            <option value="paroisse">Paroisse</option>
            <option value="district">District</option>
            <option value="region">Région</option>
            <option value="national">National</option>
          </select>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="label">Date de début *</label>
          <input type="datetime-local" value={formData.date_debut} onChange={e => setFormData({ ...formData, date_debut: e.target.value })} className="input" required />
        </div>
        <div>
          <label className="label">Date de fin</label>
          <input type="datetime-local" value={formData.date_fin} onChange={e => setFormData({ ...formData, date_fin: e.target.value })} className="input" />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="label">Lieu</label>
          <input value={formData.lieu} onChange={e => setFormData({ ...formData, lieu: e.target.value })} className="input" />
        </div>
        <div>
          <label className="label">Capacité max</label>
          <input type="number" value={formData.capacite_max} onChange={e => setFormData({ ...formData, capacite_max: e.target.value })} className="input" min="0" />
        </div>
      </div>
      <div>
        <label className="label">Description</label>
        <textarea value={formData.description} onChange={e => setFormData({ ...formData, description: e.target.value })} className="input" rows={3} />
      </div>
      <div className="flex items-center gap-2">
        <input type="checkbox" id="inscription" checked={formData.inscription_requise} onChange={e => setFormData({ ...formData, inscription_requise: e.target.checked })} className="rounded" />
        <label htmlFor="inscription" className="text-sm text-gray-700">Inscription requise</label>
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <button type="button" onClick={onCancel} className="btn-secondary">Annuler</button>
        <button type="submit" disabled={submitting} className="btn-primary flex items-center gap-2">
          {submitting ? <><Spinner size="sm" /> Création...</> : 'Créer l\'événement'}
        </button>
      </div>
    </form>
  );
};

export const EventsPage = () => {
  const [showForm, setShowForm] = useState(false);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['evenements'],
    queryFn: () => eventsApi.getEvenements({ page_size: 50 }).then(r => r.data),
  });

  const items = data?.results || [];

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header flex items-center justify-between">
          <h2 className="font-semibold text-gray-900 flex items-center gap-2">
            <Calendar size={18} className="text-primary-600" />
            Événements ({data?.count || 0})
          </h2>
          <button onClick={() => setShowForm(true)} className="btn-primary btn-sm flex items-center gap-2">
            <Plus size={16} />
            Nouvel événement
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-16"><Spinner /></div>
      ) : items.length === 0 ? (
        <EmptyState icon={Calendar} title="Aucun événement" description="Créez votre premier événement." action={{ label: 'Créer un événement', onClick: () => setShowForm(true) }} />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {items.map((event: any) => (
            <EventCard key={event.id} event={event} onClick={() => {}} />
          ))}
        </div>
      )}

      <Modal isOpen={showForm} onClose={() => setShowForm(false)} title="Créer un événement" size="lg">
        <EventForm
          onSuccess={() => { setShowForm(false); queryClient.invalidateQueries({ queryKey: ['evenements'] }); }}
          onCancel={() => setShowForm(false)}
        />
      </Modal>
    </div>
  );
};
