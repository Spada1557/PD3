import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { guest: true },
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('../views/Layout.vue'),
    redirect: '/dashboard',
    meta: { auth: true },
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
      { path: 'products', name: 'Products', component: () => import('../views/Products.vue') },
      { path: 'products/:id', name: 'ProductForm', component: () => import('../views/ProductForm.vue') },
      { path: 'stock', name: 'Stock', component: () => import('../views/Stock.vue') },
      { path: 'purchases', name: 'Purchases', component: () => import('../views/Purchases.vue') },
      { path: 'purchases/:id', name: 'PurchaseForm', component: () => import('../views/PurchaseForm.vue') },
      { path: 'sales', name: 'Sales', component: () => import('../views/Sales.vue') },
      { path: 'sales/:id', name: 'SaleForm', component: () => import('../views/SaleForm.vue') },
      { path: 'clients', name: 'Clients', component: () => import('../views/Clients.vue'), meta: { roles: ['admin', 'manager'] } },
      { path: 'suppliers', name: 'Suppliers', component: () => import('../views/Suppliers.vue'), meta: { roles: ['admin', 'warehouse'] } },
      { path: 'reports', name: 'Reports', component: () => import('../views/Reports.vue') },
      { path: 'settings', name: 'Settings', component: () => import('../views/Settings.vue'), meta: { roles: ['admin'] } },
      { path: 'users', name: 'Users', component: () => import('../views/Users.vue'), meta: { roles: ['admin'] } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.guest) {
    if (auth.isAuthenticated) {
      next('/dashboard')
    } else {
      next()
    }
  } else if (to.meta.auth) {
    if (!auth.isAuthenticated) {
      next('/login')
    } else if (to.meta.roles && !to.meta.roles.includes(auth.userRole)) {
      next('/dashboard')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router