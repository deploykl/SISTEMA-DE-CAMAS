from api.models import *
from rest_framework import serializers

class TipoCamaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoCama
        fields = ['__all__']

class EstadoCamaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoCama
        fields = ['__all__']

class IpressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ipress
        fields = ['__all__']  

class UPSViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = UPS
        fields = ['__all__']

