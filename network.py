# USO: python cancionVideo.py "ARCHIVO.amds"
# Nota: siempre va a guardar los archivos en una carpeta llamada output

# ------------ LIBRERIAS ------------

import sys
import csv
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
		self.trayectos = trayectos

class EntidadTren:
	def __init__(self, color, x, y, origen, destino, ruta): # origen y destino contienen [id, hora]
		self.color = color
		
		self.x = x
		self.y = y
		
		self.origen = origen
		self.destino = destino
		
		self.ruta = ruta

# ------------ VARIABLES ------------

posicion = 0

fondo = "Mapa.png"

ciudadesF = "Ciudades.json"
rutasF = "Rutas.json"
trenesF = "Trenes.json"

rutas = [] # Guarda todas las clases Ruta
ciudades = [] # Guarda todas las clases Ciudad
trayectos = [] # Guarda todos las clases Trenes (finaltrenes)

trenes = [] # Guarda todas las clases EntidadTren

initH = 600
fintH = 1000

horaAct = initH

fotograma = None

# ------------ FUNCIONES ------------

def horaInc(hora):
	if ( (hora - (hora // 100)*100) % 60 == 0): hora += 40 # Pasar de 0060 a 0100
	
	return hora

def calcularPosiciones():
	global trayectos, trenes
	
	# Primero mirar si hay algun tren que tenga que ser añadido
	for tren in trayectos:
		for tray in tren.trayectos:
			print(tray[2][0], tray[3][-1])

def dibujarFotograma():
	global fotograma
	
	draw = ImageDraw.Draw(fotograma)
	
	calcularPosiciones()
	
	#fotograma.save("output/" + str(posicion) + "_Suiza.png")		# Guardar el fotograma
	fotograma.show()

def prepararFondo():
	global fotograma, rutas, ciudades
	
	draw = ImageDraw.Draw(fotograma)
	
	# ======= DIBUJAR RUTAS =======
	for r in rutas:
		draw.line(r.ruta, width = 1, fill = "black")
	
	# ======= DIBUJAR RUTAS =======
	for c in ciudades:
		draw.rectangle([(c.x - 2, c.y - 2), (c.x + 2, c.y + 2)], fill = "red", outline = "red")

def main():
	global fotograma
	print("Running")
	
	fotograma = Image.open(fondo)
	
	prepararFondo()
	
	# Hacer aqui un bucle
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
	global trayectos
	
	print("Cargando trenes")
	
	f = open(trenesF, 'r')
	data = json.loads(f.read())
	
	for i in data: # Meter trenes en la lista
		trayectos.append(Tren(i['id'], i['nombre'], i['color'], i['trayectos']))
	
	f.close()
	
	print(len(trayectos), "trenes cargados")

cargarCiudades()
print()
cargarRutas()
print()
cargarTrenes()
print()

main()