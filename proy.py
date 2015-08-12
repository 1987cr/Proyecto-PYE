# -*- encoding: utf-8 -*-

## Carlos Riera CI 18.004.591 ##

import simpy
import random
import csv

## LECTURA ENTRADA ##

with open('entrada.csv') as entrada:

	reader = csv.DictReader(entrada, fieldnames=['1', '2'])

	N_INI           = int(reader.next()['2'])
	I_INI           = int(reader.next()['2'])
	MIN_D_LATE      = int(reader.next()['2'])
	MAX_D_LATE      = int(reader.next()['2'])
	P_D_E           = float(reader.next()['2'])
	N_CORR          = int(reader.next()['2'])
	D_CORR          = int(reader.next()['2'])
	FACTOR_CONTAGIO = float(reader.next()['2'])
	FACTOR_MUTA     = float(reader.next()['2'])
	MAX_D_E         = int(reader.next()['2'])
	COSTO_D_E       = float(reader.next()['2'])
	COSTO_F_E       = float(reader.next()['2'])
	COSTO_MUERTE    = float(reader.next()['2'])

class Ave:
	def __init__(self, ave_id):
		self.id           = ave_id

## GENERADOR AVES ##
def setup(env, corrida):
	global DIA

	for i in range(0,N_INI):
		if(i < I_INI):
			# Infectados iniciales
			env.process(infectadoSano(env, Ave(i)))
		else:
			# Sanos iniciales
			env.process(sano(env, Ave(i)))

	if(corrida == 1):
		# Escritura de la traza
		with open('traza.csv', 'w') as csvfile:
		    fieldnames = ['Dia', 'N', 'I&S', 'I&E', 'Muertos', 'S']
		    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',', lineterminator='\n')
		    writer.writeheader()
		    while True:
				#print(DIA,N, IS, IE, M, S)
				writer.writerow({'Dia': DIA, 'N': N, 'I&S': IS, 'I&E': IE, 'Muertos': M, 'S': S})
				yield env.timeout(1.0000001)
				DIA += 1
	else:
		yield env.timeout(0)
	

## SANO ##
def sano(env, ave):
	global IS
	global S

	while True:
		yield env.timeout(1)
		if(bernoulli(IE*FACTOR_CONTAGIO/N)):
			IS += 1
			S -= 1
			env.process(infectadoSano(env, ave))
			break
		
## INFECTADO Y SANO ##
def infectadoSano(env, ave):
	global IE
	global IS
	
	yield env.timeout(discreta_uniforme(MIN_D_LATE, MAX_D_LATE))
	
	IS -= 1
	IE += 1

	env.process(infectadoEnfermo(env, ave))
	
## INFECTADO Y SANO 2 (Aquí entra cuando el ave supera la enfermadad) ##
def infectadoSano2(env, ave):
	while True:
		yield env.timeout(1)
		if(bernoulli(IS*FACTOR_MUTA/N)):
			env.process(infectadoSano(env, ave))
			break
		
## INFECTADO ENFERMO ##
def infectadoEnfermo(env, ave):
	global IE
	global IS
	global COSTO_DIARIO

	te = geometrica(P_D_E)

	COSTO_DIARIO += COSTO_D_E*te

	if(te > MAX_D_E):
		# La enfermedad dura mas de Max_D_E dias asi que pasa al proceso donde morirá
		env.process(infectadoEnfermoMuriendo(env, ave, te))
	else:
		yield env.timeout(te)
		IE -= 1
		IS +=1

		env.process(infectadoSano2(env, ave))

	env.exit(0)

## INFECTADO ENFERMO Y MURIENDO ##
def infectadoEnfermoMuriendo(env, ave, te):
	global M
	global N
	global IE
	global COSTO_DIARIO

	yield env.timeout(te)

	M += 1
	N -= 1
	IE -= 1

	env.exit(0)

## DISTRIBUCIONES ##
def bernoulli(p):
	r = random.uniform(0,1)
	if(r < p):
		return 1
	else:
		return 0

def geometrica(p):
	x = 1
	r = bernoulli(p)

	while(r != 1):
		x += 1
		r = bernoulli(p)

	return x

def discreta_uniforme(minv, maxv):
	return int(random.uniform(minv, maxv+1))

## SIMULACIONES ##

with open('salida.csv', 'w') as csvfile:
    fieldnames = ['corrida', 'factor_contagio','factor_mutacion','N','I&S','I&E','Muertos','S','CostoEAcumulado','CostoEFinal','CostoMuerte','CostoTotal']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',', lineterminator='\n')
    writer.writeheader()
    for i in range(1,N_CORR+1):

		# FACTOR_CONTAGIO = random.uniform(0,1)

		# FACTOR_MUTA = random.uniform(0,1)

		N = N_INI
		S = N_INI - I_INI
		IS = I_INI
		IE = 0
		M = 0
		DIA = 0
		COSTO_DIARIO = 0
		COSTO_ENFERMEDAD_FINAL = 0
		COSTO_MUERTE_ACUMULADO = 0
		COSTO_TOTAL = 0

		print("Corriendo simulacion "+str(i)+"...")

		env = simpy.Environment()

		env.process(setup(env,i))

		env.run(until=D_CORR+1)

		COSTO_ENFERMEDAD_FINAL = IE*COSTO_F_E
		COSTO_MUERTE_ACUMULADO = M*COSTO_MUERTE
		COSTO_TOTAL = COSTO_DIARIO + COSTO_ENFERMEDAD_FINAL + COSTO_MUERTE_ACUMULADO

		writer.writerow({'corrida': i, 'factor_contagio': FACTOR_CONTAGIO,'factor_mutacion': FACTOR_MUTA,'N': N,'I&S': IS,'I&E': IE,'Muertos': M,'S': S,'CostoEAcumulado':COSTO_DIARIO,'CostoEFinal': COSTO_ENFERMEDAD_FINAL,'CostoMuerte': COSTO_MUERTE_ACUMULADO,'CostoTotal': COSTO_TOTAL})

		print("Simulacion "+str(i)+" terminada.\n")


