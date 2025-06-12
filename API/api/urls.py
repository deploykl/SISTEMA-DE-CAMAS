from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView  # type: ignore
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView, TokenBlacklistView  # type: ignore
from api.views import *  # Importar las ViewSets
from .views import PacienteViewSet, IngresoViewSet
from api import views

app_name = "api"

router = DefaultRouter()

# Registrar las ViewSets directamente en el router principal
router.register(r'estado-cama', EstadoCamaViewSet)
router.register(r'tipo-cama', TipoCamaViewSet)
router.register(r'ups', UPSViewSet)
router.register(r'servicio', ServicioViewSet)
router.register(r'ipress', IpressViewSet)
router.register(r'cama', CamaViewSet, basename='cama')  # Nueva ruta para camas
router.register(r'pacientes', PacienteViewSet) 
router.register(r'ingresos', IngresoViewSet, basename='ingreso')

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path('token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('token/verify/', TokenVerifyView.as_view(), name="token_verify"),
    path('token/blacklist/', TokenBlacklistView.as_view(), name="token_blacklist"),
    
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('camas/disponibles/', CamaDisponibleList.as_view(), name='camas-disponibles'),

    path('', include(router.urls)),  # Incluye todas las rutas registradas en el router
]