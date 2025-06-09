<template>
  <div class="container">
    <h2 class="my-4">Registrar Paciente en Cama</h2>
    
    <!-- Paso 1: Seleccionar paciente -->
    <div class="card mb-4" v-if="step === 1">
      <div class="card-header">
        <h3>1. Seleccionar Paciente</h3>
      </div>
      <div class="card-body">
        <div class="form-group">
          <input 
            v-model="searchPaciente" 
            @input="buscarPacientes" 
            placeholder="Buscar paciente..." 
            class="form-control"
          />
        </div>
        
        <div v-if="buscandoPacientes" class="text-center my-2">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Cargando...</span>
          </div>
        </div>
        
        <ul class="list-group" v-if="pacientesEncontrados.length > 0">
          <li 
            v-for="paciente in pacientesEncontrados" 
            :key="paciente.id" 
            @click="seleccionarPaciente(paciente)"
            class="list-group-item list-group-item-action"
          >
            {{ paciente.apellidos }}, {{ paciente.nombres }}
          </li>
        </ul>
        
        <div v-if="mostrarNuevoPaciente" class="mt-3">
          <h4>Registrar Nuevo Paciente</h4>
          <div class="form-group">
            <input v-model="nuevoPaciente.documento_identidad" placeholder="Documento" class="form-control mb-2">
            <input v-model="nuevoPaciente.nombres" placeholder="Nombres" class="form-control mb-2">
            <input v-model="nuevoPaciente.apellidos" placeholder="Apellidos" class="form-control mb-2">
            <input v-model="nuevoPaciente.fecha_nacimiento" type="date" class="form-control mb-2">
            <select v-model="nuevoPaciente.genero" class="form-control mb-2">
              <option value="M">Masculino</option>
              <option value="F">Femenino</option>
            </select>
            <button @click="registrarNuevoPaciente" class="btn btn-primary">Guardar</button>
            <button @click="mostrarNuevoPaciente = false" class="btn btn-secondary ml-2">Cancelar</button>
          </div>
        </div>
        
        <button 
          @click="mostrarNuevoPaciente = true" 
          class="btn btn-outline-primary mt-3"
          v-if="!mostrarNuevoPaciente"
        >
          Registrar Nuevo Paciente
        </button>
      </div>
    </div>
    
    <!-- Paso 2: Seleccionar cama disponible -->
    <div class="card mb-4" v-if="step === 2">
      <div class="card-header">
        <h3>2. Seleccionar Cama Disponible</h3>
      </div>
      <div class="card-body">
        <div class="row mb-3">
          <div class="col-md-4">
            <select v-model="filtroServicio" @change="filtrarCamas" class="form-control">
              <option value="">Todos los servicios</option>
              <option v-for="servicio in servicios" :key="servicio.id" :value="servicio.id">
                {{ servicio.nombre }}
              </option>
            </select>
          </div>
          <div class="col-md-4">
            <select v-model="filtroUPS" @change="filtrarCamas" class="form-control">
              <option value="">Todas las UPS</option>
              <option v-for="ups in upsList" :key="ups.id" :value="ups.id">
                {{ ups.nombre }}
              </option>
            </select>
          </div>
          <div class="col-md-4">
            <input 
              v-model="filtroBusqueda" 
              @input="filtrarCamas" 
              placeholder="Buscar cama..." 
              class="form-control"
            />
          </div>
        </div>
        
        <div v-if="camasFiltradas.length === 0" class="alert alert-info">
          No se encontraron camas disponibles con los filtros seleccionados
        </div>
        
        <ul class="list-group" v-else>
          <li 
            v-for="cama in camasFiltradas" 
            :key="cama.id" 
            @click="seleccionarCama(cama)"
            class="list-group-item list-group-item-action"
          >
            <strong>{{ cama.codcama }}</strong> - 
            {{ cama.servicio?.nombre }} - 
            {{ cama.ups?.nombre }}
          </li>
        </ul>
        
        <button @click="step = 1" class="btn btn-secondary mt-3">Volver</button>
      </div>
    </div>
    
    <!-- Paso 3: Confirmar registro -->
    <div class="card mb-4" v-if="step === 3">
      <div class="card-header">
        <h3>3. Confirmar Registro</h3>
      </div>
      <div class="card-body">
        <div class="mb-3">
          <p>Paciente seleccionado: <strong>{{ pacienteSeleccionado.apellidos }}, {{ pacienteSeleccionado.nombres }}</strong></p>
          <p>Cama seleccionada: <strong>{{ camaSeleccionada.codcama }}</strong> ({{ camaSeleccionada.servicio.nombre }})</p>
        </div>
        
        <div class="form-group">
          <label>Motivo de ingreso:</label>
          <textarea 
            v-model="motivoIngreso" 
            placeholder="Motivo de ingreso" 
            class="form-control"
            rows="3"
          ></textarea>
        </div>
        
        <div class="d-flex justify-content-between mt-4">
          <button @click="step = 2" class="btn btn-secondary">Volver</button>
          <button @click="registrarOcupacion" class="btn btn-primary">Registrar Ocupación</button>
        </div>
      </div>
    </div>
    
    <!-- Modal de confirmación -->
    <div class="modal-overlay" v-if="showModal">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Registro Exitoso</h5>
          <button type="button" class="close" @click="closeModal">
            <span>&times;</span>
          </button>
        </div>
        <div class="modal-body">
          <p>El paciente <strong>{{ pacienteSeleccionado.apellidos }}, {{ pacienteSeleccionado.nombres }}</strong> ha sido registrado exitosamente en la cama <strong>{{ camaSeleccionada.codcama }}</strong>.</p>
          <p>Estado de la cama actualizado a: <span class="badge bg-danger">Ocupada</span></p>
        </div>
        <div class="modal-footer">
          <button @click="resetForm" class="btn btn-primary">Registrar otro paciente</button>
          <button @click="irAHistorial" class="btn btn-success">Ver historial de ocupación</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-sugar.css'

const $toast = useToast()
const router = useRouter()

// Estado reactivo
const step = ref(1)
const searchPaciente = ref('')
const pacientesEncontrados = ref([])
const buscandoPacientes = ref(false)
const mostrarNuevoPaciente = ref(false)
const pacienteSeleccionado = ref(null)
const filtroServicio = ref('')
const filtroUPS = ref('')
const filtroBusqueda = ref('')
const servicios = ref([])
const upsList = ref([])
const camasDisponibles = ref([])
const camasFiltradas = ref([])
const camaSeleccionada = ref(null)
const motivoIngreso = ref('')
const showModal = ref(false)

const nuevoPaciente = ref({
  documento_identidad: '',
  nombres: '',
  apellidos: '',
  fecha_nacimiento: '',
  genero: 'M'
})

// Funciones
const buscarPacientes = async () => {
  if (searchPaciente.value.length < 3) {
    pacientesEncontrados.value = []
    return
  }
  
  buscandoPacientes.value = true
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/pacientes/', {
      params: { search: searchPaciente.value }
    })
    pacientesEncontrados.value = response.data
  } catch (error) {
    console.error('Error al buscar pacientes:', error)
    $toast.error('Error al buscar pacientes')
    pacientesEncontrados.value = []
  } finally {
    buscandoPacientes.value = false
  }
}

const seleccionarPaciente = (paciente) => {
  pacienteSeleccionado.value = paciente
  step.value = 2
}

const registrarNuevoPaciente = async () => {
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/pacientes/', nuevoPaciente.value)
    pacienteSeleccionado.value = response.data
    mostrarNuevoPaciente.value = false
    searchPaciente.value = ''
    pacientesEncontrados.value = []
    $toast.success('Paciente registrado correctamente')
    step.value = 2
  } catch (error) {
    console.error('Error al registrar paciente:', error)
    $toast.error('Error al registrar paciente')
  }
}

const cargarServicios = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/servicios/')
    servicios.value = response.data
  } catch (error) {
    console.error('Error al cargar servicios:', error)
    $toast.error('Error al cargar servicios')
  }
}

const cargarUPS = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/ups/')
    upsList.value = response.data
  } catch (error) {
    console.error('Error al cargar UPS:', error)
    $toast.error('Error al cargar UPS')
  }
}

const cargarCamasDisponibles = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/camas/disponibles/')
    camasDisponibles.value = response.data
    camasFiltradas.value = response.data
  } catch (error) {
    console.error('Error al cargar camas disponibles:', error)
    $toast.error('Error al cargar camas disponibles')
  }
}

const filtrarCamas = () => {
  camasFiltradas.value = camasDisponibles.value.filter(cama => {
    // Filtrar por servicio si está seleccionado
    if (filtroServicio.value && cama.servicio?.id.toString() !== filtroServicio.value.toString()) {
      return false
    }
    
    // Filtrar por UPS si está seleccionado
    if (filtroUPS.value && cama.ups?.id.toString() !== filtroUPS.value.toString()) {
      return false
    }
    
    // Filtrar por búsqueda si hay texto
    if (filtroBusqueda.value) {
      const searchTerm = filtroBusqueda.value.toLowerCase()
      const matchesCodigo = cama.codcama?.toLowerCase().includes(searchTerm)
      const matchesServicio = cama.servicio?.nombre.toLowerCase().includes(searchTerm)
      const matchesUPS = cama.ups?.nombre.toLowerCase().includes(searchTerm)
      
      if (!matchesCodigo && !matchesServicio && !matchesUPS) {
        return false
      }
    }
    
    return true
  })
}

const seleccionarCama = (cama) => {
  camaSeleccionada.value = cama
  step.value = 3
}

const registrarOcupacion = async () => {
  if (!motivoIngreso.value) {
    $toast.warning('Por favor ingrese el motivo de ingreso')
    return
  }
  
  try {
    const ocupacionData = {
      cama: camaSeleccionada.value.id,
      paciente: pacienteSeleccionado.value.id,
      motivo_ingreso: motivoIngreso.value,
      fecha_ingreso: new Date().toISOString()
    }
    
    await axios.post('http://127.0.0.1:8000/api/ocupaciones/', ocupacionData)
    
    // Actualizar estado de la cama
    await axios.patch(`http://127.0.0.1:8000/api/camas/${camaSeleccionada.value.id}/`, {
      estado: 'O'
    })
    
    showModal.value = true
    $toast.success('Ocupación registrada correctamente')
    
  } catch (error) {
    console.error('Error al registrar ocupación:', error)
    $toast.error('Error al registrar ocupación de cama')
  }
}

const resetForm = () => {
  step.value = 1
  searchPaciente.value = ''
  pacientesEncontrados.value = []
  pacienteSeleccionado.value = null
  camaSeleccionada.value = null
  motivoIngreso.value = ''
  filtroServicio.value = ''
  filtroUPS.value = ''
  filtroBusqueda.value = ''
  nuevoPaciente.value = {
    documento_identidad: '',
    nombres: '',
    apellidos: '',
    fecha_nacimiento: '',
    genero: 'M'
  }
  mostrarNuevoPaciente.value = false
  cargarCamasDisponibles()
  showModal.value = false
}

const closeModal = () => {
  showModal.value = false
}

const irAHistorial = () => {
  router.push('/ocupaciones')
}

// Carga inicial
onMounted(() => {
  cargarServicios()
  cargarUPS()
  cargarCamasDisponibles()
})
</script>

<style scoped>
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.card {
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.card-header {
  background-color: #f8f9fa;
  padding: 15px;
  border-bottom: 1px solid #ddd;
}

.card-body {
  padding: 20px;
}

.list-group-item {
  cursor: pointer;
  transition: background-color 0.2s;
}

.list-group-item:hover {
  background-color: #f8f9fa;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #ddd;
  padding-bottom: 15px;
  margin-bottom: 15px;
}

.modal-footer {
  display: flex;
  justify-content: space-between;
  border-top: 1px solid #ddd;
  padding-top: 15px;
  margin-top: 15px;
}

.close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.badge {
  font-size: 0.9em;
  padding: 5px 8px;
  border-radius: 4px;
}

.spinner-border {
  width: 2rem;
  height: 2rem;
}

.form-control {
  margin-bottom: 10px;
}

.btn {
  margin-right: 5px;
}
</style>