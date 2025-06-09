<template>
    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-md-12">
                <div class="card shadow-lg border-0">
                    <div class="card-header bg-gradient-info text-white">
                        <h4 class="mb-0">
                            <i class="fas fa-exchange-alt me-2"></i>
                            Transferencia de Pacientes entre Camas
                        </h4>
                    </div>
                    
                    <div class="card-body">
                        <div class="row">
                            <!-- Cama Origen -->
                            <div class="col-md-6">
                                <div class="card h-100 border-primary">
                                    <div class="card-header bg-primary text-white">
                                        <h5 class="mb-0">Cama Origen</h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="mb-3">
                                            <label class="form-label">Buscar Cama Ocupada</label>
                                            <div class="input-group">
                                                <span class="input-group-text">
                                                    <i class="fas fa-search"></i>
                                                </span>
                                                <input type="text" class="form-control" v-model="searchOrigin" 
                                                       placeholder="Buscar por código o paciente...">
                                            </div>
                                        </div>
                                        
                                        <div class="list-group" style="max-height: 300px; overflow-y: auto;">
                                            <button v-for="cama in filteredOccupiedBeds" :key="cama.id"
                                                    class="list-group-item list-group-item-action"
                                                    :class="{ 'active': selectedOriginBed?.id === cama.id }"
                                                    @click="selectOriginBed(cama)">
                                                <div class="d-flex justify-content-between align-items-center">
                                                    <div>
                                                        <strong>{{ cama.codcama }}</strong> - {{ cama.servicio?.nombre }}
                                                        <div class="small text-muted">
                                                            Paciente: {{ getPatientName(cama) }}
                                                        </div>
                                                    </div>
                                                    <i class="fas fa-arrow-right"></i>
                                                </div>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Cama Destino -->
                            <div class="col-md-6">
                                <div class="card h-100 border-success">
                                    <div class="card-header bg-success text-white">
                                        <h5 class="mb-0">Cama Destino</h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="mb-3">
                                            <label class="form-label">Buscar Cama Disponible</label>
                                            <div class="input-group">
                                                <span class="input-group-text">
                                                    <i class="fas fa-search"></i>
                                                </span>
                                                <input type="text" class="form-control" v-model="searchDestination" 
                                                       placeholder="Buscar por código o servicio...">
                                            </div>
                                        </div>
                                        
                                        <div class="list-group" style="max-height: 300px; overflow-y: auto;">
                                            <button v-for="cama in filteredAvailableBeds" :key="cama.id"
                                                    class="list-group-item list-group-item-action"
                                                    :class="{ 'active': selectedDestinationBed?.id === cama.id }"
                                                    @click="selectDestinationBed(cama)">
                                                <div class="d-flex justify-content-between align-items-center">
                                                    <div>
                                                        <strong>{{ cama.codcama }}</strong> - {{ cama.servicio?.nombre }}
                                                        <div class="small text-muted">
                                                            {{ cama.ups?.nombre }}
                                                        </div>
                                                    </div>
                                                    <span :class="`badge ${getEstadoBadge(cama.estado?.descripcion)}`">
                                                        {{ cama.estado?.descripcion }}
                                                    </span>
                                                </div>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Detalles de Transferencia -->
                        <div class="row mt-4" v-if="selectedOriginBed && selectedDestinationBed">
                            <div class="col-md-12">
                                <div class="card border-info">
                                    <div class="card-header bg-info text-white">
                                        <h5 class="mb-0">Detalles de Transferencia</h5>
                                    </div>
                                    <div class="card-body">
                                        <div class="row">
                                            <div class="col-md-6">
                                                <h6 class="text-primary">Origen</h6>
                                                <p>
                                                    <strong>Cama:</strong> {{ selectedOriginBed.codcama }}<br>
                                                    <strong>Servicio:</strong> {{ selectedOriginBed.servicio?.nombre }}<br>
                                                    <strong>UPS:</strong> {{ selectedOriginBed.ups?.nombre }}<br>
                                                    <strong>Paciente:</strong> {{ getPatientName(selectedOriginBed) }}
                                                </p>
                                            </div>
                                            <div class="col-md-6">
                                                <h6 class="text-success">Destino</h6>
                                                <p>
                                                    <strong>Cama:</strong> {{ selectedDestinationBed.codcama }}<br>
                                                    <strong>Servicio:</strong> {{ selectedDestinationBed.servicio?.nombre }}<br>
                                                    <strong>UPS:</strong> {{ selectedDestinationBed.ups?.nombre }}
                                                </p>
                                            </div>
                                        </div>
                                        
                                        <div class="mb-3">
                                            <label class="form-label">Motivo de Transferencia</label>
                                            <textarea class="form-control" v-model="transferReason" 
                                                      rows="3" placeholder="Describa el motivo de la transferencia..."></textarea>
                                        </div>
                                        
                                        <div class="d-flex justify-content-end">
                                            <button class="btn btn-primary" @click="confirmTransfer" 
                                                    :disabled="!transferReason">
                                                <i class="fas fa-exchange-alt me-2"></i>
                                                Confirmar Transferencia
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Modal de Confirmación -->
        <div v-if="showConfirmationModal" class="modal-backdrop fade show"></div>
        <div v-if="showConfirmationModal" class="modal fade show d-block">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title">Confirmar Transferencia</h5>
                        <button type="button" class="btn-close btn-close-white" @click="showConfirmationModal = false"></button>
                    </div>
                    <div class="modal-body">
                        <p>¿Está seguro que desea transferir al paciente desde la cama <strong>{{ selectedOriginBed?.codcama }}</strong> 
                        a la cama <strong>{{ selectedDestinationBed?.codcama }}</strong>?</p>
                        <p><strong>Motivo:</strong> {{ transferReason }}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" @click="showConfirmationModal = false">Cancelar</button>
                        <button type="button" class="btn btn-primary" @click="executeTransfer">Confirmar</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/components/services/auth_axios'
import { useToast } from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-sugar.css'

const toast = useToast()

// Datos
const camas = ref([])
const ocupaciones = ref([])
const selectedOriginBed = ref(null)
const selectedDestinationBed = ref(null)
const transferReason = ref('')
const searchOrigin = ref('')
const searchDestination = ref('')
const showConfirmationModal = ref(false)

// Obtener datos iniciales
onMounted(async () => {
    try {
        const ipress = JSON.parse(localStorage.getItem('user_ipress'))
        if (!ipress) return
        
        const [camasRes, ocupacionesRes] = await Promise.all([
            api.get(`cama/?ipress=${ipress.id}`),
            api.get('ocupacion-cama/?fecha_salida__isnull=true')
        ])
        
        camas.value = camasRes.data
        ocupaciones.value = ocupacionesRes.data
    } catch (error) {
        console.error('Error al cargar datos:', error)
        toast.error('Error al cargar los datos de camas y ocupaciones', { position: 'top-right' })
    }
})

// Obtener nombre del paciente para una cama
function getPatientName(cama) {
    const ocupacion = ocupaciones.value.find(o => o.cama.id === cama.id)
    if (!ocupacion || !ocupacion.paciente) return 'Sin paciente'
    return `${ocupacion.paciente.apellidos}, ${ocupacion.paciente.nombres}`
}

// Filtrar camas ocupadas
const filteredOccupiedBeds = computed(() => {
    const occupiedBedIds = ocupaciones.value.map(o => o.cama.id)
    let beds = camas.value.filter(c => occupiedBedIds.includes(c.id))
    
    if (searchOrigin.value) {
        const searchTerm = searchOrigin.value.toLowerCase()
        beds = beds.filter(c => 
            c.codcama.toLowerCase().includes(searchTerm) || 
            getPatientName(c).toLowerCase().includes(searchTerm)
        )
    }
    
    return beds
})

// Filtrar camas disponibles
const filteredAvailableBeds = computed(() => {
    const occupiedBedIds = ocupaciones.value.map(o => o.cama.id)
    let beds = camas.value.filter(c => !occupiedBedIds.includes(c.id))
    
    if (searchDestination.value) {
        const searchTerm = searchDestination.value.toLowerCase()
        beds = beds.filter(c => 
            c.codcama.toLowerCase().includes(searchTerm) || 
            c.servicio?.nombre.toLowerCase().includes(searchTerm))
    }
    
    // Si hay una cama origen seleccionada, filtrar por mismo servicio
    if (selectedOriginBed.value) {
        beds = beds.filter(c => 
            c.servicio?.id === selectedOriginBed.value.servicio?.id)
    }
    
    return beds
})

// Seleccionar camas
function selectOriginBed(cama) {
    selectedOriginBed.value = cama
    // Resetear destino si no es compatible
    if (selectedDestinationBed.value && 
        selectedDestinationBed.value.servicio?.id !== cama.servicio?.id) {
        selectedDestinationBed.value = null
    }
}

function selectDestinationBed(cama) {
    selectedDestinationBed.value = cama
}

// Confirmar transferencia
function confirmTransfer() {
    if (!selectedOriginBed.value || !selectedDestinationBed.value || !transferReason.value) {
        toast.warning('Complete todos los campos para la transferencia', { position: 'top-right' })
        return
    }
    
    showConfirmationModal.value = true
}

// Ejecutar transferencia
async function executeTransfer() {
    try {
        const response = await api.post(`cama/${selectedOriginBed.value.id}/transferir/`, {
            cama_destino_id: selectedDestinationBed.value.id,
            motivo: transferReason.value
        })
        
        toast.success('Transferencia realizada con éxito', { position: 'top-right' })
        
        // Actualizar datos
        const [camasRes, ocupacionesRes] = await Promise.all([
            api.get(`cama/?ipress=${JSON.parse(localStorage.getItem('user_ipress')).id}`),
            api.get('ocupacion-cama/?fecha_salida__isnull=true')
        ])
        
        camas.value = camasRes.data
        ocupaciones.value = ocupacionesRes.data
        
        // Resetear selección
        selectedOriginBed.value = null
        selectedDestinationBed.value = null
        transferReason.value = ''
        showConfirmationModal.value = false
    } catch (error) {
        console.error('Error en transferencia:', error)
        toast.error('Error al realizar la transferencia', { position: 'top-right' })
    }
}

// Función auxiliar para estilos de estado
function getEstadoBadge(estadoDescripcion) {
    if (!estadoDescripcion) return 'bg-secondary'
    const estadoLower = estadoDescripcion.toLowerCase()
    if (estadoLower.includes('disponible')) return 'bg-success'
    if (estadoLower.includes('ocupada')) return 'bg-danger'
    if (estadoLower.includes('manten')) return 'bg-warning'
    return 'bg-secondary'
}
</script>

<style scoped>
.list-group-item.active {
    background-color: #0d6efd;
    border-color: #0d6efd;
}
.card {
    transition: all 0.3s ease;
}
.card:hover {
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}
</style>