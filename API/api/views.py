from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.serializers import *
from api.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework_simplejwt.exceptions import InvalidToken
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from django.db.models import Q

@extend_schema_view(
    list=extend_schema(description="Lista todas las camas disponibles"),
    retrieve=extend_schema(description="Obtiene los detalles de una cama específica"),
)
class EstadoCamaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EstadoCama.objects.all().order_by('descripcion')
    serializer_class = EstadoCamaSerializer
    permission_classes = [AllowAny]

class TipoCamaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TipoCama.objects.all().order_by('descripcion')
    serializer_class = TipoCamaSerializer
    permission_classes = [AllowAny]

class UPSViewSet(viewsets.ModelViewSet):
    queryset = UPS.objects.all().order_by('nombre')
    serializer_class = UPSViewSerializer
    permission_classes = [IsAuthenticated]

class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all().order_by('nombre')
    serializer_class = ServicioSerializer
    permission_classes = [IsAuthenticated]
    
class IpressViewSet(viewsets.ModelViewSet):
    queryset = Ipress.objects.all()
    serializer_class = IpressSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Ipress.objects.all()
        return Ipress.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = ['documento_identidad', 'nombres', 'apellidos']
    filterset_fields = ['documento_identidad']  # Nuevo filtro exacto
    
    def get_queryset(self):
        # Filtra por usuario y permite búsqueda exacta por DNI
        documento = self.request.query_params.get('documento_identidad')
        queryset = Paciente.objects.filter(usuario=self.request.user)
        
        if documento:
            queryset = queryset.filter(documento_identidad=documento)
            
        return queryset.order_by('apellidos', 'nombres')

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=False, methods=['get'])
    def search(self, request):
        documento = request.query_params.get('documento', None)
        if documento:
            pacientes = self.get_queryset().filter(
                documento_identidad__iexact=documento
            )
            serializer = self.get_serializer(pacientes, many=True)
            return Response(serializer.data)
        return Response([], status=status.HTTP_200_OK)

class CamaViewSet(viewsets.ModelViewSet):
    serializer_class = CamaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def get_queryset(self):
        queryset = Cama.objects.filter(ipress__usuario=self.request.user)
        ipress_id = self.request.query_params.get('ipress')
        if ipress_id:
            queryset = queryset.filter(ipress_id=ipress_id)
        return queryset.order_by('codcama')

    def perform_create(self, serializer):
        ipress = Ipress.objects.get(usuario=self.request.user)
        serializer.save(ipress=ipress)

    @action(detail=False, methods=['get'])
    def por_ipress(self, request):
        ipress_id = request.query_params.get('ipress')
        if not ipress_id:
            return Response({'error': 'Se requiere el parámetro ipress'}, status=status.HTTP_400_BAD_REQUEST)
        
        camas = Cama.objects.filter(ipress_id=ipress_id).order_by('codcama')
        serializer = self.get_serializer(camas, many=True)
        return Response(serializer.data)

class IngresoViewSet(viewsets.ModelViewSet):
    queryset = Ingreso.objects.all()
    serializer_class = IngresoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return super().get_queryset().filter(
            usuario=self.request.user
        ).order_by('-fecha_ingreso')

    def perform_create(self, serializer):
        # Asignar automáticamente el usuario del token JWT
        serializer.save(usuario=self.request.user)
        
        # Actualizar estado de la cama a Ocupado
        cama = serializer.validated_data['cama']
        estado_ocupado = EstadoCama.objects.get(descripcion__icontains='Ocupada')
        cama.estado = estado_ocupado
        cama.save()

class CamaDisponibleList(ListAPIView):
    serializer_class = CamaDisponibleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        ipress_id = self.request.query_params.get('ipress', None)
        estado_disponible = EstadoCama.objects.get(descripcion='Disponible')  # exact match
        
        queryset = Cama.objects.filter(
            ipress_id=ipress_id,
            estado=estado_disponible,
            ipress__usuario=self.request.user
        ).select_related('tipocama', 'servicio', 'ups')
        
        return queryset

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'detail': 'Las credenciales de autenticación no se proveyeron.'}, 
                           status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(username=username).first()

        if user is None:
            return Response({'detail': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.check_password(password):
            return Response({'detail': 'Contraseña incorrecta'}, status=status.HTTP_401_UNAUTHORIZED)

        ipress = Ipress.objects.filter(usuario=user).first()
        has_ipress = ipress is not None

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        user_data = {
                    'access': access_token,
                    'refresh': str(refresh),
                    'has_ipress': has_ipress,
                    'ipress': IpressSerializer(ipress).data if ipress else None,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'is_superuser': user.is_superuser,
                        'is_staff': user.is_staff
                    }
                }

        return Response(user_data, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except InvalidToken:
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)