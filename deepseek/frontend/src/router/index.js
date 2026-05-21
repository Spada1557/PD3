import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { noAuth: true } },
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
  { path: '/products', name: 'Products', component: () => import('../views/Products.vue') },
  { path: '/stock', name: 'Stock', component: () => import('../views/Stock.vue') },
  { path: '/purchases', name: 'Purchases', component: () => import('../views/Purchases.vue') },
  { path: '/sales', name: 'Sales', component: () => import('../views/Sales.vue') },
  { path: '/reports', name: 'Reports', component: () => import('../views/Reports.vue') },
  { path: '/categories', name: 'Categories', component: () => import('../views/Categories.vue') },
  { path: '/units', name: 'Units', component: () => import('../views/Units.vue') },
  { path: '/warehouses', name: 'Warehouses', component: () => import('../views/Warehouses.vue') },
  { path: '/suppliers', name: 'Suppliers', component: () => import('../views/Suppliers.vue') },
  { path: '/clients', name: 'Clients', component: () => import('../views/Clients.vue') },
  { path: '/users', name: 'Users', component: () => import('../views/Users.vue') },
  { path: '/settings', name: 'Settings', component: () => import('../views/Settings.vue') },
  { path: '/notifications', name: 'Notifications', component: () => import('../views/Notifications.vue') },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (!to.meta.noAuth && !auth.isLoggedIn) {
    return next('/login')
  }
  if (to.path === '/login' && auth.isLoggedIn) {
    return next('/dashboard')
  }
  next()
})

export default router
