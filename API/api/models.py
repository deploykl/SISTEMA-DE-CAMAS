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
    prefijo = models.CharField(max_length=10, unique=True, verbose_name="Prefijo para código")

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"

    def __str__(self):
        return self.nombre
    
class Ipress(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="IdIpress") 
    codigo = models.CharField(max_length=255, unique=True, verbose_name="Código Ipress")  
    descripcion = models.CharField(max_length=255, unique=True, verbose_name="Descripción")  
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='ipress_registradas'
    )
    
    class Meta:
        verbose_name = "Ipress"
        verbose_name_plural = "Ipress"
        ordering = ["descripcion"]

    def __str__(self):
        return str(self.descripcion)  
    
class Cama(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="IdCama") 
    codcama = models.CharField(max_length=255, verbose_name="Código de Cama")  
    tipocama = models.ForeignKey(TipoCama, on_delete=models.CASCADE, related_name='camas', verbose_name="Tipo de Cama")
    ups = models.ForeignKey(UPS, on_delete=models.CASCADE, related_name='camas', verbose_name="UPS")
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='camas', verbose_name="Servicio")
    estado = models.ForeignKey(EstadoCama, on_delete=models.CASCADE, related_name='camas', verbose_name="Estado de Cama")
    ipress = models.ForeignKey(Ipress, on_delete=models.CASCADE, related_name='camas', verbose_name="Ipress")
    
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    
    class Meta:
        verbose_name = "Cama"
        verbose_name_plural = "Camas"
        ordering = ["codcama"]
        unique_together = ('codcama', 'ipress')

    def __str__(self):
        return f"{self.codcama} ({self.tipocama}, {self.estado})"
    
class Paciente(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="IdPaciente")
    documento_identidad = models.CharField(max_length=20, unique=True, verbose_name="DNI/CE")
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')])
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pacientes_registrados')
    
    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ["apellidos", "nombres"]

    def __str__(self):
        return f"{self.apellidos}, {self.nombres} ({self.documento_identidad})"
    
class Ingreso(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="IdIngreso")
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='ingresos')
    cama = models.ForeignKey(Cama, on_delete=models.CASCADE, related_name='ingresos')
    fecha_ingreso = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Ingreso")
    fecha_alta = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de Alta")
    diagnostico = models.TextField(verbose_name="Diagnóstico Principal")
    medico_tratante = models.CharField(max_length=255, verbose_name="Médico Tratante")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ingresos_registrados')
    
    class Meta:
        verbose_name = "Ingreso"
        verbose_name_plural = "Ingresos"
        ordering = ["-fecha_ingreso"]

    def __str__(self):
        return f"Ingreso {self.id} - {self.paciente}"

    def save(self, *args, **kwargs):
        # Al crear un ingreso, actualizar el estado de la cama a "Ocupado"
        if not self.pk:  # Solo si es un nuevo ingreso
            estado_ocupado = EstadoCama.objects.get(descripcion__icontains='Ocupada')
            self.cama.estado = estado_ocupado
            self.cama.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Al dar de alta, actualizar el estado de la cama a "Disponible"
        estado_disponible = EstadoCama.objects.get(descripcion__icontains='Disponible')
        self.cama.estado = estado_disponible
        self.cama.save()
        super().delete(*args, **kwargs)