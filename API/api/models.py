from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class EstadoCama(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="IdEstadoCama")  
    descripcion = models.CharField(max_length=255, unique=True, verbose_name="Descripción")  

    class Meta:
        verbose_name = "EstadoCama"
        verbose_name_plural = "EstadoCamas"
        ordering = ["descripcion"]

    def __str__(self):
        return str(self.descripcion)  
    
class TipoCama(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="IdTipoCama")  
    descripcion = models.CharField(max_length=255, unique=True, verbose_name="Descripción")  

    class Meta:
        verbose_name = "TipoCama"
        verbose_name_plural = "TipoCamas"
        ordering = ["descripcion"]

    def __str__(self):
        return str(self.descripcion)  
    
class UPS(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="IdUps") 
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre UPS")

    class Meta:
        verbose_name = "Ups"
        verbose_name_plural = "Ups"
        ordering = ["nombre"]

    def __str__(self):
        return str(self.nombre)  
    
class Servicio(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="IdServicios") 
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre Servicio")
    # Ejemplo: "Adultos", "Neonatal", "Pediatría"

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"

    def __str__(self):
        return self.nombre
    
class Ipress(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="IdIpress") 
    codigo = models.CharField(max_length=255, unique=True, verbose_name="Código Ipress")  
    descripcion = models.CharField(max_length=255, unique=True, verbose_name="Descripción")  

    class Meta:
        verbose_name = "Ipress"
        verbose_name_plural = "Ipress"
        ordering = ["descripcion"]

    def __str__(self):
        return str(self.descripcion)  
    
class Cama(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="IdCama") 
    codcama = models.CharField(max_length=255,unique=True, verbose_name="Código de Cama")  
    tipocama = models.ForeignKey(TipoCama, on_delete=models.CASCADE, related_name='camas', verbose_name="Tipo de Cama")
    ups  = models.ForeignKey(UPS, on_delete=models.CASCADE, related_name='camas', verbose_name="UPS")
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='camas', verbose_name="Servicio")
    estado  = models.ForeignKey(EstadoCama, on_delete=models.CASCADE, related_name='camas', verbose_name="Estado de Cama")
    ipress = models.ForeignKey(Ipress, on_delete=models.CASCADE, related_name='camas', verbose_name="Ipress")
    
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    
    class Meta:
        verbose_name = "Cama"
        verbose_name_plural = "Camas"
        ordering = ["codcama"]  

    def __str__(self):
        return f"{self.codcama} ({self.tipocama}, {self.estado})"  # Incluye estado
    
