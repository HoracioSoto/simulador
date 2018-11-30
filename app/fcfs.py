import random
import numpy as np

from app.models import *


def run_fcfs(simulacion, procesos):
    sets = {
        'cpu': {'time': 0, 'queue': [], 'count': 0},
        'es': {'time': 0, 'queue': [], 'count': 0},
        'max_total': 0, 'resources': range(5)
    }

    # Inicializamos el algoritmo
    __fcfs_init(procesos, sets)

    # Parseamos los procesos
    procesos_ord = __fcfs_parser_process(Proceso.objects.filter(simulacion=simulacion).order_by('tiempo_arribo', 'simulacion_pid'))

    sets['resources'] = range(sets['max_total'])

    # Ejecutamos hasta que se completen todas las ráfagas
    while sets['max_total']:
        # Tratamos el orden en las colas
        items_cpu = []
        items_es = []
        for i in range(len(procesos_ord)):
            if procesos_ord[i]['alive'] and len(procesos_ord[i]['cpu']):
                items_cpu.append([procesos_ord[i]['ta_cpu'], procesos_ord[i]['cpu'].pop(0), i])

        # Ordernando por idx 0
        # index 0 = ta
        # index 1 = ti
        # Index 2 = posicion del proceso
        items_cpu = sorted(items_cpu, key=lambda x: (x[0]))
        for p in items_cpu:
            # Chequear si no hay espacios entre el ultimo proceso y el que viene
            if len(sets['cpu']['queue']) and (sets['cpu']['queue'][-1]['end'] < p[0]):
                sets['cpu']['queue'].append({
                    'pid': None,
                    'label': '',
                    'start': sets['cpu']['queue'][-1]['end'],
                    'time': p[0] - sets['cpu']['queue'][-1]['end'],
                    'end': p[0],
                    'class': 'none',
                    'percent': p[0] - sets['cpu']['queue'][-1]['end']
                })
                sets['cpu']['time'] = p[0]
            # O si no hay nada antes
            if len(sets['cpu']['queue']) == 0 and p[0] !=0:
                sets['cpu']['queue'].append({
                    'pid': None,
                    'label': '',
                    'start': 0,
                    'time': p[0],
                    'end': p[0],
                    'class': 'none',
                    'percent': p[0]
                })
                sets['cpu']['time'] = p[0]
            # Agregamos el proceso a la cola de cpu
            sets['cpu']['queue'].append({
                'pid': procesos_ord[p[2]]['pid'],
                'label': procesos_ord[p[2]]['desc'],
                'start': sets['cpu']['time'],
                'time': p[1],
                'end': sets['cpu']['time'] + p[1],
                'class': procesos_ord[p[2]]['class'],
                'percent': p[1]
            })
            sets['cpu']['time'] += p[1]
            procesos_ord[p[2]]['ta_es'] = sets['cpu']['time']

            # Tratamos la cola de e/s
            if len(procesos_ord[p[2]]['es']):
                items_es.append([procesos_ord[p[2]]['ta_es'], procesos_ord[p[2]]['es'].pop(0), p[2]])
            else:
                procesos_ord[p[2]]['alive'] = False

        items_es = sorted(items_es, key=lambda x: (x[0]))
        for p in items_es:
            # Chequear si no hay espacios entre el ultimo proceso y el que viene
            if len(sets['es']['queue']) and (sets['es']['queue'][-1]['end'] < p[0]):
                sets['es']['queue'].append({
                    'pid': None,
                    'label': '',
                    'start': sets['es']['queue'][-1]['end'],
                    'time': p[0] - sets['es']['queue'][-1]['end'],
                    'end': p[0],
                    'class': 'none',
                    'percent': p[0] - sets['es']['queue'][-1]['end']
                })
                sets['es']['time'] = p[0]
            # O si no hay nada antes
            if len(sets['es']['queue']) == 0 and p[0] !=0:
                sets['es']['queue'].append({
                    'pid': None,
                    'label': '',
                    'start': 0,
                    'time': p[0],
                    'end': p[0],
                    'class': 'none',
                    'percent': p[0]
                })
                sets['es']['time'] = p[0]
            # Agregamos el proceso a la cola de es
            sets['es']['queue'].append({
                'pid': procesos_ord[p[2]]['pid'],
                'label': procesos_ord[p[2]]['desc'],
                'start': sets['es']['time'],
                'time': p[1],
                'end': sets['es']['time'] + p[1],
                'class': procesos_ord[p[2]]['class'],
                'percent': p[1]
            })
            sets['es']['time'] += p[1]
            procesos_ord[p[2]]['ta_cpu'] = sets['es']['time']

        # Incrementamos la iteracion
        sets['max_total'] = sets['max_total'] - 1

    # Calculamos porcentajes para visualizacion
    if sets['cpu']['time'] >= sets['es']['time']:
        sets['es']['queue'].append({
            'pid': None,
            'label': '',
            'start': sets['es']['time'],
            'time': sets['cpu']['time'] - sets['es']['time'],
            'end': sets['cpu']['time'],
            'class': 'none',
            'percent': sets['cpu']['time'] - sets['es']['time']
        })
        sets['es']['time'] = sets['cpu']['time']
    else:
        sets['cpu']['queue'].append({
            'pid': None,
            'label': '',
            'start': sets['cpu']['time'],
            'time': sets['es']['time'] - sets['cpu']['time'],
            'end': sets['es']['time'],
            'class': 'none',
            'percent': sets['es']['time'] - sets['cpu']['time']
        })
        sets['cpu']['time'] = sets['es']['time']

    __fcfs_calculate_percents(sets)

    return sets



def __fcfs_init(procesos, sets):
    """
    Iteramos por primera vez todos los procesos para determinar
    la cantidad de ráfagas máxima de cada recurso
    """
    for i in range(len(procesos)):
        proc_recursos = procesos[i].get_recursos()
        count_cpu = 0
        count_es = 0
        for j in range(len(proc_recursos)):
            if not j % 2:
                count_cpu += 1
            else:
                count_es += 1
        if count_cpu > sets['cpu']['count']:
            sets['cpu']['count'] = count_cpu
        if count_es > sets['es']['count']:
            sets['es']['count'] = count_es
        sets['max_total'] = sets['cpu']['count'] + sets['es']['count']


def __fcfs_parser_process(procesos):
    """
    Parseamos los procesos para generar una diccionario para trabajar
    """
    procesos_ord = []
    classes = __get_classes()
    for proc in procesos:
        random.shuffle(classes)
        proc_parser = {
            'pid': proc.simulacion_pid,
            'desc': proc.descripcion,
            'ta_cpu': int(proc.tiempo_arribo),
            'ta_es': int(proc.tiempo_arribo),
            'cpu': [],
            'es': [],
            'queue': 'cpu',
            'alive': True,
            'class': classes.pop()
        }
        recursos = proc.get_recursos()
        for i in range(len(recursos)):
            if not i % 2:
                proc_parser['cpu'].append(int(recursos[i]))
            else:
                proc_parser['es'].append(int(recursos[i]))
        procesos_ord.append(proc_parser)
    return procesos_ord


def __fcfs_calculate_percents(sets):
    for j in range(len(sets['cpu']['queue'])):
        sets['cpu']['queue'][j]['percent'] = format(sets['cpu']['queue'][j]['percent'] / sets['cpu']['time'] * 100, '.2f')
    for k in range(len(sets['es']['queue'])):
        sets['es']['queue'][k]['percent'] = format(sets['es']['queue'][k]['percent'] / sets['es']['time'] * 100, '.2f')

def __get_classes():
    return [
        'primary', 'secondary', 'success', 'danger',
        'warning', 'info', 'chartreuse', 'darkcyan',
        'dodgerblue', 'olivedrab', 'violet',
    ]