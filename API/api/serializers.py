from api.models import *
from rest_framework import serializers

class TipoCamaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoCama
        fields = '__all__'

class EstadoCamaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoCama
        fields = '__all__'
        
class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = '__all__'
        
class IpressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ipress
        fields = '__all__'
        extra_kwargs = {
            'codigo': {'required': True},
            'descripcion': {'required': True},
            'usuario': {'read_only': True}  # Asegúrate que el usuario sea requerido
        }

class UPSViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = UPS
        fields = '__all__'

class CamaSerializer(serializers.ModelSerializer):
    tipocama = TipoCamaSerializer()
    servicio = ServicioSerializer()
    ups = UPSViewSerializer()
    estado = EstadoCamaSerializer()
    ipress = IpressSerializer()

    class Meta:
        model = Cama
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    has_ipress = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_superuser', 'is_staff', 'has_ipress']

    def get_has_ipress(self, obj):
        return Ipress.objects.filter(usuario=obj).exists()