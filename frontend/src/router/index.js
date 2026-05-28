import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/login', component: () => import('../views/LoginView.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('../views/DashboardView.vue') },
      { path: 'products', component: () => import('../views/ProductsView.vue') },
      { path: 'stock', component: () => import('../views/StockView.vue') },
      { path: 'purchases', component: () => import('../views/PurchasesView.vue') },
      { path: 'purchases/:id', component: () => import('../views/PurchaseEditView.vue') },
      { path: 'sales', component: () => import('../views/SalesView.vue') },
      { path: 'sales/:id', component: () => import('../views/SaleEditView.vue') },
      { path: 'suppliers', component: () => import('../views/SuppliersView.vue') },
      { path: 'clients', component: () => import('../views/ClientsView.vue') },
      { path: 'reports', component: () => import('../views/ReportsView.vue') },
      { path: 'users', component: () => import('../views/UsersView.vue') },
      { path: 'settings', component: () => import('../views/SettingsView.vue') },
      { path: 'references', component: () => import('../views/ReferencesView.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()
  if (!auth.token && !to.meta.public) {
    next('/login')
    return
  }
  if (auth.token && !auth.user) {
    await auth.fetchMe()
  }
  next()
})

export default router
