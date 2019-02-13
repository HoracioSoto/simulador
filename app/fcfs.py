import random
import json

from app.models import *


def run_fcfs(simulacion, procesos):
    sets = {
        'cpu': {
            'queue': [],
            'time': 0,
            'count': 0
        },
        'es': {
            'queue': [],
            'time': 0,
            'count': 0
        },
        'memory': {
            'size': 0,
            'schema': '',
            'type': '',
            'full': False,
            'parts': [],
            'queue': [],
            'instances': 1
        },
        'max_total': 0,
        'resources': range(5),
        'time': 0
    }

    # Inicializamos la simulación
    __fcfs_init(simulacion, procesos, sets)

    # Parseamos los procesos
    procesos = Proceso.objects.filter(simulacion=simulacion).order_by(
        'tiempo_arribo', 'simulacion_pid')
    p_ords = __fcfs_parser_process(procesos)

    sets['resources'] = range(sets['max_total'])

    while sets['time'] is not None:
        # Seleccionamos un proceso
        selecteds = []
        for i in range(len(p_ords)):
            if (p_ords[i]['alive'] and p_ords[i]['queue'] == 'cpu' and
                    p_ords[i]['ta_cpu'] == sets['time']):
                    selecteds.append(i)
        for sld in selecteds:
            # Chequeamos que haya memoria disponible si el proceso no está en memoria
            if not p_ords[sld]['in_memory']:
                if (not sets['memory']['full'] and sets['memory']['size'] >= p_ords[sld]['size']):
                    if sets['memory']['schema'] == 'particion-fija':
                        if sets['memory']['type'] == 'first-fit':
                            for j in range(len(sets['memory']['parts'])):
                                # Si el proc no esta en memoria y la particion esta disponible y entra
                                if (not p_ords[sld]['in_memory'] and sets['memory']['parts'][j]['available'] and
                                    sets['memory']['parts'][j]['size'] >= p_ords[sld]['size'] and
                                        (len(sets['memory']['parts'][j]['procs']) == 0 or
                                        (sets['memory']['parts'][j]['procs'][-1]['tf'] is not None and sets['memory']['parts'][j]['procs'][-1]['tf'] <= p_ords[sld]['ta_cpu']))):
                                    sets['memory']['parts'][j]['procs'].append({
                                        'pid': p_ords[sld]['pid'],
                                        'label': p_ords[sld]['desc'],
                                        'size': p_ords[sld]['size'],
                                        'class': p_ords[sld]['class'],
                                        'ta': sets['time'],
                                        'tf': None
                                    })
                                    p_ords[sld]['in_memory'] = True
                                    p_ords[sld]['part'] = j
                                    sets['memory']['parts'][j]['available'] = False
                        # best-fit
                        else:
                            idx_part, idx_part_min, diff, diff_change = None, None, 0, False
                            for j in range(len(sets['memory']['parts'])):
                                diff = 0
                                # Si el proc no esta en memoria y la particion esta disponible y entra
                                if (not p_ords[sld]['in_memory'] and sets['memory']['parts'][j]['available'] and
                                    sets['memory']['parts'][j]['size'] >= p_ords[sld]['size'] and
                                        (len(sets['memory']['parts'][j]['procs']) == 0 or
                                            sets['memory']['parts'][j]['procs'][-1]['tf'] is not None)):
                                    idx_part = j
                                    if sets['memory']['parts'][idx_part]['size'] - p_ords[sld]['size'] <= diff:
                                        idx_part_min = idx_part
                                        diff = sets['memory']['parts'][idx_part]['size'] - p_ords[sld]['size']
                                        diff_change = True
                            if diff_change:
                                idx_part = idx_part_min
                            if idx_part is not None:
                                sets['memory']['parts'][idx_part]['procs'].append({
                                    'pid': p_ords[sld]['pid'],
                                    'label': p_ords[sld]['desc'],
                                    'size': p_ords[sld]['size'],
                                    'class': p_ords[sld]['class'],
                                    'ta': sets['time'],
                                    'tf': None
                                })
                                p_ords[sld]['in_memory'] = True
                                p_ords[sld]['part'] = idx_part
                                sets['memory']['parts'][idx_part]['available'] = False
                    # particion-variable
                    else:
                        # if sets['memory']['type'] == 'first-fit':
                        #     pass
                        if sets['memory']['type'] == 'worst-fit':
                            idx_part = 0
                            diference = 0
                            for j in range(len(sets['memory']['parts'])):
                                if (not p_ords[sld]['in_memory'] and
                                    sets['memory']['parts'][j]['available'] and
                                    sets['memory']['parts'][j]['size'] >= p_ords[sld]['size'] and
                                        (len(sets['memory']['parts'][j]['procs']) == 0 or
                                            sets['memory']['parts'][j]['procs'][-1]['tf'] is not None)):
                                    if sets['memory']['parts'][j]['size'] - p_ords[sld]['size'] > diference:
                                        idx_part = j
                                        diference = sets['memory']['parts'][j]['size'] - p_ords[sld]['size']
                            if diference != 0:
                                sets['memory']['parts'][idx_part]['procs'].append({
                                    'pid': p_ords[sld]['pid'],
                                    'label': p_ords[sld]['desc'],
                                    'size': p_ords[sld]['size'],
                                    'class': p_ords[sld]['class'],
                                    'ta': sets['time'],
                                    'tf': None
                                })
                                p_ords[sld]['in_memory'] = True
                                p_ords[sld]['part'] = idx_part
                                sets['memory']['parts'][idx_part]['available'] = False
            if p_ords[sld]['in_memory']:
                if len(p_ords[sld]['cpu']):
                    # Chequear si no hay espacios entre el ultimo proceso y el que viene
                    if len(sets['cpu']['queue']) and (sets['cpu']['queue'][-1]['end'] < p_ords[sld]['ta_cpu']):
                        sets['cpu']['queue'].append({
                            'pid': None,
                            'size': '',
                            'start': sets['cpu']['queue'][-1]['end'],
                            'time': p_ords[sld]['ta_cpu'] - sets['cpu']['queue'][-1]['end'],
                            'end': p_ords[sld]['ta_cpu'],
                            'class': 'none',
                            'percent': p_ords[sld]['ta_cpu'] - sets['cpu']['queue'][-1]['end']
                        })
                        sets['cpu']['time'] = p_ords[sld]['ta_cpu']
                    # O si no hay nada antes
                    if len(sets['cpu']['queue']) == 0 and p_ords[sld]['ta_cpu'] != 0:
                        sets['cpu']['queue'].append({
                            'pid': None,
                            'label': '',
                            'start': 0,
                            'time': p_ords[sld]['ta_cpu'],
                            'end': p_ords[sld]['ta_cpu'],
                            'class': 'none',
                            'percent': p_ords[sld]['ta_cpu']
                        })
                        sets['cpu']['time'] = p_ords[sld]['ta_cpu']
                    # Agregamos el proceso a la cola de cpu
                    actual_cpu = p_ords[sld]['cpu'].pop(0)
                    sets['cpu']['queue'].append({
                        'pid': p_ords[sld]['pid'],
                        'label': p_ords[sld]['desc'],
                        'start': sets['cpu']['time'],
                        'time': actual_cpu,
                        'end': sets['cpu']['time'] + actual_cpu,
                        'class': p_ords[sld]['class'],
                        'percent': actual_cpu
                    })
                    sets['cpu']['time'] += actual_cpu
                    p_ords[sld]['ta_es'] = sets['cpu']['time']

                    # Tratamos E/S
                    if len(p_ords[sld]['es']):
                        # Chequear si no hay espacios entre el ultimo proceso y el que viene
                        if len(sets['es']['queue']) and (sets['es']['queue'][-1]['end'] < p_ords[sld]['ta_es']):
                            sets['es']['queue'].append({
                                'pid': None,
                                'label': '',
                                'start': sets['es']['queue'][-1]['end'],
                                'time': p_ords[sld]['ta_es'] - sets['es']['queue'][-1]['end'],
                                'end': p_ords[sld]['ta_es'],
                                'class': 'none',
                                'percent': p_ords[sld]['ta_es'] - sets['es']['queue'][-1]['end']
                            })
                            sets['es']['time'] = p_ords[sld]['ta_es']
                        # O si no hay nada antes
                        if len(sets['es']['queue']) == 0 and p_ords[sld]['ta_es'] != 0:
                            sets['es']['queue'].append({
                                'pid': None,
                                'label': '',
                                'start': 0,
                                'time': p_ords[sld]['ta_es'],
                                'end': p_ords[sld]['ta_es'],
                                'class': 'none',
                                'percent': p_ords[sld]['ta_es']
                            })
                            sets['es']['time'] = p_ords[sld]['ta_es']
                        # Agregamos el proceso a la cola de es
                        actual_es = p_ords[sld]['es'].pop(0)
                        sets['es']['queue'].append({
                            'pid': p_ords[sld]['pid'],
                            'label': p_ords[sld]['desc'],
                            'start': sets['es']['time'],
                            'time': actual_es,
                            'end': sets['es']['time'] + actual_es,
                            'class': p_ords[sld]['class'],
                            'percent': actual_es
                        })
                        sets['es']['time'] += actual_es
                        p_ords[sld]['ta_cpu'] = sets['es']['time']
                    else:
                        p_ords[sld]['alive'] = False
                        sets['memory']['parts'][p_ords[sld]['part']]['procs'][-1]['tf'] = sets['cpu']['time']
                        sets['memory']['parts'][p_ords[sld]['part']]['available'] = True
                else:
                    p_ords[sld]['alive'] = False
                    sets['memory']['parts'][p_ords[sld]['part']]['procs'][-1]['tf'] = sets['cpu']['time']
                    sets['memory']['parts'][p_ords[sld]['part']]['available'] = True
            else:
                # Si no consigue lugar en memoria lo posponemos
                p_ords[sld]['ta_cpu'] = sets['cpu']['time']

        sets['time'] += 1
        if sets['time'] == 2000:
            sets['time'] = None

    # Ordenamos la memoria para visualizacion
    __fcfs_order_memory(sets)

    # Calculamos porcentajes para visualizacion
    __fcfs_calculate_percents(sets)
    print(sets['memory'])
    return sets


def __fcfs_init(simulacion, procesos, sets):
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

    """
    Inicializamos los parámetros de la memoria
    """
    memory = Memoria.objects.get(simulacion=simulacion)
    sets['memory']['size'] = memory.size
    sets['memory']['schema'] = memory.esquema
    sets['memory']['type'] = memory.algoritmo_colocacion
    parts = memory.particiones.split(',')
    for p in range(len(parts)):
        if p == 0:
            sets['memory']['parts'].append({
                'size': int(parts[p]),
                'available': True,
                'start': 0,
                'end': int(parts[p]),
                'procs': []
            })
        else:
            sets['memory']['parts'].append({
                'size': int(parts[p]),
                'available': True,
                'start': sets['memory']['parts'][-1]['end'],
                'end': sets['memory']['parts'][-1]['end'] + int(parts[p]),
                'procs': []
            })


def __fcfs_parser_process(procesos):
    """
    Parseamos los procesos para generar una diccionario para trabajar
    """
    p_ords = []
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
            'class': classes.pop(),
            'size': proc.size,
            'in_memory': False,
            'part': None
        }
        recursos = proc.get_recursos()
        for i in range(len(recursos)):
            if not i % 2:
                proc_parser['cpu'].append(int(recursos[i]))
            else:
                proc_parser['es'].append(int(recursos[i]))
        p_ords.append(proc_parser)
    return p_ords


def __fcfs_order_memory(sets):
    ta_mem = sets['cpu']['time']
    instances = 0
    # busco el menor tiempo de arribo
    for p in range(len(sets['memory']['parts'])):
        ta_mem = sets['cpu']['time']
        part = sets['memory']['parts'][p]
        for pro in range(len(part['procs'])):
            # if part['procs'][pro]['ta'] <= ta_mem:
            ta_mem = part['procs'][pro]['ta']
            sets['memory']['queue'].append({
                'ta': ta_mem,
                'elems': []
            })
            for k in range(len(sets['memory']['parts'])):
                part_s = sets['memory']['parts'][k]
                if len(part_s['procs']):
                    for pro_s in range(len(part_s['procs'])):
                        if part_s['procs'][pro_s]['ta'] <= ta_mem and part_s['procs'][pro_s]['tf'] > ta_mem:
                            # Se agregan todos los proc en memoria menor a ta_mem
                            # siempre en la ultima instancia creada
                            if k == 0:
                                sets['memory']['queue'][-1]['elems'].append({
                                    'pid': part_s['procs'][pro_s]['pid'],
                                    'label': part_s['procs'][pro_s]['label'],
                                    'start': 0,
                                    'size': part_s['procs'][pro_s]['size'],
                                    'end': part_s['procs'][pro_s]['size'],
                                    'class': part_s['procs'][pro_s]['class'],
                                    'percent': part_s['procs'][pro_s]['size']
                                })
                            else:
                                sets['memory']['queue'][-1]['elems'].append({
                                    'pid': part_s['procs'][pro_s]['pid'],
                                    'label': part_s['procs'][pro_s]['label'],
                                    'start': part_s['start'],
                                    'size': part_s['procs'][pro_s]['size'],
                                    'end': part_s['start'] + part_s['procs'][pro_s]['size'],
                                    'class': part_s['procs'][pro_s]['class'],
                                    'percent': part_s['procs'][pro_s]['size']
                                })
                            if part_s['size'] != part_s['procs'][pro_s]['size']:
                                sets['memory']['queue'][-1]['elems'].append({
                                    'pid': None,
                                    'label': '',
                                    'start': sets['memory']['queue'][-1]['elems'][-1]['end'],
                                    'size': part_s['size'] - part_s['procs'][pro_s]['size'],
                                    'end': part_s['end'],
                                    'class': 'none',
                                    'percent': part_s['size'] - part_s['procs'][pro_s]['size']
                                })
                        # Si no hay proceso en esa parte de la memoria para ese ta ponemos vacio
                        # aca me quede, hay que ver como se visualzia la memoria
                        # else:
                        #     sets['memory']['queue'][-1]['elems'].append({
                        #         'pid': None,
                        #         'label': '',
                        #         'start': part_s['start'],
                        #         'size': part_s['size'],
                        #         'end': part_s['start'] + part_s['size'],
                        #         'class': 'none',
                        #         'percent': part_s['size']
                        #     })
                else:
                    sets['memory']['queue'][-1]['elems'].append({
                        'pid': None,
                        'label': '',
                        'start': part_s['start'],
                        'size': part_s['size'],
                        'end': part_s['start'] + part_s['size'],
                        'class': 'none',
                        'percent': part_s['size']
                    })
    sets['memory']['instances'] = len(sets['memory']['queue'])
    sets['memory']['queue'] = sorted(sets['memory']['queue'], key=lambda x: (x['ta']))


def __fcfs_calculate_percents(sets):
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
    for x in range(len(sets['memory']['queue'])):
        for p in range(len(sets['memory']['queue'][x]['elems'])):
            sets['memory']['queue'][x]['elems'][p]['percent'] = format(sets['memory']['queue'][x]['elems'][p]['percent'] / sets['memory']['size'] * 100, '.2f')


def __get_classes():
    return [
        'primary', 'secondary', 'success', 'danger',
        'warning', 'info', 'chartreuse', 'darkcyan',
        'dodgerblue', 'olivedrab', 'violet',
    ]
