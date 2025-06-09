import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import NotFoundView from '../views/NotFoundView.vue';
import LoginView from '../views/login/LoginView.vue';
import IpressRegister from '../views/IpressRegister.vue'; // Importa el nuevo componente
import CamasStock from '../views/CamasStock.vue'; // Importa el componente de gestión de camas
import TransferenciaCama from '../views/TransferenciaCama.vue'; // Importa el componente de gestión de camas
import RegistroPacienteView from '../views/RegistroPacienteView.vue'; // Importa el componente de gestión de camas

const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView,
    meta: {
      title: "HOME",
      requiresAuth: true,
    },
  },
  {
    path: '/register-ipress',
    name: 'register-ipress',
    component: IpressRegister,
    meta: {
      title: 'Registro IPRESS',
      requiresAuth: true,
    },
  },
  {
    path: '/camas',
    name: 'camas',
    component: CamasStock,
    meta: {
      title: 'Gestión de Camas',
      requiresAuth: true,
    },
  },
    {
    path: '/transferencia',
    name: 'transferencia',
    component: TransferenciaCama,
    meta: {
      title: 'Transferencias de Camas',
      requiresAuth: true,
    },
  },
    {
    path: '/paciente',
    name: 'paciente',
    component: RegistroPacienteView,
    meta: {
      title: 'Registrar Paciente',
      requiresAuth: true,
    },
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: {
      title: 'Login',
    },
  },
  {
    path: '/:catchAll(.*)',
    name: 'not-found',
    component: NotFoundView,
    meta: {
      title: 'Página no encontrada',
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('auth_token');
  const hasIpress = localStorage.getItem('has_ipress') === 'true';
  const userIpress = localStorage.getItem('user_ipress'); // Verificar si ya tenemos IPRESS guardada

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login');
  } else if (isAuthenticated && to.name === 'login') {
    // Si ya está autenticado, redirigir según tenga IPRESS
    next(hasIpress ? '/camas' : '/register-ipress');
  } else if (isAuthenticated && !hasIpress && to.name !== 'register-ipress') {
    // Si no tiene IPRESS, solo puede ir al registro
    next('/register-ipress');
  } else if (isAuthenticated && hasIpress && to.name === 'register-ipress') {
    // Si ya tiene IPRESS pero intenta acceder al registro, redirigir a camas
    next('/camas');
  } else {
    next();
  }
});


export default router;