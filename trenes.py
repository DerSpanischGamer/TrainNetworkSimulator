# USO: python cancionVideo.py "ARCHIVO.amds"
# Nota: siempre va a guardar los archivos en una carpeta llamada output

# ------------ LIBRERIAS ------------

import sys
import csv
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ------------ CLASES ------------

class Ciudad:
	
	def __init__(self, cod, posX, posY):
		self.codigo = cod
		
		self.x = posX
		self.y = posY

class Ruta:
	def __init__(self, pos, paradas): # pos : es un array con arrays que contienen [x, y] ; paradas : es un array con las paradas que hace (en codigo)
		self.ruta = pos
		self.paradas = paradas

class Tren:

	def __init__(self, paradas, llegadas, salidas, color):
		self.paradas = paradas
		self.llegadas = llegadas
		self.salidas = salidas
		
		self.color = color

# ------------ VARIABLES ------------

posicion = 0

GE = Ciudad(0, 10, 700)
LS = Ciudad(1, 70, 620)

ruta = Ruta([[10, 700], [11, 699], [12, 698], [13, 697], [14, 696]], [GE, LS])

ciudades = [GE, LS]
rutas = [ruta]

fotograma = None

# ------------ FUNCIONES ------------

def dibujarFotograma():
	global fotograma
	
	draw = ImageDraw.Draw(fotograma)
	fotograma.save("output/" + str(posicion) + "_Suiza.png")		# Guardar el fotograma

def prepararFondo():
	global fotograma

	# ======= DIBUJAR RUTAS =======
	for r in rutas:
		for p in r.ruta:
			fotograma.putpixel(p, (97, 97, 97))

def main():
	global fotograma
	print("Running")
	
	fotograma = Image.new(mode = "RGB", size = (1920, 1080), color = (0, 0, 255))
	
	prepararFondo()
	
	# Hacer aqui un bucle
	dibujarFotograma()


main()
