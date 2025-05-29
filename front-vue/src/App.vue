<template>
  <div id="app">
    <!-- Barra de navegación -->
    <nav v-if="showNavbar" class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
      <div class="container">
        <router-link to="/" class="navbar-brand">Gestión de Camas</router-link>
        
        <button class="navbar-toggler" type="button" @click="toggleNavbar">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div :class="['collapse navbar-collapse', { 'show': navbarOpen }]" id="navbarSupportedContent">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link to="/" class="nav-link" active-class="active">Inicio</router-link>
            </li>
            <li v-if="isAuthenticated && hasIpress" class="nav-item">
              <router-link to="/camas" class="nav-link" active-class="active">Mis Camas</router-link>
            </li>
            <li v-if="isAdmin" class="nav-item">
              <router-link to="/admin" class="nav-link" active-class="active">Admin</router-link>
            </li>
          </ul>
          
          <div class="d-flex">
            <div v-if="isAuthenticated" class="dropdown">
              <button class="btn btn-outline-light dropdown-toggle" type="button" id="userDropdown" data-bs-toggle="dropdown">
                {{ userEmail }}
              </button>
              <ul class="dropdown-menu dropdown-menu-end">
                <li><a class="dropdown-item" href="#" @click="logout">Cerrar sesión</a></li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Contenido principal -->
    <main class="container-fluid mt-3">
      <router-view />
    </main>

    <!-- Footer -->
    <footer v-if="showNavbar" class="bg-light mt-5 py-3 border-top">
      <div class="container">
        <span class="text-muted">Sistema de Gestión de Camas &copy; {{ currentYear }}</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'

const router = useRouter()
const store = useStore()

const navbarOpen = ref(false)
const currentYear = ref(new Date().getFullYear())

// Datos del usuario - DECLARACIÓN ÚNICA DE CADA VARIABLE
const isAuthenticated = computed(() => !!localStorage.getItem('auth_token'))
const isAdmin = computed(() => localStorage.getItem('is_superuser') === 'true' || localStorage.getItem('is_staff') === 'true')
const hasIpress = computed(() => {
  // Usa solo un método para verificar, elige uno de estos:
  return localStorage.getItem('has_ipress') === 'true' // Opción 1
  // return !!localStorage.getItem('user_ipress') // Opción 2
})
const userEmail = computed(() => localStorage.getItem('user_email') || 'Usuario')

// Mostrar navbar solo en rutas autenticadas
const showNavbar = computed(() => {
  return isAuthenticated.value && router.currentRoute.value.name !== 'login'
})

// Métodos (mantén igual)
const toggleNavbar = () => {
  navbarOpen.value = !navbarOpen.value
}

const logout = () => {
  localStorage.removeItem('auth_token')
  localStorage.removeItem('refreshToken')
  localStorage.removeItem('user_ipress')
  localStorage.removeItem('user_email')
  localStorage.removeItem('has_ipress') // Añade esto si usas la opción 1
  router.push('/login')
}

onMounted(() => {
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.navbar')) {
      navbarOpen.value = false
    }
  })
})
</script>

<style>
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

main {
  flex: 1;
}

.navbar {
  padding: 0.5rem 1rem;
}

.nav-link {
  padding: 0.5rem 1rem;
}

.nav-link.active {
  font-weight: bold;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 0.25rem;
}

.dropdown-menu {
  right: 0;
  left: auto;
}

footer {
  background-color: #f8f9fa;
}
</style>