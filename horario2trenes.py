# ESTRUCTURA EXCEL : CADA TREN SE PONE EN UNA HOJA DIFERENTE, EN LA PRIMERA FILA SE PONEN LOS LIMITES DE DONDE SE DEBE LEER
#							 minX1 | maxX1 | minY1 | maxY1 | minX2 | maxX2 | minY2 | maxY2

import json
import copy
import openpyxl
from tqdm import tqdm
from openpyxl.styles import Font
from json.decoder import JSONDecodeError

# ============ EN DESARROLLO ============

# TODO : ACEPTAR LINEAS QUE A VECES SE SALTAN PARADAS (TIPO IC61)

# ============ MÁS TARDE ============

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

def getPosParadaRuta(idP, ruta):	# Devuelve la posicion de la parada con id "idP" en la ruta "ruta" (trayecto[1]) 
	for r in range(len(ruta)):
		if (idP == ruta[r][0]): return r
	
	return -1

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
	if(horaInt == None): return None
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

def verificarCiudades(tener, tiene):	# Verificar que la lista "tiene" tiene todas las paradas en "tener" en el mismo orden
	for i in range(len(tener)):
		if (tener[0] != tiene[0]): return i
		
		del tener[0]
		del tiene[0]
	
	return -1

def crearLinea(i, ciuds):
	print("Creando hoja para " + finaltrenes[i].nombre)
	nuevoTren = workbook.create_sheet(title = finaltrenes[i].nombre)
	
	# Añadir el primer horario
	nuevoTren.cell(row = 1, column = 1, value = 2)
	nuevoTren.cell(row = 1, column = 2, value = 3)
	nuevoTren.cell(row = 1, column = 3, value = 4)
	nuevoTren.cell(row = 1, column = 4, value = 3 + len(ciuds))
	
	# Añadir el texto del tren
	negrita = Font(bold = True, size = 10, name = "Arial")
	
	nuevoTren.merge_cells("A2:C2")
	nuevoTren.cell(row = 2, column = 1, value = finaltrenes[i].nombre).font = negrita
	
	nuevoTren.cell(row = 3, column = 1, value = "Parada").font = negrita
	nuevoTren.cell(row = 3, column = 2, value = "Llegada").font = negrita
	nuevoTren.cell(row = 3, column = 3, value = "Salida").font = negrita
	
	# Añadir los datos del tren actual
	for c in range(len(ciuds)):
		nuevoTren.cell(row = c + 4, column = 1, value = ciuds[c]).font = negrita		# Añadir las paradas del tren
		
		nuevoTren.cell(row = c + 4, column = 2, value = finaltrenes[i].trayectos[0][2][c])	# Añadir el horario actual de llegada
		nuevoTren.cell(row = c + 4, column = 3, value = finaltrenes[i].trayectos[0][3][c])	# Añadir el horario actual de salida
	
	# Añadir el texto de la vuelta
	nuevoTren.cell(row = 1, column = 5, value = 2)
	nuevoTren.cell(row = 1, column = 6, value = 2)
	nuevoTren.cell(row = 1, column = 7, value = 9 + len(ciuds))
	nuevoTren.cell(row = 1, column = 8, value = 8 + (2 * len(ciuds)))
	
	nuevoTren.merge_cells('A' + str(7 + len(ciuds)) + ":C" + str(7 + len(ciuds)))
	nuevoTren.cell(row = 7 + len(ciuds), column = 1, value = finaltrenes[i].nombre).font = negrita
	
	nuevoTren.cell(row = 8 + len(ciuds), column = 1, value = "Parada").font = negrita
	
	# Añadir las paradas para el horario de vuelta
	ciuds.reverse()
	for c in range(len(ciuds)):	nuevoTren.cell(row = c + 9 + len(ciuds), column = 1, value = ciuds[c]).font = negrita # Añadir las paradas del tren
	
	workbook.save(horariosF)	# Guardar el archivo

def procesarTrenes():
	for i in tqdm(range(len(finaltrenes)), unit = "Trenes"):		# Bucle que pasa por todos los trenes ya existentes
		horariosIda = copy.deepcopy(finaltrenes[i].trayectos[0])	# Coger el primer horario que deberia ser de ida
		trenesEscribir.append(Tren(finaltrenes[i].id, finaltrenes[i].nombre, finaltrenes[i].color, [])) # Crear un trayecto vacio
		trenesEscribir[i].trayectos.append(copy.deepcopy(horariosIda))
		
		# Coger el nombre de las ciudades
		ciudades = copy.deepcopy(horariosIda[0])
		for c in range(len(ciudades)):
			ciudades[c] = getCiudadfromId(ciudades[c]).nombre.upper()
		
		# Coger la línea del tren desde el Excel si existe, si no, crearla
		try:
			sheet = workbook[finaltrenes[i].nombre]
		except KeyError:
			crearLinea(i, copy.deepcopy(ciudades))
			sheet = workbook.create_sheet(finaltrenes[i].nombre)	# Crear la hoja si no existe
			continue
		
		# Crear la base de los horarios de vuelta (lo mismo que de ida pero al reves)
		horariosVuelta = copy.deepcopy(finaltrenes[i].trayectos[0])	# Los trayectos de vuelta son iguales que los de ida, excepto que se invierte el orden de las paradas
		horariosVuelta[0] = horariosVuelta[0][::-1] # Invertir las paradas
		horariosVuelta[1] = horariosVuelta[1][::-1] # Invertir la ruta
		
		curr = copy.deepcopy(horariosIda)
		
		# Leer valores para empezar el trayecto de ida
		start_col = sheet.cell(row = 1, column = 1).value
		end_col = sheet.cell(row = 1, column = 2).value
		start_row = sheet.cell(row = 1, column = 3).value
		end_row = sheet.cell(row = 1, column = 4).value
		
		# Verificar ciudades de ida
		res = verificarCiudades(copy.deepcopy(ciudades), [str(sheet.cell(row = r, column = 1).value).upper() for r in range(start_row, end_row + 1)])
		if (res != -1):
			print("El nombre de las ciudades para la línea", sheet.title, "no concuerda. Se esperaba", ciudades[res], "se encontró", sheet.cell(row = start_row + res, column = 1).value)
			continue
		
		if (end_row + 1 - start_row != len(curr[2])):
			print(sheet.title, end_row + 1 - start_row , "paradas en el Excel, se esperaban", len(curr[2]), "paradas")
			continue
		
		for col in range(start_col, end_col, 2):
			curr = copy.deepcopy(horariosIda)	# Resetear el horario de ida por si se han borrado paradas
			
			tiempoLleg = []
			tiempoSali = []
			
			for row in range(start_row, end_row + 1):
				llegada = int2hora(sheet.cell(row = row, column = col).value)
				salida = int2hora(sheet.cell(row = row, column = col + 1).value)
				
				if (salida == None and llegada == None):
					idParada = curr[0].pop(row - start_row)		# Quitar la parada de la lista de paradas del trayecto
					pos = getPosParadaRuta(idParada, curr[1])
					
					if (pos == -1):
						print("La parada no se ha encontrado en la ruta. Saliendo"	)
						quit()
					else: curr[1][pos][0] = -1	# Anotar en la ruta que ya no es una parada si no una ruta de paso
				elif (salida <= llegada):
					print("Hora incorrecta para " + sheet.title + ", la hora de salida", salida, "es inferior o igual a la hora de llegada", llegada)
					break
				
				# TODO : MAYBE DO SOME SANITY CHECK THAT EITHER salida NOR llegada ARE None ON THEIR OWN
				
				tiempoLleg.append(llegada)
				tiempoSali.append(salida)
				
			curr[2] = copy.deepcopy(tiempoLleg)
			curr[3] = copy.deepcopy(tiempoSali)
			trenesEscribir[i].trayectos.append(copy.deepcopy(curr))
		
		# Leer valores para empezar el trayecto de vuelta
		start_col = sheet.cell(row = 1, column = 5).value
		end_col = sheet.cell(row = 1, column = 6).value
		start_row = sheet.cell(row = 1, column = 7).value
		end_row = sheet.cell(row = 1, column = 8).value
		
		curr = copy.deepcopy(horariosVuelta)
		
		# Verificar ciudades de ida
		ciudades.reverse()
		res = verificarCiudades(copy.deepcopy(ciudades), [str(sheet.cell(row = r, column = 1).value).upper() for r in range(start_row, end_row + 1)])
		if (res != -1):
			print("El nombre de las ciudades para la línea", sheet.title, "no concuerda. Se esperaba", ciudades[res], "se encontró", sheet.cell(row = start_row + res, column = 1).value)
			continue
		
		if (end_row + 1 - start_row != len(curr[3])):
			print(sheet.title, end_row + 1 - start_row , "paradas en el Excel, se esperaban", len(curr[3]), "paradas")
			continue
		
		for col in range(start_col, end_col, 2):
			curr = copy.deepcopy(horariosVuelta)	# Resetear el horario de vuelta por si se han borrado paradas
				
			tiempoLleg = []
			tiempoSali = []
			
			for row in range(start_row, end_row + 1):
				llegada = int2hora(sheet.cell(row = row, column = col).value)
				salida  = int2hora(sheet.cell(row = row, column = col + 1).value)
				
				
				if (salida == None and llegada == None):
					idParada = curr[0].pop(row - start_row)		# Quitar la parada de la lista de paradas del trayecto
					pos = getPosParadaRuta(idParada, curr[1])
					
					if (pos == -1):
						print("La parada no se ha encontrado en la ruta. Saliendo"	)
						quit()
					else: curr[1][pos][0] = -1	# Anotar en la ruta que ya no es una parada si no una ruta de paso
				elif (salida <= llegada):
					print("Hora incorrecta para " + sheet.title + ", la hora de salida", salida, "es inferior o igual a la hora de llegada", llegada)
					break
				
				# TODO : MAYBE DO SOME SANITY CHECK THAT EITHER salida NOR llegada ARE None ON THEIR OWN
				
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