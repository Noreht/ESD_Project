import { createRouter, createWebHistory } from 'vue-router'
import Login from '../components/Login.vue';
import App from '../App.vue';
import Dashboard from '../components/dashboard.vue';


const routes = [
        {
        path: '/',
        name: 'Login',
        component: Login,
        props: true
    },
    {
        path: '/dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { requiresAuth: true },
        props: true,
    },
]


const router = createRouter({
    history: createWebHistory(),
    routes
  })

router.beforeEach((to, from, next) => {
const isAuthenticated = localStorage.getItem('authToken')
if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login' })
} else {
    next()
}
})
  
export default router      