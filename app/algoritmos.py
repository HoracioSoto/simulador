import random

from app.models import *


data = {
    'CPU': {
        'procesos': [],
        'ttime': 0
    },
    'ES': {
        'procesos': [],
        'ttime': 0
    },
    'recursos': range(1)
}

classes = [
    'primary', 'secondary', 'success', 'danger',
    'warning', 'info', 'light', 'dark', 'white',
]


def run_fcfs(simulacion, procesos):
    # inicializamos variables
    __fcfs_init(procesos)
    cpu_time = 0
    cpu_idx = 0
    # es_time = 0
    # Traemos los procesos ordenamos por ta (para este algoritmo)
    p_ords = __fcfs_order(Proceso.objects.filter(simulacion=simulacion).order_by('tiempo_arribo'))
    print(p_ords)

    # Si el primer proceso no tiene ta = 0 agregamos
    if p_ords[0]['ta'] != 0:
        data['CPU']['procesos'].append({
            'pid': None,
            'label': '',
            'start': 0,
            'time': p_ords[0]['ta'],
            'end': p_ords[0]['ta'],
            'class': 'bg-none',
            'percent': format(p_ords[0]['ta'] / data['CPU']['ttime'] * 100, '.2f')
        })
        cpu_time += p_ords[0]['ta']

    # Agregamos el primer proceso
    cpu_tactual = p_ords[0]['cpu'].pop(cpu_idx)
    data['CPU']['procesos'].append({
        'pid': p_ords[0]['pid'],
        'label': p_ords[0]['desc'],
        'start': p_ords[0]['ta'],
        'end': p_ords[0]['ta'] + cpu_tactual,
        'time': cpu_tactual,
        'class': p_ords[0]['class'],
        'percent': format(cpu_tactual / data['CPU']['ttime'] * 100, '.2f')
    })
    cpu_time += cpu_tactual
    for i in range(1, len(p_ords)):
        if p_ords[i]['alive'] and len(p_ords[i]['cpu']):
            # Chequear si no hay espacios entre el ultimo proceso y el que viene
            if data['CPU']['procesos'][-1]['end'] < p_ords[i]['ta']:
                cpu_tactual = p_ords[i]['ta'] - data['CPU']['procesos'][-1]['end']
                print(cpu_tactual)
                data['CPU']['procesos'].append({
                    'pid': None,
                    'label': '',
                    'start': data['CPU']['procesos'][-1]['end'],
                    'time': cpu_tactual,
                    'end': data['CPU']['procesos'][-1]['end'] + cpu_tactual,
                    'class': 'bg-none',
                    'percent': format(cpu_tactual / data['CPU']['ttime'] * 100, '.2f')
                })
                cpu_time += cpu_tactual
            cpu_tactual = p_ords[i]['cpu'].pop(cpu_idx)
            data['CPU']['procesos'].append({
                'pid': p_ords[i]['pid'],
                'label': p_ords[i]['desc'],
                'start': data['CPU']['procesos'][-1]['end'],
                'time': cpu_tactual,
                'end': data['CPU']['procesos'][-1]['end'] + cpu_tactual,
                'class': p_ords[i]['class'],
                'percent': format(cpu_tactual / data['CPU']['ttime'] * 100, '.2f')
            })
            cpu_time += cpu_tactual
    cpu_idx += 1

    return data


def __fcfs_init(procesos):
    # Iteramos por primera vez todos los procesos para determinar
    # la cantidad de ráfagas máxima de recursos, tiempo total de cpu y de e/s
    rafagas = 1
    data['CPU']['ttime'] = 0
    data['ES']['ttime'] = 0
    for proc in procesos:
        proc_recursos = proc.get_recursos()
        for idx in range(len(proc_recursos)):
            if not idx % 2:
                data['CPU']['ttime'] += int(proc_recursos[idx])
            else:
                data['ES']['ttime'] += int(proc_recursos[idx])
        if len(proc_recursos) > rafagas:
            rafagas = len(proc_recursos)
    data['recursos'] = range(rafagas)


def __fcfs_order(procesos):
    # Ordenamos y parseamos los procesos
    proc_ord = []
    for proc in procesos:
        proc_parser = {
            'pid': proc.simulacion_pid,
            'desc': proc.descripcion,
            'ta': int(proc.tiempo_arribo),
            'cpu': [],
            'es': [],
            'alive': True,
            'class': classes.pop(random.randrange(len(classes)))
        }
        proc_recursos = proc.get_recursos()
        for idx in range(len(proc_recursos)):
            if not idx % 2:
                proc_parser['cpu'].append(int(proc_recursos[idx]))
            else:
                proc_parser['es'].append(int(proc_recursos[idx]))
        proc_ord.append(proc_parser)
    return proc_ord


def run_sjf():
    return {}


def run_round_robin():
    return {}
