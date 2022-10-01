# En este programa se puede abrir una imagen en la que se selecciona si se quiere crear una ruta o poner ciudades y crea los archivos .json que lo acompañan

# Teclas: R = Ruta ; C = Ciudad ; T = Tren ; BACKSPACE = Borrar

# TODO : ACEPTAR COMO INPUT DEL USUARIO LOS ARCHIVOS PARA UTILIZAR
# TODO : AÑADIR ZOOM

import copy
import math
import json
from tkinter import *
from tkinter.constants import *
from PIL import Image, ImageTk

# --------- VARIABLES ---------

ciudad = True

ciudadesF = "Ciudades.json"
rutasF = "Rutas.json"

moviendo = []
moviendoC = [-1] # Guarda la informacion de lo que hay que mover cuando se mueve una ciudad

finalciudades = [] # Guarda las clases Ciudad
ciudades = [] # Guarda las ciudades que son dibujadas
finalrutas = [] # Guarda las clases Ruta que seran las que se escribiran en el json
rutas = [] # Guarda las rutas que son dibujadas

idR = -1
idC = -1

lineas = []  # Guarda los puntos de inflexion de la linea actual
paradas = [] # Guarda los ids de las paradas
circulos = []	# Guarda el item circulo de la linea actual
linea = None # Guarda la ruta actual dibujada (cosa tkinter)

# --------- CLASES ---------

class LineaDibujada:
	def __init__(self, ruta, linea, circulos):
		self.ruta = ruta
		self.linea = linea
		self.circulos = circulos
	
class Ruta:
	def __init__(self, id, ruta, par):
		self.id = id
		self.ruta = ruta
		self.paradas = par

class CiudadDibujada:
	def __init__(self, ciudad, cuadrado):
		self.ciudad = ciudad
		self.cuadrado = cuadrado

class Ciudad:
	def __init__(self, id, x, y):
		self.id = id
		self.x = x
		self.y = y

class Tren:
	def __init__(self, id, ruta, paradas, llegadas, salidas):
		self.id = id
		self.ruta = ruta
		
		self.paradas = paradas
		self.llegadas = llegadas
		self.salidas = salidas

# --------- SETUP ---------

root = Tk()

canvas = Canvas(width=5914, height=3691, bg='black') # Create the canvas with the image size

myimg = ImageTk.PhotoImage(Image.open('smol.jpg'))
canvas.create_image(0, 0, image=myimg, anchor=NW) # Put the image in the frame

texto = canvas.create_text(300, 50, text="Creador de rutas", fill="black", font=('Helvetica 15'))

# --------- FUNCIONES ---------

def create_circle(x, y, r, canvas): #center coordinates, radius
    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r
    return canvas.create_oval(x0, y0, x1, y1)

def generarIdCiudad():
	global idC, finalciudades
	
	idC = -1
	
	ok = True
	while ok:
		idC = idC + 1
		ok = False
		
		for c in finalciudades:
			if (idC == c.id):
				ok = True
				break

def generarIdRuta():
	global idR, finalrutas
	
	idR = -1
	
	ok = True
	while ok:
		idR = idR + 1
		ok = False
		
		for r in finalrutas:
			if (idR == r.id):
				ok = True
				break

def distancia(pos0, pos1): # Distancia entre dos puntos
	return math.sqrt( (pos0[0] - pos1[0])**2 + (pos0[1] - pos1[1])**2 )

def distPointLine(p, pos0, pos1): # Distancia entre un punto y una recta designada por dos puntos
    return abs( (pos1[0] - pos0[0])*(pos0[1] - p[1]) - (pos0[0] - p[0])*(pos1[1] - pos0[1]) )/math.sqrt( (pos1[0] - pos0[0])**2 + (pos1[1] - pos0[1])**2 )

def setModo(modo): # 1 = CIUDADES ; 2 = RUTAS
	global texto, ciudad, linea
	
	if (modo == 1):
		if (linea != None): # Check que no se esten editando rutas
			return
		
		ciudad = True
		canvas.itemconfig(texto, text="Creador de ciudades")
	else:
		ciudad = False
		canvas.itemconfig(texto, text="Creador de rutas")

def dibujarLinea():
	global linea
	
	if (len(lineas) >= 2):
		canvas.delete(linea)
		linea = canvas.create_line(lineas)

def clickCiudad(event):
	global finalciudades, ciudades, idC
	
	temp = Ciudad(idC, event.x, event.y)
	finalciudades.append(temp)
	ciudades.append(CiudadDibujada(temp, canvas.create_rectangle(event.x - 2, event.y - 2, event.x + 2, event.y + 2, fill="red", activefill="cyan")))
	
	generarIdCiudad()

def click(event):
	global moviendo, ciudad
	
	if (ciudad):
		clickCiudad(event)
		return
	
	if (len(moviendo) == 2): # Si se esta moviendo, out
		return
	
	coords = [event.x, event.y]
	
	paradas.append(-1)
	circulo = create_circle(event.x, event.y, 3, canvas)
	circulos.append(circulo)
	
	for i in range(len(finalciudades)): # Detectar si el click ha sido cerca de una ciudad para registrarlo como una parada
		if (distancia(coords, [finalciudades[i].x, finalciudades[i].y]) < 5):
			canvas.delete(circulo)
			circulos[-1] = -1 # Mantener algo por si acaso se borrara la estacion
			
			coords = [finalciudades[i].x, finalciudades[i].y]
			paradas[-1] = finalciudades[i].id
			break
	
	lineas.append(coords) # Si no se ha seleccionado una ciudad, entonces se crea un circulo para poder mover
	
	dibujarLinea()

def editarCiudad(coords):
	global finalciudades, ciudades, moviendoC
	
	for i in range(len(finalciudades)):
		if (distancia([finalciudades[i].x, finalciudades[i].y], coords) < 4):
			moviendoC = [i]
			break

def editar(event):
	global moviendo, ciudad, finalrutas, rutas, canvas
	
	coords = [event.x, event.y]
	
	if (ciudad):
		editarCiudad(coords)
		return
	
	if (linea != None or len(rutas) == 0): # Si esta creando una linea o no hay lineas que editar, se vuelve
		return
	
	for r in range(len(finalrutas)): # Detectar si el click ha sido en un punto de inflexion de la ruta para moverlo
		for i in range(len(finalrutas[r].ruta)):
			if (finalrutas[r].paradas[i] == -1 and distancia(finalrutas[r].ruta[i], coords) < 5):
				moviendo = [r, i]
				return
	
	if (len(moviendo) > 0): # Si ya se está moviendo un punto de inflexion, volver
		return
	
	for r in range(len(finalrutas)): # Añadir puntos en una recta
		for i in range(len(finalrutas[r].ruta) - 1):
			if (distPointLine(coords, finalrutas[r].ruta[i], finalrutas[r].ruta[i + 1]) < 5):
				finalrutas[r].ruta.insert(i+1, [event.x, event.y])
				finalrutas[r].paradas.insert(i+1, -1)
				rutas[r].circulos.insert(i+1, create_circle(event.x, event.y, 3, canvas))
				moviendo = [r, i+1]
				break
	
	dibujarLinea()

def soltar(event):
	global moviendo, moviendoC, linea, lineas, ciudad, finalciudades, ciudades
	
	if (ciudad and moviendoC[0] != -1):
		finalciudades[moviendoC[0]].x = ciudades[moviendoC[0]].ciudad.x
		finalciudades[moviendoC[0]].y = ciudades[moviendoC[0]].ciudad.y
		
		moviendoC = [-1]
		return
	
	if (len(moviendo) == 0): # Si no se esta moviendo nada : return
		return
	
	finalrutas[moviendo[0]].ruta = copy.deepcopy(lineas)
	
	rutas[moviendo[0]].linea = canvas.create_line(lineas)
	rutas[moviendo[0]].ruta.ruta = copy.deepcopy(lineas)
	
	canvas.delete(linea)
	linea = None
	
	lineas = []
	circulos = []
	
	moviendo = []

def moverCiudad(event):
	global ciudades, moviendoC, canvas, finalciudades
	
	if (moviendoC[0] != -1):
		ciudades[moviendoC[0]].ciudad.x = event.x
		ciudades[moviendoC[0]].ciudad.y = event.y
		
		canvas.delete(ciudades[moviendoC[0]].cuadrado)
		ciudades[moviendoC[0]].cuadrado = canvas.create_rectangle(event.x - 2, event.y - 2, event.x + 2, event.y + 2, fill="red", activefill="cyan")
	
		# TODO : ESTARIA BIEN QUE MOVIERA TODAS LAS RUTAS CONECTADAS A ESA CIUDAD

def mmove(event):
	global rutas, linea, lineas, moviendo, ciudad
	
	if (ciudad):
		moverCiudad(event)
		return
	
	if (len(moviendo) == 2):
		lineas = copy.deepcopy(finalrutas[moviendo[0]].ruta)
		lineas[moviendo[1]] = [event.x, event.y]
		
		canvas.delete(rutas[moviendo[0]].linea)
		canvas.delete(rutas[moviendo[0]].circulos[moviendo[1]])
		rutas[moviendo[0]].circulos[moviendo[1]] = create_circle(event.x, event.y, 3, canvas)
		
		# TODO : A LO MEJOR AÑADIR PARADAS SI SE PASA CERCA MIENTRAS SE ESTA EDITANDO
	else:
		temp = copy.deepcopy(lineas)
		temp.append([event.x, event.y])
	
	dibujarLinea()

def guardarRuta(event):
	global idR, linea, lineas, paradas, circulos
	
	if (len(lineas) < 2):
		return
	
	temp = canvas.create_line(lineas)
	finalrutas.append(Ruta(idR, lineas, paradas))
	rutas.append(LineaDibujada(finalrutas[-1], temp, circulos))
	
	canvas.delete(linea)
	linea = None # Resetear variables
	
	lineas = []
	paradas = []
	circulos = []
	
	print("Ruta guardada con id", idR)
	
	generarIdRuta()

def borrarItem(event): # Para poder borrar se tiene que estar editando una ciudad o una ruta
	global canvas, finalciudades, ciudad, moviendo, moviendoC, finalrutas, rutas, lineas, linea, circulos
	
	if (ciudad and moviendoC[0] != -1): # Si se quiere borrar una ciudad, hacer todo esto
		for r in range(len(finalrutas)): # Borrar la ciudad de paradas
			for i in range(len(finalrutas[r].paradas)):
				if (finalrutas[r].paradas[i] == finalciudades[moviendoC[0]].id):
					finalrutas[r].paradas[i] = -1
					rutas[r].circulos[i] = create_circle(finalrutas[r].ruta[i][0], finalrutas[r].ruta[i][1], 3, canvas)
					
			rutas[r].ruta = copy.deepcopy(finalrutas[r]) # Copiar just in case
		
		canvas.delete(ciudades[moviendoC[0]].cuadrado)
		
		del ciudades[moviendoC[0]] # Borrar la ciudad de los arrays de ciudad
		del finalciudades[moviendoC[0]]
		
		moviendoC = [-1]
		return
	
	# Si estamos aqui es porque se esta borrando una ruta
	if (len(moviendo) == 2): # Se quiere borrar una linea que se estaba modificando
		print("a")
		
		lineas = []
		
		canvas.delete(rutas[moviendo[0]].linea) # Borrar linea
		for c in rutas[moviendo[0]].circulos: # Borrar circulos
			canvas.delete(c)
		
		del finalrutas[moviendo[0]] # Quitar la ruta de lo que se escriba en el json
		del rutas[moviendo[0]] # No hay ruta que dibujar, por lo que se borra
		
		canvas.delete(linea)
		linea = None
		
		moviendo = []
	elif (linea != None):# Se quiere borrar la linea que se estaba haciendo
		lineas = []
		circulos = []
		paradas = []
		
		canvas.delete(linea)
		linea = None

def escribir(event):
	if (ciudad):
		escribirCiudades()
	else:
		escribirRutas()

def escribirCiudades():
	global finalciudades
	
	with open(ciudadesF, "w+") as f:
		stringF = json.dump([c.__dict__ for c in finalciudades], f, indent=4)
		f.close()
	print("Ciudades guardadas")

def escribirRutas():
	global finalrutas
	
	with open(rutasF, "w+") as f:
		stringF = json.dump([r.__dict__ for r in finalrutas], f, indent=4)
		f.close()
	print("Rutas guardadas")

# --------- BINDS ---------

canvas.pack()

canvas.bind("<ButtonPress-1>", click)

canvas.bind("<ButtonPress-3>", editar)
canvas.bind("<ButtonRelease-3>", soltar)

canvas.bind("<Double-1>", guardarRuta)
canvas.bind("<Motion>", mmove)

root.bind("<C>", lambda event, a = 1 : setModo(a))
root.bind("<R>", lambda event, a = 2 : setModo(a))

root.bind("<BackSpace>", borrarItem)

root.bind("<Return>", escribir)

canvas.pack()

# --------- INIT FUNCS ---------

def cargarCiudades():
	global canvas, finalciudades, ciudades
	
	print("Cargando ciudades")
	
	f = open(ciudadesF, 'r')
	data = json.loads(f.read())
	
	for i in data: # Dibujar ciudades
		temp = Ciudad(i['id'], i['x'], i['y'])
		finalciudades.append(temp)
		
		ciudades.append(CiudadDibujada(temp, canvas.create_rectangle(i['x'] - 2, i['y'] - 2, i['x'] + 2, i['y'] + 2, fill="red", activefill="cyan")))
	
	f.close()
	
	print(len(finalciudades), "ciudades cargadas")

def cargarRutas():
	global canvas, finalrutas, rutas

	print("Cargando rutas")
	
	f = open(rutasF, 'r')
	data = json.loads(f.read())
	
	for i in data: # Dibujar rutas
		temp = Ruta(i['id'], i['ruta'], i['paradas'])
		finalrutas.append(temp)
		
		tempC = []
		
		for i in range(len(temp.ruta)):
			if (temp.paradas[i] != -1):
				continue
			tempC.append(create_circle(temp.ruta[i][0], temp.ruta[i][1], 3, canvas))
		
		rutas.append(LineaDibujada(temp, canvas.create_line(temp.ruta), tempC))
	
	f.close()
	
	print(len(finalrutas), "rutas cargadas")

cargarCiudades()
print()
cargarRutas()
print()
setModo(2)
generarIdRuta()
generarIdCiudad()
print()

mainloop()