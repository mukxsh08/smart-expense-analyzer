// frontend/src/api.js

import axios from 'axios';

// All API calls go to our FastAPI backend
const API = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// ─── EXPENSES ────────────────────────────────────────────────────────
export const getExpenses = (params = {}) => API.get('/expenses/', { params });
export const createExpense = (data) => API.post('/expenses/', data);
export const deleteExpense = (id) => API.delete(`/expenses/${id}`);
export const uploadCSV = (formData) =>
  API.post('/expenses/upload/csv', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

// ─── CATEGORIES ──────────────────────────────────────────────────────
export const getCategories = () => API.get('/categories/');
export const seedCategories = () => API.post('/categories/seed');

// ─── RULES ───────────────────────────────────────────────────────────
export const getRules = () => API.get('/rules/');
export const seedRules = () => API.post('/rules/seed');
export const testRule = (data) => API.post('/rules/test', data);

// ─── ANALYTICS ───────────────────────────────────────────────────────
export const getDashboard = () => API.get('/analytics/dashboard');
export const getCategorySpending = (params = {}) => API.get('/analytics/by-category', { params });
export const getMonthlyData = (params = {}) => API.get('/analytics/monthly', { params });
export const getAnomalies = () => API.get('/analytics/anomalies');

export default API;