from django.contrib import admin
from .models import *


class ProcesoInline(admin.TabularInline):
    model = Proceso
    max_num = 0
    fields = (
        'simulacion_pid',
        'descripcion',
        'tiempo_arribo',
        'tiempo_recursos'
    )


class SimulacionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'algoritmo_planificacion',
        'fecha_creacion',
        'usuario'
    )
    search_fields = (
        'id',
        'algoritmo_planificacion',
        'fecha_creacion',
        'usuario__username',
    )
    inlines = [
        ProcesoInline,
    ]


class ProcesoAdmin(admin.ModelAdmin):
    list_display = (
        'simulacion',
        'simulacion_pid',
        'descripcion',
        'tiempo_arribo',
        'tiempo_recursos'
    )
    search_fields = (
        'simulacion__id',
        'simulacion__algoritmo_planificacion',
    )


# admin.site.register(Memoria)
admin.site.register(Simulacion, SimulacionAdmin)
admin.site.register(Proceso, ProcesoAdmin)
