import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useQuery } from '@tanstack/react-query';
import { membersApi } from '../../api/members';
import { hierarchyApi } from '../../api/hierarchy';
import { Spinner } from '../ui/Spinner';

const schema = z.object({
  nom: z.string().min(1, 'Nom requis'),
  prenom: z.string().min(1, 'Prénom requis'),
  genre: z.enum(['H', 'F', 'A']),
  date_naissance: z.string().optional(),
  telephone: z.string().optional(),
  email: z.string().email('Email invalide').optional().or(z.literal('')),
  adresse: z.string().optional(),
  profession: z.string().optional(),
  situation_familiale: z.enum(['celibataire', 'marie', 'divorce', 'veuf']).optional(),
  eglise: z.number().min(1, 'Église requise'),
  statut: z.enum(['actif', 'inactif', 'transfere', 'decede']).optional(),
  date_inscription: z.string().optional(),
});

type FormData = z.infer<typeof schema>;

interface FideleFormProps {
  fidele?: any;
  onSuccess: () => void;
  onCancel: () => void;
}

export const FideleForm = ({ fidele, onSuccess, onCancel }: FideleFormProps) => {
  const { data: eglisesData } = useQuery({
    queryKey: ['eglises-all'],
    queryFn: () => hierarchyApi.getEglises({ page_size: 500 }).then(r => r.data),
  });

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: fidele ? {
      ...fidele,
      eglise: fidele.eglise,
    } : {
      genre: 'H',
      situation_familiale: 'celibataire',
      statut: 'actif',
      date_inscription: new Date().toISOString().split('T')[0],
    },
  });

  const onSubmit = async (data: FormData) => {
    try {
      if (fidele) {
        await membersApi.updateFidele(fidele.id, data);
      } else {
        await membersApi.createFidele(data);
      }
      onSuccess();
    } catch (err: any) {
      console.error(err.response?.data);
    }
  };

  const eglises = eglisesData?.results || [];

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="label">Prénom *</label>
          <input {...register('prenom')} className={`input ${errors.prenom ? 'input-error' : ''}`} placeholder="Jean" />
          {errors.prenom && <p className="text-red-500 text-xs mt-1">{errors.prenom.message}</p>}
        </div>
        <div>
          <label className="label">Nom *</label>
          <input {...register('nom')} className={`input ${errors.nom ? 'input-error' : ''}`} placeholder="DUPONT" />
          {errors.nom && <p className="text-red-500 text-xs mt-1">{errors.nom.message}</p>}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="label">Genre *</label>
          <select {...register('genre')} className="input">
            <option value="H">Homme</option>
            <option value="F">Femme</option>
            <option value="A">Autre</option>
          </select>
        </div>
        <div>
          <label className="label">Date de naissance</label>
          <input {...register('date_naissance')} type="date" className="input" />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="label">Téléphone</label>
          <input {...register('telephone')} className="input" placeholder="+225 07 00 00 00" />
        </div>
        <div>
          <label className="label">Email</label>
          <input {...register('email')} type="email" className={`input ${errors.email ? 'input-error' : ''}`} placeholder="jean@email.com" />
          {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="label">Situation familiale</label>
          <select {...register('situation_familiale')} className="input">
            <option value="celibataire">Célibataire</option>
            <option value="marie">Marié(e)</option>
            <option value="divorce">Divorcé(e)</option>
            <option value="veuf">Veuf/Veuve</option>
          </select>
        </div>
        <div>
          <label className="label">Profession</label>
          <input {...register('profession')} className="input" placeholder="Enseignant, Commerçant..." />
        </div>
      </div>

      <div>
        <label className="label">Église locale *</label>
        <select {...register('eglise', { valueAsNumber: true })} className={`input ${errors.eglise ? 'input-error' : ''}`}>
          <option value="">-- Sélectionner une église --</option>
          {eglises.map((e: any) => (
            <option key={e.id} value={e.id}>{e.nom} ({e.code_complet})</option>
          ))}
        </select>
        {errors.eglise && <p className="text-red-500 text-xs mt-1">{errors.eglise.message}</p>}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="label">Date d'inscription</label>
          <input {...register('date_inscription')} type="date" className="input" />
        </div>
        <div>
          <label className="label">Statut</label>
          <select {...register('statut')} className="input">
            <option value="actif">Actif</option>
            <option value="inactif">Inactif</option>
            <option value="transfere">Transféré</option>
            <option value="decede">Décédé</option>
          </select>
        </div>
      </div>

      <div>
        <label className="label">Adresse</label>
        <textarea {...register('adresse')} className="input" rows={2} placeholder="Adresse complète..." />
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <button type="button" onClick={onCancel} className="btn-secondary">Annuler</button>
        <button type="submit" disabled={isSubmitting} className="btn-primary flex items-center gap-2">
          {isSubmitting ? <><Spinner size="sm" /> Enregistrement...</> : (fidele ? 'Mettre à jour' : 'Enregistrer')}
        </button>
      </div>
    </form>
  );
};
