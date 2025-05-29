<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card shadow">
          <div class="card-header bg-primary text-white">
            <h4 class="mb-0">Registro de IPRESS</h4>
          </div>
          <div class="card-body">
            <form @submit.prevent="registerIpress">
              <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
              
              <div class="mb-3">
                <label for="codigo" class="form-label">Código IPRESS</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="codigo" 
                  v-model="ipressData.codigo"
                  required
                >
              </div>
              
              <div class="mb-3">
                <label for="descripcion" class="form-label">Nombre del Establecimiento</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="descripcion" 
                  v-model="ipressData.descripcion"
                  required
                >
              </div>
              
              <div class="d-grid">
                <button type="submit" class="btn btn-primary">
                  Registrar IPRESS
                </button>
              </div>
            </form>
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

const router = useRouter()
const errorMessage = ref('')
const ipressData = ref({
  codigo: '',
  descripcion: ''
})

const registerIpress = async () => {
  try {
    const payload = {
      codigo: ipressData.value.codigo,
      descripcion: ipressData.value.descripcion
    }

    const response = await api.post('ipress/', payload)
    
    if (response.data?.id) {
      localStorage.setItem('has_ipress', 'true')
      // Guardar la IPRESS completa en localStorage
      localStorage.setItem('user_ipress', JSON.stringify(response.data))
      router.push('/camas')
    }
  } catch (error) {
    // Manejo de errores...
  }
}
</script>