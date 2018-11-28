from app.models import *


data = {
    'CPU': {
        'procesos': [],
        'total_time': 0
    },
    'ES': {
        'procesos': [],
        'total_time': 0
    },
    'recursos': range(1)
}

classes = (
	'primary', 'secondary', 'success', 'danger',
	'warning', 'info', 'light', 'dark', 'white',
)

def run_fcfs(simulacion, procesos):
	# inicializamos variables
	data['recursos'], data['CPU']['total_time'], data['ES']['total_time'] = __fcfs_init(procesos)
	tiempo_cpu = 0
	tiempo_es = 0
	idx = 0
	# Traemos los procesos ordenamos por ta (para este algoritmo)
	proc_ord = __fcfs_order(Proceso.objects.filter(simulacion=simulacion).order_by('tiempo_arribo'))
	print(proc_ord)
	# Si el primer proceso no tiene ta = 0 agregamos
	if proc_ord[idx]['tiempo_arribo'] != 0:
		data['CPU']['procesos'].append({
			'pid': None,
			'label': '',
			'start': 0,
			'time': proc_ord[idx]['tiempo_arribo'],
			'end': proc_ord[idx]['tiempo_arribo'],
			'class': 'bg-none',
			'percent': format(proc_ord[idx]['tiempo_arribo']/data['CPU']['total_time']*100, '.2f')
		})
	while tiempo_cpu < data['CPU']['total_time']:
		# Agregamos el primer procesos y arrancamos
		data['CPU']['procesos'].append({
			'pid': proc_ord[idx]['pid'],
			'label': proc_ord[idx]['descripcion'],
			'start': proc_ord[idx]['tiempo_arribo'],
			'time': proc.tiempo_arribo,
			'end': proc.tiempo_arribo,
			'class': 'bg-none',
			'percent': format(proc_ord[pid].tiempo_arribo/data['CPU']['total_time']*100, '.2f')
		})
		
	return data

def __fcfs_init(procesos):
	# Iteramos por primera vez todos los procesos para determinar
	# la cantidad de ráfagas máxima de recursos, tiempo total de cpu y de e/s
	rafagas = 1
	tiempo_cpu = 0
	tiempo_es = 0
	proc_ord = []
	for proc in procesos:
		proc_recursos = proc.get_recursos()
		for idx in range(len(proc_recursos)):
			if not idx % 2:
				tiempo_cpu += int(proc_recursos[idx])
			else:
				tiempo_es += int(proc_recursos[idx])
		if len(proc_recursos) > rafagas:
			rafagas = len(proc_recursos)
	return range(rafagas), tiempo_cpu, tiempo_es

def __fcfs_order(procesos):
	# Ordenamos y parseamos los procesos
	proc_ord = []
	for proc in procesos:
		proc_parser = {
			'pid': proc.simulacion_pid,
			'descripcion': proc.descripcion,
			'tiempo_arribo': int(proc.tiempo_arribo),
			'cpu': [],
			'es': [],
			'alive': True
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
