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
from django_filters.rest_framework import DjangoFilterBackend  # type: ignore
from rest_framework.filters import OrderingFilter

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
        # Asigna automáticamente el usuario actual
        serializer.save(usuario=self.request.user)
        
class CamaViewSet(viewsets.ModelViewSet):
    serializer_class = CamaSerializer
    permission_classes = [IsAuthenticated]  # Ajusta los permisos según necesites

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
            'ipress': IpressSerializer(ipress).data if ipress else None  # Añadir datos de IPRESS si existe
        }

        return Response(user_data, status=status.HTTP_200_OK)



class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Crea un objeto RefreshToken a partir del token recibido
            token = RefreshToken(refresh_token)
            # Añade el token a la lista negra
            token.blacklist()
            return Response({"detail": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except InvalidToken:
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)