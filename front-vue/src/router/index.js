import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import NotFoundView from '../views/NotFoundView.vue'; // Componente para 404

const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView,
    meta: {
      title: "HOME",
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

export default router;
