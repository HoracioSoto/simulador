from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from app.models import *
from app.fcfs import *
from app.sjf import *


@login_required(login_url='/admin/login/')
def index(request):
    return render(request, 'app/home.html', {})


@login_required(login_url='/admin/login/')
@require_POST
def guardar_simulacion(request):
    sim = Simulacion(
        algoritmo_planificacion=request.POST.get('algoritmo'),
        quantum=request.POST.get('quantum'),
        # memoria=Memoria.objects.get(id=1),
        usuario=request.user
    )
    sim.save()
    for proceso in request.POST.getlist('procesos'):
        data = proceso.split('-')
        new_process = Proceso(
            descripcion=data[1].strip(),
            tiempo_arribo=data[2],
            tiempo_recursos=data[3].strip(),
            simulacion_pid=data[0],
            simulacion=sim
        )
        new_process.save()
    return redirect('simulacion', id=sim.id)


@login_required(login_url='/admin/login/')
def simulacion(request, id):
    sim = get_object_or_404(Simulacion, id=id)
    procs = Proceso.objects.filter(simulacion=sim).order_by('simulacion_pid')
    if sim.algoritmo_planificacion == 'FCFS':
        data = run_fcfs(sim, procs)
    if sim.algoritmo_planificacion == 'SJF':
        data = run_sjf(sim, procs)
    if sim.algoritmo_planificacion == 'RR':
        data = run_sjf(sim, procs)
    return render(request, 'app/results.html', {
        'data': data,
        'simulacion': sim,
        'procesos': procs
    })


@login_required(login_url='/admin/login/')
def simulaciones(request):
    return render(request, 'app/simulaciones.html', {
        'simulaciones': Simulacion.objects.all()
    })
