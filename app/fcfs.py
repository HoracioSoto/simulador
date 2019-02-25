from app.models import *
from app.utils import __utils_init, __utils_parser_process, __utils_compress_memory, __utils_order_memory, __utils_calculate_percents


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
            'parts_var': [],
            'queue': [],
            'instances': 1
        },
        'max_total': 0,
        'resources': range(5),
        'time': 0
    }

    # Inicializamos la simulación
    __utils_init(simulacion, procesos, sets)

    # Parseamos los procesos
    procesos = Proceso.objects.filter(simulacion=simulacion).order_by(
        'tiempo_arribo', 'simulacion_pid')
    p_ords = __utils_parser_process(procesos)

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
                            idx_part, idx_part_min, diff, diff_change = None, None, 10000, False
                            for j in range(len(sets['memory']['parts'])):
                                # Si el proc no esta en memoria y la particion esta disponible y entra
                                if (not p_ords[sld]['in_memory'] and sets['memory']['parts'][j]['available'] and
                                    sets['memory']['parts'][j]['size'] >= p_ords[sld]['size'] and
                                        (len(sets['memory']['parts'][j]['procs']) == 0 or
                                            (sets['memory']['parts'][j]['procs'][-1]['tf'] is not None and sets['memory']['parts'][j]['procs'][-1]['tf'] <= p_ords[sld]['ta_cpu']))):
                                    idx_part = j
                                    if sets['memory']['parts'][idx_part]['size'] - p_ords[sld]['size'] < diff:
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
                        if sets['memory']['type'] == 'first-fit':
                            for j in range(len(sets['memory']['parts'])):
                                if (not p_ords[sld]['in_memory'] and sets['memory']['parts'][j]['available'] and
                                    sets['memory']['parts'][j]['size'] >= p_ords[sld]['size']):
                                    sets['memory']['parts'][j]['procs'].append({
                                        'pid': p_ords[sld]['pid'],
                                        'label': p_ords[sld]['desc'],
                                        'size': p_ords[sld]['size'],
                                        'class': p_ords[sld]['class'],
                                        'ta': sets['time'],
                                        'tf': None,
                                        'memory_data': {
                                            'size': sets['memory']['parts'][j]['size'],
                                            'start': sets['memory']['parts'][j]['start'],
                                            'end': sets['memory']['parts'][j]['end']
                                        }
                                    })
                                    p_ords[sld]['in_memory'] = True
                                    p_ords[sld]['part'] = j
                                    sets['memory']['parts'][j]['available'] = False

                                    if p_ords[sld]['size'] < sets['memory']['parts'][j]['size']:
                                        new_part = {
                                            'size': sets['memory']['parts'][j]['size'] - p_ords[sld]['size'],
                                            'available': True,
                                            'burnt': False,
                                            'start': sets['memory']['parts'][j]['start'] + p_ords[sld]['size'],
                                            'end': sets['memory']['parts'][j]['end'],
                                            'procs': []
                                        }
                                        sets['memory']['parts'] = sets['memory']['parts'][:j+1] + [new_part] + sets['memory']['parts'][j+1:]
                                        sets['memory']['parts'][j]['size'] = p_ords[sld]['size']
                                        sets['memory']['parts'][j]['end'] = sets['memory']['parts'][j]['start'] + p_ords[sld]['size']

                        # worst-fit
                        else:
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
                        # __utils_compress_memory(sets, p_ords[sld]['part'])
                else:
                    p_ords[sld]['alive'] = False
                    sets['memory']['parts'][p_ords[sld]['part']]['procs'][-1]['tf'] = sets['cpu']['time']
                    sets['memory']['parts'][p_ords[sld]['part']]['available'] = True
            else:
                # Si no consigue lugar en memoria lo posponemos un batido de reloj mas
                p_ords[sld]['ta_cpu'] = p_ords[sld]['ta_cpu'] + 1

        sets['time'] += 1
        if sets['time'] == 2000:
            sets['time'] = None
    # Ordenamos la memoria para visualizacion
    __utils_order_memory(sets)

    # Calculamos porcentajes para visualizacion
    __utils_calculate_percents(sets)

    return sets
