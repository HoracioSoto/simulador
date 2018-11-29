import random

from app.models import *


data = {}

classes = []


def run_fcfs(simulacion, procesos):
    # inicializamos variables
    cpu_time = 0
    cpu_idx = 0
    cpu_queue = []
    es_time = 0
    es_idx = 0
    es_queue = []
    __fcfs_init(procesos, cpu_queue)
    data = __data_init()

    # Traemos los procesos ordenados por ta
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
            'class': 'none',
            'percent': p_ords[0]['ta']
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
        'percent': cpu_tactual
    })
    cpu_time += cpu_tactual
    p_ords[0]['ta'] += cpu_time
    cpu_queue.pop(0)

    # Y el espacio libre en ES
    data['ES']['procesos'].append({
        'pid': None,
        'label': '',
        'start': 0,
        'time': cpu_time,
        'end': cpu_time,
        'class': 'none',
        'percent': cpu_time
    })
    es_time += cpu_time

    if len(p_ords[0]['es']):
        es_tactual = p_ords[0]['es'].pop(es_idx)
        data['ES']['procesos'].append({
            'pid': p_ords[0]['pid'],
            'label': p_ords[0]['desc'],
            'start': es_time,
            'end': es_time + es_tactual,
            'time': es_tactual,
            'class': p_ords[0]['class'],
            'percent': es_tactual
        })
        es_time += es_tactual
        p_ords[0]['ta'] += es_time

        cpu_queue.append(0)
    else:
        p_ords[0]['alive'] = False

    while len(cpu_queue):
        for i in range(len(cpu_queue)):
            if p_ords[cpu_queue[i]]['alive'] and len(p_ords[cpu_queue[i]]['cpu']):
                # Chequear si no hay espacios entre el ultimo proceso y el que viene
                if data['CPU']['procesos'][-1]['end'] < p_ords[cpu_queue[i]]['ta']:
                    # Pero antes chequeamos si no hay algun proceso en cola
                    add_process = False
                    for j in range(i, len(cpu_queue)):
                        if (p_ords[cpu_queue[j]]['ta'] < p_ords[cpu_queue[i]]['ta']) and len(p_ords[cpu_queue[j]]['cpu']):
                            # Tratamos el proceso
                            add_process = j
                            cpu_tactual = p_ords[cpu_queue[j]]['cpu'].pop(cpu_idx)
                            data['CPU']['procesos'].append({
                                'pid': p_ords[cpu_queue[j]]['pid'],
                                'label': p_ords[cpu_queue[j]]['desc'],
                                'start': data['CPU']['procesos'][-1]['end'],
                                'time': cpu_tactual,
                                'end': data['CPU']['procesos'][-1]['end'] + cpu_tactual,
                                'class': p_ords[cpu_queue[j]]['class'],
                                'percent': cpu_tactual
                            })
                            cpu_time += cpu_tactual
                            p_ords[cpu_queue[j]]['ta'] += cpu_time

                            if len(p_ords[cpu_queue[j]]['es']):
                                # Chequear si no hay espacios entre el ultimo proceso y el que viene es ES
                                if data['ES']['procesos'][-1]['end'] < cpu_time:
                                    es_tactual = cpu_time - data['ES']['procesos'][-1]['end']
                                    data['ES']['procesos'].append({
                                        'pid': None,
                                        'label': '',
                                        'start': data['ES']['procesos'][-1]['end'],
                                        'time': es_tactual,
                                        'end': data['ES']['procesos'][-1]['end'] + es_tactual,
                                        'class': 'none',
                                        'percent': es_tactual
                                    })
                                    es_time += es_tactual

                                # Tratamos el proceso en ES
                                es_tactual = p_ords[cpu_queue[j]]['es'].pop(es_idx)
                                data['ES']['procesos'].append({
                                    'pid': p_ords[cpu_queue[j]]['pid'],
                                    'label': p_ords[cpu_queue[j]]['desc'],
                                    'start': es_time,
                                    'time': es_tactual,
                                    'end': es_time + es_tactual,
                                    'class': p_ords[cpu_queue[j]]['class'],
                                    'percent': es_tactual
                                })
                                es_time += es_tactual

                                cpu_queue.append(cpu_queue[j])
                    if add_process != False:
                        # cpu_queue.pop(len(cpu_queue) - cpu_queue[::-1].index(cpu_queue[add_process]) - 1)
                        cpu_queue.pop(add_process)
                    if data['CPU']['procesos'][-1]['end'] < p_ords[cpu_queue[i]]['ta']:
                        cpu_tactual = p_ords[cpu_queue[i]]['ta'] - data['CPU']['procesos'][-1]['end']
                        data['CPU']['procesos'].append({
                            'pid': None,
                            'label': '',
                            'start': data['CPU']['procesos'][-1]['end'],
                            'time': cpu_tactual,
                            'end': data['CPU']['procesos'][-1]['end'] + cpu_tactual,
                            'class': 'none',
                            'percent': cpu_tactual
                        })
                        cpu_time += cpu_tactual

                # Tratamos el proceso en CPU
                cpu_tactual = p_ords[cpu_queue[i]]['cpu'].pop(cpu_idx)
                data['CPU']['procesos'].append({
                    'pid': p_ords[cpu_queue[i]]['pid'],
                    'label': p_ords[cpu_queue[i]]['desc'],
                    'start': data['CPU']['procesos'][-1]['end'],
                    'time': cpu_tactual,
                    'end': data['CPU']['procesos'][-1]['end'] + cpu_tactual,
                    'class': p_ords[cpu_queue[i]]['class'],
                    'percent': cpu_tactual
                })
                cpu_time += cpu_tactual
                p_ords[cpu_queue[i]]['ta'] += cpu_time

                if len(p_ords[cpu_queue[i]]['es']):
                    # Chequear si no hay espacios entre el ultimo proceso y el que viene es ES
                    if data['ES']['procesos'][-1]['end'] < cpu_time:
                        es_tactual = cpu_time - data['ES']['procesos'][-1]['end']
                        data['ES']['procesos'].append({
                            'pid': None,
                            'label': '',
                            'start': data['ES']['procesos'][-1]['end'],
                            'time': es_tactual,
                            'end': data['ES']['procesos'][-1]['end'] + es_tactual,
                            'class': 'none',
                            'percent': es_tactual
                        })
                        es_time += es_tactual

                    # Tratamos el proceso en ES
                    es_tactual = p_ords[cpu_queue[i]]['es'].pop(es_idx)
                    data['ES']['procesos'].append({
                        'pid': p_ords[cpu_queue[i]]['pid'],
                        'label': p_ords[cpu_queue[i]]['desc'],
                        'start': es_time,
                        'time': es_tactual,
                        'end': es_time + es_tactual,
                        'class': p_ords[cpu_queue[i]]['class'],
                        'percent': es_tactual
                    })
                    es_time += es_tactual

                if len(p_ords[cpu_queue[i]]['cpu']):
                    cpu_queue.append(cpu_queue[i])
                else:
                    p_ords[cpu_queue[i]]['alive'] = False

        # update cpu_queue
        cpu_queue = list(set([x for x in cpu_queue if cpu_queue.count(x) > 1]))

    cpu_idx += 1

    if cpu_time > es_time:
        data['CPU']['ttime'] = cpu_time
        data['ES']['ttime'] = cpu_time
        # Y el espacio libre en ES
        data['ES']['procesos'].append({
            'pid': None,
            'label': '',
            'start': es_time,
            'time': cpu_time - es_time,
            'end': cpu_time,
            'class': 'none',
            'percent': cpu_time - es_time
        })
    if data['ES']['ttime'] > data['CPU']['ttime']:
        data['CPU']['ttime'] = es_time
        data['ES']['ttime'] = es_time
        # Y el espacio libre en CPU
        data['CPU']['procesos'].append({
            'pid': None,
            'label': '',
            'start': cpu_time,
            'time': es_time - cpu_time,
            'end': es_time,
            'class': 'none',
            'percent': es_time - cpu_time
        })
    return data


def __fcfs_init(procesos, cpu_queue):
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

    # Iteramos por primera vez todos los procesos para determinar
    # la cantidad de ráfagas máxima de recursos, tiempo total de cpu y de e/s
    rafagas = 1
    data['CPU']['ttime'] = 0
    data['ES']['ttime'] = 0
    for i in range(len(procesos)):
        cpu_queue.append(i)
        proc_recursos = procesos[i].get_recursos()
        for idx in range(len(proc_recursos)):
            if not idx % 2:
                data['CPU']['ttime'] += int(proc_recursos[idx])
            else:
                data['ES']['ttime'] += int(proc_recursos[idx])
        if len(proc_recursos) > rafagas:
            rafagas = len(proc_recursos)
    data['recursos'] = range(rafagas)


def __fcfs_order(procesos):
    classes = __classes_init()

    # Ordenamos y parseamos los procesos
    proc_ord = []
    for proc in procesos:
        random.shuffle(classes)
        proc_parser = {
            'pid': proc.simulacion_pid,
            'desc': proc.descripcion,
            'ta': int(proc.tiempo_arribo),
            'cpu': [],
            'es': [],
            'alive': True,
            'class': classes.pop()
        }
        proc_recursos = proc.get_recursos()
        for idx in range(len(proc_recursos)):
            if not idx % 2:
                proc_parser['cpu'].append(int(proc_recursos[idx]))
            else:
                proc_parser['es'].append(int(proc_recursos[idx]))
        proc_ord.append(proc_parser)
    return proc_ord


def __data_init():
    return {
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


def __classes_init():
    return [
        'primary', 'secondary', 'success', 'danger',
        'warning', 'info', 'chartreuse', 'darkcyan',
        'dodgerblue', 'olivedrab', 'violet',
    ]


def run_sjf():
    return {}


def run_round_robin():
    return {}
