import json
import copy
from tqdm import tqdm
import openpyxl
from json.decoder import JSONDecodeError

# ============ EN DESARROLLO ============

# TODO : VERIFICAR QUE TODO ESTE OK

# ============ MÁS TARDE ============

# --------- CLASES ---------

class Tren:
	def __init__(self, id, nombre, color, trayectos):
		self.id = id
		self.nombre = nombre
		self.color = color
		
		self.trayectos = trayectos # [ [paradas, ruta, llegadas , salidas], ... ] Array de arrays contiene las paradas (ids de las ciudades), la ruta a seguir (tal y como está en rutasActuales), llegadas y salidas de cada tren (pueden haber varios a la vez con rutas diferentes)

# --------- VARIABLES ---------

trenesF = "Trenes.json" # Nombre del archivo en el que se escriben
finaltrenes = [] # Finaltrenes como en los otros scripts
trenesEscribir = [] # Finaltrenes para ser escrito

# --------- FUNCIONES ---------

def int2hora(horaInt):
    temp = str(horaInt)
    return ('0' * (4 - len(temp))) + temp

# --------- CARGAR TRENES ---------

try:
	f = open(trenesF, 'r')
	data = json.loads(f.read())
	
	for i in data: # Meter trenes en la lista
		finaltrenes.append(Tren(i['id'], i['nombre'], i['color'], i['trayectos']))
	
	f.close()
	print("Lectura completada con exito")
except JSONDecodeError:
	print("Error leyendo el JSON")
	pass

workbook = openpyxl.load_workbook('Horarios.xlsx', data_only = True)

# Bucle que pasa por todos los trenes ya existentes
for i in tqdm(range(len(finaltrenes)), unit = "Trenes"):
	sheet = workbook[finaltrenes[i].nombre]
	
	horariosIda = copy.deepcopy(finaltrenes[i].trayectos[0])

	horariosVuelta = copy.deepcopy(finaltrenes[i].trayectos[0])
	horariosVuelta[0] = horariosVuelta[0][::-1]
	horariosVuelta[1] = horariosVuelta[1][::-1]
	
	trenesEscribir.append(Tren(finaltrenes[i].id, finaltrenes[i].nombre, finaltrenes[i].color, [])) # Crear un trayecto vacio
	trenesEscribir[i].trayectos.append(copy.deepcopy(horariosIda))
	trenesEscribir[i].trayectos.append(copy.deepcopy(horariosVuelta))
	
	if (sheet == None): continue # Si no existe una hoja con el nombre del tren -> ignorar (TODO : AÑADIR EL TREN AUNQUE NO ESTE EN EL EXCEL)
	
	# TODO : MIRAR AQUI SI TODO ESTA OK
	
	# Leer valores para empezar el trayecto de ida
	start_col = sheet.cell(row = 1, column = 1).value
	end_col = sheet.cell(row = 1, column = 2).value
	start_row = sheet.cell(row = 1, column = 3).value
	end_row = sheet.cell(row = 1, column = 4).value
	
	for col in range(start_col, end_col + 1, 2):
		tiempoLleg = []
		tiempoSali = []
		
		for row in range(start_row, end_row + 1):
			tiempoLleg.append(int2hora(sheet.cell(row = row, column = col).value))
			tiempoSali.append(int2hora(sheet.cell(row = row, column = col + 1).value))
		
		curr = copy.deepcopy(horariosIda)
		curr[2] = copy.deepcopy(tiempoLleg)
		curr[3] = copy.deepcopy(tiempoSali)
		
		trenesEscribir[i].trayectos.append(copy.deepcopy(curr))
	
	# Leer valores para empezar el trayecto de vuelta
	start_col = sheet.cell(row = 1, column = 5).value
	end_col = sheet.cell(row = 1, column = 6).value
	start_row = sheet.cell(row = 1, column = 7).value
	end_row = sheet.cell(row = 1, column = 8).value
	
	for col in range(start_col, end_col + 1, 2):
		tiempoLleg = []
		tiempoSali = []
		
		for row in range(start_row, end_row + 1):
			tiempoLleg.append(int2hora(sheet.cell(row = row, column = col).value))
			tiempoSali.append(int2hora(sheet.cell(row = row, column = col + 1).value))
		
		curr = copy.deepcopy(horariosVuelta)
		curr[2] = copy.deepcopy(tiempoLleg)
		curr[3] = copy.deepcopy(tiempoSali)
		
		trenesEscribir[i].trayectos.append(copy.deepcopy(curr))

# --------- GUARDAR TRENES ---------

with open(trenesF, "w+") as f:
	json.dump([t.__dict__ for t in trenesEscribir], f, indent = 4)
	f.close()