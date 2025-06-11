<template>
  <div class="container-fluid mt-4">
    <div class="row">
      <div class="col-md-12">
        <div class="card shadow-lg border-0">
          <div class="card-header bg-gradient-info text-white d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center">
              <i class="fas fa-user-injured fa-2x me-3"></i>
              <div>
                <h4 class="mb-0">Registro de Pacientes</h4>
                <small class="opacity-75">{{ ipressName || 'Cargando establecimiento...' }}</small>
              </div>
            </div>
          </div>

          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <div class="card mb-4">
                  <div class="card-header bg-light">
                    <h5 class="mb-0">Datos del Paciente</h5>
                  </div>
                  <div class="card-body">
                    <form @submit.prevent="searchPaciente">
                      <div class="mb-3">
                        <label class="form-label">Documento de Identidad</label>
                        <div class="input-group">
                          <input type="text" class="form-control" v-model="documentoIdentidad"
                            placeholder="Ingrese DNI/CE" required>
                          <button class="btn btn-primary" type="submit">
                            <i class="fas fa-search me-2"></i> Buscar
                          </button>
                        </div>
                      </div>
                    </form>

                    <form @submit.prevent="savePaciente" v-if="showPacienteForm">
                      <div class="row g-3">
                        <div class="col-md-6">
                          <label class="form-label">Nombres <span class="text-danger">*</span></label>
                          <input type="text" class="form-control" v-model="paciente.nombres" required>
                        </div>
                        <div class="col-md-6">
                          <label class="form-label">Apellidos <span class="text-danger">*</span></label>
                          <input type="text" class="form-control" v-model="paciente.apellidos" required>
                        </div>
                        <div class="col-md-6">
                          <label class="form-label">Documento Identidad <span class="text-danger">*</span></label>
                          <input type="text" class="form-control" v-model="paciente.documento_identidad" required>
                        </div>
                        <div class="col-md-6">
                          <label class="form-label">Fecha Nacimiento <span class="text-danger">*</span></label>
                          <input type="date" class="form-control" v-model="paciente.fecha_nacimiento" required>
                        </div>
                        <div class="col-md-6">
                          <label class="form-label">Género <span class="text-danger">*</span></label>
                          <select class="form-select" v-model="paciente.genero" required>
                            <option value="M">Masculino</option>
                            <option value="F">Femenino</option>
                            <option value="O">Otro</option>
                          </select>
                        </div>
                        <div class="col-md-6">
                          <label class="form-label">Teléfono</label>
                          <input type="text" class="form-control" v-model="paciente.telefono"
                            placeholder="Ingrese teléfono">
                        </div>
                        <div class="col-md-12">
                          <label class="form-label">Dirección</label>
                          <input type="text" class="form-control" v-model="paciente.direccion"
                            placeholder="Ingrese dirección">
                        </div>
                      </div>
                      <div class="d-flex justify-content-end mt-3">
                        <button type="submit" class="btn btn-primary">
                          <i class="fas fa-save me-2"></i> Guardar Paciente
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              </div>

              <div class="col-md-6">
                <div class="card">
                  <div class="card-header bg-light">
                    <h5 class="mb-0">Asignación de Cama</h5>
                  </div>
                  <div class="card-body">
                    <div v-if="paciente.id">
                      <div class="alert alert-info mb-4">
                        <i class="fas fa-info-circle me-2"></i>
                        Paciente seleccionado: <strong>{{ paciente.nombres }} {{ paciente.apellidos }}</strong>
                      </div>

                      <!-- Detalles del paciente encontrado -->
                      <div class="mb-4">
                        <h6 class="mb-3">Información del Paciente</h6>
                        <div class="row">
                          <div class="col-md-6">
                            <p><strong>Documento:</strong> {{ paciente.documento_identidad }}</p>
                            <p><strong>Fecha Nacimiento:</strong> {{ formatDate(paciente.fecha_nacimiento) }}</p>
                          </div>
                          <div class="col-md-6">
                            <p><strong>Género:</strong> {{ formatGenero(paciente.genero) }}</p>
                            <p><strong>Teléfono:</strong> {{ paciente.telefono || 'No registrado' }}</p>
                          </div>
                          <div class="col-12" v-if="paciente.direccion">
                            <p><strong>Dirección:</strong> {{ paciente.direccion }}</p>
                          </div>
                        </div>
                      </div>

                      <div class="mb-3">
                        <label class="form-label">Diagnóstico Principal <span class="text-danger">*</span></label>
                        <textarea class="form-control" v-model="ingreso.diagnostico" required></textarea>
                      </div>

                      <div class="mb-3">
                        <label class="form-label">Médico Tratante <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" v-model="ingreso.medico_tratante" required>
                      </div>

                      <div class="mb-4">
                        <label class="form-label">Observaciones</label>
                        <textarea class="form-control" v-model="ingreso.observaciones"></textarea>
                      </div>

                      <div class="mb-4">
                        <label class="form-label">Seleccionar Cama Disponible <span class="text-danger">*</span></label>
                        <div class="table-responsive">
                          <table class="table table-sm table-hover">
                            <thead>
                              <tr>
                                <th>Código</th>
                                <th>Tipo</th>
                                <th>Servicio</th>
                                <th>UPS</th>
                                <th>Acción</th>
                              </tr>
                            </thead>
                            <tbody>
                              <tr v-for="cama in camasDisponibles" :key="cama.id">
                                <td>{{ cama.codcama }}</td>
                                <td>{{ cama.tipocama.descripcion }}</td>
                                <td>{{ cama.servicio.nombre }}</td>
                                <td>{{ cama.ups.nombre }}</td>
                                <td>
                                  <button class="btn btn-sm btn-primary" @click="selectCama(cama)" :disabled="loading">
                                    <i class="fas fa-bed me-1"></i>
                                    {{ loading && selectedCamaId === cama.id ? 'Asignando...' : 'Asignar' }}
                                  </button>
                                </td>
                              </tr>
                              <tr v-if="camasDisponibles.length === 0">
                                <td colspan="5" class="text-center text-muted py-3">
                                  No hay camas disponibles en este momento
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                    <div v-else class="text-center text-muted py-4">
                      <i class="fas fa-user-clock fa-2x mb-3"></i>
                      <p>Primero busque o registre un paciente</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'  // Añade nextTick aquíimport { api } from '@/components/services/auth_axios'
import { useToast } from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-sugar.css'
import { api } from '@/components/services/auth_axios'

const toast = useToast()

// Datos
const ipressName = ref('')
const documentoIdentidad = ref('')
const showPacienteForm = ref(false)
const camasDisponibles = ref([])
const loading = ref(false)
const selectedCamaId = ref(null)

// Modelos
const paciente = ref({
  id: null,
  documento_identidad: '',
  nombres: '',
  apellidos: '',
  fecha_nacimiento: '',
  genero: 'M',
  telefono: '',
  direccion: ''
})

const ingreso = ref({
  paciente_id: null,
  cama_id: null,
  diagnostico: '',
  medico_tratante: '',
  observaciones: ''
})

// Función de validación de DNI/CE mejorada
function validarDocumentoIdentidad(doc) {
  if (!doc) return false
  
  // Eliminar espacios y caracteres no numéricos (excepto para CE que puede tener letras)
  const limpio = doc.toString().trim().toUpperCase()
  
  // Validar DNI (8 dígitos)
  if (/^\d{8}$/.test(limpio)) {
    return true
  }
  
  // Validar CE (Carné de Extranjería) - formato variado, normalmente letras y números
  if (/^[A-Z0-9]{9,12}$/.test(limpio)) {
    return true
  }
  
  return false
}

async function searchPaciente() {
  try {
    // Validar documento antes de proceder
    if (!documentoIdentidad.value || !validarDocumentoIdentidad(documentoIdentidad.value)) {
      toast.error('Ingrese un documento válido (DNI: 8 dígitos | CE: 9-12 caracteres alfanuméricos)', {
        position: 'top-right',
        duration: 5000
      })
      return
    }

    // Mostrar estado de carga
    loading.value = true
    
    // Limpiar resultados anteriores
    resetForms()
    
    // Asignar el documento al modelo (sin formato)
    paciente.value.documento_identidad = documentoIdentidad.value.replace(/\D/g, '')
    
    // Buscar exactamente por documento
    const response = await api.get(`pacientes/?documento_identidad=${paciente.value.documento_identidad}`)
    
    if (response.data.length > 0) {
      // Mostrar el primer resultado (debería ser único por la unicidad del documento)
      paciente.value = {
        ...response.data[0],
        // Asegurar formato de fecha para el input date
        fecha_nacimiento: response.data[0].fecha_nacimiento?.split('T')[0] || ''
      }
      
      showPacienteForm.value = false
      
      // Cargar camas disponibles
      await fetchCamasDisponibles()
      
      toast.success('Paciente encontrado', { position: 'top-right' })
      
      // Mover el foco a la sección de asignación de cama
      nextTick(() => {
        const camaSection = document.querySelector('.col-md-6 .card')
        if (camaSection) {
          camaSection.scrollIntoView({ behavior: 'smooth' })
        }
      })
    } else {
      // Preparar nuevo registro si no se encuentra
      paciente.value = {
        documento_identidad: paciente.value.documento_identidad,
        nombres: '',
        apellidos: '',
        fecha_nacimiento: '',
        genero: 'M',
        telefono: '',
        direccion: ''
      }
      showPacienteForm.value = true
      
      toast.info('Documento no registrado. Complete los datos para nuevo registro', {
        position: 'top-right',
        duration: 4000
      })
      
      // Enfocar el campo de nombres
      nextTick(() => {
        const nombresInput = document.querySelector('input[v-model="paciente.nombres"]')
        if (nombresInput) {
          nombresInput.focus()
        }
      })
    }
  } catch (error) {
    console.error('Error en búsqueda:', error)
    
    let errorMessage = 'Error al buscar paciente'
    if (error.response) {
      if (error.response.data) {
        if (typeof error.response.data === 'object') {
          errorMessage = Object.entries(error.response.data)
            .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
            .join('; ')
        } else {
          errorMessage = error.response.data
        }
      }
    } else {
      errorMessage = error.message
    }
    
    toast.error(errorMessage, {
      position: 'top-right',
      duration: 5000
    })
  } finally {
    loading.value = false
  }
}

// Función para formatear documento (opcional, para mostrar mejor)
function formatearDocumento(doc) {
  if (!doc) return ''
  
  // DNI peruano: 8 dígitos
  if (/^\d{8}$/.test(doc)) {
    return doc
  }
  
  // CE: mostrar con formato (ejemplo: ABC-12345)
  if (/^[A-Z0-9]{9,12}$/.test(doc)) {
    if (doc.length <= 3) return doc
    return `${doc.substring(0, 3)}-${doc.substring(3)}`
  }
  
  return doc
}

function formatDate(dateString) {
  if (!dateString) return 'No registrado';
  const date = new Date(dateString);
  return date.toLocaleDateString('es-PE', { year: 'numeric', month: '2-digit', day: '2-digit' });
}

function formatGenero(genero) {
  const generos = {
    'M': 'Masculino',
    'F': 'Femenino',
    'O': 'Otro'
  };
  return generos[genero] || genero;
}

async function savePaciente() {
    try {
        let response;
        
        // Primero verificar si el paciente ya existe
        const checkResponse = await api.get(`pacientes/?documento_identidad=${paciente.value.documento_identidad}`);
        if (checkResponse.data.length > 0 && !paciente.value.id) {
            // Si existe, cargar sus datos
            paciente.value = checkResponse.data[0];
            toast.info('Paciente encontrado, se cargaron sus datos', {position: 'top-right'});
            showPacienteForm.value = false;
            await fetchCamasDisponibles();
            return;
        }
        
        // Guardar o actualizar paciente
        if (paciente.value.id) {
            response = await api.put(`pacientes/${paciente.value.id}/`, paciente.value);
            toast.success('Paciente actualizado', {position: 'top-right'});
        } else {
            response = await api.post('pacientes/', paciente.value);
            paciente.value.id = response.data.id;
            toast.success('Paciente registrado', {position: 'top-right'});
        }
        
        // Si hay datos de ingreso, asignar cama
        if (ingreso.value.diagnostico && ingreso.value.medico_tratante) {
            await assignCamaAfterSave();
        } else {
            showPacienteForm.value = false;
            await fetchCamasDisponibles();
        }
    } catch (error) {
        console.error('Error:', error);
        toast.error(`Error: ${error.response?.data?.detail || error.message}`, {position: 'top-right'});
    }
}

async function assignCamaAfterSave() {
    if (!camasDisponibles.value.length) {
        toast.warning('No hay camas disponibles', {position: 'top-right'});
        return;
    }
    
    // Asignar primera cama disponible
    const cama = camasDisponibles.value[0];
    ingreso.value.paciente_id = paciente.value.id;
    ingreso.value.cama_id = cama.id;
    
    try {
        await api.post('ingresos/', ingreso.value);
        toast.success(`Cama ${cama.codcama} asignada`, {position: 'top-right'});
        resetForms();
    } catch (error) {
        console.error('Error al asignar cama:', error);
        toast.error(`Error al asignar cama: ${error.response?.data?.detail || error.message}`, {position: 'top-right'});
    }
}

async function fetchCamasDisponibles() {
  try {
    if (!paciente.value.id) return

    const ipress = JSON.parse(localStorage.getItem('user_ipress'))
    if (!ipress || !ipress.id) {
      toast.error('No se pudo determinar el establecimiento', { position: 'top-right' })
      return
    }

    const response = await api.get(`camas/disponibles/?ipress=${ipress.id}`)
    camasDisponibles.value = response.data
  } catch (error) {
    console.error('Error al cargar camas disponibles:', error)
    toast.error('Error al cargar camas disponibles: ' + (error.response?.data?.detail || error.message), { position: 'top-right' })
  }
}

function validateIngreso() {
  if (!ingreso.value.diagnostico?.trim()) {
    toast.error('El diagnóstico es requerido', { position: 'top-right' });
    return false;
  }
  if (!ingreso.value.medico_tratante?.trim()) {
    toast.error('El médico tratante es requerido', { position: 'top-right' });
    return false;
  }
  if (!paciente.value.id) {
    toast.error('Seleccione un paciente válido', { position: 'top-right' });
    return false;
  }
  if (!JSON.parse(localStorage.getItem('user'))?.id) {
    toast.error('No se pudo identificar al usuario', { position: 'top-right' });
    return false;
  }
  return true;
}

async function selectCama(cama) {
  if (!validateIngreso()) return;
  
  if (confirm(`¿Confirmar asignación de cama ${cama.codcama} al paciente ${paciente.value.nombres} ${paciente.value.apellidos}?`)) {
    try {
      loading.value = true;
      selectedCamaId.value = cama.id;

      const ingresoData = {
        paciente: paciente.value.id,
        cama: cama.id,
        diagnostico: ingreso.value.diagnostico,
        medico_tratante: ingreso.value.medico_tratante,
        observaciones: ingreso.value.observaciones || ''
      };

      const response = await api.post('ingresos/', ingresoData);
      toast.success('Paciente ingresado correctamente', { position: 'top-right' });
      resetForms();
      await fetchCamasDisponibles();
    } catch (error) {
      let errorMessage = 'Error al registrar ingreso';
      
      if (error.response) {
        if (error.response.data) {
          if (typeof error.response.data === 'object') {
            errorMessage = Object.entries(error.response.data)
              .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
              .join('; ');
          } else {
            errorMessage = error.response.data;
          }
        }
      } else {
        errorMessage = error.message;
      }

      toast.error(errorMessage, { position: 'top-right', duration: 5000 });
      console.error('Error completo:', error);
    } finally {
      loading.value = false;
      selectedCamaId.value = null;
    }
  }
}

function resetForms() {
  documentoIdentidad.value = ''
  paciente.value = {
    id: null,
    documento_identidad: '',
    nombres: '',
    apellidos: '',
    fecha_nacimiento: '',
    genero: 'M',
    telefono: '',
    direccion: ''
  }
  ingreso.value = {
    paciente_id: null,
    cama_id: null,
    diagnostico: '',
    medico_tratante: '',
    observaciones: ''
  }
  showPacienteForm.value = false
  camasDisponibles.value = []
}

// Inicialización
onMounted(() => {
  const ipress = JSON.parse(localStorage.getItem('user_ipress'))
  ipressName.value = ipress?.descripcion || 'Establecimiento'
})
</script>

<style scoped>
.card-header.bg-gradient-info {
  background: linear-gradient(135deg, #17a2b8 0%, #117a8b 100%);
}

.alert-info {
  background-color: #d1ecf1;
  border-color: #bee5eb;
  color: #0c5460;
}

.table th {
  font-size: 0.8rem;
  font-weight: 600;
}

.table td {
  font-size: 0.9rem;
  vertical-align: middle;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
}

.form-label {
  font-weight: 500;
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Estilos para la sección de información del paciente */
.patient-info-section {
  background-color: #f8f9fa;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.patient-info-section h6 {
  color: #495057;
  font-weight: 600;
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}

.patient-info-section p {
  margin-bottom: 0.5rem;
}
</style>