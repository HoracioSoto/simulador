from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from app.models import *
from app.fcfs import *
from app.sjf import *
from app.rr import *


@login_required(login_url='/admin/login/')
def index(request):
    return render(request, 'app/home.html', {})


@login_required(login_url='/admin/login/')
@require_POST
def guardar_simulacion(request):
    sim = Simulacion(
        algoritmo_planificacion=request.POST.get('algoritmo'),
        quantum=request.POST.get('quantum'),
        usuario=request.user
    )
    sim.save()

    mem = request.POST.get('memoria_tipo')
    m_parts = int(request.POST.get('partes'))

    if mem == 'pf-best-fit':
        esquema = 'particion-fija'
        algoritmo = 'best-fit'
        size = int(request.POST.get('memoria'))
        parts = ','.join([str(int(size / m_parts)) for i in range(m_parts)])
    if mem == 'pf-first-fit':
        esquema = 'particion-fija'
        algoritmo = 'first-fit'
        size = int(request.POST.get('memoria'))
        parts = ','.join([str(int(size / m_parts)) for i in range(m_parts)])
    if mem == 'pv-worst-fit':
        esquema = 'particion-variable'
        algoritmo = 'worst-fit'
        parts = request.POST.get('partes_variables').strip()
        size = 0
        for x in parts.split(','):
            size += int(x)
    if mem == 'pv-first-fit':
        esquema = 'particion-variable'
        algoritmo = 'first-fit'
        parts = request.POST.get('partes_variables').strip()
        size = 0
        for x in parts.split(','):
            size += int(x)

    memoria = Memoria(
        size=size,
        esquema=esquema,
        algoritmo_colocacion=algoritmo,
        simulacion=sim,
        particiones=parts
    )
    memoria.save()

    for proceso in request.POST.getlist('procesos'):
        data = proceso.split('-')
        new_process = Proceso(
            descripcion=data[1].strip(),
            tiempo_arribo=data[2],
            tiempo_recursos=data[3].strip(),
            simulacion_pid=data[0],
            simulacion=sim,
            size=data[4]
        )
        new_process.save()
    return redirect('simulacion', id=sim.id)


@login_required(login_url='/admin/login/')
def simulacion(request, id):
    sim = get_object_or_404(Simulacion, id=id)
    procs = Proceso.objects.filter(simulacion=sim).order_by('simulacion_pid')
    memoria = Memoria.objects.get(simulacion=sim)
    if sim.algoritmo_planificacion == 'FCFS':
        data = run_fcfs(sim, procs)
    if sim.algoritmo_planificacion == 'SJF':
        data = run_sjf(sim, procs)
    if sim.algoritmo_planificacion == 'RR':
        data = run_rr(sim, procs)

    if memoria.particiones:
        particiones = [int(x) for x in memoria.particiones.split(',')]
        for i in range(len(particiones)):
            if i == 0:
                start = 0
            else:
                start = particiones[i - 1]['end']
            particiones[i] = {
                'start': start,
                'size': particiones[i],
                'end': start + particiones[i],
                'percent': format(particiones[i] / memoria.size * 100, '.2f')
            }
    else:
        particiones = []

    return render(request, 'app/results.html', {
        'data': data,
        'simulacion': sim,
        'memoria': memoria,
        'particiones': particiones,
        'tot_part': len(particiones),
        'procesos': procs
    })


@login_required(login_url='/admin/login/')
def simulaciones(request):
    return render(request, 'app/simulaciones.html', {
        'simulaciones': Simulacion.objects.all()
    })
