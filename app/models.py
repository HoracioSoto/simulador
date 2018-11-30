from django.db import models
from django.contrib.auth.models import User


class Simulacion(models.Model):
    id = models.AutoField(primary_key=True)
    algoritmo_planificacion = models.CharField(max_length=30)
    quantum = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    model = 'Simulacion'

    class Meta:
        verbose_name = 'Simulación'
        verbose_name_plural = 'Simulaciones'

    def __str__(self):
        return '{} - {}'.format(self.id, self.algoritmo_planificacion)


class Memoria(models.Model):
    id = models.AutoField(primary_key=True)
    size = models.IntegerField(verbose_name='Tamaño (KB)')
    esquema = models.CharField(max_length=30,
                               verbose_name='Esquema')
    particiones = models.CharField(null=True, blank=True,
                                   verbose_name='Particiones',
                                   max_length=255)
    algoritmo_colocacion = models.CharField(max_length=30,
                                            verbose_name='Tipo')
    simulacion = models.ForeignKey(Simulacion,
                                   related_name='Memoria',
                                   verbose_name='Simulación',
                                   on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Memoria'
        verbose_name_plural = 'Memorias'

    def __str__(self):
        return str(self.id)


class Proceso(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(null=True, blank=True, max_length=255,
                                   default='')
    tiempo_arribo = models.IntegerField(verbose_name='Tiempo de arribo')
    tiempo_recursos = models.CharField(verbose_name='Tiempo de recursos',
                                       max_length=255)
    simulacion = models.ForeignKey(Simulacion,
                                   related_name='Procesos',
                                   verbose_name='Simulación',
                                   on_delete=models.CASCADE)
    simulacion_pid = models.IntegerField(verbose_name='PID')
    size = models.IntegerField(null=True, blank=True,
                               verbose_name='Tamaño (KB)')

    class Meta:
        verbose_name = 'Proceso'
        verbose_name_plural = 'Procesos'

    def __str__(self):
        return str(self.id)

    def get_recursos(self):
        return self.tiempo_recursos.split(',')
