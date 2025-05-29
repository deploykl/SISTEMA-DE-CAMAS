<template>
    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-md-12">
                <div class="card shadow-lg border-0">
                    <div
                        class="card-header bg-gradient-primary text-white d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-bed fa-2x me-3"></i>
                            <div>
                                <h4 class="mb-0">Gestión de Camas</h4>
                                <small class="opacity-75">{{ ipressName || 'Cargando establecimiento...' }}</small>
                            </div>
                        </div>
                        <button class="btn btn-light btn-rounded" @click="openAddModal">
                            <i class="fas fa-plus me-2"></i> Nueva Cama
                        </button>
                    </div>

                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-hover align-middle mb-0">
                                <thead class="bg-light">
                                    <tr>
                                        <th class="ps-4">Código</th>
                                        <th>Tipo</th>
                                        <th>Servicio</th>
                                        <th>UPS</th>
                                        <th>Estado</th>
                                        <th class="text-end pe-4">Acciones</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="cama in camas" :key="cama.id" class="border-top">
                                        <td class="ps-4">
                                            <div class="d-flex align-items-center">
                                                <i class="fas fa-bed text-primary me-3"></i>
                                                <strong>{{ cama.codcama }}</strong>
                                            </div>
                                        </td>
                                        <td>
                                            <span class="badge bg-soft-primary text-primary">
                                                {{ cama.tipocama?.descripcion || 'No especificado' }}
                                            </span>
                                        </td>
                                        <td>
                                            <div class="d-flex align-items-center">
                                                <i :class="`fas ${getServicioIcon(cama.servicio?.nombre)} me-2`"></i>
                                                {{ cama.servicio?.nombre || 'No asignado' }}
                                            </div>
                                        </td>
                                        <td>{{ cama.ups?.nombre || 'No asignada' }}</td>
                                        <td>
                                            <span :class="`badge ${getEstadoBadge(cama.estado?.descripcion)}`">
                                                <i :class="`fas ${getEstadoIcon(cama.estado?.descripcion)} me-1`"></i>
                                                {{ cama.estado?.descripcion || 'Desconocido' }}
                                            </span>
                                        </td>
                                        <td class="text-end pe-4">
                                            <button class="btn btn-sm btn-icon btn-outline-primary me-2"
                                                @click="editCama(cama)">
                                                <i class="fas fa-pen"></i>
                                            </button>
                                            <button class="btn btn-sm btn-icon btn-outline-danger"
                                                @click="confirmDelete(cama)">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </td>
                                    </tr>
                                    <tr v-if="camas.length === 0">
                                        <td colspan="6" class="text-center py-4 text-muted">
                                            <i class="fas fa-bed fa-2x mb-3"></i>
                                            <p class="mb-0">No hay camas registradas</p>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal para agregar/editar cama -->
        <div v-if="showAddModal" class="modal fade show d-block" tabindex="-1" aria-modal="true" role="dialog"
            style="background-color: rgba(0,0,0,0.5);">
            <div class="modal-dialog modal-lg modal-dialog-centered">
                <div class="modal-content border-0 shadow">
                    <div class="modal-header bg-gradient-primary text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-bed me-2"></i>
                            {{ editingCama ? 'Editar Cama' : 'Registrar Nueva Cama' }}
                        </h5>
                        <button type="button" class="btn-close btn-close-white" @click="closeModal"
                            aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form @submit.prevent="saveCama">
                            <div class="row g-3">
                                <div class="col-md-6">
                                    <label class="form-label">Código de Cama <span class="text-danger">*</span></label>
                                    <div class="input-group">
                                        <span class="input-group-text bg-light">
                                            <i class="fas fa-hashtag text-primary"></i>
                                        </span>
                                        <input type="text" class="form-control" v-model="currentCama.codcama" required
                                            placeholder="Ej: CAMA-001">
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Tipo de Cama <span class="text-danger">*</span></label>
                                    <div class="input-group">
                                        <span class="input-group-text bg-light">
                                            <i class="fas fa-procedures text-primary"></i>
                                        </span>
                                        <select class="form-select" v-model="currentCama.tipocama_id" required>
                                            <option value="" disabled>Seleccione un tipo</option>
                                            <option v-for="tipo in tiposCama" :key="tipo.id" :value="tipo.id">{{
                                                tipo.descripcion }}</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Servicio <span class="text-danger">*</span></label>
                                    <div class="input-group">
                                        <span class="input-group-text bg-light">
                                            <i class="fas fa-stethoscope text-primary"></i>
                                        </span>
                                        <select class="form-select" v-model="currentCama.servicio_id" required>
                                            <option value="" disabled>Seleccione un servicio</option>
                                            <option v-for="servicio in servicios" :key="servicio.id"
                                                :value="servicio.id">{{ servicio.nombre }}</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">UPS <span class="text-danger">*</span></label>
                                    <div class="input-group">
                                        <span class="input-group-text bg-light">
                                            <i class="fas fa-clinic-medical text-primary"></i>
                                        </span>
                                        <select class="form-select" v-model="currentCama.ups_id" required>
                                            <option value="" disabled>Seleccione una UPS</option>
                                            <option v-for="ups in upsList" :key="ups.id" :value="ups.id">{{ ups.nombre
                                                }}</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Estado <span class="text-danger">*</span></label>
                                    <div class="input-group">
                                        <span class="input-group-text bg-light">
                                            <i class="fas fa-info-circle text-primary"></i>
                                        </span>
                                        <select class="form-select" v-model="currentCama.estado_id" required>
                                            <option value="" disabled>Seleccione un estado</option>
                                            <option v-for="estado in estadosCama" :key="estado.id" :value="estado.id">{{
                                                estado.descripcion }}</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="d-flex justify-content-between mt-4">
                                <button type="button" class="btn btn-outline-secondary" @click="closeModal">
                                    <i class="fas fa-times me-2"></i> Cancelar
                                </button>
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-save me-2"></i>
                                    {{ editingCama ? 'Actualizar Cama' : 'Guardar Cama' }}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
            <div class="modal-backdrop fade show" @click.stop></div>
        </div>

        <!-- Modal de confirmación para eliminar -->
        <div v-if="showDeleteModal" class="modal fade show d-block" tabindex="-1" aria-modal="true" role="dialog"
            style="background-color: rgba(0,0,0,0.5);">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content border-0 shadow">
                    <div class="modal-header bg-gradient-danger text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Confirmar Eliminación
                        </h5>
                        <button type="button" class="btn-close btn-close-white"
                            @click="showDeleteModal = false"></button>
                    </div>
                    <div class="modal-body">
                        <div class="text-center mb-4">
                            <i class="fas fa-bed fa-3x text-danger mb-3"></i>
                            <h5>¿Eliminar cama {{ camaToDelete?.codcama }}?</h5>
                            <p class="text-muted">Esta acción no se puede deshacer</p>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline-secondary" @click="showDeleteModal = false">
                            <i class="fas fa-times me-2"></i> Cancelar
                        </button>
                        <button type="button" class="btn btn-danger" @click="deleteCama">
                            <i class="fas fa-trash me-2"></i> Sí, Eliminar
                        </button>
                    </div>
                </div>
            </div>
            <div class="modal-backdrop fade show" @click.stop></div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/components/services/auth_axios'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-sugar.css'

const router = useRouter()
const toast = useToast()

// Datos
const camas = ref([])
const tiposCama = ref([])
const servicios = ref([])
const upsList = ref([])
const estadosCama = ref([])
const ipressName = ref('')

// Estados UI
const showAddModal = ref(false)
const showDeleteModal = ref(false)
const editingCama = ref(false)
const camaToDelete = ref(null)
const currentCama = ref(createEmptyCama())

function openAddModal() {
    document.body.classList.add('modal-open');
    showAddModal.value = true;
}

function closeModal() {
    document.body.classList.remove('modal-open');
    showAddModal.value = false;
    editingCama.value = false;
    currentCama.value = createEmptyCama();
}

function confirmDelete(cama) {
    camaToDelete.value = cama
    showDeleteModal.value = true
}

async function deleteCama() {
    try {
        await api.delete(`cama/${camaToDelete.value.id}/`)
        toast.success('Cama eliminada correctamente', { position: 'top-right' })
        showDeleteModal.value = false
        await fetchData()
    } catch (error) {
        console.error('Error al eliminar cama:', error)
        toast.error('Error al eliminar la cama', { position: 'top-right' })
    }
}

// Funciones auxiliares
function createEmptyCama() {
    const ipress = JSON.parse(localStorage.getItem('user_ipress'))
    return {
        id: null,
        codcama: '',
        tipocama_id: '',
        servicio_id: '',
        ups_id: '',
        estado_id: '',
        ipress: ipress?.id || null
    }
}

function getServicioIcon(servicioNombre) {
    if (!servicioNombre) return 'fa-procedures'

    const servicioLower = servicioNombre.toLowerCase()
    if (servicioLower.includes('pediatr')) return 'fa-child'
    if (servicioLower.includes('neo')) return 'fa-baby'
    if (servicioLower.includes('mater')) return 'fa-female'
    if (servicioLower.includes('terap')) return 'fa-heartbeat'
    return 'fa-procedures'
}

function getEstadoIcon(estadoDescripcion) {
    if (!estadoDescripcion) return 'fa-info-circle'

    const estadoLower = estadoDescripcion.toLowerCase()
    if (estadoLower.includes('disponible')) return 'fa-check-circle'
    if (estadoLower.includes('ocupada')) return 'fa-times-circle'
    if (estadoLower.includes('manten')) return 'fa-tools'
    return 'fa-info-circle'
}

function getEstadoBadge(estadoDescripcion) {
    if (!estadoDescripcion) return 'bg-soft-secondary text-secondary'

    const estadoLower = estadoDescripcion.toLowerCase()
    if (estadoLower.includes('disponible')) return 'bg-soft-success text-success'
    if (estadoLower.includes('ocupada')) return 'bg-soft-danger text-danger'
    if (estadoLower.includes('manten')) return 'bg-soft-warning text-warning'
    return 'bg-soft-secondary text-secondary'
}

// Operaciones CRUD
async function fetchData() {
    try {
        const userIpress = localStorage.getItem('user_ipress')
        if (!userIpress) {
            router.push('/register-ipress')
            return
        }

        const ipress = JSON.parse(userIpress)
        ipressName.value = ipress.descripcion || 'Establecimiento'

        const [camasRes, tiposRes, serviciosRes, upsRes, estadosRes] = await Promise.all([
            api.get(`cama/?ipress=${ipress.id}`),
            api.get('tipo-cama/'),
            api.get('servicio/'),
            api.get('ups/'),
            api.get('estado-cama/')
        ])

        camas.value = camasRes.data
        tiposCama.value = tiposRes.data
        servicios.value = serviciosRes.data
        upsList.value = upsRes.data
        estadosCama.value = estadosRes.data
    } catch (error) {
        console.error('Error al cargar datos:', error)
        toast.error('Error al cargar los datos de camas', { position: 'top-right' })
    }
}

function editCama(cama) {
    currentCama.value = {
        id: cama.id,
        codcama: cama.codcama,
        tipocama_id: cama.tipocama?.id || '',
        servicio_id: cama.servicio?.id || '',
        ups_id: cama.ups?.id || '',
        estado_id: cama.estado?.id || '',
        ipress: cama.ipress?.id || null
    }
    editingCama.value = true
    openAddModal()
}

async function saveCama() {
    try {
        const camaData = {
            codcama: currentCama.value.codcama,
            tipocama: currentCama.value.tipocama_id,
            servicio: currentCama.value.servicio_id,
            ups: currentCama.value.ups_id,
            estado: currentCama.value.estado_id,
            ipress: currentCama.value.ipress,
        }

        if (editingCama.value) {
            await api.put(`cama/${currentCama.value.id}/`, camaData)
            toast.success('Cama actualizada correctamente', { position: 'top-right' })
        } else {
            await api.post('cama/', camaData)
            toast.success('Cama creada correctamente', { position: 'top-right' })
        }

        closeModal()
        await fetchData()
    } catch (error) {
        console.error('Error al guardar cama:', error)
        const errorMsg = error.response?.data?.message || 'Error al guardar la cama'
        toast.error(errorMsg, { position: 'top-right' })
    }
}

// Inicialización
onMounted(fetchData)
</script>

<style scoped>
.card-header.bg-gradient-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.btn-rounded {
    border-radius: 50px;
}

.modal-header.bg-gradient-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.modal-header.bg-gradient-danger {
    background: linear-gradient(135deg, #f5365c 0%, #f56036 100%);
}

.bg-soft-primary {
    background-color: rgba(102, 126, 234, 0.1);
}

.bg-soft-success {
    background-color: rgba(40, 167, 69, 0.1);
}

.bg-soft-danger {
    background-color: rgba(220, 53, 69, 0.1);
}

.bg-soft-warning {
    background-color: rgba(255, 193, 7, 0.1);
}

.bg-soft-secondary {
    background-color: rgba(108, 117, 125, 0.1);
}

.table th {
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.5px;
}

.table td,
.table th {
    vertical-align: middle;
}

.btn-icon {
    width: 32px;
    height: 32px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
}

.form-label span.text-danger {
    font-size: 0.8em;
}

/* Estilos adicionales para corregir el problema */
.modal {
    overflow-y: auto;
}

.modal-open {
    overflow: hidden;
}

.modal-content {
    pointer-events: auto;
}

.modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1040;
    width: 100vw;
    height: 100vh;
    background-color: rgba(0, 0, 0, 0.5);
}
</style>