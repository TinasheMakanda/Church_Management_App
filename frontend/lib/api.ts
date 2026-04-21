import axios from 'axios';
import Cookies from 'js-cookie';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://church-management-app-ae98.onrender.com/api';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Important for session cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add CSRF and Auth tokens
api.interceptors.request.use((config) => {
  // Add Auth token if we have it
  const authToken = Cookies.get('auth_token');
  if (authToken) {
    config.headers['Authorization'] = `Token ${authToken}`;
  }

  // If we're performing a mutation, we need the CSRF token
  if (config.method && ['post', 'put', 'patch', 'delete'].includes(config.method.toLowerCase())) {
    const csrfToken = Cookies.get('csrftoken');
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
  }
  return config;
});

export default api;
