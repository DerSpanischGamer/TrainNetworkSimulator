# USO: python cancionVideo.py "ARCHIVO.amds"
# Nota: siempre va a guardar los archivos en una carpeta llamada output

# ------------ LIBRERIAS ------------

import os
import sys
import numpy as np
import json
from PIL import Image, ImageDraw, ImageFont

# ------------ CLASES ------------

class Ciudad:
	def __init__(self, id, nombre, x, y):
		self.id = id
		self.nombre = nombre
		self.x = x
		self.y = y

class Ruta:
	def __init__(self, id, ruta, paradas): # pos : es un array con arrays que contienen [x, y] ; paradas : es un array con las paradas que hace [-1 transito ; id parada]
		self.id = id
		self.ruta = ruta
		self.paradas = paradas

class Tren:
	def __init__(self, id, nombre, color, trayectos):
		self.id = id
		
		self.nombre = nombre
		
		self.color = color
		
		self.trayectos = trayectos # [ [paradas, ruta, llegadas , salidas], ... ] donde, cada elemento de ruta es [ciudad.id | -1 , [x, y]] Array de arrays contiene las paradas (ids de las ciudades), la ruta a seguir (tal y como está en rutasActuales), llegadas y salidas de cada tren (pueden haber varios a la vez con rutas diferentes)

class EntidadTren:
	def __init__(self, color, ruta, initH, fintH, moviendose): # origen y destino contienen [id, hora]
		self.color = color
		
		self.initH = initH # Guarda todas las horas de salida   
		self.fintH = fintH # Guarda todas las horas de llegada  SE VAN BORRANDO CONFORME NO SEAN UTILES, ASI SIEMPRE ESTAN EN 0
		
		self.ruta = ruta # Guarda toda la ruta que tiene que seguir el tren. Se va borrando una vez se llega a una parada
		
		self.moviendose = moviendose # Boolean : False = en parada ; True = en medio de una ruta
		
		self.disTot = 0 # Distancia total a recorrer entre parada y parada

# ------------ VARIABLES ------------

FPS = 10
SPM = 0.1 # Segundos por minuto ; ATENCION : ¡¡¡ El producto de FPS y SPM tiene que ser un numero entero !!!

fondo = "Mapa.png"

ciudadesF = "Ciudades.json"
rutasF = "Rutas.json"
trenesF = "Trenes.json"

rutas = [] # Guarda todas las clases Ruta
ciudades = [] # Guarda todas las clases Ciudad
finaltrenes = [] # Guarda todos las clases Trenes (finaltrenes)

trenes = [] # Guarda todas las clases EntidadTren

initH = 600
fintH = 800
horaAct = initH # Hora actual

fotograma = None # Guarda el fondo sobre el que se van a dibujar los trenes
frame = None # Guarda el elemento para dibujar
outputF = "trenes" # Nombre del archivo de video

# ------------ FUNCIONES ------------

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
	return ((hora // 100) * 60) + (hora - (hora // 100)*100)

def diferenciaHoras(h0, h1): # Devuelve la diferencia en minutos [ h1 > h0 ]
	if (h0 > h1):
		c = h1
		h1 = h0
		h0 = c
	
	return hora2mins(h1) - hora2mins(h0)

def dibujarReloj(x, y):  # x, y son el centro del reloj
	global draw, horaAct

	draw.ellipse()

def actualizarTrenes():
	global finaltrenes, trenes, horaAct
	
	for tren in trenes: # Primero mirar si algun tren ha llegado a la parada
		if (tren.moviendose and tren.initH[0] == horaAct):
			tren.moviendose = False
			tren.disTot = 0
			
			del tren.initH[0] # Eliminar la parada de llegada ya que ya estamos en la parada
			del tren.fintH[0]
			
			i = 1
			while (tren.ruta[i][0] == -1):	i += 1
			
			del tren.ruta[0:i]

	for tren in finaltrenes:	# Mirar si hay algun tren que tenga que ser añadido
		for tray in tren.trayectos: # Mirar en cada horario
			if (horaAct == tray[2][0]):
				trenes.append(EntidadTren(tren.color, tray[1], tray[2], tray[3], False))
				
				del trenes[-1].initH[0]
	
	for i in range(len(trenes), 0, -1):		# Mirar si hay trenes que se tienen que despawnear : recorrer la lista al reves para ir borrando
		if (len(trenes[i - 1].fintH) == 1 and horaAct == trenes[i - 1].fintH[0]):
			del trenes[i - 1]
	
	for tren in trenes: # Por ultimo mirar si hay que sacar algun tren la estacion
		if (not tren.moviendose and tren.fintH[0] == horaAct):
			tren.moviendose = True
			tren.disTot = 0 # Sanity check (no deberia ser util)
			
			print("Salida estacion")
			
			for i in range(1, len(tren.ruta)): # Calcular la distancia total que tiene que transcurrir el tren
				tren.disTot += distancia(tren.ruta[i - 1][1][0], tren.ruta[i - 1][1][1], tren.ruta[i][1][0], tren.ruta[i][1][1])
				
				if (tren.ruta[i][0] != -1): break # Es la parada en la que hay que pararse

def calcularPosiciones():
	global finaltrenes, draw, trenes
	
	for tren in trenes:
		if (tren.moviendose):
			disRec = 0
			i = 1
			
			disAct = tren.disTot * linAprox(hora2mins(tren.initH[0]), hora2mins(tren.fintH[0]), hora2mins(horaAct))
			
			print(tren.fintH[0], horaAct, tren.initH[0], linAprox(hora2mins(tren.initH[0]), hora2mins(tren.fintH[0]), hora2mins(horaAct)), disAct)
			
			while (i < len(tren.ruta) and disRec < disAct):
				disRec += distancia(tren.ruta[i - 1][1][0], tren.ruta[i - 1][1][1], tren.ruta[i][1][0], tren.ruta[i][1][1])
				i += 1
			
			dist = distancia(tren.ruta[i - 2][1][0], tren.ruta[i - 2][1][1], tren.ruta[i - 1][1][0], tren.ruta[i - 1][1][1])
			
			perc = (disRec - disAct) / dist # Porcentaje de distancia recorrida en pixeles
			
			x = tren.ruta[i - 1][1][0] + perc * (tren.ruta[i - 2][1][0] - tren.ruta[i - 1][1][0])
			y = tren.ruta[i - 1][1][1] + perc * (tren.ruta[i - 2][1][1] - tren.ruta[i - 1][1][1])
			
			draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill = tren.color, outline = tren.color)

def progressBar(iterable, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"): # Proudly stolen from Stackoverflow
    """
    Call in a loop to create terminal progress bar
    @params:
        iterable    - Required  : iterable object (Iterable)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)
    # Progress Bar Printing Function
    def printProgressBar (iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print()

def dibujarFotograma():
	global fotograma, horaAct, draw
	
	frames = [i for i in range(int(FPS * SPM * diferenciaHoras(initH, fintH)))] # Hacer una lista de todos los frames
	
	# for i in progressBar(frames, prefix = 'Progreso:', suffix = 'Completado', length = 50):
	for i in frames:
		frame = fotograma.copy()
		draw = ImageDraw.Draw(frame)
		
		if ((i + 1) % (FPS * SPM) == 0):
			horaAct = horaInc(horaAct)
			actualizarTrenes()

		calcularPosiciones()
		
		font = ImageFont.truetype("arial.ttf",  16)
		draw.text((0, 0), str(horaAct), "#00ff00", font = font)

		frame.save("output/" + str(i) + "_Suiza.png")		# Guardar el fotograma
		draw = None
	
	
	print("Acabado")

def prepararFondo():
	global fotograma, rutas, ciudades
	
	draw = ImageDraw.Draw(fotograma)
	
	# ======= DIBUJAR RUTAS =======
	for r in rutas:
		draw.line(r.ruta, width = 1, fill = "black")
	
	# ======= DIBUJAR CIUDADES =======
	for c in ciudades:
		draw.rectangle([(c.x - 2, c.y - 2), (c.x + 2, c.y + 2)], fill = "red", outline = "red")

def main():
	global fotograma
	print("Running")
	
	fotograma = Image.open(fondo)
	
	prepararFondo()
	
	dibujarFotograma()

# ==================== INIT FUNCTIONS ====================

def cargarCiudades():
	global ciudades
	
	print("Cargando ciudades")
	
	f = open(ciudadesF, 'r')
	data = json.loads(f.read())
	
	for i in data: # Dibujar ciudades
		ciudades.append(Ciudad(i['id'], i['nombre'], i['x'], i['y']))
	
	f.close()
	
	print(len(ciudades), "ciudades cargadas")

def cargarRutas():
	global rutas

	print("Cargando rutas")
	
	f = open(rutasF, 'r')
	data = json.loads(f.read())
	
	for i in data: # Dibujar rutas
		temp = []
		for punto in i['ruta']:
			temp.append(tuple(punto))
		
		rutas.append(Ruta(i['id'], temp, i['paradas']))
	
	f.close()
	
	print(len(rutas), "rutas cargadas")

def cargarTrenes():
	global finaltrenes
	
	print("Cargando trenes")
	
	f = open(trenesF, 'r')
	data = json.loads(f.read())
	
	for i in data: # Meter trenes en la lista
		finaltrenes.append(Tren(i['id'], i['nombre'], i['color'], i['trayectos']))
		for tray in finaltrenes[-1].trayectos:
			for i in range(len(tray[2])):
				tray[2][i] = int(tray[2][i])
				tray[3][i] = int(tray[3][i])
	
	f.close()
	
	print(len(finaltrenes), "trenes cargados")

cargarCiudades()
print()
cargarRutas()
print()
cargarTrenes()
print()

main()

os.system('ffmpeg -r ' + str(FPS) + ' -s 1920x1080 -i output/%d_Suiza.png -vcodec libx264 -crf 15 -y -pix_fmt yuv420p ' + outputF + '.mp4') # Create video