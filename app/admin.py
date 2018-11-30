from django.contrib import admin
from .models import *


class ProcesoInline(admin.TabularInline):
    model = Proceso
    max_num = 0
    fields = (
        'simulacion_pid',
        'descripcion',
        'tiempo_arribo',
        'tiempo_recursos',
        'size'
    )


class MemoriaInline(admin.TabularInline):
    model = Memoria
    max_num = 1
    fields = (
        'size',
        'esquema',
        'algoritmo_colocacion',
        'particiones'
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
        MemoriaInline,
        ProcesoInline,
    ]


class ProcesoAdmin(admin.ModelAdmin):
    list_display = (
        'simulacion',
        'simulacion_pid',
        'descripcion',
        'tiempo_arribo',
        'tiempo_recursos',
        'size'
    )
    search_fields = (
        'simulacion__id',
        'simulacion__algoritmo_planificacion',
    )


class MemoriaAdmin(admin.ModelAdmin):
    list_display = (
        'size',
        'esquema',
        'algoritmo_colocacion',
        'particiones'
    )
    search_fields = (
        'simulacion__id',
        'simulacion__algoritmo_planificacion',
    )


admin.site.register(Memoria, MemoriaAdmin)
admin.site.register(Simulacion, SimulacionAdmin)
admin.site.register(Proceso, ProcesoAdmin)
