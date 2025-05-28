from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Cama, HistoricoCama
import json

User = get_user_model()

@receiver(pre_save, sender=Cama)
def capturar_estado_anterior(sender, instance, **kwargs):
    if instance.pk:  # Solo si ya existe (no es creación)
        try:
            original = Cama.objects.get(pk=instance.pk)
            instance._estado_anterior = {
                'codcama': original.codcama,
                'tipocama_id': original.tipocama_id,
                'Ups_id': original.Ups_id,
                'estadocama_id': original.estadocama_id,
                'ipress_id': original.ipress_id,
            }
        except Cama.DoesNotExist:
            pass

@receiver(post_save, sender=Cama)
def registrar_historico(sender, instance, created, **kwargs):
    if created:
        cambio = "Creación de cama"
    else:
        cambio = "Actualización de cama"
        estado_anterior = getattr(instance, '_estado_anterior', None)
        
    # Obtener el usuario actual (requiere autenticación)
    usuario = None
    from django.contrib.auth import get_user
    try:
        usuario = get_user(kwargs.get('request', None))
    except:
        pass
    
    HistoricoCama.objects.create(
        cama=instance,
        usuario=usuario,
        cambio_realizado=cambio,
        estado_anterior=estado_anterior,
    )