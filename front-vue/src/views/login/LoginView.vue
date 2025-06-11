<template>
  <div class="container">
    <div class="d-flex justify-content-center align-items-center min-vh-100">
      <div class="login-box">
        <div class="card shadow-lg p-4" style="max-width: 600px; width: 100%;">
          <div class="card-body">

            <!-- Mostrar mensaje de error -->
            <div v-if="errorMessage" class="alert alert-danger text-center mb-4" role="alert">
              {{ errorMessage }}
            </div>

            <form @submit.prevent="handleSubmit">
              <div class="mb-3">
                <label for="username" class="form-label">Nombre de usuario</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="fas fa-user"></i>
                  </span>
                  <input
                    type="text"
                    id="username"
                    v-model="username"
                    @input="handleLowerCASE"
                    class="form-control"
                    placeholder="Usuario"
                    required
                  />
                </div>
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Contraseña</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="fas fa-lock"></i>
                  </span>
                  <input
                    type="password"
                    id="password"
                    v-model="password"
                    class="form-control"
                    placeholder="Contraseña"
                    required
                  />
                </div>
              </div>
              <div class="text-center">
                <button type="submit" class="btn btn-primary">
                  <i class="fas fa-sign-in-alt"></i> Ingresar
                </button>
              </div>
            </form>
          </div>

          <!-- Fila inferior con borde morado -->
          <div class="card-footer border-top text-center">
            <small>Gestión Administrativa V.1</small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/components/services/auth_axios'

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const router = useRouter()

const handleLowerCASE = (event) => {
  const targetField = event.target.id
  if (targetField === 'username') {
    username.value = event.target.value.toLowerCase()
  }
}

const handleSubmit = async () => {
  try {
    const response = await api.post('login/', {
      username: username.value,
      password: password.value,
    });

    const { access, refresh, has_ipress, ipress, user } = response.data; // Asegúrate que el backend envíe estos datos

    localStorage.setItem('auth_token', access);
    localStorage.setItem('refreshToken', refresh);
    localStorage.setItem('has_ipress', has_ipress);
    
    // Guardar datos del usuario
    localStorage.setItem('user', JSON.stringify({
      id: user.id,
      username: user.username,
      email: user.email,
      is_superuser: user.is_superuser,
      is_staff: user.is_staff
    }));
    
    // Guardar datos de IPRESS si existen
    if (ipress) {
      localStorage.setItem('user_ipress', JSON.stringify(ipress));
    }

    // Redirigir según si tiene IPRESS registrada
    if (has_ipress) {
      router.push('/camas');
    } else {
      router.push('/register-ipress');
    }

  } catch (error) {
    if (error.response && error.response.data && error.response.data.detail) {
      errorMessage.value = error.response.data.detail;
    } else {
      errorMessage.value = 'Error al iniciar sesión. Verifica tus credenciales.';
    }
  }
}



</script>

<style scoped>
.card-footer {
  border-bottom: 5px solid #6f42c1;
}
</style>
