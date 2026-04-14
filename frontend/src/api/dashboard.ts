import api from './client';

export const dashboardApi = {
  getStats: () => api.get('/dashboard/'),
  getRapportFideles: (params?: object) => api.get('/rapports/fideles/', { params }),
  getRapportFinancier: (params?: object) => api.get('/rapports/financier/', { params }),
};

export const eventsApi = {
  getEvenements: (params?: object) => api.get('/evenements/', { params }),
  getEvenement: (id: number) => api.get(`/evenements/${id}/`),
  createEvenement: (data: object) => api.post('/evenements/', data),
  updateEvenement: (id: number, data: object) => api.patch(`/evenements/${id}/`, data),
  deleteEvenement: (id: number) => api.delete(`/evenements/${id}/`),
  getEvenementsAVenir: () => api.get('/evenements/a_venir/'),
  inscrire: (id: number, fideleId: number) => api.post(`/evenements/${id}/inscrire/`, { fidele: fideleId }),
  getAnnonces: (params?: object) => api.get('/annonces/', { params }),
  createAnnonce: (data: object) => api.post('/annonces/', data),
};

export const notificationsApi = {
  getNotifications: () => api.get('/notifications/'),
  getNonLues: () => api.get('/notifications/non_lues/'),
  marquerLue: (id: number) => api.post(`/notifications/${id}/marquer_lue/`),
  marquerToutesLues: () => api.post('/notifications/marquer_toutes_lues/'),
};
