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
            'usuario': {'read_only': True}
        }

class UPSViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = UPS
        fields = '__all__'

class CamaSerializer(serializers.ModelSerializer):
    ingreso = serializers.SerializerMethodField()  # Añade este campo
    class Meta:
        model = Cama
        fields = '__all__'
        extra_kwargs = {
            'codcama': {'read_only': True},
            'tipocama': {'required': True},
            'servicio': {'required': True},
            'ups': {'required': True},
            'estado': {'required': True},
            'ipress': {'required': True}
        }
        
    def get_ingreso(self, obj):
        # Obtiene el ingreso activo (sin fecha de alta) para esta cama
        ingreso = obj.ingresos.filter(fecha_alta__isnull=True).first()
        if ingreso:
            return {
                'id': ingreso.id,
                'fecha_ingreso': ingreso.fecha_ingreso,
                'diagnostico': ingreso.diagnostico,
                'medico_tratante': ingreso.medico_tratante,
                'observaciones': ingreso.observaciones,
                'paciente': {
                    'id': ingreso.paciente.id,
                    'documento': ingreso.paciente.documento_identidad,
                    'nombres': ingreso.paciente.nombres,
                    'apellidos': ingreso.paciente.apellidos,
                    'fecha_nacimiento': ingreso.paciente.fecha_nacimiento,
                    'genero': ingreso.paciente.genero
                }
            }
        return None
    
    def create(self, validated_data):
        servicio = validated_data['servicio']
        ipress = validated_data['ipress']

        camas_existentes = Cama.objects.filter(
            servicio=servicio,
            ipress=ipress
        ).values_list('codcama', flat=True)

        numeros_existentes = []
        for codigo in camas_existentes:
            try:
                numero = int(codigo.split('-')[1])
                numeros_existentes.append(numero)
            except (IndexError, ValueError):
                continue
            
        siguiente_numero = 1
        if numeros_existentes:
            max_numero = max(numeros_existentes)
            for i in range(1, max_numero + 2):
                if i not in numeros_existentes:
                    siguiente_numero = i
                    break
                
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
    
# En tu archivo serializers.py
class UserSerializer(serializers.ModelSerializer):
    has_ipress = serializers.SerializerMethodField()
    ipress = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_superuser', 'is_staff', 'has_ipress', 'ipress']

    def get_has_ipress(self, obj):
        return Ipress.objects.filter(usuario=obj).exists()

    def get_ipress(self, obj):
        ipress = Ipress.objects.filter(usuario=obj).first()
        if ipress:
            return IpressSerializer(ipress).data
        return None
    
class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'
        extra_kwargs = {
            'usuario': {'read_only': True}
        }

class IngresoSerializer(serializers.ModelSerializer):
    cama = CamaSerializer(read_only=True)  # Añadir esta línea

    class Meta:
        model = Ingreso
        fields = '__all__'
        extra_kwargs = {
            'paciente': {'required': True},
            'cama': {'required': True},
            'usuario': {'read_only': True},  # Cambiado a read_only
            'diagnostico': {'required': True},
            'medico_tratante': {'required': True},
        }

class CamaDisponibleSerializer(serializers.ModelSerializer):
    tipocama = serializers.StringRelatedField()
    servicio = serializers.StringRelatedField()
    ups = serializers.StringRelatedField()
    
    class Meta:
        model = Cama
        fields = ['id', 'codcama', 'tipocama', 'servicio', 'ups']