import { format, formatDistance } from 'date-fns';
import { fr } from 'date-fns/locale';

export const formatDate = (date: string | Date | null, fmt = 'dd/MM/yyyy'): string => {
  if (!date) return '-';
  return format(new Date(date), fmt, { locale: fr });
};

export const formatDateTime = (date: string | Date | null): string => {
  if (!date) return '-';
  return format(new Date(date), 'dd/MM/yyyy HH:mm', { locale: fr });
};

export const formatRelative = (date: string | Date | null): string => {
  if (!date) return '-';
  return formatDistance(new Date(date), new Date(), { addSuffix: true, locale: fr });
};

export const formatMontant = (montant: number | string, devise = 'XOF'): string => {
  const num = typeof montant === 'string' ? parseFloat(montant) : montant;
  return new Intl.NumberFormat('fr-FR', {
    style: 'currency',
    currency: devise === 'XOF' ? 'XOF' : devise,
    minimumFractionDigits: 0,
  }).format(num);
};

export const STATUT_FIDELE_COLORS: Record<string, string> = {
  actif: 'badge-green',
  inactif: 'badge-gray',
  transfere: 'badge-yellow',
  decede: 'badge-red',
};

export const STATUT_COTISATION_COLORS: Record<string, string> = {
  valide: 'badge-green',
  en_attente: 'badge-yellow',
  rejete: 'badge-red',
  rembourse: 'badge-blue',
};

export const MOIS_LABELS = [
  'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
  'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
];
