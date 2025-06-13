<template>
  <div class="container-fluid mt-4">
    <div class="row">
      <div class="col-md-12">
        <div class="card shadow-lg border-0">
          <div class="card-header bg-gradient-primary text-white">
            <div class="d-flex align-items-center">
              <i class="fas fa-procedures fa-2x me-3"></i>
              <div>
                <h4 class="mb-0">Distribución de Camas por UPS</h4>
                <small class="opacity-75">{{ ipressName || 'Cargando establecimiento...' }}</small>
              </div>
            </div>
          </div>

          <div class="card-body">
            <!-- Vista de Camas por UPS -->
            <div v-if="camas.length > 0" class="ups-container">
              <div v-for="ups in groupedCamas" :key="ups.id" class="ups-section mb-5">
                <div class="ups-header d-flex align-items-center mb-4">
                  <div class="ups-icon me-3">
                    <i class="fas fa-hospital fa-2x text-primary"></i>
                  </div>
                  <div>
                    <h4 class="mb-0">{{ ups.nombre }}</h4>
                    <small class="text-muted">
                      {{ ups.totalDisponibles }} camas disponibles de {{ ups.totalCamas }}
                    </small>
                  </div>
                </div>

                <div class="servicios-container">
                  <div v-for="servicio in ups.servicios" :key="servicio.id" class="servicio-section mb-4">
                    <h5 class="servicio-title mb-3">
                      <i class="fas fa-clinic-medical me-2"></i> {{ servicio.nombre }}
                      <span class="badge bg-secondary ms-2">{{ servicio.camas.length }}</span>
                    </h5>

                    <div class="camas-grid">
                      <div v-for="cama in servicio.camas" :key="cama.id" class="cama-item">
                       <div class="cama-card" :class="{
  'available': cama.estado?.descripcion?.toLowerCase() === 'disponible',
  'occupied': cama.estado?.descripcion?.toLowerCase() !== 'disponible'
}" @click="showCamaDetails(cama)">
  <div class="cama-icon">
    <i class="fas fa-bed"></i>
  </div>
  <div class="cama-info">
    <div class="cama-codigo">{{ cama.codcama }}</div>
    <div class="cama-tipo">{{ cama.tipocama?.descripcion || 'No especificado' }}</div>
    <div v-if="cama.estado?.descripcion?.toLowerCase() === 'disponible'" class="cama-status available">
      Disponible
    </div>
    <div v-else class="cama-status occupied">
      {{ cama.estado?.descripcion || 'Ocupada' }}
    </div>
    <div v-if="cama.ingreso" class="cama-paciente">
      <small>{{ cama.ingreso.paciente?.nombres }} {{ cama.ingreso.paciente?.apellidos }}</small>
    </div>
  </div>
</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="text-center py-5">
              <i class="fas fa-bed fa-4x text-muted mb-3"></i>
              <h5 class="text-muted">No hay camas registradas en este establecimiento</h5>
              <button class="btn btn-primary mt-3" @click="fetchCamas">
                <i class="fas fa-sync-alt me-2"></i> Intentar nuevamente
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de Detalles de Cama -->
    <div class="modal fade" id="camaModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header" :class="{
            'bg-success': selectedCama?.estado?.descripcion === 'Disponible',
            'bg-danger': selectedCama?.estado?.descripcion !== 'Disponible'
          }">
            <h5 class="modal-title text-white">
              <i class="fas fa-bed me-2"></i> Cama {{ selectedCama?.codcama }}
              <span class="badge bg-light text-dark ms-2">{{ selectedCama?.estado?.descripcion || 'Desconocido' }}</span>
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedCama">
              <div class="row">
                <!-- Información de la cama -->
                <div class="col-md-6">
                  <div class="card mb-4">
                    <div class="card-header bg-light">
                      <h6 class="mb-0"><i class="fas fa-info-circle me-2"></i>Información de la Cama</h6>
                    </div>
                    <div class="card-body">
                      <div class="mb-3">
                        <label class="form-label fw-bold">UPS:</label>
                        <p class="form-control-plaintext">{{ selectedCama.ups?.nombre || 'No asignada' }}</p>
                      </div>
                      <div class="mb-3">
                        <label class="form-label fw-bold">Servicio:</label>
                        <p class="form-control-plaintext">{{ selectedCama.servicio?.nombre || 'No asignado' }}</p>
                      </div>
                      <div class="mb-3">
                        <label class="form-label fw-bold">Tipo de Cama:</label>
                        <p class="form-control-plaintext">{{ selectedCama.tipocama?.descripcion || 'No especificado' }}</p>
                      </div>
                      <div class="mb-3">
                        <label class="form-label fw-bold">Estado:</label>
                        <p class="form-control-plaintext">
                          <span :class="{
                            'badge bg-success': selectedCama.estado?.descripcion === 'Disponible',
                            'badge bg-danger': selectedCama.estado?.descripcion !== 'Disponible'
                          }">
                            {{ selectedCama.estado?.descripcion || 'Desconocido' }}
                          </span>
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Información del paciente (si está ocupada) -->
                <div class="col-md-6" v-if="selectedCama?.ingreso?.paciente">
                  <div class="card">
                    <div class="card-header bg-light">
                      <h6 class="mb-0"><i class="fas fa-user-injured me-2"></i>Paciente Ocupante</h6>
                    </div>
                    <div class="card-body">
                      <div class="d-flex align-items-start mb-4">
                        <div class="avatar me-3">
                          <i class="fas fa-user-circle fa-3x text-primary"></i>
                        </div>
                        <div>
                          <h5>{{ selectedCama.ingreso.paciente.nombres }} {{ selectedCama.ingreso.paciente.apellidos }}</h5>
                          <p class="text-muted mb-1">
                            <i class="fas fa-id-card me-1"></i> DNI: {{ selectedCama.ingreso.paciente.documento_identidad }}
                          </p>
                          <p class="text-muted mb-1">
                            <i class="fas fa-venus-mars me-1"></i>
                            Género: {{ formatGender(selectedCama.ingreso.paciente.genero) }}
                          </p>
                          <p class="text-muted mb-1">
                            <i class="fas fa-birthday-cake me-1"></i>
                            Edad: {{ calculateAge(selectedCama.ingreso.paciente.fecha_nacimiento) }}
                          </p>
                          <p class="text-muted mb-1" v-if="selectedCama.ingreso.paciente.telefono">
                            <i class="fas fa-phone me-1"></i>
                            Teléfono: {{ selectedCama.ingreso.paciente.telefono }}
                          </p>
                          <p class="text-muted mb-1" v-if="selectedCama.ingreso.paciente.direccion">
                            <i class="fas fa-map-marker-alt me-1"></i>
                            Dirección: {{ selectedCama.ingreso.paciente.direccion }}
                          </p>
                        </div>
                      </div>

                      <div class="row">
                        <div class="col-md-6">
                          <div class="mb-3">
                            <label class="form-label fw-bold">Fecha de Ingreso:</label>
                            <p class="form-control-plaintext">{{ formatDateTime(selectedCama.ingreso.fecha_ingreso) }}</p>
                          </div>
                          <div class="mb-3">
                            <label class="form-label fw-bold">Tiempo de Ocupación:</label>
                            <p class="form-control-plaintext">{{ calculateTimeSince(selectedCama.ingreso.fecha_ingreso) }}</p>
                          </div>
                        </div>
                        <div class="col-md-6">
                          <div class="mb-3">
                            <label class="form-label fw-bold">Médico Tratante:</label>
                            <p class="form-control-plaintext">{{ selectedCama.ingreso.medico_tratante || 'No especificado' }}</p>
                          </div>
                        </div>
                      </div>

                      <div class="mb-3">
                        <label class="form-label fw-bold">Diagnóstico:</label>
                        <p class="form-control-plaintext">{{ selectedCama.ingreso.diagnostico || 'No especificado' }}</p>
                      </div>

                      <div class="mb-3" v-if="selectedCama.ingreso.observaciones">
                        <label class="form-label fw-bold">Observaciones:</label>
                        <p class="form-control-plaintext">{{ selectedCama.ingreso.observaciones }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              <i class="fas fa-times me-1"></i> Cerrar
            </button>
            <button v-if="selectedCama?.estado?.descripcion !== 'Disponible' && selectedCama?.ingreso?.paciente"
              type="button" class="btn btn-primary" @click="iniciarTransferencia">
              <i class="fas fa-exchange-alt me-1"></i> Transferir Paciente
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal para Transferencia -->
    <div class="modal fade" id="transferModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">
              <i class="fas fa-exchange-alt me-2"></i> Transferir Paciente
            </h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedCama?.ingreso?.paciente">
              <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                Transferir a <strong>{{ selectedCama.ingreso.paciente.nombres }} {{ selectedCama.ingreso.paciente.apellidos }}</strong>
                (DNI: {{ selectedCama.ingreso.paciente.documento_identidad }}) a una nueva cama
              </div>

              <div class="mb-4">
                <label class="form-label fw-bold">Filtrar por:</label>
                <div class="d-flex gap-3">
                  <select v-model="filtroUps" class="form-select">
                    <option value="">Todas las UPS</option>
                    <option v-for="ups in upss" :value="ups.id">{{ ups.nombre }}</option>
                  </select>
                  <select v-model="filtroServicio" class="form-select">
                    <option value="">Todos los Servicios</option>
                    <option v-for="servicio in servicios" :value="servicio.id">{{ servicio.nombre }}</option>
                  </select>
                </div>
              </div>

              <div class="camas-disponibles">
                <h6 class="mb-3">Camas Disponibles</h6>

                <div v-if="camasDisponibles.length === 0" class="alert alert-warning">
                  No hay camas disponibles con los filtros seleccionados
                </div>

                <div class="row">
                  <div v-for="cama in camasDisponiblesFiltradas" :key="cama.id" class="col-md-4 mb-3"
                    @click="seleccionarCama(cama)">
                    <div class="card h-100" :class="{ 'border-primary': camaSeleccionada?.id === cama.id }">
                      <div class="card-body text-center">
                        <h5>{{ cama.codcama }}</h5>
                        <div class="text-muted">{{ cama.ups?.nombre }}</div>
                        <div class="text-muted">{{ cama.servicio?.nombre }}</div>
                        <div class="text-muted">{{ cama.tipocama?.descripcion }}</div>
                        <div class="badge bg-success mt-2">Disponible</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              <i class="fas fa-times me-1"></i> Cancelar
            </button>
            <button type="button" class="btn btn-primary" :disabled="!camaSeleccionada" @click="confirmarTransferencia">
              <i class="fas fa-check me-1"></i> Confirmar Transferencia
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { api } from '@/components/services/auth_axios'
import { useToast } from 'vue-toast-notification'
import { Modal } from 'bootstrap'
import 'vue-toast-notification/dist/theme-sugar.css'

const toast = useToast()

// Datos principales
const ipressName = ref('')
const camas = ref([])
const selectedCama = ref(null)
const camaModal = ref(null)
const transferModal = ref(null)

// Datos para transferencia
const camasDisponibles = ref([])
const camaSeleccionada = ref(null)
const filtroUps = ref('')
const filtroServicio = ref('')
const upss = ref([])
const servicios = ref([])

// Computed
const groupedCamas = computed(() => {
  const grouped = {}

  camas.value.forEach(cama => {
    // Verificar que la cama tenga UPS y Servicio
    if (!cama.ups || !cama.servicio) return
    
    if (!grouped[cama.ups.id]) {
      grouped[cama.ups.id] = {
        id: cama.ups.id,
        nombre: cama.ups.nombre,
        servicios: {},
        totalCamas: 0,
        totalDisponibles: 0
      }
    }

    if (!grouped[cama.ups.id].servicios[cama.servicio.id]) {
      grouped[cama.ups.id].servicios[cama.servicio.id] = {
        id: cama.servicio.id,
        nombre: cama.servicio.nombre,
        camas: []
      }
    }

    grouped[cama.ups.id].servicios[cama.servicio.id].camas.push(cama)
    grouped[cama.ups.id].totalCamas++
    if (cama.estado?.descripcion === 'Disponible') {
      grouped[cama.ups.id].totalDisponibles++
    }
  })

  for (const upsId in grouped) {
    grouped[upsId].servicios = Object.values(grouped[upsId].servicios)
  }

  return Object.values(grouped)
})

// Camas disponibles filtradas
const camasDisponiblesFiltradas = computed(() => {
  return camasDisponibles.value.filter(cama => {
    const cumpleUps = !filtroUps.value || (cama.ups && cama.ups.id == filtroUps.value)
    const cumpleServicio = !filtroServicio.value || (cama.servicio && cama.servicio.id == filtroServicio.value)
    return cumpleUps && cumpleServicio
  })
})

// Métodos
function formatDateTime(dateTimeString) {
  if (!dateTimeString) return 'No disponible'
  const date = new Date(dateTimeString)
  return date.toLocaleString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function calculateAge(birthDate) {
  if (!birthDate) return 'No disponible'
  const today = new Date()
  const birthDateObj = new Date(birthDate)
  let age = today.getFullYear() - birthDateObj.getFullYear()
  const monthDiff = today.getMonth() - birthDateObj.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDateObj.getDate())) {
    age--
  }
  return `${age} años`
}

function formatGender(genderCode) {
  const genders = {
    'M': 'Masculino',
    'F': 'Femenino',
    'O': 'Otro'
  }
  return genders[genderCode] || 'No especificado'
}

function calculateTimeSince(dateTimeString) {
  if (!dateTimeString) return 'No disponible'
  const now = new Date()
  const then = new Date(dateTimeString)
  const diff = now - then

  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))

  let result = ''
  if (days > 0) result += `${days} día${days > 1 ? 's' : ''} `
  if (hours > 0) result += `${hours} hora${hours > 1 ? 's' : ''} `
  if (minutes > 0 || result === '') result += `${minutes} minuto${minutes !== 1 ? 's' : ''}`

  return result.trim()
}

async function fetchCamas() {
  try {
    const ipress = JSON.parse(localStorage.getItem('user_ipress'))
    if (!ipress || !ipress.id) {
      toast.error('No se pudo determinar el establecimiento', { position: 'top-right' })
      return
    }

    ipressName.value = ipress.descripcion || 'Establecimiento'
    
    // Modificado para incluir todos los datos relacionados
    const response = await api.get(`cama/?ipress=${ipress.id}&expand=ups,servicio,tipocama,estado,ingreso.paciente`)
    camas.value = response.data
    
    // Cargar también las UPS y servicios para los filtros
    const [upsRes, serviciosRes] = await Promise.all([
      api.get('ups/'),
      api.get('servicio/')
    ])
    
    upss.value = upsRes.data
    servicios.value = serviciosRes.data
    
  } catch (error) {
    console.error('Error al cargar datos:', error)
    toast.error('Error al cargar datos: ' + (error.response?.data?.detail || error.message), { position: 'top-right' })
  }
}

async function fetchCamasDisponibles() {
  try {
    const ipress = JSON.parse(localStorage.getItem('user_ipress'))
    if (!ipress || !ipress.id) return

    // Obtener camas con estado "Disponible"
    const response = await api.get(`cama/?ipress=${ipress.id}&estado__descripcion=Disponible&expand=ups,servicio,tipocama,estado`)
    
    // Filtrar para asegurar que solo sean camas disponibles
    camasDisponibles.value = response.data.filter(cama => 
      cama.estado?.descripcion?.toLowerCase() === 'disponible'
    )

    // Actualizar listas de filtros
    upss.value = [...new Set(response.data
      .filter(cama => cama.ups)
      .map(cama => ({
        id: cama.ups.id,
        nombre: cama.ups.nombre
      }))
    )]

    servicios.value = [...new Set(response.data
      .filter(cama => cama.servicio)
      .map(cama => ({
        id: cama.servicio.id,
        nombre: cama.servicio.nombre
      }))
    )]
    
  } catch (error) {
    console.error('Error al cargar camas disponibles:', error)
    toast.error('Error al cargar camas disponibles: ' + (error.response?.data?.detail || error.message))
  }
}

async function iniciarTransferencia() {
  try {
    await fetchCamasDisponibles()

    if (!transferModal.value) {
      transferModal.value = new Modal(document.getElementById('transferModal'))
    }

    camaSeleccionada.value = null
    filtroUps.value = selectedCama.value.ups?.id || ''
    filtroServicio.value = selectedCama.value.servicio?.id || ''

    camaModal.value.hide()
    transferModal.value.show()
  } catch (error) {
    console.error('Error al iniciar transferencia:', error)
    toast.error('Error al preparar transferencia: ' + (error.response?.data?.detail || error.message))
  }
}

function seleccionarCama(cama) {
  camaSeleccionada.value = cama
}

async function confirmarTransferencia() {
  if (!selectedCama.value || !camaSeleccionada.value) {
    toast.warning('Debe seleccionar una cama destino', { position: 'top-right' })
    return
  }

  try {
    const response = await api.post(`ingresos/${selectedCama.value.ingreso.id}/transferir/`, {
      nueva_cama_id: camaSeleccionada.value.id
    }, {
      validateStatus: function (status) {
        return status < 500; // Manejar todos los errores excepto 500
      }
    })

    if (response.status === 200) {
      toast.success('Paciente transferido con éxito', { position: 'top-right' })
      await fetchCamas()
      if (transferModal.value) transferModal.value.hide()
      if (camaModal.value) camaModal.value.hide()
    } else {
      // Mostrar error específico del servidor
      const errorMsg = response.data?.error || 'Error al transferir paciente'
      toast.error(errorMsg, { position: 'top-right' })
    }

  } catch (error) {
    console.error('Error en transferencia:', error)
    let errorMsg = 'Error al conectar con el servidor'
    
    if (error.response) {
      errorMsg = error.response.data?.error || 
                 error.response.data?.detail || 
                 'Error en la transferencia'
    }
    
    toast.error(errorMsg, { position: 'top-right' })
  }
}

async function showCamaDetails(cama) {
  try {
    // Hacer una copia del objeto cama para evitar mutaciones directas
    selectedCama.value = { ...cama }

    // Si no hay ingreso o paciente, cargar los datos completos
    if (!selectedCama.value.ingreso || !selectedCama.value.ingreso.paciente) {
      const response = await api.get(`cama/${cama.id}/?expand=ingreso.paciente,ups,servicio,tipocama,estado`)
      selectedCama.value = response.data
    }

    if (!camaModal.value) {
      camaModal.value = new Modal(document.getElementById('camaModal'))
    }
    camaModal.value.show()
  } catch (error) {
    console.error('Error al cargar detalles de la cama:', error)
    toast.error('Error al cargar detalles del paciente: ' + (error.response?.data?.detail || error.message))
  }
}

// Inicialización
onMounted(() => {
  fetchCamas()
})
</script>

<style scoped>
.card-header.bg-gradient-primary {
  background: linear-gradient(135deg, #4e73df 0%, #224abe 100%);
}

.ups-container {
  padding: 0 15px;
}

.ups-section {
  background-color: #f8faff;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.ups-header {
  padding-bottom: 15px;
  border-bottom: 1px solid #e0e6ed;
}

.ups-icon {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #e3f2fd;
  border-radius: 50%;
}

.servicios-container {
  margin-top: 20px;
}

.servicio-section {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.05);
}

.servicio-title {
  color: #3a5169;
  font-size: 1.1rem;
  padding-bottom: 10px;
  border-bottom: 1px dashed #e0e6ed;
}

.camas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.cama-item {
  transition: transform 0.2s;
}

.cama-item:hover {
  transform: translateY(-3px);
}

.cama-card {
  display: flex;
  align-items: center;
  padding: 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
}

.cama-card.available {
  background-color: #e8f5e9;
  border-left: 4px solid #4caf50;
}

.cama-card.occupied {
  background-color: #ffebee;
  border-left: 4px solid #f44336;
}

.cama-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 1.5rem;
}

.cama-card.available .cama-icon {
  color: #4caf50;
}

.cama-card.occupied .cama-icon {
  color: #f44336;
}

.cama-info {
  flex: 1;
}

.cama-codigo {
  font-weight: 600;
  margin-bottom: 3px;
}

.cama-tipo {
  font-size: 0.8rem;
  color: #666;
  margin-bottom: 5px;
}

.cama-status {
  font-size: 0.75rem;
  font-weight: 500;
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
}

.cama-status.available {
  background-color: #c8e6c9;
  color: #2e7d32;
}

.cama-status.occupied {
  background-color: #ffcdd2;
  color: #c62828;
}

.paciente-avatar {
  padding: 10px;
}

.paciente-data {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 5px;
}

.paciente-data p {
  margin-bottom: 8px;
}

.modal-header {
  border-top-left-radius: 0;
  border-top-right-radius: 0;
}

.bg-success {
  background-color: #4caf50 !important;
}

.bg-danger {
  background-color: #f44336 !important;
}

.text-success {
  color: #4caf50 !important;
}

.text-danger {
  color: #f44336 !important;
}

.badge {
  font-size: 0.75rem;
  font-weight: 500;
}

/* Estilos para el modal de transferencia */
.camas-disponibles {
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 5px;
}

.card {
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.card.border-primary {
  border-color: #0d6efd !important;
}

/* Mejoras para los select de filtro */
.form-select {
  flex: 1;
  min-width: 150px;
}

/* Estilo para el botón de transferencia */
.btn-transferir {
  background-color: #6c757d;
  border-color: #6c757d;
  color: white;
}

.btn-transferir:hover {
  background-color: #5c636a;
  border-color: #565e64;
}

/* Estilos para cuando no hay datos */
.text-center.py-5 {
  padding: 3rem 0;
}

.text-center.py-5 i {
  opacity: 0.5;
}
</style>