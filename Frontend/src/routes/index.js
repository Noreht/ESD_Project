import { createRouter, createWebHistory } from 'vue-router'
import Login from './components/Login.vue';
import App from './components/App.vue';
import Dashboard from './components/dashboard.vue';


const routes = [
        {
        path: '/login',
        name: 'login',
        component: Login
    },
    {
        path: '/app',
        name: 'Home',
        component: App
    },
    {
        path: '/',
        name: 'Dashboard',
        component: Dashboard
    },
]


const router = createRouter({
    history: createWebHistory(),
    routes
  })

export default router      