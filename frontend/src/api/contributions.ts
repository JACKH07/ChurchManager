import api from './client';

export const contributionsApi = {
  getCotisations: (params?: object) => api.get('/cotisations/', { params }),
  getCotisation: (id: number) => api.get(`/cotisations/${id}/`),
  createCotisation: (data: object) => api.post('/cotisations/', data),
  validerCotisation: (id: number) => api.post(`/cotisations/${id}/valider/`),
  rejeterCotisation: (id: number, motif: string) => api.post(`/cotisations/${id}/rejeter/`, { motif }),
  getResume: (params?: object) => api.get('/cotisations/resume/', { params }),
  getEvolutionMensuelle: (params?: object) => api.get('/cotisations/evolution_mensuelle/', { params }),
  getImpayes: (params?: object) => api.get('/cotisations/impay%C3%A9s/', { params }),
  getRecus: (params?: object) => api.get('/recus/', { params }),
  getObjectifs: (params?: object) => api.get('/objectifs/', { params }),
  createObjectif: (data: object) => api.post('/objectifs/', data),
};
