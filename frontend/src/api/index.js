import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api

export const authApi = {
  login: (data) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
}

export const usersApi = {
  list: (params) => api.get('/users', { params }),
  get: (id) => api.get(`/users/${id}`),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  remove: (id) => api.delete(`/users/${id}`),
}

export const referencesApi = {
  categories: () => api.get('/references/categories'),
  createCategory: (data) => api.post('/references/categories', data),
  units: () => api.get('/references/units'),
  createUnit: (data) => api.post('/references/units', data),
  warehouses: () => api.get('/references/warehouses'),
  createWarehouse: (data) => api.post('/references/warehouses', data),
  suppliers: (params) => api.get('/references/suppliers', { params }),
  createSupplier: (data) => api.post('/references/suppliers', data),
  updateSupplier: (id, data) => api.put(`/references/suppliers/${id}`, data),
  removeSupplier: (id) => api.delete(`/references/suppliers/${id}`),
  clients: (params) => api.get('/references/clients', { params }),
  createClient: (data) => api.post('/references/clients', data),
  updateClient: (id, data) => api.put(`/references/clients/${id}`, data),
  removeClient: (id) => api.delete(`/references/clients/${id}`),
}

export const productsApi = {
  list: (params) => api.get('/products', { params }),
  get: (id) => api.get(`/products/${id}`),
  create: (data) => api.post('/products', data),
  update: (id, data) => api.put(`/products/${id}`, data),
  remove: (id) => api.delete(`/products/${id}`),
  uploadImage: (id, file) => {
    const form = new FormData()
    form.append('file', file)
    return api.post(`/products/${id}/upload-image`, form, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
}

export const stockApi = {
  list: (params) => api.get('/stock', { params }),
  movements: (params) => api.get('/stock/movements', { params }),
  inventory: (data) => api.post('/stock/inventory', data),
  move: (data) => api.post('/stock/move', null, { params: data }),
}

export const purchasesApi = {
  list: (params) => api.get('/purchases', { params }),
  get: (id) => api.get(`/purchases/${id}`),
  create: (data) => api.post('/purchases', data),
  update: (id, data) => api.put(`/purchases/${id}`, data),
  remove: (id) => api.delete(`/purchases/${id}`),
  post: (id) => api.post(`/purchases/${id}/post`),
  cancel: (id) => api.post(`/purchases/${id}/cancel`),
}

export const salesApi = {
  list: (params) => api.get('/sales', { params }),
  get: (id) => api.get(`/sales/${id}`),
  create: (data) => api.post('/sales', data),
  update: (id, data) => api.put(`/sales/${id}`, data),
  remove: (id) => api.delete(`/sales/${id}`),
  post: (id) => api.post(`/sales/${id}/post`),
  cancel: (id) => api.post(`/sales/${id}/cancel`),
}

export const dashboardApi = {
  get: (params) => api.get('/dashboard', { params }),
  notifications: () => api.get('/dashboard/notifications'),
}

export const reportsApi = {
  sales: (params) => api.get('/reports/sales', { params }),
  stock: (params) => api.get('/reports/stock', { params }),
  topProducts: (params) => api.get('/reports/top-products', { params }),
  purchases: (params) => api.get('/reports/purchases', { params }),
}

export const settingsApi = {
  get: () => api.get('/settings/company'),
  update: (data) => api.put('/settings/company', data),
  getDb: () => api.get('/settings/db'),
  updateDb: (data) => api.put('/settings/db', data),
}
