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
                            placeholder="Ingrese DNI/CE" maxlength="8" @input="validateDocumento" required>
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
                        <input type="text" class="form-control" v-model="paciente.telefono"
                          placeholder="Ingrese teléfono">
                        <input type="text" class="form-control" v-model="paciente.direccion"
                          placeholder="Ingrese dirección">
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

                      <!-- Mostrar datos de ingreso si el paciente ya tiene uno activo -->
                      <!-- Mostrar datos de ingreso si el paciente ya tiene uno activo -->
                      <div v-if="ingresoExistente" class="mb-4">
                        <h6 class="fw-bold mb-3">Datos de Ingreso Actual</h6>
                        <div class="mb-2">
                          <label class="form-label fw-bold">Fecha de Ingreso:</label>
                          <p class="form-control-plaintext">{{ formatDateTime(ingresoExistente.fecha_ingreso) }}</p>
                        </div>
                        <div class="mb-2">
                          <label class="form-label fw-bold">Diagnóstico Principal:</label>
                          <p class="form-control-plaintext">{{ ingresoExistente.diagnostico }}</p>
                        </div>
                        <div class="mb-2">
                          <label class="form-label fw-bold">Médico Tratante:</label>
                          <p class="form-control-plaintext">{{ ingresoExistente.medico_tratante }}</p>
                        </div>
                        <div class="mb-2" v-if="ingresoExistente.observaciones">
                          <label class="form-label fw-bold">Observaciones:</label>
                          <p class="form-control-plaintext">{{ ingresoExistente.observaciones }}</p>
                        </div>
                        <div class="mb-2">
                          <label class="form-label fw-bold">Cama Asignada:</label>
                          <p class="form-control-plaintext">
                            {{ ingresoExistente.cama?.codcama }}
                            ({{ ingresoExistente.cama?.servicio?.nombre }} -
                            {{ ingresoExistente.cama?.estado?.descripcion }})
                          </p>
                        </div>
                        <div class="alert alert-warning mt-3">
                          <i class="fas fa-exclamation-triangle me-2"></i>
                          Este paciente ya tiene un ingreso activo.
                        </div>
                      </div>

                      <!-- Mostrar formulario de ingreso solo si no hay ingreso existente -->
                      <div v-else>
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
                          <label class="form-label">Seleccionar Cama Disponible <span
                              class="text-danger">*</span></label>
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
                                    <button class="btn btn-sm btn-primary" @click="selectCama(cama)"
                                      :disabled="loading">
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
import { ref, onMounted } from 'vue'
import { api } from '@/components/services/auth_axios'
import { useToast } from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-sugar.css'

const toast = useToast()

// Datos
const ipressName = ref('')
const documentoIdentidad = ref('')
const showPacienteForm = ref(false)
const camasDisponibles = ref([])
const loading = ref(false)
const selectedCamaId = ref(null)
const ingresoExistente = ref(null)

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

// Funciones
function formatDateTime(dateTimeString) {
  if (!dateTimeString) return 'No disponible';

  const date = new Date(dateTimeString);
  return date.toLocaleString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

async function searchPaciente() {
  try {
    // Primero buscar coincidencia exacta
    const exactMatch = await api.get(`pacientes/?documento_identidad=${documentoIdentidad.value}`);

    if (exactMatch.data.length > 0) {
      paciente.value = exactMatch.data[0];
      showPacienteForm.value = false;

      // Verificar si el paciente tiene un ingreso activo
      await checkIngresoExistente(paciente.value.id);

      // Solo buscar camas si no tiene ingreso activo
      if (!ingresoExistente.value) {
        await fetchCamasDisponibles();
      }

      toast.success('Paciente encontrado', { position: 'top-right' });
      return;
    }

    // Si no hay coincidencia exacta, buscar parcial
    const partialMatch = await api.get(`pacientes/search/?documento=${documentoIdentidad.value}`);

    if (partialMatch.data.length > 0) {
      paciente.value = partialMatch.data[0];
      showPacienteForm.value = false;

      // Verificar si el paciente tiene un ingreso activo
      await checkIngresoExistente(paciente.value.id);

      // Solo buscar camas si no tiene ingreso activo
      if (!ingresoExistente.value) {
        await fetchCamasDisponibles();
      }

      toast.success('Paciente encontrado', { position: 'top-right' });
    } else {
      // Preparar nuevo registro
      paciente.value = {
        id: null,
        documento_identidad: documentoIdentidad.value,
        nombres: '',
        apellidos: '',
        fecha_nacimiento: '',
        genero: 'M',
        telefono: '',
        direccion: ''
      };
      showPacienteForm.value = true;
      ingresoExistente.value = null;
      toast.info('Complete los datos para nuevo registro', { position: 'top-right' });
    }
  } catch (error) {
    console.error('Error en búsqueda:', error);
    toast.error(`Error: ${error.response?.data?.detail || error.message}`, { position: 'top-right' });
  }
}

async function checkIngresoExistente(pacienteId) {
  try {
    const response = await api.get(`ingresos/?paciente=${pacienteId}&fecha_alta__isnull=true`);
    if (response.data.length > 0) {
      // Obtener detalles completos del ingreso (incluyendo cama)
      const ingresoDetalle = await api.get(`ingresos/${response.data[0].id}/`);
      ingresoExistente.value = ingresoDetalle.data;
    } else {
      ingresoExistente.value = null;
    }
  } catch (error) {
    console.error('Error al verificar ingreso:', error);
    ingresoExistente.value = null;
  }
}
function validateDocumento(event) {
  // Elimina cualquier carácter que no sea número
  documentoIdentidad.value = documentoIdentidad.value.replace(/\D/g, '');
  
  // Limita a 8 caracteres (por si acaso el maxlength no funciona)
  if (documentoIdentidad.value.length > 8) {
    documentoIdentidad.value = documentoIdentidad.value.slice(0, 8);
  }
}

function validatePacienteDocumento() {
  // Elimina cualquier carácter que no sea número
  paciente.value.documento_identidad = paciente.value.documento_identidad.replace(/\D/g, '');
  
  // Limita a 8 caracteres
  if (paciente.value.documento_identidad.length > 8) {
    paciente.value.documento_identidad = paciente.value.documento_identidad.slice(0, 8);
  }
}

async function savePaciente() {
  try {
    let response;

    // Primero verificar si el paciente ya existe
    const checkResponse = await api.get(`pacientes/?documento_identidad=${paciente.value.documento_identidad}`);
    if (checkResponse.data.length > 0 && !paciente.value.id) {
      // Si existe, cargar sus datos
      paciente.value = checkResponse.data[0];
      toast.info('Paciente encontrado, se cargaron sus datos', { position: 'top-right' });
      showPacienteForm.value = false;

      // Verificar si tiene ingreso activo
      await checkIngresoExistente(paciente.value.id);

      // Solo buscar camas si no tiene ingreso activo
      if (!ingresoExistente.value) {
        await fetchCamasDisponibles();
      }
      return;
    }

    // Guardar o actualizar paciente
    if (paciente.value.id) {
      response = await api.put(`pacientes/${paciente.value.id}/`, paciente.value);
      toast.success('Paciente actualizado', { position: 'top-right' });
    } else {
      response = await api.post('pacientes/', paciente.value);
      paciente.value.id = response.data.id;
      toast.success('Paciente registrado', { position: 'top-right' });
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
    toast.error(`Error: ${error.response?.data?.detail || error.message}`, { position: 'top-right' });
  }
}

async function assignCamaAfterSave() {
  if (!camasDisponibles.value.length) {
    toast.warning('No hay camas disponibles', { position: 'top-right' });
    return;
  }

  // Asignar primera cama disponible
  const cama = camasDisponibles.value[0];
  ingreso.value.paciente_id = paciente.value.id;
  ingreso.value.cama_id = cama.id;

  try {
    await api.post('ingresos/', ingreso.value);
    toast.success(`Cama ${cama.codcama} asignada`, { position: 'top-right' });
    resetForms();
  } catch (error) {
    console.error('Error al asignar cama:', error);
    toast.error(`Error al asignar cama: ${error.response?.data?.detail || error.message}`, { position: 'top-right' });
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

      // Actualizar el ingreso existente después de la asignación
      await checkIngresoExistente(paciente.value.id);

      resetForms();
    } catch (error) {
      let errorMessage = 'Error al registrar ingreso';

      if (error.response) {
        if (error.response.data) {
          errorMessage = typeof error.response.data === 'object'
            ? JSON.stringify(error.response.data)
            : error.response.data;
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

.form-control-plaintext {
  padding: 0.375rem 0;
  margin-bottom: 0;
  background-color: transparent;
  border: solid transparent;
  border-width: 1px 0;
}

.fw-bold {
  font-weight: 600;
}
</style>