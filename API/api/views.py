from django.shortcuts import render
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from api.serializers import *
from api.models import *

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

class UPSViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UPS.objects.all().order_by('nombre')
    serializer_class = UPSViewSerializer
    permission_classes = [AllowAny]

class IpressViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ipress.objects.all().order_by('descripcion')
    serializer_class = IpressSerializer
    permission_classes = [AllowAny]