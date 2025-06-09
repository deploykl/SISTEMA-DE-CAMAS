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
    class Meta:
        model = Cama
        fields = '__all__'
        extra_kwargs = {
            'codcama': {'read_only': True},  # Hacemos que el código sea de solo lectura
            'tipocama': {'required': True},
            'servicio': {'required': True},
            'ups': {'required': True},
            'estado': {'required': True},
            'ipress': {'required': True}
        }

    def create(self, validated_data):
        servicio = validated_data['servicio']
        ipress = validated_data['ipress']

        # Obtener todas las camas del mismo servicio en la misma IPRESS
        camas_existentes = Cama.objects.filter(
            servicio=servicio,
            ipress=ipress
        ).values_list('codcama', flat=True)

        # Extraer números existentes
        numeros_existentes = []
        for codigo in camas_existentes:
            try:
                numero = int(codigo.split('-')[1])
                numeros_existentes.append(numero)
            except (IndexError, ValueError):
                continue
            
        # Encontrar el siguiente número disponible
        siguiente_numero = 1
        if numeros_existentes:
            max_numero = max(numeros_existentes)
            # Buscar el primer hueco disponible
            for i in range(1, max_numero + 2):
                if i not in numeros_existentes:
                    siguiente_numero = i
                    break
                
        # Formatear el nuevo código
        nuevo_codigo = f"{servicio.prefijo}-{siguiente_numero:03d}"
        validated_data['codcama'] = nuevo_codigo

        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tipocama'] = TipoCamaSerializer(instance.tipocama).data
        representation['servicio'] = ServicioSerializer(instance.servicio).data
        representation['ups'] = UPSViewSerializer(instance.ups).data
        representation['estado'] = EstadoCamaSerializer(instance.estado).data
        representation['ipress'] = IpressSerializer(instance.ipress).data
        return representation
    
class UserSerializer(serializers.ModelSerializer):
    has_ipress = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_superuser', 'is_staff', 'has_ipress']

    def get_has_ipress(self, obj):
        return Ipress.objects.filter(usuario=obj).exists()
    
    
class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'

class OcupacionCamaSerializer(serializers.ModelSerializer):
    paciente = PacienteSerializer()
    cama = CamaSerializer()
    
    class Meta:
        model = OcupacionCama
        fields = '__all__'
        read_only_fields = ('fecha_ingreso', 'usuario_registro')

class TransferenciaCamaSerializer(serializers.ModelSerializer):
    ocupacion_origen = OcupacionCamaSerializer()
    cama_destino = CamaSerializer()
    
    class Meta:
        model = TransferenciaCama
        fields = '__all__'
        read_only_fields = ('fecha_transferencia', 'usuario')