from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from app.models import *
from app.algoritmos import *


@login_required(login_url='/admin/login/')
def index(request):
    return render(request, 'app/home.html', {})


@login_required(login_url='/admin/login/')
@require_POST
def guardar_simulacion(request):
    sim = Simulacion(
        algoritmo_planificacion=request.POST.get('algoritmo'),
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
    return redirect('simulacion', id=4)


@login_required(login_url='/admin/login/')
def simulacion(request, id):
    simulacion = get_object_or_404(Simulacion, id=id)
    procesos = Proceso.objects.filter(simulacion=simulacion).order_by('simulacion_pid')
    data = {
        'CPU': {
            'procesos': [
                {'pid': 1, 'label': 'proc1', 'start': 0, 'time': 100, 'end': 100,'class': 'bg-info', 'percent': format(100/750*100, '.2f')},
                {'pid': None, 'label': '', 'start': 100, 'time': 50, 'end': 150,'class': 'bg-none', 'percent': format(50/750*100, '.2f')},
                {'pid': 2, 'label': 'proc2', 'start': 150, 'time': 150, 'end': 300,'class': 'bg-success', 'percent': format(150/750*100, '.2f')},
                {'pid': 3, 'label': 'proc3', 'start': 300, 'time': 50, 'end': 350,'class': 'bg-warning', 'percent': format(50/750*100, '.2f')},
                {'pid': 1, 'label': 'proc1', 'start': 350, 'time': 100, 'end': 450,'class': 'bg-info', 'percent': format(100/750*100, '.2f')},
                {'pid': 4, 'label': 'proc4', 'start': 450, 'time': 50, 'end': 500,'class': 'bg-primary', 'percent': format(50/750*100, '.2f')},
                {'pid': 2, 'label': 'proc2', 'start': 500, 'time': 50, 'end': 550,'class': 'bg-success', 'percent': format(50/750*100, '.2f')},
                {'pid': 3, 'label': 'proc3', 'start': 550, 'time': 150, 'end': 700,'class': 'bg-warning', 'percent': format(150/750*100, '.2f')},
                {'pid': 4, 'label': 'proc4', 'start': 700, 'time': 50, 'end': 750,'class': 'bg-primary', 'percent': format(50/750*100, '.2f')}
            ],
            'total_time': 750
        },
        'ES': {
            'procesos': [
                {'pid': None, 'label': '', 'start': 0, 'time': 100, 'end': 100, 'class': 'bg-none', 'percent': format(100/750*100, '.2f')},
                {'pid': 1, 'label': 'proc1', 'start': 100, 'time': 150, 'end': 250, 'class': 'bg-info', 'percent': format(150/750*100, '.2f')},
                {'pid': None, 'label': '', 'start': 250, 'time': 50, 'end': 300, 'class': 'bg-none', 'percent': format(50/750*100, '.2f')},
                {'pid': 2, 'label': 'proc2', 'start': 300, 'time': 200, 'end': 500, 'class': 'bg-success', 'percent': format(200/750*100, '.2f')},
                {'pid': 3, 'label': 'proc3', 'start': 500, 'time': 50, 'end': 550, 'class': 'bg-warning', 'percent': format(50/750*100, '.2f')},
                {'pid': 4, 'label': 'proc4', 'start': 550, 'time': 50, 'end': 600, 'class': 'bg-primary', 'percent': format(50/750*100, '.2f')},
                {'pid': None, 'label': '', 'start': 600, 'time': 150, 'end': 750, 'class': 'bg-none', 'percent': format(150/750*100, '.2f')}
            ],
            'total_time': 600
        },
        'recursos': range(5)
    }
    if simulacion.algoritmo_planificacion == 'FCFS':
        result = run_fcfs(simulacion, procesos)
    print(result)
    return render(request, 'app/results.html', {
        'data': data,
        'simulacion': simulacion,
        'procesos': procesos
    })
