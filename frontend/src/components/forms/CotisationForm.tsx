import { useState, useEffect } from 'react';
import { useForm, useWatch } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useQuery } from '@tanstack/react-query';
import { membersApi } from '../../api/members';
import { contributionsApi } from '../../api/contributions';
import { Spinner } from '../ui/Spinner';
import { MOIS_LABELS } from '../../utils/format';
import { cn } from '../../utils/cn';

const MODES_AVEC_REFERENCE = ['wave', 'orange_money', 'mtn_momo', 'virement', 'cheque'] as const;

const schema = z
  .object({
    fidele: z.number().min(1, 'Fidèle requis'),
    type_cotisation: z.string().min(1, 'Type requis'),
    montant: z.number().positive('Montant doit être positif'),
    mode_paiement: z.string().min(1, 'Mode de paiement requis'),
    transaction_id: z.string().optional(),
    periode_mois: z.number().optional(),
    periode_annee: z.number().optional(),
    notes: z.string().optional(),
  })
  .superRefine((data, ctx) => {
    if (MODES_AVEC_REFERENCE.includes(data.mode_paiement as (typeof MODES_AVEC_REFERENCE)[number])) {
      const v = (data.transaction_id || '').trim();
      if (!v) {
        ctx.addIssue({
          code: 'custom',
          message: 'Saisissez le numéro ou la référence liée à ce mode de paiement.',
          path: ['transaction_id'],
        });
      }
    }
  });

type FormData = z.infer<typeof schema>;

interface CotisationFormProps {
  onSuccess: () => void;
  onCancel: () => void;
}

function labelReferencePaiement(mode: string): string {
  switch (mode) {
    case 'wave':
    case 'orange_money':
    case 'mtn_momo':
      return 'Numéro de téléphone du compte (Mobile Money)';
    case 'virement':
      return 'Référence ou numéro de compte / RIB';
    case 'cheque':
      return 'Numéro du chèque';
    default:
      return 'Référence de paiement';
  }
}

function aideReferencePaiement(mode: string): string {
  switch (mode) {
    case 'wave':
      return 'Indiquez le numéro Wave utilisé pour le paiement.';
    case 'orange_money':
      return 'Indiquez le numéro Orange Money utilisé pour le paiement.';
    case 'mtn_momo':
      return 'Indiquez le numéro MTN MoMo utilisé pour le paiement.';
    case 'virement':
      return 'Indiquez la référence du virement ou les derniers chiffres du compte débiteur.';
    case 'cheque':
      return 'Indiquez le numéro figurant sur le chèque.';
    default:
      return '';
  }
}

export const CotisationForm = ({ onSuccess, onCancel }: CotisationFormProps) => {
  const now = new Date();
  const [tab, setTab] = useState<'details' | 'reference'>('details');

  const { data: fidelesData } = useQuery({
    queryKey: ['fideles-list'],
    queryFn: () => membersApi.getFideles({ statut: 'actif', page_size: 500 }).then((r) => r.data),
  });

  const {
    register,
    handleSubmit,
    control,
    formState: { errors, isSubmitting },
    setValue,
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      mode_paiement: 'especes',
      type_cotisation: 'mensuelle_membre',
      periode_mois: now.getMonth() + 1,
      periode_annee: now.getFullYear(),
      transaction_id: '',
    },
  });

  const modePaiement = useWatch({ control, name: 'mode_paiement' });
  const besoinReference =
    modePaiement && MODES_AVEC_REFERENCE.includes(modePaiement as (typeof MODES_AVEC_REFERENCE)[number]);

  useEffect(() => {
    if (!besoinReference && tab === 'reference') {
      setTab('details');
    }
  }, [besoinReference, tab]);

  const onSubmit = async (data: FormData) => {
    try {
      const payload = {
        ...data,
        transaction_id: data.mode_paiement === 'especes' ? '' : (data.transaction_id || '').trim(),
      };
      await contributionsApi.createCotisation(payload);
      onSuccess();
    } catch (err: unknown) {
      console.error(err);
    }
  };

  const fideles = fidelesData?.results || [];
  const regModePaiement = register('mode_paiement');

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="flex rounded-lg border border-gray-200 p-0.5 bg-gray-50">
        <button
          type="button"
          onClick={() => setTab('details')}
          className={cn(
            'flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors',
            tab === 'details' ? 'bg-white text-primary-700 shadow-sm' : 'text-gray-600 hover:text-gray-900'
          )}
        >
          Détails de la cotisation
        </button>
        <button
          type="button"
          onClick={() => setTab('reference')}
          disabled={!besoinReference}
          className={cn(
            'flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors',
            tab === 'reference' ? 'bg-white text-primary-700 shadow-sm' : 'text-gray-600 hover:text-gray-900',
            !besoinReference && 'opacity-50 cursor-not-allowed'
          )}
        >
          Référence paiement
        </button>
      </div>

      {tab === 'details' && (
        <>
          <div>
            <label className="label">Fidèle *</label>
            <select {...register('fidele', { valueAsNumber: true })} className={`input ${errors.fidele ? 'input-error' : ''}`}>
              <option value="">-- Sélectionner un fidèle --</option>
              {fideles.map((f: { id: number; prenom: string; nom: string; code_fidele: string }) => (
                <option key={f.id} value={f.id}>
                  {f.prenom} {f.nom} ({f.code_fidele})
                </option>
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
              <input
                {...register('montant', { valueAsNumber: true })}
                type="number"
                min="0"
                className={`input ${errors.montant ? 'input-error' : ''}`}
                placeholder="5000"
              />
              {errors.montant && <p className="text-red-500 text-xs mt-1">{errors.montant.message}</p>}
            </div>
          </div>

          <div>
            <label className="label">Mode de paiement *</label>
            <select
              className="input"
              {...regModePaiement}
              onChange={(e) => {
                regModePaiement.onChange(e);
                const v = e.target.value;
                if (MODES_AVEC_REFERENCE.includes(v as (typeof MODES_AVEC_REFERENCE)[number])) {
                  setTab('reference');
                } else {
                  setValue('transaction_id', '');
                  setTab('details');
                }
              }}
            >
              <option value="especes">Espèces</option>
              <option value="wave">Wave</option>
              <option value="orange_money">Orange Money</option>
              <option value="mtn_momo">MTN MoMo</option>
              <option value="virement">Virement bancaire</option>
              <option value="cheque">Chèque</option>
            </select>
            <p className="text-xs text-gray-500 mt-1">
              {besoinReference
                ? 'Après le choix du mode, saisissez la référence dans l’onglet « Référence paiement ».'
                : 'Les espèces ne nécessitent pas de numéro de référence.'}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Mois concerné</label>
              <select {...register('periode_mois', { valueAsNumber: true })} className="input">
                {MOIS_LABELS.map((m, i) => (
                  <option key={i + 1} value={i + 1}>
                    {m}
                  </option>
                ))}
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
        </>
      )}

      {tab === 'reference' && besoinReference && (
        <div className="space-y-3">
          <p className="text-sm text-gray-600">
            Mode sélectionné : <span className="font-medium capitalize">{modePaiement?.replace('_', ' ')}</span>
          </p>
          <div>
            <label className="label">{labelReferencePaiement(modePaiement)} *</label>
            <input
              {...register('transaction_id')}
              type="text"
              className={`input ${errors.transaction_id ? 'input-error' : ''}`}
              placeholder="Ex. 07 XX XX XX XX"
              autoComplete="off"
            />
            {errors.transaction_id && (
              <p className="text-red-500 text-xs mt-1">{errors.transaction_id.message}</p>
            )}
            {aideReferencePaiement(modePaiement) && (
              <p className="text-xs text-gray-500 mt-1">{aideReferencePaiement(modePaiement)}</p>
            )}
          </div>
          <button type="button" onClick={() => setTab('details')} className="btn-ghost text-sm">
            Retour aux détails
          </button>
        </div>
      )}

      <div className="flex justify-end gap-3 pt-2">
        <button type="button" onClick={onCancel} className="btn-secondary">
          Annuler
        </button>
        <button type="submit" disabled={isSubmitting} className="btn-primary flex items-center gap-2">
          {isSubmitting ? (
            <>
              <Spinner size="sm" /> Enregistrement...
            </>
          ) : (
            'Enregistrer'
          )}
        </button>
      </div>
    </form>
  );
};
