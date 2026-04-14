import api from './client';

export const hierarchyApi = {
  // National
  getNational: (params?: object) => api.get('/national/', { params }),
  createNational: (data: object) => api.post('/national/', data),
  updateNational: (id: number, data: object) => api.patch(`/national/${id}/`, data),
  // Régions
  getRegions: (params?: object) => api.get('/regions/', { params }),
  getRegion: (id: number) => api.get(`/regions/${id}/`),
  createRegion: (data: object) => api.post('/regions/', data),
  updateRegion: (id: number, data: object) => api.patch(`/regions/${id}/`, data),
  deleteRegion: (id: number) => api.delete(`/regions/${id}/`),
  getRegionStats: (id: number) => api.get(`/regions/${id}/statistiques/`),
  // Districts
  getDistricts: (params?: object) => api.get('/districts/', { params }),
  getDistrict: (id: number) => api.get(`/districts/${id}/`),
  createDistrict: (data: object) => api.post('/districts/', data),
  updateDistrict: (id: number, data: object) => api.patch(`/districts/${id}/`, data),
  // Paroisses
  getParoisses: (params?: object) => api.get('/paroisses/', { params }),
  getParoisse: (id: number) => api.get(`/paroisses/${id}/`),
  createParoisse: (data: object) => api.post('/paroisses/', data),
  updateParoisse: (id: number, data: object) => api.patch(`/paroisses/${id}/`, data),
  // Églises
  getEglises: (params?: object) => api.get('/eglises/', { params }),
  getEglise: (id: number) => api.get(`/eglises/${id}/`),
  createEglise: (data: object) => api.post('/eglises/', data),
  updateEglise: (id: number, data: object) => api.patch(`/eglises/${id}/`, data),
};
