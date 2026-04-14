import api from './client';

export const membersApi = {
  getFideles: (params?: object) => api.get('/fideles/', { params }),
  getFidele: (id: number) => api.get(`/fideles/${id}/`),
  createFidele: (data: FormData | object) => api.post('/fideles/', data, {
    headers: data instanceof FormData ? { 'Content-Type': 'multipart/form-data' } : {},
  }),
  updateFidele: (id: number, data: FormData | object) => api.patch(`/fideles/${id}/`, data, {
    headers: data instanceof FormData ? { 'Content-Type': 'multipart/form-data' } : {},
  }),
  deleteFidele: (id: number) => api.delete(`/fideles/${id}/`),
  getStatsFideles: () => api.get('/fideles/statistiques/'),
  getCarteMembre: (id: number) => api.get(`/fideles/${id}/carte_membre/`, { responseType: 'blob' }),
  getQRCode: (id: number) => api.get(`/fideles/${id}/qrcode/`, { responseType: 'blob' }),
  transfererFidele: (id: number, data: object) => api.post(`/fideles/${id}/transferer/`, data),
  getMinisteres: (params?: object) => api.get('/ministeres/', { params }),
  createMinistere: (data: object) => api.post('/ministeres/', data),
};
