/**
 * API Client
 * Axios instance sa konfiguracijom za komunikaciju sa backend-om
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Ovde možemo dodati auth token ako je potreban
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server odgovorio sa error statusom
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Request poslat ali nema odgovora
      console.error('Network Error:', error.request);
    } else {
      // Greška pri kreiranju requesta
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// Made with Bob
