import random
from copy import deepcopy

from app.models import *

def __utils_init(simulacion, procesos, sets):
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
    if memory.esquema == 'particion-variable':
        sets['memory']['parts_var'].update({
            0: [{
                'available': True,
                'start': 0,
                'end': memory.size,
                'size': memory.size,
                'percent': memory.size,
                'proc': None
            }]
        })


def __utils_parser_process(procesos):
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


def __get_classes():
    return [
        'primary', 'secondary', 'success', 'danger',
        'warning', 'info', 'chartreuse', 'darkcyan',
        'dodgerblue', 'olivedrab', 'violet',
    ]


def __utils_compress_memory(sets):
    new_to_rem = []
    new_part_to_copy = []
    for x in range(len(sets['memory']['parts_to_remove'])):
        to_rem = sets['memory']['parts_to_remove'][x].copy()
        if to_rem['time'] == sets['time'] and to_rem['time'] in sets['memory']['parts_var']:
            p_to_copy = deepcopy(sets['memory']['parts_var'][ to_rem['time'] ])
            for j in range(len(p_to_copy)):
                if p_to_copy[j]['proc'] is not None and p_to_copy[j]['proc']['pid'] == to_rem['pid']:
                    # Si es la primera parte
                    if j == 0:
                        # y tiene una despues
                        if j+1 in p_to_copy and p_to_copy[j+1]['available'] and p_to_copy[j+1]['proc'] is None:
                            p_to_copy[j+1]['start'] = p_to_copy[j]['start']
                            p_to_copy[j+1]['size'] += p_to_copy[j]['size']
                            new_part_to_copy = deepcopy(p_to_copy[j+1:])
                        else:
                            p_to_copy[j]['available'] = True
                            p_to_copy[j]['proc'] = None
                            new_part_to_copy = deepcopy(p_to_copy)
                    # Si es la ultima parte
                    elif j == (len(p_to_copy) - 1):
                        # y tiene una antes
                        if p_to_copy[j-1] in p_to_copy and p_to_copy[j-1]['available'] and p_to_copy[j-1]['proc'] is None:
                            p_to_copy[j-1]['end'] = p_to_copy[j]['end']
                            p_to_copy[j-1]['size'] += p_to_copy[j]['size']
                            new_part_to_copy = deepcopy(p_to_copy[:-1])
                        else:
                            p_to_copy[j]['available'] = True
                            p_to_copy[j]['proc'] = None
                            new_part_to_copy = deepcopy(p_to_copy)
                    # Entonces esta en el medio
                    else:
                        # Tiene partes antes y/o despues
                        if (p_to_copy[j-1] in p_to_copy and p_to_copy[j+1] in p_to_copy and
                                p_to_copy[j-1]['available'] and p_to_copy[j-1]['proc'] is None and
                                    p_to_copy[j+1]['available'] and p_to_copy[j+1]['proc'] is None):
                            p_to_copy[j-1]['end'] = p_to_copy[j+1]['end']
                            p_to_copy[j-1]['size'] += p_to_copy[j]['size'] + p_to_copy[j+1]['size']
                            new_part_to_copy = deepcopy(p_to_copy[:j] + p_to_copy[j+2:])
                        elif p_to_copy[j-1] in p_to_copy and p_to_copy[j-1]['available'] and p_to_copy[j-1]['proc'] is None:
                            p_to_copy[j-1]['end'] = p_to_copy[j]['end']
                            p_to_copy[j-1]['size'] += p_to_copy[j]['size']
                            new_part_to_copy = deepcopy(p_to_copy[:j] + p_to_copy[j+1:])
                        elif p_to_copy[j+1] in p_to_copy and p_to_copy[j+1]['available'] and p_to_copy[j+1]['proc'] is None:
                            p_to_copy[j+1]['start'] = p_to_copy[j]['start']
                            p_to_copy[j+1]['size'] += p_to_copy[j]['size']
                            new_part_to_copy = deepcopy(p_to_copy[:j] + p_to_copy[j+1:])
                        # no tiene partes antes o despues
                        else:
                            p_to_copy[j]['available'] = True
                            p_to_copy[j]['proc'] = None
                            new_part_to_copy = deepcopy(p_to_copy)

            sets['memory']['parts_var'][ to_rem['time'] ] = deepcopy(new_part_to_copy)
        else:
            new_to_rem.append(to_rem)
    sets['memory']['parts_to_remove'] = deepcopy(new_to_rem)


def __utils_order_memory(sets):
    ta_mem = sets['cpu']['time']
    instances = 0
    # busco el menor tiempo de arribo
    for p in range(len(sets['memory']['parts'])):
        ta_mem = sets['cpu']['time']
        part = sets['memory']['parts'][p]
        for pro in range(len(part['procs'])):
            ta_mem = part['procs'][pro]['ta']
            sets['memory']['queue'].append({
                'ta': ta_mem,
                'elems': []
            })
            for k in range(len(sets['memory']['parts'])):
                part_s = sets['memory']['parts'][k]
                if len(part_s['procs']):
                    for pro_s in range(len(part_s['procs'])):
                        if part_s['procs'][pro_s]['ta'] <= ta_mem < part_s['procs'][pro_s]['tf']:
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
    queue_only = []
    for ptt in range(len(sets['memory']['queue'])):
        part = sets['memory']['queue'][ptt]
        exists = False
        for ptt2 in range(len(queue_only)):
            part2 = sets['memory']['queue'][ptt2]
            if part2['ta'] == part['ta']:
                exists = True
        if not exists:
            queue_only.append(part)
    sets['memory']['queue'] = queue_only
    queue_for = []
    for ptt in range(len(sets['memory']['queue'])):
        part_old = sets['memory']['queue'][ptt]
        part_new = {
            'ta': part_old['ta'],
            'elems': []
        }
        for idx in range(len(part_old['elems'])):
            if idx == 0 and part_old['elems'][idx]['start'] != 0:
                part_new['elems'].append({
                    'pid': None,
                    'label': '',
                    'start': 0,
                    'size': part_old['elems'][idx]['start'],
                    'end': part_old['elems'][idx]['start'],
                    'class': 'none',
                    'percent': part_old['elems'][idx]['start']
                })
            part_new['elems'].append(part_old['elems'][idx])
            try:
                if part_old['elems'][idx]['end'] != part_old['elems'][idx + 1]['start']:
                    part_new['elems'].append({
                        'pid': None,
                        'label': '',
                        'start': part_old['elems'][idx]['end'],
                        'size': part_old['elems'][idx + 1]['start'] - part_old['elems'][idx]['end'],
                        'end': part_old['elems'][idx + 1]['start'],
                        'class': 'none',
                        'percent': part_old['elems'][idx + 1]['start'] - part_old['elems'][idx]['end']
                    })
            except Exception as e:
                pass
        queue_for.append(part_new)
    sets['memory']['queue'] = queue_for
    sets['memory']['instances'] = len(sets['memory']['queue'])
    sets['memory']['queue'] = sorted(sets['memory']['queue'], key=lambda x: (x['ta']))


def __utils_calculate_percents(sets):
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
    if sets['memory']['schema'] == 'particion-fija':
        for x in range(len(sets['memory']['queue'])):
            for p in range(len(sets['memory']['queue'][x]['elems'])):
                sets['memory']['queue'][x]['elems'][p]['percent'] = format(sets['memory']['queue'][x]['elems'][p]['percent'] / sets['memory']['size'] * 100, '.2f')
    else:
        for x in range(len(sets['memory']['parts_var'])):
            if x in sets['memory']['parts_var']:
                for p in range(len(sets['memory']['parts_var'][x])):
                    sets['memory']['parts_var'][x][p]['percent'] = format(float(sets['memory']['parts_var'][x][p]['size']) / sets['memory']['size'] * 100, '.2f')
