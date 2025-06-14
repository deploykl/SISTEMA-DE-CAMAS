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
    permission_classes = [AllowAny]

class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all().order_by('nombre')
    serializer_class = ServicioSerializer
    permission_classes = [AllowAny]
    
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
        
    @action(detail=True, methods=['post'])
    def transferir(self, request, pk=None):
        ingreso = self.get_object()
        nueva_cama_id = request.data.get('nueva_cama_id')
        
        if not nueva_cama_id:
            return Response({'error': 'Se requiere el ID de la nueva cama'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verificar que el ingreso pertenece al usuario
            if ingreso.usuario != request.user:
                return Response(
                    {'error': 'No tiene permisos para transferir este ingreso'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            nueva_cama = Cama.objects.get(id=nueva_cama_id)
            
            # Verificar que la nueva cama pertenece al mismo IPRESS
            if nueva_cama.ipress != ingreso.cama.ipress:
                return Response(
                    {'error': 'No se puede transferir a una cama de otro establecimiento'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Verificar que la cama destino está disponible
            if nueva_cama.estado.descripcion.lower() != 'disponible':
                return Response(
                    {'error': 'La cama destino no está disponible'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Realizar la transferencia
            ingreso.transferir_a_cama(nueva_cama, request.user)
            
            # Serializar los datos actualizados
            serializer = self.get_serializer(ingreso)
            return Response({
                'status': 'Transferencia exitosa',
                'data': serializer.data
            })
            
        except Cama.DoesNotExist:
            return Response({'error': 'Cama no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Error en la transferencia: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        cama = serializer.validated_data['cama']
        if cama.estado.descripcion != 'Disponible':
            raise serializers.ValidationError("La cama seleccionada no está disponible")

        # Rest of your existing code
        serializer.save(usuario=self.request.user)

        estado_ocupado = EstadoCama.objects.get(descripcion__icontains='Ocupada')
        cama.estado = estado_ocupado
        cama.save()

class CamaDisponibleList(ListAPIView):
    serializer_class = CamaDisponibleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        ipress_id = self.request.query_params.get('ipress')
        
        # Asegurarse de obtener el estado "Disponible" correctamente
        try:
            estado_disponible = EstadoCama.objects.get(descripcion__iexact='Disponible')
        except EstadoCama.DoesNotExist:
            estado_disponible = None
        
        queryset = Cama.objects.filter(
            ipress_id=ipress_id,
            ipress__usuario=self.request.user
        ).select_related('tipocama', 'servicio', 'ups', 'estado')
        
        # Filtrar solo camas disponibles si existe el estado
        if estado_disponible:
            queryset = queryset.filter(estado=estado_disponible)
        
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