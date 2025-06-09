from django.shortcuts import render
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from api.serializers import *
from api.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.db.models import Q
from django.utils import timezone

@extend_schema_view(
    list=extend_schema(description="Lista todas las camas disponibles"),
    retrieve=extend_schema(description="Obtiene los detalles de una cama específica"),
    create=extend_schema(description="Crea una o múltiples camas nuevas"),
    update=extend_schema(description="Actualiza una cama existente"),
    partial_update=extend_schema(description="Actualiza parcialmente una cama"),
    destroy=extend_schema(description="Elimina una cama"),
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
    ordering = ["id"]
    ordering_fields = "__all__"
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all().order_by('apellidos', 'nombres')
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    search_fields = ['documento_identidad', 'nombres', 'apellidos']

class OcupacionCamaViewSet(viewsets.ModelViewSet):
    queryset = OcupacionCama.objects.all().order_by('-fecha_ingreso')
    serializer_class = OcupacionCamaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    
    def perform_create(self, serializer):
        serializer.save(usuario_registro=self.request.user)

class TransferenciaCamaViewSet(viewsets.ModelViewSet):
    queryset = TransferenciaCama.objects.all().order_by('-fecha_transferencia')
    serializer_class = TransferenciaCamaSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

class CamaViewSet(viewsets.ModelViewSet):
    serializer_class = CamaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, OrderingFilter)

    def get_queryset(self):
        queryset = Cama.objects.all()
        ipress_id = self.request.query_params.get('ipress')
        if ipress_id:
            queryset = queryset.filter(ipress_id=ipress_id)
        return queryset.order_by('codcama')

    @action(detail=False, methods=['get'])
    def por_ipress(self, request):
        ipress_id = request.query_params.get('ipress')
        if not ipress_id:
            return Response({'error': 'Se requiere el parámetro ipress'}, status=status.HTTP_400_BAD_REQUEST)
        
        camas = Cama.objects.filter(ipress_id=ipress_id).order_by('codcama')
        serializer = self.get_serializer(camas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filtrar solo camas disponibles (no ocupadas)
        ocupadas_ids = OcupacionCama.objects.filter(
            fecha_salida__isnull=True
        ).values_list('cama_id', flat=True)
        
        queryset = queryset.exclude(id__in=ocupadas_ids)
        
        # Aplicar filtros adicionales
        servicio_id = request.query_params.get('servicio')
        if servicio_id:
            queryset = queryset.filter(servicio_id=servicio_id)
            
        ups_id = request.query_params.get('ups')
        if ups_id:
            queryset = queryset.filter(ups_id=ups_id)
            
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(codcama__icontains=search) |
                Q(servicio__nombre__icontains=search) |
                Q(ups__nombre__icontains=search)
            )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def transferir(self, request, pk=None):
        cama_origen = self.get_object()
        
        # Validar que la cama origen esté ocupada
        ocupacion_activa = OcupacionCama.objects.filter(
            cama=cama_origen, 
            fecha_salida__isnull=True
        ).first()
        
        if not ocupacion_activa:
            return Response(
                {"error": "La cama de origen no tiene un paciente asignado"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar datos de la transferencia
        cama_destino_id = request.data.get('cama_destino_id')
        if not cama_destino_id:
            return Response(
                {"error": "Debe especificar una cama de destino"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cama_destino = Cama.objects.get(pk=cama_destino_id)
        except Cama.DoesNotExist:
            return Response(
                {"error": "Cama de destino no encontrada"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validar que la cama destino esté disponible
        if OcupacionCama.objects.filter(cama=cama_destino, fecha_salida__isnull=True).exists():
            return Response(
                {"error": "La cama de destino ya está ocupada"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar compatibilidad de servicios
        if cama_origen.servicio != cama_destino.servicio:
            return Response(
                {"error": "No se puede transferir entre diferentes servicios"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Realizar la transferencia
        motivo = request.data.get('motivo', 'Transferencia de cama')
        
        try:
            # 1. Registrar salida de la cama origen
            ocupacion_activa.fecha_salida = timezone.now()
            ocupacion_activa.motivo_salida = motivo
            ocupacion_activa.save()
            
            # 2. Registrar ingreso en cama destino
            nueva_ocupacion = OcupacionCama.objects.create(
                cama=cama_destino,
                paciente=ocupacion_activa.paciente,
                motivo_ingreso=motivo,
                usuario_registro=request.user
            )
            
            # 3. Registrar la transferencia
            transferencia = TransferenciaCama.objects.create(
                ocupacion_origen=ocupacion_activa,
                cama_destino=cama_destino,
                motivo=motivo,
                usuario=request.user
            )
            
            # 4. Actualizar estados de las camas
            estado_ocupado = EstadoCama.objects.get(descripcion='Ocupada')
            estado_disponible = EstadoCama.objects.get(descripcion='Disponible')
            
            cama_origen.estado = estado_disponible
            cama_origen.save()
            
            cama_destino.estado = estado_ocupado
            cama_destino.save()
            
            return Response(
                TransferenciaCamaSerializer(transferencia).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'detail': 'Las credenciales de autenticación no se proveyeron.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(username=username).first()

        if user is None:
            return Response({'detail': 'Usuario no encontrado'}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.check_password(password):
            return Response({'detail': 'Contraseña incorrecta'}, status=status.HTTP_401_UNAUTHORIZED)

        # Verificar si el usuario tiene IPRESS y obtenerla
        ipress = Ipress.objects.filter(usuario=user).first()
        has_ipress = ipress is not None

        # Generar tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        user_data = {
            'access': access_token,
            'refresh': str(refresh),
            'has_ipress': has_ipress,
            'ipress': IpressSerializer(ipress).data if ipress else None
        }

        return Response(user_data, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [AllowAny]

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