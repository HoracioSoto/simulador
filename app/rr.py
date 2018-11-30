import random

from app.models import *


def run_rr(simulacion, procesos):
    sets = {
        'cpu': {'time': 0, 'queue': [], 'count': 0},
        'es': {'time': 0, 'queue': [], 'count': 0},
        'max_total': 0, 'resources': range(5),
        'quantum': simulacion.quantum
    }

    # Inicializamos el algoritmo
    __rr_init(procesos, sets)

    # Parseamos los procesos
    p_ords = __rr_parser_process(Proceso.objects.filter(simulacion=simulacion).order_by('tiempo_arribo', 'simulacion_pid'))

    sets['resources'] = range(sets['max_total'])

    # Ejecutamos hasta que se completen todas las ráfagas
    iteracion = 0
    # Bandera para saber si algún proceso superó el quantum
    again = [False]
    while iteracion < sets['cpu']['count']:
        items_es = []
        if again[0]:
            again[0] = False
            for i in range(len(p_ords)):
                if p_ords[i]['again']:
                    __rr_check_previuos(sets, p_ords[i]['ta_cpu'])
                    __rr_check(p_ords, i, sets, iteracion, again, items_es)
        else:
            for i in range(len(p_ords)):
                __rr_check_previuos(sets, p_ords[i]['ta_cpu'])
                __rr_check(p_ords, i, sets, iteracion, again, items_es)

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
            if len(sets['es']['queue']) == 0 and p[0] != 0:
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
                'pid': p_ords[p[2]]['pid'],
                'label': p_ords[p[2]]['desc'],
                'start': sets['es']['time'],
                'time': p[1],
                'end': sets['es']['time'] + p[1],
                'class': p_ords[p[2]]['class'],
                'percent': p[1]
            })
            sets['es']['time'] += p[1]
            p_ords[p[2]]['ta_cpu'] = sets['es']['time']

        if not again[0]:
            # Incrementamo el contador
            iteracion += 1

    # Calculamos porcentajes para visualizacion
    __rr_calculate_percents(sets)

    return sets


def __rr_init(procesos, sets):
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


def __rr_parser_process(procesos):
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
            'again': False,
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


def __rr_calculate_percents(sets):
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


def __rr_check(p_ords, i, sets, iteracion, again, items_es):
    if p_ords[i]['cpu'][iteracion] > sets['quantum']:
        # Agregamos el proceso con ti = quantum
        sets['cpu']['queue'].append({
            'pid': p_ords[i]['pid'],
            'label': p_ords[i]['desc'],
            'start': sets['cpu']['time'],
            'time': sets['quantum'],
            'end': sets['cpu']['time'] + sets['quantum'],
            'class': p_ords[i]['class'],
            'percent': sets['quantum']
        })
        sets['cpu']['time'] += sets['quantum']
        p_ords[i]['ta_es'] = sets['cpu']['time']
        p_ords[i]['cpu'][iteracion] = p_ords[i]['cpu'][iteracion] - sets['quantum']
        p_ords[i]['again'] = True
        again[0] = True
    else:
        # Agregamos el proceso a la cola de cpu
        sets['cpu']['queue'].append({
            'pid': p_ords[i]['pid'],
            'label': p_ords[i]['desc'],
            'start': sets['cpu']['time'],
            'time': p_ords[i]['cpu'][iteracion],
            'end': sets['cpu']['time'] + p_ords[i]['cpu'][iteracion],
            'class': p_ords[i]['class'],
            'percent': p_ords[i]['cpu'][iteracion]
        })
        sets['cpu']['time'] += p_ords[i]['cpu'][iteracion]
        p_ords[i]['ta_es'] = sets['cpu']['time']
        p_ords[i]['again'] = False

        # Tratamos la cola de e/s
        if len(p_ords[i]['es']):
            items_es.append([p_ords[i]['ta_es'], p_ords[i]['es'].pop(0), i])
        else:
            p_ords[i]['alive'] = False


def __rr_check_previuos(sets, tiempo_arribo):
    # Chequear si no hay espacios entre el ultimo proceso y el que viene
    if len(sets['cpu']['queue']) and (sets['cpu']['queue'][-1]['end'] < tiempo_arribo):
        sets['cpu']['queue'].append({
            'pid': None,
            'label': '',
            'start': sets['cpu']['queue'][-1]['end'],
            'time': tiempo_arribo - sets['cpu']['queue'][-1]['end'],
            'end': tiempo_arribo,
            'class': 'none',
            'percent': tiempo_arribo - sets['cpu']['queue'][-1]['end']
        })
        sets['cpu']['time'] = tiempo_arribo
    # O si no hay nada antes
    if len(sets['cpu']['queue']) == 0 and tiempo_arribo != 0:
        sets['cpu']['queue'].append({
            'pid': None,
            'label': '',
            'start': 0,
            'time': tiempo_arribo,
            'end': tiempo_arribo,
            'class': 'none',
            'percent': tiempo_arribo
        })
        sets['cpu']['time'] = tiempo_arribo