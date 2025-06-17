import axios from 'axios';

const API_URL = 'http://127.0.0.1:8001';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para manejar errores globalmente
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Aquí puedes manejar los errores de manera global
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default api; 