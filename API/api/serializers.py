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
    estado = EstadoCamaSerializer(read_only=True)
    ingreso = serializers.SerializerMethodField()  # Añade este campo
    tipocama = TipoCamaSerializer()  # Serializador completo en lugar de StringRelatedField
    servicio = ServicioSerializer()  # Serializador completo
    ups = UPSViewSerializer()       # Serializador completo
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
        ingreso = obj.ingresos.filter(fecha_alta__isnull=True).first()
        if not ingreso:
            return None

        paciente_data = None
        if hasattr(ingreso, 'paciente') and ingreso.paciente:
            paciente_data = {
                'id': ingreso.paciente.id,
                'documento': ingreso.paciente.documento_identidad,
                'nombres': ingreso.paciente.nombres,
                'apellidos': ingreso.paciente.apellidos,
                'fecha_nacimiento': ingreso.paciente.fecha_nacimiento,
                'genero': ingreso.paciente.genero
            }

        return {
            'id': ingreso.id,
            'fecha_ingreso': ingreso.fecha_ingreso,
            'diagnostico': ingreso.diagnostico,
            'medico_tratante': ingreso.medico_tratante,
            'observaciones': ingreso.observaciones,
            'paciente': paciente_data
        }

    def create(self, validated_data):
        try:
            servicio = validated_data.get('servicio')
            ipress = validated_data.get('ipress')
            
            if not servicio or not ipress:
                raise serializers.ValidationError("Servicio e IPRESS son requeridos para generar el código de cama")
                
            # Generar código de cama
            camas_existentes = Cama.objects.filter(
                servicio=servicio,
                ipress=ipress
            )
            
            siguiente_numero = 1
            if camas_existentes.exists():
                # Extraer números existentes
                numeros = []
                for cama in camas_existentes:
                    try:
                        num = int(cama.codcama.split('-')[1])
                        numeros.append(num)
                    except (IndexError, ValueError):
                        continue
                    
                if numeros:
                    max_num = max(numeros)
                    # Buscar huecos en la numeración
                    for i in range(1, max_num + 2):
                        if i not in numeros:
                            siguiente_numero = i
                            break
                    else:
                        siguiente_numero = max_num + 1
            
            validated_data['codcama'] = f"{servicio.prefijo}-{siguiente_numero:03d}"
            
            return super().create(validated_data)
            
        except Exception as e:
            raise serializers.ValidationError(f"Error al generar código de cama: {str(e)}")

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
    cama = serializers.PrimaryKeyRelatedField(queryset=Cama.objects.all())  # Cambiado a escribible

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