import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '../api/auth';

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  setAuth: (user: User, access: string, refresh: string) => void;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      setAuth: (user, access, refresh) => {
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
        set({ user, accessToken: access, refreshToken: refresh, isAuthenticated: true });
      },
      logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false });
      },
      updateUser: (userData) =>
        set((state) => ({ user: state.user ? { ...state.user, ...userData } : null })),
    }),
    { name: 'church-auth' }
  )
);

// Rôles hiérarchiques
export const ROLES = {
  SUPER_ADMIN: 'super_admin',
  ADMIN_NATIONAL: 'admin_national',
  ADMIN_REGION: 'admin_region',
  SUPERVISEUR_DISTRICT: 'superviseur_district',
  CHEF_PAROISSE: 'chef_paroisse',
  PASTEUR_LOCAL: 'pasteur_local',
  FIDELE: 'fidele',
} as const;

export const ROLE_LABELS: Record<string, string> = {
  super_admin: 'Super Administrateur',
  admin_national: 'Administrateur National',
  admin_region: 'Administrateur Régional',
  superviseur_district: 'Superviseur de District',
  chef_paroisse: 'Chef de Paroisse',
  pasteur_local: 'Pasteur Local',
  fidele: 'Fidèle',
};

const ROLE_HIERARCHY = [
  'fidele', 'pasteur_local', 'chef_paroisse',
  'superviseur_district', 'admin_region', 'admin_national', 'super_admin'
];

export const hasMinRole = (userRole: string, minRole: string): boolean => {
  return ROLE_HIERARCHY.indexOf(userRole) >= ROLE_HIERARCHY.indexOf(minRole);
};
