import api from './client';

export interface LoginPayload { email: string; password: string; }
export interface User {
  id: number; email: string; first_name: string; last_name: string; full_name: string;
  phone: string; role: string; entity_type: string; entity_id: number | null;
  is_active: boolean; date_joined: string; last_login: string | null; avatar: string | null;
}
export interface AuthResponse { access: string; refresh: string; user: User; }

export const authApi = {
  login: (data: LoginPayload) => api.post<AuthResponse>('/auth/login/', data),
  logout: (refresh: string) => api.post('/auth/logout/', { refresh }),
  me: () => api.get<User>('/auth/users/me/'),
  changePassword: (data: { old_password: string; new_password: string; new_password_confirm: string }) =>
    api.post('/auth/change-password/', data),
  updateProfile: (data: Partial<User>) => api.patch('/auth/profile/', data),
};
