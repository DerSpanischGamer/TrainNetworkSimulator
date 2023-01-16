import json
import copy
import openpyxl
from json.decoder import JSONDecodeError

# --------- CLASES ---------

class Tren:
	def __init__(self, id, nombre, color, trayectos):
		self.id = id
		self.nombre = nombre
		self.color = color
		
		self.trayectos = trayectos # [ [paradas, ruta, llegadas , salidas], ... ] Array de arrays contiene las paradas (ids de las ciudades), la ruta a seguir (tal y como está en rutasActuales), llegadas y salidas de cada tren (pueden haber varios a la vez con rutas diferentes)

# --------- VARIABLES ---------

trenesF = "Trenes.json"
finaltrenes = []

# --------- CARGAR TRENES ---------

try:
	f = open(trenesF, 'r')
	data = json.loads(f.read())
	
	for i in data: # Meter trenes en la lista
		finaltrenes.append(Tren(i['id'], i['nombre'], i['color'], i['trayectos']))
	
	f.close()
except JSONDecodeError:
	pass

horariosIda = copy.deepcopy(finaltrenes[0].trayectos[0])

# Open the workbook
workbook = openpyxl.load_workbook('Horarios.xlsx', data_only = True)

# Get the active sheet
sheet = workbook['IC1']

start_row = 3
end_row = 16
start_col = 2
end_col = 29

# Loop through the cells in the range and print their values
for row in range(start_row, end_row + 1, 2):
	tiempoLleg = []
	tiempoSali = []
	
	for col in range(start_col, end_col + 1):
		tiempoLleg.append(sheet.cell(row = row, column = col).value)
		tiempoSali.append(sheet.cell(row = row + 1, column = col).value)
	
	curr = copy.deepcopy(horariosIda)
	
	curr[2] = copy.deepcopy(tiempoLleg)
	curr[3] = copy.deepcopy(tiempoSali)
	
	finaltrenes[0].trayectos.append(copy.deepcopy(curr))

print(finaltrenes[0].trayectos)


# --------- GUARDAR TRENES ---------

global finaltrenes
	
with open(trenesF, "w+") as f:
	json.dump([t.__dict__ for t in finaltrenes], f, indent = 4)
	f.close()
	