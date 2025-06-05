# USO: python network.py
# Nota: siempre va a guardar los archivos en una carpeta llamada output

# ------------ LIBRERIAS ------------

import os
import sys
import json
import copy
import math
import numpy as np
from tqdm import tqdm
from PIL import Image, ImageDraw, ImageFont

# ============ EN DESARROLLO ============

# ============ MÁS TARDE ============

# ------------ CLASES ------------

class Ciudad:
	def __init__(self, id, nombre, coords):
		self.id = id
		self.nombre = nombre
		self.coords = coords

class Punto:
	def __init__(self, coords, parada, id_ciudad): # Cuando es usado para ruta, parada siempre es False y ciudad = None si no hay ciudad
		self.coords = coords
		self.parada = parada
		self.id_ciudad = id_ciudad

class Ruta:
	def __init__(self, id, puntos):
		self.id = id
		self.puntos = puntos

class Trayecto:
	def __init__(self, puntos, salidas, llegadas):
		self.puntos = puntos
		
		self.llegadas = llegadas
		self.salidas = salidas

class Linea:
	def __init__(self, id, nombre, color, trayectos, rutas):
		self.id = id
		self.nombre = nombre
		self.color = color
		
		self.trayectos = trayectos
		self.rutas = rutas

class EntidadTren:
	def __init__(self, imagen, ruta, initH, fintH, moviendose): # origen y destino contienen [id, hora]
		self.imagen = imagen # Posicion en el array imagenes del logo de la linea
		
		self.initH = initH # Guarda todas las horas de salida   
		self.fintH = fintH # Guarda todas las horas de llegada (se van borrando conforme no sean utiles, asi siempre esten en la posicion 0)
		
		self.ruta = ruta # Guarda toda la ruta que tiene que seguir el tren. Se va borrando una vez se llega a una parada
		
		self.moviendose = moviendose # Boolean : False = en parada ; True = en medio de una ruta
		
		self.disTot = 0 # Distancia total a recorrer entre parada y parada

# ------------ VARIABLES ------------

FPS = 30
SPM = 0.1 # Segundos por minuto ; ATENCION : ¡¡¡ El producto de FPS y SPM tiene que ser un numero entero !!!

fondo = "Mapa.png"

ciudadesF = "Ciudades.json"
rutasF = "Rutas.json"
lineasF = "LineasIR_output.json"
imagesF = "line2image.json"

rutas = [] # Guarda todas las clases Ruta
ciudades = [] # Guarda todas las clases Ciudad
lineas = [] # Guarda todos las clases Trenes (lineas)
images = [] # Guarda las imagenes de las lineas
linea2imagen = None # Diccionario que guarda la posicion en imagenes de la imagen correspondiente a cada linea

img_width = 50
img_height = int(0.43 * img_width)

trenes = [] # Guarda todas las clases EntidadTren

initH = 400  # Hora de inicio
fintH = 2300 # Hora de fin
horaAct = initH # Hora actual = Hora de inicio

fotograma = None # Guarda el fondo sobre el que se van a dibujar los trenes
frame = None # Guarda el elemento para dibujar
outputF = "trenes" # Nombre del archivo de video
borrarArchivos = True # Define si se tienen que borrar archivos una vez se haya acabado de crear el video

# ------------ FUNCIONES ------------

def formatHora(): # Devuelve la hora en formato xxhyy
	global horaAct
	hora = '0'*(2 - len(str(horaAct // 100))) + str(horaAct // 100)
	minuto = '0'*(2 - len(str(horaAct % 100))) + str(horaAct % 100)
	return hora + 'h' + minuto

def horaInc(hora): # Incrementar la hora
	hora += 1
	if ( (hora - (hora // 100)*100) % 60 == 0): hora += 40 # Pasar de 0060 a 0100
	
	return hora

def linAprox(x0, x1, x): # x1 > x0 ; si x = x0 => 0, si x = x1 => 1
	if (x0 > x1):
		c = x1
		x1 = x0
		x0 = c
	
	return (x - x0) / (x1 - x0)

def distancia(x0, y0, x1, y1): # Calcula la distancia entre dos puntos
	return ( (x1 - x0)**2 + (y1 - y0)**2 )**(1/2)

def hora2mins(hora):
	hora = int(hora)
	return ((hora // 100) * 60) + (hora - (hora // 100)*100)

def diferenciaHoras(h0, h1): # Devuelve la diferencia en minutos [ h1 > h0 ]
	if (h0 > h1):
		c = h1
		h1 = h0
		h0 = c
	
	return hora2mins(h1) - hora2mins(h0)

def dibujarReloj():
	global draw, horaAct
	
	# Definir las propiedades del reloj
	hora = horaAct // 100
	minuto = horaAct - (hora * 100)
	
	relojTam = 256
	relojCent = relojTam // 2
	
	horaLen = 0.32 * relojTam
	minuLen = 0.45 * relojTam
	
	mark_length = 0.1 * relojTam
	
	# Dibujar las marcas del reloj
	for i in range(4):
		angulo = i * math.pi / 2
		dx = mark_length * math.cos(angulo)
		dy = mark_length * math.sin(angulo)
	
	# Calcular los angulos
	angHora = 2 * math.pi * (hora / 12.0 + minuto / 720.0) - (math.pi / 2)
	hour_dx = horaLen * math.cos(angHora)
	hour_dy = horaLen * math.sin(angHora)
	
	angMinuto = 2 * math.pi * (minuto / 60.0) - (math.pi / 2)
	minute_dx = minuLen * math.cos(angMinuto)
	minute_dy = minuLen * math.sin(angMinuto)
	
	# Dibujar las manillas del reloj
	draw.line((relojCent, relojCent, relojCent + hour_dx, relojCent + hour_dy), fill = 'black', width = 12)		# Horas 
	draw.line((relojCent, relojCent, relojCent + minute_dx, relojCent + minute_dy), fill = 'black', width = 8)	# Minutos
	draw.ellipse((0, 0, relojTam - 1, relojTam - 1), outline = 'black', width = 2)								# Circulo
	
	# Dibujar las marcas del reloj (minutos)
	barraLen = - relojCent / 10
	angle = 2 * math.pi / 60
	
	points = [(relojCent + int(relojCent * math.cos(angle * i)),  relojCent - int(relojCent * math.sin(angle * i)), relojCent + int((relojCent + barraLen) * math.cos(angle * i)), relojCent - int((relojCent + barraLen) * math.sin(angle * i))) for i in range(60)]
	for x1, y1, x2, y2 in points:
		draw.line((x1, y1, x2, y2), fill = 'black', width = 4)
	
	# Dibujar las marcas del reloj (horas)
	barraLen = - relojCent / 4
	angle = 2 * math.pi / 12
	
	points = [(relojCent + int(relojCent * math.cos(angle * i)),  relojCent - int(relojCent * math.sin(angle * i)), relojCent + int((relojCent + barraLen) * math.cos(angle * i)), relojCent - int((relojCent + barraLen) * math.sin(angle * i))) for i in range(12)]
	for x1, y1, x2, y2 in points:
		draw.line((x1, y1, x2, y2), fill = 'black', width = 6)

def actualizarTrenes():
	global lineas, trenes, horaAct
	
	for tren in trenes: # Primero mirar si algun tren ha llegado a la parada
		if (tren.moviendose and tren.initH[0] == horaAct):
			tren.moviendose = False
			tren.disTot = 0
			
			del tren.initH[0] # Eliminar la parada de llegada ya que ya estamos en la parada
			del tren.fintH[0]
			
			if (len(tren.ruta.puntos) > 1): # No tiene que desaparecer
				i = 1
				while (tren.ruta.puntos[i].parada == False):
					i += 1
				
				del tren.ruta.puntos[0:i]

	for i in range(len(trenes), 0, -1):		# Mirar si hay trenes que se tienen que despawnear : recorrer la lista al reves para ir borrando
		if (len(trenes[i - 1].fintH) == 1 and horaAct == trenes[i - 1].fintH[0]):
			del trenes[i - 1]
	
	for tren in lineas:	# Mirar si hay algun tren que tenga que spawnear
		for i in range(len(tren.trayectos)): # Mirar en cada horario
			tray = copy.deepcopy(tren.trayectos[i])
			if (horaAct == int(tray.llegadas[0])):
				trenes.append(EntidadTren(linea2imagen[tren.nombre], copy.deepcopy(tren.rutas[i]), copy.deepcopy(tray.llegadas), copy.deepcopy(tray.salidas), False))
				
				del trenes[-1].initH[0]
	
	for tren in trenes: # Por ultimo mirar si hay que sacar algun tren la estacion
		if (not tren.moviendose and tren.fintH[0] == horaAct):
			tren.moviendose = True
			tren.disTot = 0 # Sanity check (no deberia ser util)
			
			for i in range(1, len(tren.ruta.puntos)): # Calcular la distancia total que tiene que transcurrir el tren hasta 
				tren.disTot += distancia(tren.ruta.puntos[i - 1].coords[0], tren.ruta.puntos[i - 1].coords[1], tren.ruta.puntos[i].coords[0], tren.ruta.puntos[i].coords[1])
				
				if tren.ruta.puntos[i].parada: break # True -> Es la parada en la que hay que pararse

def calcularPosiciones():
	global lineas, draw, trenes, frame, images
	
	for tren in trenes:
		if tren.moviendose:
			disRec = 0
			i = 1
			
			disAct = tren.disTot * linAprox(hora2mins(tren.initH[0]), hora2mins(tren.fintH[0]), hora2mins(horaAct))
			
			while (i < len(tren.ruta.puntos) and disRec < disAct):
				disRec += distancia(tren.ruta.puntos[i - 1].coords[0], tren.ruta.puntos[i - 1].coords[1], tren.ruta.puntos[i].coords[0], tren.ruta.puntos[i].coords[1])
				i += 1
			
			dist = distancia(tren.ruta.puntos[i - 2].coords[0], tren.ruta.puntos[i - 2].coords[1], tren.ruta.puntos[i - 1].coords[0], tren.ruta.puntos[i - 1].coords[1]) # Distancia entre la parada actual y la proxima parada
			
			if (dist != 0):
				perc = (disRec - disAct) / dist # Porcentaje de distancia recorrida en pixeles
			else:
				perc = 1
			
			x = int(tren.ruta.puntos[i - 1].coords[0] + perc * (tren.ruta.puntos[i - 2].coords[0] - tren.ruta.puntos[i - 1].coords[0]))
			y = int(tren.ruta.puntos[i - 1].coords[1] + perc * (tren.ruta.puntos[i - 2].coords[1] - tren.ruta.puntos[i - 1].coords[1]))
			
			frame.paste(images[tren.imagen], (x - images[tren.imagen].width // 2, y - images[tren.imagen].height // 2), images[tren.imagen])

def dibujarFotograma():
	global fotograma, horaAct, draw, frame
	
	frames = [i for i in range(int(FPS * SPM * diferenciaHoras(initH, fintH)))] # Hacer una lista de todos los frames
	
	for i in tqdm(frames, unit = 'Fotogramas'):
		frame = fotograma.copy()
		draw = ImageDraw.Draw(frame)
		
		if ((i + 1) % (FPS * SPM) == 0):
			horaAct = horaInc(horaAct)
			actualizarTrenes()
		
		calcularPosiciones()
		
		font = ImageFont.truetype("arial.ttf",  48)
		dibujarReloj()
		draw.text((256, 128), formatHora(), "#000000", font = font)

		frame.save("output/" + str(i) + "_Suiza.png")		# Guardar el fotograma
		draw = None
	
	print("Acabado")

def prepararFondo():
	global fotograma, rutas, ciudades
	
	draw = ImageDraw.Draw(fotograma)
	
	# ======= DIBUJAR RUTAS =======
	for r in rutas:
		puntos_dibujar =[p.coords for p in r.puntos]
		draw.line([coord for coords in puntos_dibujar for coord in coords], width = 1, fill = "black")
	
	# ======= DIBUJAR CIUDADES =======
	for c in ciudades:
		draw.rectangle([(c.coords[0] - 2, c.coords[1] - 2), (c.coords[0] + 2, c.coords[1] + 2)], fill = "red", outline = "red")

def main():
	global fotograma
	print("Running")
	
	fotograma = Image.open(fondo)
	
	prepararFondo()
	
	dibujarFotograma()

# --- Funciones para cargar datos ---

def cargar_ciudades():
	global ciudadesF, ciudades
	
	try:
		f = open(ciudadesF, 'r')
		data = json.loads(f.read())
		
		for i in data: # Cargar ciudades
			ciudades.append( Ciudad(i['id'], i['nombre'], i['coords']) )
		
	except JSONDecodeError:
		pass

def cargar_rutas():
	global rutasF, rutas
	
	try:
		f = open(rutasF, 'r')
		data = json.loads(f.read())
		
		for i in data: # Cargar ciudades
			puntos = [Punto(p["coords"], p["parada"], p["id_ciudad"]) for p in i["puntos"]]
			ruta = Ruta(i["id"], puntos)
			rutas.append(ruta)
		
	except JSONDecodeError:
		pass

def cargar_lineas():
	global lineas, lineasF, linea_actual
	
	with open(lineasF, "r") as f:
		data = json.load(f)
		
		for linea_dict in data:
			id_linea = linea_dict["id"]
			nombre = linea_dict["nombre"]
			color = linea_dict["color"]

			# Parse trayectos
			trayectos = []
			for trayecto_dict in linea_dict["trayectos"]:
				puntos = [
					Punto(p["coords"], p["parada"], p.get("id_ciudad"))
					for p in trayecto_dict["puntos"]
				]
				salidas = trayecto_dict["salidas"]
				llegadas = trayecto_dict["llegadas"]
				trayectos.append(Trayecto(puntos, salidas, llegadas))

			# Parse rutas
			rutas = []
			for ruta_dict in linea_dict["rutas"]:
				puntos = [
					Punto(p["coords"], p["parada"], p.get("id_ciudad"))
					for p in ruta_dict["puntos"]
				]
				rutas.append(Ruta(ruta_dict["id"], puntos))
			
			lineas.append(Linea(id_linea, nombre, color, trayectos, rutas))
	
	for l in range(len(lineas)):
		for t in range(len(lineas[l].trayectos)):
			for i in range(len(lineas[l].trayectos[t].llegadas)):
				lineas[l].trayectos[t].llegadas[i] = int(lineas[l].trayectos[t].llegadas[i])
				lineas[l].trayectos[t].salidas[i] = int(lineas[l].trayectos[t].salidas[i])

def cargar_imagenes():
	global imagenes, linea2imagen
	
	data = None
	with open(imagesF) as f:
		data = json.load(f)
	
	i = 0
	lin = []
	img = []
	linea2imagen = {}
	for d in data.keys():
		lin.append(d)
		
		if data[d] in img:
			img.append(None)
			linea2imagen[d] = img.index(data[d])
		else:
			images.append(Image.open(data[d]).convert("RGBA"))  # Use RGBA to preserve transparency
			
			scale_factor = 0.9
			
			if "ir" in data[d]: scale_factor = 0.75
			
			images[-1] = images[-1].resize((int(scale_factor * img_width), int(scale_factor * img_height)), Image.Resampling.LANCZOS)
			
			linea2imagen[d] = i
		
		i += 1
	
	


def verificarTrenes(): # Verificar que un tren no se para en dos puntos seguidos
	global lineas
	
	error = False
	
	for linea in lineas:
		for trayecto in linea.trayectos:
			for i in range(len(trayecto[1]) - 1):
				if (trayecto[1][i][1][0] == trayecto[1][i + 1][1][0] and trayecto[1][i][1][1] == trayecto[1][i + 1][1][1]):
					print("Ruta invalida en linea", linea.nombre, "posicion", i)
					print(trayecto[1][i][0], trayecto[1][i][1][0], trayecto[1][i][1][1])
					print(trayecto[1][i+1][0], trayecto[1][i+1][1][0], trayecto[1][i+1][1][1])
					error = True
	
	if (error): quit()

# ==================== INIT FUNCTIONS ====================

# Cargar datos
print("Cargando datos...")
cargar_ciudades()
print()
cargar_rutas()
print()
cargar_lineas()
print()
cargar_imagenes()
print()

# Verificar datos
print("Verificando datos...")
#verificarTrenes()

main()

# ==================== FINAL FUNCTIONS ====================

print("Generando vídeo...")
os.system('ffmpeg -r ' + str(FPS) + ' -s 1920x1080 -i output/%d_Suiza.png -vcodec libx264 -crf 15 -y -pix_fmt yuv420p ' + outputF + '.mp4') # Create video

if (borrarArchivos):
	print("Borrando imagenes...")
	
	files = os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output'))
	
	# Loop through the files and delete them
	for file in files:
		file_path = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output'), file)
		os.remove(file_path)

print("Finish !")