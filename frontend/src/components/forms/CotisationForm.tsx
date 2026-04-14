import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useQuery } from '@tanstack/react-query';
import { membersApi } from '../../api/members';
import { contributionsApi } from '../../api/contributions';
import { Spinner } from '../ui/Spinner';
import { MOIS_LABELS } from '../../utils/format';

const schema = z.object({
  fidele: z.number().min(1, 'Fidèle requis'),
  type_cotisation: z.string().min(1, 'Type requis'),
  montant: z.number().positive('Montant doit être positif'),
  mode_paiement: z.string().min(1, 'Mode de paiement requis'),
  periode_mois: z.number().optional(),
  periode_annee: z.number().optional(),
  notes: z.string().optional(),
});

type FormData = z.infer<typeof schema>;

interface CotisationFormProps { onSuccess: () => void; onCancel: () => void; }

export const CotisationForm = ({ onSuccess, onCancel }: CotisationFormProps) => {
  const now = new Date();
  const { data: fidelesData } = useQuery({
    queryKey: ['fideles-list'],
    queryFn: () => membersApi.getFideles({ statut: 'actif', page_size: 500 }).then(r => r.data),
  });

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      mode_paiement: 'especes',
      type_cotisation: 'mensuelle_membre',
      periode_mois: now.getMonth() + 1,
      periode_annee: now.getFullYear(),
    },
  });

  const onSubmit = async (data: FormData) => {
    try {
      await contributionsApi.createCotisation(data);
      onSuccess();
    } catch (err: any) {
      console.error(err.response?.data);
    }
  };

  const fideles = fidelesData?.results || [];

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="label">Fidèle *</label>
        <select {...register('fidele', { valueAsNumber: true })} className={`input ${errors.fidele ? 'input-error' : ''}`}>
          <option value="">-- Sélectionner un fidèle --</option>
          {fideles.map((f: any) => (
            <option key={f.id} value={f.id}>{f.prenom} {f.nom} ({f.code_fidele})</option>
          ))}
        </select>
        {errors.fidele && <p className="text-red-500 text-xs mt-1">{errors.fidele.message}</p>}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="label">Type de cotisation *</label>
          <select {...register('type_cotisation')} className="input">
            <option value="mensuelle_membre">Cotisation mensuelle membre</option>
            <option value="dime">Dîme</option>
            <option value="offrande">Offrande</option>
            <option value="contribution_paroisse">Contribution Paroisse</option>
            <option value="don_special">Don Spécial</option>
            <option value="projet">Projet Spécial</option>
          </select>
        </div>
        <div>
          <label className="label">Montant (XOF) *</label>
          <input {...register('montant', { valueAsNumber: true })} type="number" min="0" className={`input ${errors.montant ? 'input-error' : ''}`} placeholder="5000" />
          {errors.montant && <p className="text-red-500 text-xs mt-1">{errors.montant.message}</p>}
        </div>
      </div>

      <div>
        <label className="label">Mode de paiement *</label>
        <select {...register('mode_paiement')} className="input">
          <option value="especes">Espèces</option>
          <option value="wave">Wave</option>
          <option value="orange_money">Orange Money</option>
          <option value="mtn_momo">MTN MoMo</option>
          <option value="virement">Virement bancaire</option>
          <option value="cheque">Chèque</option>
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="label">Mois concerné</label>
          <select {...register('periode_mois', { valueAsNumber: true })} className="input">
            {MOIS_LABELS.map((m, i) => <option key={i + 1} value={i + 1}>{m}</option>)}
          </select>
        </div>
        <div>
          <label className="label">Année</label>
          <input {...register('periode_annee', { valueAsNumber: true })} type="number" className="input" min="2020" max="2030" />
        </div>
      </div>

      <div>
        <label className="label">Notes (optionnel)</label>
        <textarea {...register('notes')} className="input" rows={2} placeholder="Informations complémentaires..." />
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <button type="button" onClick={onCancel} className="btn-secondary">Annuler</button>
        <button type="submit" disabled={isSubmitting} className="btn-primary flex items-center gap-2">
          {isSubmitting ? <><Spinner size="sm" /> Enregistrement...</> : 'Enregistrer'}
        </button>
      </div>
    </form>
  );
};
