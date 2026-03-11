import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      { path: '', redirect: '/dashboard' },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/pages/dashboard/DashboardOverview.vue'),
        meta: { title: 'Dashboard' }
      },
      {
        path: 'inventory',
        name: 'tool-io-list',
        component: () => import('@/pages/tool-io/OrderList.vue'),
        meta: { title: 'Registry' }
      },
      {
        path: 'inventory/create',
        name: 'tool-io-create',
        component: () => import('@/pages/tool-io/OrderCreate.vue'),
        meta: { title: 'New Request' }
      },
      {
        path: 'inventory/keeper',
        name: 'tool-io-keeper',
        component: () => import('@/pages/tool-io/KeeperProcess.vue'),
        meta: { title: 'Workbench' }
      },
      {
        path: 'inventory/:orderNo',
        name: 'tool-io-detail',
        component: () => import('@/pages/tool-io/OrderDetail.vue'),
        props: true,
        meta: { title: 'Details' }
      }
    ]
  }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
