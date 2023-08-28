# ESTRUCTURA EXCEL : CADA TREN SE PONE EN UNA HOJA DIFERENTE, EN LA PRIMERA FILA SE PONEN LOS LIMITES DE DONDE SE DEBE LEER
#							 minX1 | maxX1 | minY1 | maxY1 | minX2 | maxX2 | minY2 | maxY2

import json
import copy
from tqdm import tqdm
import openpyxl
from json.decoder import JSONDecodeError

# ============ EN DESARROLLO ============

# ============ MÁS TARDE ============

# TODO : VERIFICAR QUE TODO ESTE OK (CIUDADES)
# TODO : NO COPAR EL PRIUMER TRAYECTO DE IDA Y SOLO INVERTIRLO (LIKE BRUH) POR LO MENOS BORRARLO, YA QUE LOS HORARIOS ESTAN MAL
# TODO : ACEPTAR LINEAS QUE A VECES SE SALTAN PARADAS (TIPO IC61)

# --------- CLASES ---------

class Tren:
	def __init__(self, id, nombre, color, trayectos):
		self.id = id
		self.nombre = nombre
		self.color = color
		
		self.trayectos = trayectos # [ [paradas, ruta, llegadas , salidas], ... ] Array de arrays contiene las paradas (ids de las ciudades), la ruta a seguir (tal y como está en rutasActuales), llegadas y salidas de cada tren (pueden haber varios a la vez con rutas diferentes)

class Ciudad:
	def __init__(self, id, nombre, x, y):
		self.id = id
		self.nombre = nombre
		self.x = x
		self.y = y

# --------- VARIABLES ---------

horariosF = "Horarios.xlsx" # Nombre del archivo en el que se leen los horarios

ciudadesF = "Ciudades.json" # Nombre des archivo en el que se leen las ciudades para verificar
trenesF = "Trenes.json" # Nombre del archivo en el que se leen y guardan los trenes

finalciudades = [] # Finalciudades como en los otros scripts

finaltrenes = [] # Finaltrenes como en los otros scripts
trenesEscribir = [] # Finaltrenes para ser escrito

# --------- FUNCIONES ---------

def getCiudadfromId(id): 	# Devuelve la ciudad desde una id
	for c in finalciudades:
		if (c.id == id):
			return c
	return None

def idC2ciudades(ids): 		# Recibe un array con ids de ciudades y devuelve un array con los nombres de las ciudades
	temp = []
	for id in ids:
		c = getCiudadfromId(id)
		if (c == None):
			print("Error inesperado, el id de una parada de tren no existe")
			return None
		
		temp.append(c.nombre)
	return temp

def int2hora(horaInt):
    temp = str(horaInt)
    return ('0' * (4 - len(temp))) + temp

def cargarCiudades():
	global canvas, finalciudades
	
	print("Cargando ciudades")
	
	try:
		f = open(ciudadesF, 'r')
		data = json.loads(f.read())
		
		for i in data: # Dibujar ciudades
			temp = Ciudad(i['id'], i['nombre'], i['x'], i['y'])
			finalciudades.append(temp)
		
		f.close()
	except JSONDecodeError:
		print("Error leyendo las ciudades")
		pass
	
	print(len(finalciudades), "ciudades cargadas")

def cargarTrenes():
	global finaltrenes
	
	print("Cargando trenes")
	
	try:
		f = open(trenesF, 'r')
		data = json.loads(f.read())
		
		for i in data: # Meter trenes en la lista
			finaltrenes.append(Tren(i['id'], i['nombre'], i['color'], i['trayectos']))
		
		f.close()
	except JSONDecodeError:
		print("Error leyendo los trenes")
		pass
	
	print(len(finaltrenes), "trenes cargados")

def procesarTrenes():
	for i in tqdm(range(len(finaltrenes)), unit = "Trenes"): # Bucle que pasa por todos los trenes ya existentes
		sheet = workbook[finaltrenes[i].nombre]
		
		if (sheet == None): continue # Si no existe una hoja con el nombre del tren -> ignorar (TODO : AÑADIR EL TREN AUNQUE NO ESTE EN EL EXCEL) <- the fuck he talking about
		
		# Coger el primer horario que deberia ser de ida
		horariosIda = copy.deepcopy(finaltrenes[i].trayectos[0])
		
		# Comprobar que las ciudades que pasa son las mismas que las del Excel
		ciudades = horariosIda
		
		# Crear la base de los horarios de vuelta (lo mismo que de ida pero al reves)
		horariosVuelta = copy.deepcopy(finaltrenes[i].trayectos[0])	# Los trayectos de vuelta son iguales que los de ida, excepto que se invierte el orden de las paradas TODO : DONT ? ESTO LO QUE HACE ES AÑADIR UN TRAYECTO CON EL *MISMO* HORARIO QUE EL PRIMER TRAYECTO DE IDA
		horariosVuelta[0] = horariosVuelta[0][::-1] # Invertir las paradas
		horariosVuelta[1] = horariosVuelta[1][::-1] # Invertir la ruta
		
		trenesEscribir.append(Tren(finaltrenes[i].id, finaltrenes[i].nombre, finaltrenes[i].color, [])) # Crear un trayecto vacio
		trenesEscribir[i].trayectos.append(copy.deepcopy(horariosIda))
		
		curr = copy.deepcopy(horariosIda)
		
		# Leer valores para empezar el trayecto de ida
		start_col = sheet.cell(row = 1, column = 1).value
		end_col = sheet.cell(row = 1, column = 2).value
		start_row = sheet.cell(row = 1, column = 3).value
		end_row = sheet.cell(row = 1, column = 4).value
		
		if (end_row + 1 - start_row != len(curr[2])): 	continue
		
		for col in range(start_col, end_col, 2):
			tiempoLleg = []
			tiempoSali = []
			
			for row in range(start_row, end_row + 1):
				tiempoLleg.append(int2hora(sheet.cell(row = row, column = col).value))
				tiempoSali.append(int2hora(sheet.cell(row = row, column = col + 1).value))
			
			curr[2] = copy.deepcopy(tiempoLleg)
			curr[3] = copy.deepcopy(tiempoSali)
			trenesEscribir[i].trayectos.append(copy.deepcopy(curr))
		
		# Leer valores para empezar el trayecto de vuelta
		start_col = sheet.cell(row = 1, column = 5).value
		end_col = sheet.cell(row = 1, column = 6).value
		start_row = sheet.cell(row = 1, column = 7).value
		end_row = sheet.cell(row = 1, column = 8).value
		
		curr = copy.deepcopy(horariosVuelta)
		
		if (end_row + 1 - start_row != len(curr[3])):
			print(sheet.title, end_row + 1 - start_row , "paradas en el Excel, se esperaban", len(curr[3]), "paradas")
			continue
		
		print("Yendo de", openpyxl.utils.cell.get_column_letter(start_col), openpyxl.utils.cell.get_column_letter(end_col), start_row, end_row)
		
		for col in range(start_col, end_col, 2):
			tiempoLleg = []
			tiempoSali = []
			
			for row in range(start_row, end_row + 1):
				llegada = int2hora(sheet.cell(row = row, column = col).value)
				salida  = int2hora(sheet.cell(row = row, column = col + 1).value)
				
				if (salida <= llegada):
					print("Hora incorrecta para " + sheet.title + ", la hora de salida", salida, "es inferior o igual a la hora de llegada", llegada)
					break
				
				tiempoLleg.append(llegada)
				tiempoSali.append(salida)
			
			curr[2] = copy.deepcopy(tiempoLleg)
			curr[3] = copy.deepcopy(tiempoSali)
			trenesEscribir[i].trayectos.append(copy.deepcopy(curr))

# --------- INIT FUNCTS ---------

cargarCiudades()
cargarTrenes()

workbook = openpyxl.load_workbook(horariosF, data_only = True) # Cargar los horarios en el Excel

if (len(finaltrenes) > 0 and len(finalciudades) > 0): # Sanity check
	procesarTrenes()
else:
	quit()

# --------- GUARDAR TRENES ---------

with open(trenesF, "w+") as f:
	json.dump([t.__dict__ for t in trenesEscribir], f, indent = 4)
	f.close()