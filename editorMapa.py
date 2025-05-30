# En este programa se puede abrir una imagen en la que se selecciona si se quiere crear una ruta o poner ciudades y crea los archivos .json que lo acompañan

# Teclas: R = Ruta ; C = Ciudad ; T = Tren ; BACKSPACE = Borrar

# IMPORTANTE : ¡¡¡ EMPEZAR A CREAR LAS LINEAS DE TRENES UNA VEZ QUE LAS RUTAS Y LAS ESTACIONES ESTÉN ACABADAS !!!

# ============ EN DESARROLLO ============

# ERROR : getRutaPuntos SIGUE ROTO

# ============ MÁS TARDE ============

# TODO : ACABAR LA FUNCION seleccionarOpcion(1)
# TODO : EL CUADRADO DE UNA CIUDAD NO ESTA CENTRADO EN LA CIUDAD SINO EN LA ESQUINA INFERIOR DERECHA
# TODO : GENERALIZAR A n BUSQUEDAS : CREO QUE VA A HACER FALTA UN METODO RECURSIVO LOL - LO QUE HAY QUE HACER ES QUE CADA CIUDAD EN LA QUE SE PUEDA BUSCAR VA A DIVIDIRSE HASTA QUE : a) LLEGUE A LA CIUDAD DESEADA b) PASE POR LA MISMA CIUDAD 2 VECES
# ERROR : CUANDO HAY MULTIPLES RUTAS, BORRA EL ULTIMO Y NO EL QUE DEBERIA (ni idea de lo que habla) - OK CRO QUE LO HE ENTENDIDO, SIGNIFICA QUE CUANDO SE TENIA QUE SELECCIONAR ENTRE VARIAS RUTAS BORRA LA ULTIMA (creo)
# ERROR : A VECES (NO REPLICABLE) CUANDO SE EDITA UNA RUTA Y SE BORRA UN PUNTO QUEDA UN CIRCULO Y HACE MIERDA CON LAS OTRAS

import copy
import math
import json
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from tkinter.constants import *
from tkinter import colorchooser
from tkinter.messagebox import askyesno
from json.decoder import JSONDecodeError

# --------- VARIABLES ---------

top = None # Ventana extra para informaciones
idTedit = None # id del tren que se está editando
selecLn = None # OptionMenu para seleccionar linea de tren
textBox = None # Textbox con el nombre de la ciudad que se esta creando
nombreLin = None # Textbox con el nombre de la linea que se esta creando
horarioAct = None # Label con el numero del horario que estamos editando ahora

anadirParada = None # Boton de añadir parada
trayectoSig = None # Siguiente trayecto (añade uno si no existe)
trayectoAnt = None # Trayecto anterior (el boton se oculta si no hay)
trayectoDel = None # Borrar el trayecto actual
lineaDel = None # Borrar la linea

ciudad = False # Estamos en modo ciudad ?
eraCiudad = False # Estamos moviendo un punto que era una ciudad ?

fondo = "Mapa.png"

ciudadesF = "Ciudades.json"
rutasF = "Rutas.json"
trenesF = "Trenes.json"

moviendo = [] # Vacio cuando no se mueve una ruta, cuando se mueve una ruta [ruta_conectada , pos_ocupaba_ciudad]
moviendoC = [-1] # Guarda la informacion de lo que hay que mover cuando se mueve una ciudad [id_ciudad , [ruta_conectada , pos_ocupaba_ciudad], ...]

finalciudades = [] # Guarda las clases Ciudad
ciudades = [] # Guarda las ciudades que son dibujadas

finalrutas = [] # Guarda las clases Ruta que seran las que se escribiran en el json
rutas = [] # Guarda las rutas que son dibujadas

colorTren = None # Guarda el boton color del tren
posActual = 0 # Que trayecto se esta modificando
trayectosActuales = [[]] # Guarda todos los horarios que puede tener un tren [ columna1 ; columna2 ; ... ; columnnan]
finaltrenes = [] # Guarda las classes Tren que seran las que se escribiran en el json

selec = None # Ventana donde se selecciona una de las rutas
lineaRuta = None # Ruta en verde que muestra por donde va a ir el tren
rutaSelect = None # OptionMenu para seleccionar la ruta
proponerAlt = True # Proponer una ruta inderecta si se ha encontrado una ruta directa
rutasActuales = [[]] # Array de array en el que se guarda la ruta con las paradas de cada array [paradas ; puntos] si un punto no corresponde a ninguna parada, entonces la parada tiene -1. Los dos arrays tienen la misma longitud

tipo = 0 # Continue el tipo de parada que es : 0 = primera parada ; 1 = entre dos paradas ; 2 = ultima parada
posTop = None # Ventana donde se va a mostrar el OptionMenu con todas las opciones
lineaTemp = None # La linea que se ha seleccionado
posiblesRutas = [] # Rutas propuestas entre dos puntos para el trayecto de un tren (solo contienen las posiciones de cada punto de la linea)
puntoDivergencia = [] # Donde se separa la ruta
lineaTemp = None # Linea que muestra la ruta qeu se ha seleccionado
posibSelec = None # La opcion que se ha seleccionado

idR = -1 # Id para la proxima ruta
idC = -1 # Id para la proxima ciudad
idT = -1 # Id para el proximo tren

lineas = []  # Guarda los puntos de inflexion de la linea actual
paradas = [] # Guarda los ids de las paradas
circulos = []	# Guarda el item circulo de la linea actual
linea = None # Guarda la ruta actual dibujada (cosa tkinter)

# --------- CLASES ---------

class Ruta:
	def __init__(self, id, ruta, par):
		self.id = id
		self.ruta = ruta
		self.paradas = par

class LineaDibujada:
	def __init__(self, ruta, linea, circulos):
		self.ruta = ruta
		self.linea = linea
		self.circulos = circulos

class Ciudad:
	def __init__(self, id, nombre, x, y):
		self.id = id
		self.nombre = nombre
		self.x = x
		self.y = y

class CiudadDibujada:
	def __init__(self, ciudad, cuadrado):
		self.ciudad = ciudad
		self.cuadrado = cuadrado

class Tren:
	def __init__(self, id, nombre, color, trayectos):
		self.id = id
		self.nombre = nombre
		self.color = color
		
		self.trayectos = trayectos # [ [paradas, ruta, llegadas , salidas], ... ] Array de arrays contiene las paradas (ids de las ciudades), la ruta a seguir (tal y como está en rutasActuales), llegadas y salidas de cada tren (pueden haber varios a la vez con rutas diferentes)

# --------- SETUP ---------

root = Tk()
root.title("Editor de rutas")

canvas = Canvas(width = 1920, height = 1080, bg = 'black') # Create the canvas with the image size

myimg = ImageTk.PhotoImage(Image.open(fondo))
canvas.create_image(0, 0, image = myimg, anchor = NW) # Put the image in the frame

texto = canvas.create_text(300, 50, text = "Creador de rutas", fill = "black", font = ('Helvetica 15'))

root.resizable(False, False)

# --------- FUNCIONES ---------

def hacerCirculo(x, y, r, canvas): # Dibujar un circulo con coords centro y radio
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

def generarIdTren():
	global idT, finaltrenes
	
	idT = -1
	
	ok = True
	while ok:
		idT = idT + 1
		ok = False
		
		for t in finaltrenes:
			if (idT == t.id):
				ok = True
				break

def distancia(pos0, pos1): # Distancia entre dos puntos
	return math.sqrt( (pos0[0] - pos1[0])**2 + (pos0[1] - pos1[1])**2 )

def distPointLine(P0, P1, P2): # P0 es el punto, P1 y P2 son las extremidades del segmento de linea
	px = P2[0] - P1[0]
	py = P2[1] - P1[1]
	
	if (px == 0 and py == 0): return 0
	
	norm = px**2 + py**2
	
	u =  ((P0[0] - P1[0]) * px + (P0[1] - P1[1]) * py) / float(norm)
	
	if u > 1: u = 1
	elif u < 0: u = 0
	
	x = P1[0] + u * px
	y = P1[1] + u * py
	
	dx = x - P0[0]
	dy = y - P0[1]
	
	return math.sqrt(dx*dx + dy*dy)

def setModo(modo): # 1 = CIUDADES ; 2 = RUTAS ; 3 = TREN
	global texto, ciudad, linea, top, moviendo, moviendoC
	
	if (top != None or linea != None or len(moviendo) > 0 or moviendoC[0] != -1): return # No cambiar de modo si se esta creando una nueva ciudad, una nueva linea. Editando una ruta o una ciudad 
	
	if (modo == 1):
		if (linea != None): return # Check que no se esten editando rutas
		
		ciudad = True
		canvas.itemconfig(texto, text = "Editor/creador de ciudades")
	elif (modo == 2):
		ciudad = False
		canvas.itemconfig(texto, text = "Editor/creador de rutas")
	else:
		crearLineaTren()

def existeNombre(nombre): # Check si existe el nombre de la ciudad o no
	global finalciudades
	
	for n in finalciudades:
		if (nombre == n.nombre):
			return True
	
	return False

def getLineasDisponibles(): # Devuelve el nombre de todas las lineas de tren disponibles para modificar
	return [t.nombre for t in finaltrenes]

def getRuta(id): # Devuelve la posicion de la Ruta en finalrutas
	global finalrutas
	
	for i in range(len(finalrutas)):
		if (finalrutas[i].id == id):
			return i
	
	return None

def getTren(nombre): # Devuelve la posicion de la Tren en finaltrenes
	global finaltrenes
	
	for i in range(len(finaltrenes)):
		if (finaltrenes[i].nombre == nombre):
			return i
	
	return None

def getTrenId(id):
	global finaltrenes
	
	for i in range(len(finaltrenes)):
		if (finaltrenes[i].id == id):
			return i
	
	return None

def getRutaId(idR): # Devuelve la posicion de Ruta en finalrutas
	global finalrutas
	
	for i in range(len(finalrutas)):
		if (finalrutas[i].id == idR):
			return i
	
	return None

def getRutasPorCiudad(idC): # Devuelve el id de las rutas que pasan por una ciudad
	temp = [] # Ciudades 

	for r in finalrutas:
		if (idC in r.paradas and not r.id in temp):
			temp.append(r.id)

	return temp

def getCiudadId(id): # Devuelve la posicion de la Ciudad en finalciudades dando el id de la ciudad
	global finalciudades
	
	for i in range(len(finalciudades)):
		if (finalciudades[i].id == id):
			return i
	
	return None

def getCiudad(nombre): # Devuelve la posicion de la Ciudad en finalciudades dando el nombre de la ciudad
	global finalciudades
	
	for i in range(len(finalciudades)):
		if (finalciudades[i].nombre == nombre):
			return i
	
	return None

def getCiudades(idC, idQ): # Devuelve la lista de todas las ciudades disponibles para que pase un tren
	global finalciudades, finalrutas
	
	if (idC == None):
		after = [c.nombre for c in finalciudades]
		if (idQ != None): after.remove(finalciudades[getCiudadId(idQ)].nombre)
		return after
	
	previo = [idC]	# Lista con ids de las paradas que hay que escanear
	after = []		# Lista con ids de las paradas que han sido escaneadas
	
	while (previo != after):
		for c in previo:
			if (c in after): # NO escanear las que ya han sido escaneadas
				continue
			
			temp = getRutasPorCiudad(c) # Coge las rutas que pasan por la ciudad c
			after.append(c) # Ya se ha investigado la ciudad c, por lo que se añade en after
			
			for r in temp:
				for par in finalrutas[getRuta(r)].paradas:
					if (par != -1 and not par in previo):
						previo.append(par)
	
	if (idQ != None and idQ in after):	after.remove(idQ) # Quitar la ciudad de origen
	
	return [finalciudades[getCiudadId(c)].nombre for c in after] # Quitar la ciudad que se nos ha dado

def mostrarRuta(pos):
	global canvas, lineaTemp, posiblesRutas
	
	if (lineaTemp != None): canvas.delete(lineaTemp)
	
	lineaTemp = canvas.draw_line(posiblesRutas[pos])

def mostrarRutas():
	global posTop, posiblesRutas, esperarInput
	
	posTop = Toplevel()
	
	posTop.geometry("200x300")
	posTop.title("Selecciona ruta")
	posTop.resizable(False, False)
	
	pos = StringVar()
	poss = ["Ruta " + str(i) for i in range(len(posiblesRutas))]
	
	pos.set(poss[0])
	
	menu = OptionMenu(posTop, pos, *poss)
	menu.pack()
	for i in range(len(posiblesRutas)):
		menu["menu"].add_command(label = str(i), command = lambda a = i : mostrar(a))
	
	esperarInput = True
	
	Button(posTop, text = "", command = lambda : aceptarRuta()).pack()
	
	return None

def getRutaPuntosRec(origen, destino, rDestin, visitadas = []): # Origen es la ciudad en la que nos encontramos, destino es el destino final, rDestin son las rutas que pasan por el destino (asi no hay que calcularlas siempre) y visitadas son las ciudades por las que ya hemos pasado
	global finalrutas, finalciudades # TODO : DO
	
	if (origen in visitadas): return None # Desde el punto de vista de la función : si la parada en la que estamos ya la hemos visitado, entonces salimos
	
	rOrigen = getRutasPorCiudad(origen) # Rutas que pasan por el origen
	
	for rutaId in rOrigen:
		ruta = finalrutas[getRutaId(rutaId)]
		
		if rutaId in rDestin: # La ruta esta en el destino
			visitadas.append(origen)
			return visitadas

def getRutaPuntos(origen, destino): # Devuelve una ruta (serie de puntos) entre dos puntos (origen, destino) recibiendo el id de las ciudades de origen y destino TODO : REHACER PARA QUE SEA RECURSIVO
	global finalrutas, finalciudades, posiblesRutas, puntoDivergencia
	
	if (origen == destino): return
	
	rOrigen = getRutasPorCiudad(origen) 	# Coger todas las rutas que pasan por el origen
	rDestin = getRutasPorCiudad(destino) 	# Same for el destino
	
	posiblesRutas.clear() # Todas las rutas que se puden tomar
	puntoDivergencia.clear()
	
	# Primero mirar si hay una ruta que pasa por los dos (origen y destino)
	for rutaId in rOrigen: 
		if (rutaId in rDestin):
			ruta = finalrutas[getRutaId(rutaId)] # Existe la ruta directa
			
			org = ruta.paradas.index(origen)
			dst = ruta.paradas.index(destino)
			
			if (dst > org):	posiblesRutas.append(ruta.ruta[org:(dst + 1)])		# Devolver la ruta sin el origen ni el destino cada punto es [x, y]
			else:			posiblesRutas.append(ruta.ruta[dst:(org + 1)][::-1])		# Si se va al reves hay que llamar a la funcion reversed para que el orden sea correcto
			
			puntoDivergencia.append("Directo " + str(len(puntoDivergencia)))
	
	if (len(posiblesRutas) == 1 and not proponerAlt):	return posiblesRutas
	
	# Si estamos aqui es que no hay ruta directa por lo que buscar una ruta alternativa TODO : ES AQUI DONDE SE PUEDE HACER CON n INTERCAMBIOS
	for rutaId in rOrigen:
		rutaOr = finalrutas[getRutaId(rutaId)]
		
		if (destino in rutaOr.paradas): continue # Ignorar rutas directas
		
		for destId in rDestin:
			if (destId == rutaId): continue	# Ignorar rutas directas
			
			rutaDe = finalrutas[getRutaId(destId)]
			
			for parada in rutaOr.paradas:
				if (parada == -1): continue								# Ignorar los puntos de la ruta que no son paradas
				if (parada == destino or parada == origen):	continue	# Ignorar el destino y el origen
				
				if (parada in rutaDe.paradas):
					org = rutaOr.paradas.index(origen)
					vi1 = rutaOr.paradas.index(parada)
					vi2 = rutaDe.paradas.index(parada)
					dst = rutaDe.paradas.index(destino)
					
					temp = []
					
					# En el primer trayecto NO se incluye NI el origen NI el punto de intercambio   ;   En el ultimo punto NO se incluye el destino pero SI el punto de intercambio
					if (vi1 > org):	[temp.append(r) for r in rutaOr.ruta[org:vi1]]
					else:			[temp.append(r) for r in rutaOr.ruta[vi1:(org + 1)][::-1]]
					
					if (vi2 > dst): [temp.append(r) for r in rutaDe.ruta[(dst + 1):vi2][::-1]]
					else:			[temp.append(r) for r in rutaDe.ruta[vi2:dst]]
					
					puntoDivergencia.append("Via " + finalciudades[getCiudadId(parada)].nombre)
					posiblesRutas.append(temp)
	
	if (len(posiblesRutas) >= 1):	return posiblesRutas # Devolver posiblesRutas y despues que se decida mas tarde
	else:							return None # Devolver None para indicar que no hay ruta entre las ciudades

def getParada(par): # Devuelve la posicion en trayectosActuales[posActual] y el id de la ciudad de una parada par (par es el id de la parada)
	global trayectosActuales, posActual, finalciudades
	
	for i in range(len(trayectosActuales[posActual])):
		if (trayectosActuales[posActual][i][4] == par):
			nombrePar = trayectosActuales[posActual][i][5].get()
			for ciudad in finalciudades:
				if (ciudad.nombre == nombrePar):
					return [ciudad.id, i] # Devolver la id de la ciudad y su posicion en el array trayectosActuales
	
	return None

def getPositions(pos): # Devuelve las posiciones de la parada , la anterior y la posterior en el array rutasActuales[posActual] ; toma como argumento el id de la linea de widgets (length)
	global rutasActuales, posActual
	
	obj = None
	
	for i in range(len(trayectosActuales[posActual])):
		if (trayectosActuales[posActual][i][4] == pos):
			obj = i
			break
	
	if (obj == None): return None # Sanity check
	
	cuenta = -1
	
	pre = None
	n = None
	pos = None
	
	for i in range(len(rutasActuales[posActual])):
		if (rutasActuales[posActual][i][0] != -1):
			pre = n
			n = i
			
			cuenta += 1
		
		if (cuenta == obj):
			for j in range(i + 1, len(rutasActuales[posActual])):
				if (rutasActuales[posActual][j][0] != -1):
					pos = j
					return[pre, n, pos]
	
	return [pre, n, pos] # Este array devuelve [0] = None si es la primera posicion, [2] = None si es la ultima, y si no es que esta en medio

def beautifyTiempo(txt):
	return "0" * (4 - len(txt)) + txt # Devuelve la hora con ceros delante

def checkTiempo(t):
	return (len(t) == 4 and t.isnumeric() and int(t[0:1]) < 24 and int(t[2:3]) < 60) # Devuelve true si es un numero valable

def dibujarLinea():
	global linea
	
	if (len(lineas) >= 2):
		canvas.delete(linea)
		linea = canvas.create_line(lineas, width = 3, fill = "red")

def registrarCiudad(event = None):
	global top, extBox, finalciudades, ciudades, idC
	
	nombre = textBox.get("1.0", "end-1c")
	
	if (len(nombre) < 2 or len(nombre) > 15 or existeNombre(nombre)):
		return
	
	if (nombre[-1] == '\n'):
		nombre = nombre[0:-1]
	
	temp = Ciudad(idC, nombre, lineas[0], lineas[1])
	finalciudades.append(temp)
	ciudades.append(CiudadDibujada(temp, canvas.create_rectangle(lineas[0] - 2, lineas[1] - 2, lineas[0] + 2, lineas[1] + 2, fill="red", activefill="cyan")))
	
	generarIdCiudad()
	
	cancelarCiudad()

def cancelarCiudad(event = None):
	global top, lineas, textBox
	
	top.destroy()
	
	top = None
	textBox = None
	
	lineas = []

def clickCiudad(event):
	global top, textBox, lineas
	
	if (top != None): return
	
	lineas = [event.x, event.y]
	
	top = Toplevel()
	top.title("Crear ciudad	")
	top.resizable(False, False)
	
	textBox = Text(top, height = 1, width = 15)
	textBox.focus()
	textBox.pack()
	
	acc = Button(top, text = "Aceptar", command = registrarCiudad).pack()
	
	can = Button(top, text = "Cancelar", command = cancelarCiudad).pack()
	
	top.bind("<Return>", registrarCiudad)
	top.bind("<Escape>", cancelarCiudad)
	
	top.protocol("WM_DELETE_WINDOW",  cancelarCiudad)
	
	top.focus_force()

def click(event):
	global moviendo, ciudad
	
	if (ciudad):
		clickCiudad(event)
		return
	
	if (len(moviendo) == 2 or top != None): return # Si se esta moviendo o haciendo una linea de tren
	
	coords = [event.x, event.y]
	
	if (len(lineas) >= 1 and coords[0] == lineas[-1][0] and coords[1] == lineas[-1][1]): return
	
	paradas.append(-1)
	circulos.append(hacerCirculo(event.x, event.y, 3, canvas)) # Añadir circulo del lugar actual
	
	lineas.append(coords) # Si no se ha seleccionado una ciudad, entonces se crea un circulo para poder mover (no pasa con lineas nuevas)
	
	for i in range(len(finalciudades)): # Detectar si el click ha sido cerca de una ciudad para registrarlo como una parada
		if (distancia(coords, [finalciudades[i].x, finalciudades[i].y]) < 5):
			canvas.delete(circulos[-1])
			circulos[-1] = -1 # Mantener algo por si acaso se borrara la estacion
			
			if (len(paradas) > 1 and paradas[-2] == finalciudades[i].id):
				lineas.pop()
				paradas.pop()
				break
			
			coords = [finalciudades[i].x, finalciudades[i].y]
			paradas[-1] = finalciudades[i].id
			break
	
	dibujarLinea()

def editarCiudad(coords):
	global canvas, finalciudades, finalrutas, ciudades, moviendoC
	
	for i in range(len(finalciudades)): # Coger ciudad
		if (distancia([finalciudades[i].x, finalciudades[i].y], coords) < 4):
			moviendoC = [i]
			
			canvas.itemconfig(texto, text = "Moviendo " + finalciudades[i].nombre)
			for r in range(len(finalrutas)):
				for p in range(len(finalrutas[r].paradas)):
					if (finalrutas[r].paradas[p] == finalciudades[i].id):
						moviendoC.append([r, p]) # Añadir este punto a mover
			break

def editar(event):
	global moviendo, ciudad, finalrutas, rutas, canvas, lineas, eraCiudad
	
	coords = [event.x, event.y]
	
	if (ciudad):
		editarCiudad(coords)
		return
	
	if (linea != None or len(rutas) == 0): return # Si esta creando una linea o no hay lineas que editar, se vuelve
	
	for r in range(len(finalrutas)): # Detectar si el click ha sido en un punto de inflexion de la ruta para moverlo
		for i in range(len(finalrutas[r].ruta)):
			if (distancia(finalrutas[r].ruta[i], coords) < 5):
				moviendo = [r, i]
				
				eraCiudad = False
				
				if (finalrutas[r].paradas[i] != -1): # El punto que se ha seleccionado es una parada
					rutas[r].circulos[i] = hacerCirculo(event.x, event.y, 3, canvas) # Crear un circulo visto que ya no es una parada, si no un punto de inflexion de la ruta
					
					finalrutas[r].paradas[i] = -1 # Decir que la parada anterior ya no es una parada
					
					eraCiudad = True
				
				return
	
	if (len(moviendo) > 0): return # Si ya se está moviendo un punto de inflexion, volver
	
	for r in range(len(finalrutas)): # Añadir puntos en una recta
		for i in range(1, len(finalrutas[r].ruta)):
			if (distPointLine(coords, finalrutas[r].ruta[i - 1], finalrutas[r].ruta[i]) < 5):
				
				finalrutas[r].ruta.insert(i, [event.x, event.y]) # Insertar la posicion actual en la lista
				finalrutas[r].paradas.insert(i, -1) # Decir que el punto que acabamos de insertar no es una parada
				
				rutas[r].circulos.insert(i, hacerCirculo(event.x, event.y, 3, canvas)) # Poner un ciculo visto que no es una parada
				
				moviendo = [r, i] # Indicar el punto que estamos moviendo visto que ya ha sido integrado en la lista
				
				lineas = copy.deepcopy(finalrutas[r].ruta) # Copiar la lista lineas para poder dibujar la linea que estamos editando
				
				eraCiudad = False
				
				break
	
	dibujarLinea()

def soltar(event):
	global moviendo, moviendoC, linea, lineas, ciudad, finalciudades, ciudades, rutas, finalrutas
	
	if (ciudad and moviendoC[0] != -1): # Si se esta moviendo una ciudad
		finalciudades[moviendoC[0]].x = ciudades[moviendoC[0]].ciudad.x
		finalciudades[moviendoC[0]].y = ciudades[moviendoC[0]].ciudad.y
		
		for i in range(1, len(moviendoC)): # Guardar el hecho que hemos movido la ruta que estaba conectada a la ciudad
			rutas[moviendoC[i][0]].ruta.ruta = copy.deepcopy(finalrutas[moviendoC[i][0]].ruta) # Guadar las nuevas posiciones
			rutas[moviendoC[i][0]].ruta.paradas = copy.deepcopy(finalrutas[moviendoC[i][0]].paradas) # Guardar las paradas si se ha conectado a una nueva parada
		
		moviendoC = [-1]
		
		canvas.itemconfig(texto, text = "Creador de ciudades")
		return
	
	if (len(moviendo) == 0): return # Si no se esta moviendo nada : return
	
	finalrutas[moviendo[0]].ruta = copy.deepcopy(lineas)
	
	rutas[moviendo[0]].linea = canvas.create_line(lineas)
	rutas[moviendo[0]].ruta.ruta = copy.deepcopy(lineas) # [Array con las clases LineaDibujada].[Clase Ruta].[Array que guarda todos los puntos de inflexion]
	rutas[moviendo[0]].ruta.paradas = copy.deepcopy(finalrutas[moviendo[0]].paradas) # Copiar las paradas
	
	canvas.delete(linea)
	linea = None
	
	lineas = []
	circulos = []
	
	moviendo = []

def moverCiudad(event):
	global ciudades, moviendoC, canvas, finalciudades, rutas, moviendo
	
	if (moviendoC[0] != -1):
		ciudades[moviendoC[0]].ciudad.x = event.x
		ciudades[moviendoC[0]].ciudad.y = event.y
		
		canvas.delete(ciudades[moviendoC[0]].cuadrado)
		ciudades[moviendoC[0]].cuadrado = canvas.create_rectangle(event.x - 2, event.y - 2, event.x + 2, event.y + 2, fill="red", activefill="cyan")
		
		for i in range(1, len(moviendoC)): # Mover las rutas que estaban conectadas a la ciudad
			finalrutas[moviendoC[i][0]].ruta[moviendoC[i][1]][0] = event.x
			finalrutas[moviendoC[i][0]].ruta[moviendoC[i][1]][1] = event.y
			
			canvas.delete(rutas[moviendoC[i][0]].linea)
			rutas[moviendoC[i][0]].linea = canvas.create_line(finalrutas[moviendoC[i][0]].ruta)

def mmove(event):
	global rutas, linea, lineas, moviendo, ciudad
	
	if (ciudad):
		moverCiudad(event)
		return
	
	if (len(moviendo) == 2):
		lineas = copy.deepcopy(finalrutas[moviendo[0]].ruta)
		lineas[moviendo[1]] = [event.x, event.y] # El punto que estamos moviendo
		
		canvas.delete(rutas[moviendo[0]].linea)
		canvas.delete(rutas[moviendo[0]].circulos[moviendo[1]])
		
		rutas[moviendo[0]].circulos[moviendo[1]] = hacerCirculo(event.x, event.y, 3, canvas)
		
		dibujarLinea()
		
		if (eraCiudad): return # Si era ciudad, no hay que mirar que este cerca de una parada ya que detectara la ciudad en la que estaba
		
		for c in finalciudades:
			if (distancia([c.x, c.y], lineas[moviendo[1]]) < 5): # Estamos cerca de una ciudad -> establecerla como parada
				lineas[moviendo[1]] = [c.x, c.y]
				
				finalrutas[moviendo[0]].paradas[moviendo[1]] = c.id # Registrar la parada
				
				canvas.delete(rutas[moviendo[0]].circulos[moviendo[1]]) # Borrar el circulo que decia que este punto era independiente
				rutas[moviendo[0]].circulos[moviendo[1]] = -1 # Echoes of a circle
				
				soltar(None) # Ejecutar como si hubiera soltado el raton :>
				return

	dibujarLinea()

def guardarRuta(event):
	global idR, linea, lineas, paradas, circulos
	
	if (len(lineas) < 2):
		if (len(circulos) > 0): canvas.delete(circulos[0])
		circulos = []
		lineas = []
		paradas = []
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

def borrarPunto(event): # Borrar un punto en una ruta
	global ciudad, moviendo, canvas, rutas, finalrutas, lineas, linea
	
	if (ciudad or len(moviendo) != 2): return # Si se estan editando las ciudades o no se esta editando una recta -> return
	
	if (len(finalrutas[moviendo[0]].ruta) == 2): # Mirar que hay mas de dos puntos, si hay menos se borra
		borrarItem(event)
		return
	
	del finalrutas[moviendo[0]].ruta[moviendo[1]]
	del finalrutas[moviendo[0]].paradas[moviendo[1]]
	
	rutas[moviendo[0]].linea = canvas.create_line(finalrutas[moviendo[0]].ruta)
	
	canvas.delete(rutas[moviendo[0]].circulos[moviendo[1]])
	
	del rutas[moviendo[0]].circulos[moviendo[1]]
	
	rutas[moviendo[0]].ciudad = copy.deepcopy(finalrutas[moviendo[0]])
	
	canvas.delete(linea)
	linea = None
	
	lineas = []
	moviendo = []
	circulos = []

def borrarItem(event): # Borrar una ruta entera
	global canvas, finalciudades, ciudad, moviendo, moviendoC, finalrutas, rutas, lineas, linea, circulos
	
	if (ciudad and moviendoC[0] != -1): # Si se quiere borrar una ciudad, hacer todo esto
		for r in range(len(finalrutas)): # Borrar la ciudad de paradas
			for i in range(len(finalrutas[r].paradas)):
				if (finalrutas[r].paradas[i] == finalciudades[moviendoC[0]].id):
					finalrutas[r].paradas[i] = -1
					rutas[r].circulos[i] = hacerCirculo(finalrutas[r].ruta[i][0], finalrutas[r].ruta[i][1], 3, canvas)
					
			rutas[r].ruta = copy.deepcopy(finalrutas[r]) # Copiar just in case
		
		canvas.delete(ciudades[moviendoC[0]].cuadrado)
		
		del ciudades[moviendoC[0]] # Borrar la ciudad de los arrays de ciudad
		del finalciudades[moviendoC[0]]
		
		moviendoC = [-1]
		return
	
	# Si estamos aqui es porque se esta borrando una ruta
	if (len(moviendo) == 2): # Se quiere borrar una linea que se estaba modificando
		
		lineas = []
		
		canvas.delete(rutas[moviendo[0]].linea) # Borrar linea
		for c in rutas[moviendo[0]].circulos: # Borrar circulos
			canvas.delete(c)
		
		del finalrutas[moviendo[0]] # Quitar la ruta de lo que se escriba en el json
		del rutas[moviendo[0]] # No hay ruta que dibujar, por lo que se borra
		
		canvas.delete(linea)
		linea = None
		
		moviendo = []
	elif (len(circulos) > 0):# Se quiere borrar la linea que se estaba haciendo´´
		
		for c in circulos:
			canvas.delete(c)
		
		lineas = []
		circulos = []
		paradas = []
		
		if (linea != None): canvas.delete(linea)
		
		linea = None

def elegirCiudad(value):
	global trayectosActuales
	
	print("Ciudad elegida : " + value)
	return None

def dibujarLineaRuta():
	global canvas, lineaRuta, rutasActuales, posActual
	
	if (lineaRuta != None): canvas.delete(lineaRuta) # Borrar la linea
	
	if (len(rutasActuales[posActual]) > 1): lineaRuta = canvas.create_line([ruta[1] for ruta in rutasActuales[posActual]], width = 3, fill = "green")

def actualizarPosibilidades():
	global root, trayectosActuales, posActual, finalciudades
	
	if (len(trayectosActuales[posActual]) == 1): # Si solo hay una parada, mostrar todas las posibilidades
		preNombre = trayectosActuales[posActual][0][5].get()
		
		trayectosActuales[posActual][0][1]['menu'].delete(0, 'end')
		
		ciuds = getCiudades(None, finalciudades[getCiudad(preNombre)].id)
		
		for c in ciuds:
			trayectosActuales[posActual][0][1]['menu'].add_command(label = c, command = lambda vals = [trayectosActuales[posActual][0][4], c] : paradaSeleccionada(vals[0], False, 0, vals[1]))
		
		return # Nada más que hacer aquí
	
	for i in range(len(trayectosActuales[posActual])):
		preNombre = trayectosActuales[posActual][i][5].get() 	# Nombre de la ciudad actual
		posNombre = getCiudad(preNombre)						# Posicion de la ciudad en finalciudades
		
		ciuds = []
		
		trayectosActuales[posActual][i][1]['menu'].delete(0, 'end')
		
		if (i == 0): ciuds = getCiudades(finalciudades[posNombre].id, finalciudades[getCiudad(trayectosActuales[posActual][1][5].get())].id) # Primera posicion
		elif (i == len(trayectosActuales[posActual]) - 1):	ciuds = getCiudades(finalciudades[posNombre].id, finalciudades[getCiudad(trayectosActuales[posActual][-2][5].get())].id) # Ultima posicion
		else: # En medio
			ciuds = getCiudades(finalciudades[posNombre].id, finalciudades[getCiudad(trayectosActuales[posActual][i - 1][5].get())].id)
			sig = finalciudades[getCiudad(trayectosActuales[posActual][i + 1][5].get())].nombre
			if (sig in ciuds): ciuds.remove(sig)
		
		ciuds.remove(finalciudades[posNombre].nombre) # Quitar la proxima parada
		
		for c in ciuds:
			trayectosActuales[posActual][i][1]["menu"].add_command(label = c, command = lambda vals = [trayectosActuales[posActual][i][4], i, c] : paradaSeleccionada(vals[0], False, vals[1], vals[2]))

def quitarParadaRuta(par): # Par es la "id" de la linea de widgets (4º posicion) ; devuelve la ultima posicion de una parada en rutasActuales[posActual]  ¡¡¡ ATENCION !!! Tambien borra la parada
	global trayectosActuales, posActual, rutasActuales
	
	poss = getPositions(par) # [anterior ; buscamos ; posterior]
	
	if (poss[0] == None):	del rutasActuales[posActual][0:poss[2]]            		# Es la primera posicion la que ha sido cambiada
	elif (poss[2] == None): del rutasActuales[posActual][(poss[0] + 1):]            # Es la ultima posicion la que ha sido cambiada
	else: 					del rutasActuales[posActual][(poss[0] + 1):poss[2]] 	# Es una posicion intermedia
	
	return poss # Devolver todas las posiciones

def quitarParada(par, borrar = True):
	global trayectosActuales, posActual, anadirParada, trayectoAnt, trayectoSig, trayectoDel, lineaDel, rutasActuales
	
	if (len(trayectosActuales[posActual]) <= 1): return
	
	parada = getParada(par)
	
	if (parada == None): return # Sanity check
	
	for i in range(len(trayectosActuales[posActual][parada[1]]) - 2):
		trayectosActuales[posActual][parada[1]][i].destroy()
		
	length = len(trayectosActuales[posActual])
	dX = [10, 30, 250, 325]
	
	for i in range(parada[1] + 1, length):
		dY = [63 + i*30, 60 + i*30, 65 + i*30, 65 + i*30]
		for j in range(4):
			trayectosActuales[posActual][i][j].place(x = dX[j], y = dY[j])
	
	length -= 1
	
	anadirParada.destroy()
	anadirParada = Button(top, text = "Añadir parada", command = addParada)
	anadirParada.place(x = 10, y = 95 + (length * 30))
	
	trayectoAnt.destroy()
	trayectoAnt = Button(top, text = "Anterior", command = lambda : cambiarHorario(-1))
	trayectoAnt.place(x = 110, y = 95 + (length * 30))
	
	trayectoSig.destroy()
	trayectoSig = Button(top, text = "Siguiente", command = lambda : cambiarHorario(1))
	trayectoSig.place(x = 175, y = 95 + (length * 30))
	
	trayectoDel.destroy()
	trayectoDel = Button(top, text = "Borrar horario", command = borrarHorario)
	trayectoDel.place(x = 240, y = 95 + (length * 30))
	
	lineaDel.destroy()
	lineaDel = Button(top, text = "Borrar linea", command = borrarLinea)
	lineaDel.place(x = 330, y = 95 + (length * 30))
	
	if (borrar):
		poss = quitarParadaRuta(par)
	
		if (poss[0] != None and poss[2] != None): # Recalcular la ruta si la parada que se ha quitado estaba entre medias de otras dos
			posRuta = getRutaPuntos(rutasActuales[posActual][poss[0]][0], rutasActuales[posActual][poss[0] + 1][0])
			
			for i in range(len(posRuta)):
				rutasActuales[posActual].insert(poss[0] + 1 + i, [-1, posRuta[i]])
		
	del trayectosActuales[posActual][parada[1]]
	
	actualizarPosibilidades()
	
	dibujarLineaRuta()

def cambiarHorario(dir, copiar = True): # dir es la direccion en la que nos movemos en posActual -1 o +1
	global top, trayectosActuales, posActual, anadirParada, trayectoAnt, trayectoSig, trayectoDel, lineaDel, horarioAct, rutasActuales
	
	for ruta in trayectosActuales[posActual]: # Esconder los elementos de la ruta que se estaba editando
		for i in range(4):
			ruta[i].place(x = 500, y = 0) # Fuera del frame lol
	
	posActual += dir # Aplicar el cambio deseado
	
	if (posActual >= 0 and posActual < len(trayectosActuales)): # No hay que crear un horario, solamente traer de vuelta los widgets que habia antes
		
		for i in range(len(trayectosActuales[posActual])): # Reposicionar los widgets
			if (len(trayectosActuales[posActual][i]) == 0): continue
		
			for j in range(4):
				dX = [10, 30, 250, 325]
				dY = [93 + i*30, 90 + i*30, 95 + i*30, 95 + i*30]
	
				trayectosActuales[posActual][i][j].place(x = dX[j], y = dY[j]) # Reposicionar todos los elementos para que sean visibles
		
		if (anadirParada != None):
			anadirParada.destroy()
			trayectoAnt.destroy()
			trayectoSig.destroy()
		
		length = len(trayectosActuales[posActual])
		
		anadirParada.destroy()
		anadirParada = Button(top, text = "Añadir parada", command = addParada)
		anadirParada.place(x = 10, y = 95 + (length * 30))
		
		trayectoAnt.destroy()
		trayectoAnt = Button(top, text = "Anterior", command = lambda : cambiarHorario(-1))
		trayectoAnt.place(x = 110, y = 95 + (length * 30))
		
		trayectoSig.destroy()
		trayectoSig = Button(top, text = "Siguiente", command = lambda : cambiarHorario(1))
		trayectoSig.place(x = 175, y = 95 + (length * 30))
		
		trayectoDel.destroy()
		trayectoDel = Button(top, text = "Borrar horario", command = borrarHorario)
		trayectoDel.place(x = 240, y = 95 + (length * 30))
		
		lineaDel.destroy()
		lineaDel = Button(top, text = "Borrar linea", command = borrarLinea)
		lineaDel.place(x = 330, y = 95 + (length * 30))
	
	else: # Estamos "out of bounds" por lo que hay que crear una nueva posicion
		if (posActual < 0):
			posActual = 0
			rutasActuales.insert(0, [])
			trayectosActuales.insert(0, [])
		else:
			rutasActuales.append([])
			trayectosActuales.append([])
		
		if (copiar):
			for parada in trayectosActuales[posActual - dir]:
				addParada(parada[5].get(), parada[2].get("1.0", 'end-1c'), parada[3].get("1.0", 'end-1c'), True) # Añadir las paradas de la anterior
			
			rutasActuales[posActual] = rutasActuales[posActual - dir]
	
	horarioAct.set("Horario " + str(posActual + 1) + '/' + str(len(trayectosActuales)))
	
	dibujarLineaRuta()

def borrarLinea():
	global finaltrenes, idTedit
	
	respuesta = askyesno(title = "Confirmación", message = "¿ Estás seguro que quiere borrar una línea ?")
	
	if (not respuesta): return
	
	if (getTrenId(idTedit) != None): del finaltrenes[getTrenId(idTedit)] # Si la linea existia : borrarla
	
	escribirTrenes()
	generarIdTren()
	
	cancelarTren()
	crearLineaTren()

def borrarHorario():
	global trayectosActuales, rutasActuales, posActual
	
	if (len(trayectosActuales) <= 1): return # Sanity check
	
	pre = posActual
	
	if (posActual > 0):
		cambiarHorario(-1)
		del trayectosActuales[pre]
		del rutasActuales[pre]
	else:
		cambiarHorario(1)
		del trayectosActuales[pre]
		del rutasActuales[pre]
		cambiarHorario(-1)
	
	cambiarHorario(0)

def colorearLinea(value):
	global canvas, posiblesRutas, puntoDivergencia, lineaTemp, posibSelec, parada
	
	if (lineaTemp != None): canvas.delete(lineaTemp) # Borrar linea
	
	posC = getCiudadId(parada[0])
	
	posibSelec = puntoDivergencia.index(value)
	
	puntosTemp = copy.deepcopy(posiblesRutas[posibSelec])
	puntosTemp.append([finalciudades[posC].x, finalciudades[posC].y])
	
	lineaTemp = canvas.create_line(puntosTemp, width = 3, fill = "yellow")

def posibilidadesCerrar(cancelar = True):
	global canvas, selec, rutaSelect, lineaTemp, trayectosActuales, posActual, posibSelec
	
	if (cancelar): # Hacer como si el usuario no hubiera elegido la parada
		quitarParada(trayectosActuales[posActual][-1][4], False)
	
	selec.destroy()
	
	canvas.delete(lineaTemp)
	lineaTemp = None
	
	posiblesRutas = None
	posibSelec = None
	rutaSelect = None
	selec = None

def mostrarPosiblesRutas(t): # t es cómo se tiene que incrustar la ruta una vez se seleccione
	global selec, rutaSelect, rutaSelect, puntoDivergencia, tipo
	
	tipo = t # Guardar el tipo de ruta
	
	selec = Toplevel()
	
	selec.geometry("200x200")
	selec.title("Selecciona una ruta")
	selec.resizable(False, False)
	selec.protocol("WM_DELETE_WINDOW", posibilidadesCerrar) # Llamar funcion cuando se cierre el Toplevel
	
	Label(selec, text = "Elige una ruta").place(x = 50, y = 20)
	Button(selec, text = "Aceptar", command = seleccionarOpcion).place(x = 50, y = 100)
	
	rutaSelectSv = StringVar()
	rutaSelectSv.set(puntoDivergencia[0])
	
	rutaSelect = OptionMenu(selec, rutaSelectSv, *puntoDivergencia, command = colorearLinea)
	rutaSelect.place(x = 50, y = 50)
	
	colorearLinea(puntoDivergencia[0]) # Dibujar la primera ruta cause why fucking not

def seleccionarOpcion(): # Cuando se confirma una ruta a traves de una ruta or smth idk
	global tipo, posActual, posProx, parada, rutasActuales, posibSelec, posiblesRutas, puntoDivergencia, linea
	
	posC = getCiudadId(parada[0])
	
	if (tipo == 0):
		rutasActuales[posActual].insert(0, [parada[0], [finalciudades[posC].x, finalciudades[posC].y]])
		for i in range(len(posiblesRutas[posibSelec])):	rutasActuales[posActual].insert(1 + i, [-1, posiblesRutas[posibSelec][i]]) # Si es la primera posicion, no se borra ninguna parada
	elif (tipo == 1):
		print("1") # ha ha gracias yo del pasado - what the actual f ? TODO
	else:
		for i in range(len(posiblesRutas[posibSelec])):	rutasActuales[posActual].insert(posProx[1] + i, [-1, posiblesRutas[posibSelec][i]]) # Si es la primera posicion, no se borra ninguna parada
		rutasActuales[posActual].append([parada[0], [finalciudades[posC].x, finalciudades[posC].y]]) # Añadir al final del todo la parada que se ha modificado	
	
	posibilidadesCerrar(False)
	dibujarLineaRuta()

def paradaSeleccionada(par, nuevo, index = None, value = None, auto = False): # Se llama cada vez que se cambia de parada ; recibe como argumento el 4º argumento de trayectosActuales[posActual] el pseudo id de cada linea en trayectosActuales[posActual]
	global finalciudades, trayectosActuales, posActual, parada, posProx, rutasActuales
	
	if (auto): # Si la parada ha sido generada automaticamente cuando se carga una linea de tren generada previamente, no hay que crear una ruta
		actualizarPosibilidades()
		return
	
	if (index != None): trayectosActuales[posActual][index][5].set(value)
	
	parada = getParada(par) # Coger [id_ciudad , index_trayectosActuales]
	
	posC = getCiudadId(parada[0]) # Posicion de la ciudad en finalciudades
	if (nuevo):
		posRuta = getRutaPuntos(finalciudades[getCiudad(trayectosActuales[posActual][parada[1] - 1][5].get())].id, parada[0])
		
		if (len(trayectosActuales[posActual]) > 1 and len(posRuta) > 0):
			for i in range(len(posRuta[0]) - 1):
				rutasActuales[posActual].append([-1, posRuta[0][i]])
			
		rutasActuales[posActual].append([parada[0], [finalciudades[posC].x, finalciudades[posC].y]]) # Añadir la posicion de la ciudad que hemos seleccionado con el [id [c_id, [c_x, c_y]]
	else: # Si estamos aqui es porque se ha modificado una parada ya existente
		if (len(trayectosActuales[posActual]) == 1):
			rutasActuales[posActual] = [[parada[0], [finalciudades[posC].x, finalciudades[posC].y]]]
			actualizarPosibilidades()
			return
		
		posProx = quitarParadaRuta(par)
		
		if (posProx[0] == None): # Hay que insertarla al principio
			posRuta = getRutaPuntos(parada[0], finalciudades[getCiudad(trayectosActuales[posActual][parada[1] + 1][5].get())].id)
			
			if (len(posRuta) > 1):
				mostrarPosiblesRutas(0)
				return
			
			rutasActuales[posActual].insert(0, [parada[0], [finalciudades[posC].x, finalciudades[posC].y]])
			
			posRuta = posRuta[0]
			
			for i in range(len(posRuta)):	rutasActuales[posActual].insert(1 + i, [-1, posRuta[i]]) # Si es la primera posicion, no se borra ninguna parada
		elif (posProx[2] == None): # Hay que insertarla al final
			posRuta = getRutaPuntos(rutasActuales[posActual][posProx[0]][0], parada[0])
			
			if (len(posRuta) > 1):	# ERROR : A VECES EL TIPO ES None (POR QUE)
				mostrarPosiblesRutas(2)
				return
			
			posRuta = posRuta[0]
			
			for i in range(len(posRuta)):	rutasActuales[posActual].insert(posProx[1] + i, [-1, posRuta[i]]) # Si es la primera posicion, no se borra ninguna parada
			
			rutasActuales[posActual].append([parada[0], [finalciudades[posC].x, finalciudades[posC].y]]) # Añadir al final del todo la parada que se ha modificado	
		else: # Hay que insertarla entre medias
			posRuta = getRutaPuntos(rutasActuales[posActual][posProx[0]][0], parada[0]) # Desde el punto anterior hasta la nueva parada
			
			if (len(posRuta) > 1):
				mostrarPosiblesRutas(2)
				return
			
			finPos = posProx[0] + 1 # Posicion donde se tiene que insertar
			
			posRuta = posRuta[0]
			
			for i in range(len(posRuta)):
				rutasActuales[posActual].insert(finPos, [-1, posRuta[i]])
				finPos += 1
			
			rutasActuales[posActual].insert(finPos, [parada[0], [finalciudades[posC].x, finalciudades[posC].y]])
			finPos += 1
			
			posRuta = getRutaPuntos(parada[0], finalciudades[getCiudad(trayectosActuales[posActual][parada[1] + 1][5].get())].id)
			
			if (len(posRuta) > 1):
				mostrarPosiblesRutas(2)
				return
			
			posRuta = posRuta[0]
			
			for i in range(len(posRuta)):
				rutasActuales[posActual].insert(finPos + i, [-1, posRuta[i]])
		
		actualizarPosibilidades() # Actualizar las paradas que se pueden elegir
	
	dibujarLineaRuta()

def addParada(pos = "None", lleg = "0000", sali = "0005", autoV = False): # Añadir una parada al horario actual (posActual)
	global root, top, anadirParada, trayectosActuales, posActual, trayectoAnt, trayectoSig, trayectoDel, lineaDel
	
	if (len(trayectosActuales[posActual]) > 0):
		idAnterior = finalciudades[getCiudad(trayectosActuales[posActual][-1][5].get())].id
		ciuds = getCiudades(idAnterior, idAnterior)
	else: ciuds = getCiudades(None, None)
	
	if (len(ciuds) == 0): # Si la parada anterior no esta conectada a ninguna otra, mostrar error y parar
		messagebox.showerror(title = "Error", message = "La parada no tiene ninguna conexión disponible")
		return
	
	ciud = StringVar()
	
	if (pos == "None"): ciud.set(ciuds[0])
	else: ciud.set(pos)
	
	length = len(trayectosActuales[posActual])
	
	dX = [10, 30, 250, 325]
	dY = [93 + (length * 30), 90 + (length * 30), 95 + (length * 30), 95 + (length * 30)]
	
	posId = length
	
	while (posId in [tray[4] for tray in trayectosActuales[posActual]]): posId += 1
	
	trayectosActuales[posActual].append([]) # Crear una nueva parada
	
	# Añadir elementos
	trayectosActuales[posActual][-1].append(Button(top, text = "X", command = lambda a = posId : quitarParada(a)))
	trayectosActuales[posActual][-1].append(OptionMenu(top, ciud, *ciuds, command = lambda a = posId : paradaSeleccionada(a, False)))
	trayectosActuales[posActual][-1].append(Text(top, heigh = 1, width = 4))
	trayectosActuales[posActual][-1].append(Text(top, heigh = 1, width = 4))
	trayectosActuales[posActual][-1].append(posId)
	trayectosActuales[posActual][-1].append(ciud)
	
	paradaSeleccionada(posId, True, auto = autoV) # Llamar que se ha seleccionado una parada en cuanto se crea una nueva parada
	actualizarPosibilidades()
	
	for i in range(4): # Mover todo a la posicion que le corresponde
		trayectosActuales[posActual][-1][i].place(x = dX[i], y = dY[i])
	
	if (len(trayectosActuales[posActual]) > 1 and lleg == "0000" and sali == "0005"):
		trayectosActuales[posActual][-1][2].insert(END, beautifyTiempo(str(int(trayectosActuales[posActual][-2][2].get("1.0",'end-1c')) + 100)))
		trayectosActuales[posActual][-1][3].insert(END, beautifyTiempo(str(int(trayectosActuales[posActual][-2][3].get("1.0",'end-1c')) + 100)))
	else:
		trayectosActuales[posActual][-1][2].insert(END, beautifyTiempo(lleg))
		trayectosActuales[posActual][-1][3].insert(END, beautifyTiempo(sali))
	
	if (anadirParada != None):
		anadirParada.destroy()
		trayectoAnt.destroy()
		trayectoSig.destroy()
		trayectoDel.destroy()
		lineaDel.destroy()
	
	anadirParada = Button(top, text = "Añadir parada", command = addParada)
	anadirParada.place(x = 10, y = 125 + (length * 30))
	
	trayectoAnt = Button(top, text = "Anterior", command = lambda : cambiarHorario(-1))
	trayectoAnt.place(x = 110, y = 125 + (length * 30))
	
	trayectoSig = Button(top, text = "Siguiente", command = lambda : cambiarHorario(1))
	trayectoSig.place(x = 175, y = 125 + (length * 30))
	
	trayectoDel = Button(top, text = "Borrar horario", command = borrarHorario)
	trayectoDel.place(x = 240, y = 125 + (length * 30))
	
	lineaDel = Button(top, text = "Borrar linea", command = borrarLinea)
	lineaDel.place(x = 330, y = 125 + (length * 30))

def elegirColorTren():
	global colorTren
	
	colorTren.configure(bg = colorchooser.askcolor(title ="Elige un color")[1])

def nuevoTren():
	global top, finalciudades, nombreLin, idT, trayectosActuales, posActual, horarioAct, rutasActuales, canvas, lineaRuta, colorTren, selecLn
	
	for i in range(len(trayectosActuales)): # Resetear por si se estaba haciendo una ruta y se pincha en nueva otra vez
		if (len(trayectosActuales[i]) == 0): continue
		for j in range(4):
			trayectosActuales[i][j].destroy()
	
	if (lineaRuta != None): canvas.delete(lineaRuta)
	if (selecLn != None): selecLn.destroy()
	
	posActual = 0
	trayectosActuales = [[]]
	rutasActuales = [[]]
	lineaRuta = None
	
	colorTren = Button(top, bg = "#ff0000", command = elegirColorTren)
	colorTren.place(x = 10, y = 10)
	
	horarioAct.set("Horario " + str(posActual + 1) + '/' + str(len(trayectosActuales)))
	
	if (nombreLin == None): nombreLin = Text(top, height = 1, width = 15)
	
	nombreLin.place(x = 175, y = 50)
	nombreLin.insert(END, "Linea " + str(idT))
	
	Button(top, text = "Guardar", command = guardarTren).place(x = 175, y = 575)
	
	addParada()
	
def trenElegido(value):
	global top, idTedit, trayectosActuales, posActual, finaltrenes, finalciudades, nombreLin, rutasActuales, canvas, lineaRuta, colorTren, selecLn
	
	pos = getTren(value)
	idTedit = finaltrenes[pos].id
	
	print("Cargando el horario de", finaltrenes[pos].nombre)
	
	if (lineaRuta != None): canvas.delete(lineaRuta)
	
	posActual = 0
	trayectosActuales = [[]]
	rutasActuales = [[]]
	lineaRuta = None
	
	selecLn.destroy()
	
	if (nombreLin == None): nombreLin = Text(top, height = 1, width = 15)
	
	nombreLin.place(x = 175, y = 50)
	nombreLin.insert(END, value)
	nombreLin.focus()
	
	for i in range(len(finaltrenes[pos].trayectos)):
		for j in range(len(finaltrenes[pos].trayectos[i][0])):
			addParada(finalciudades[getCiudadId(finaltrenes[pos].trayectos[i][0][j])].nombre, finaltrenes[pos].trayectos[i][2][j], finaltrenes[pos].trayectos[i][3][j], True)
		
		rutasActuales[posActual] = finaltrenes[pos].trayectos[i][1]
		dibujarLineaRuta()
		
		if (i != len(finaltrenes[pos].trayectos) - 1): cambiarHorario(1, False)
	
	Button(top, text = "Guardar", command = guardarTren).place(x = 175, y = 575)
	
	colorTren = Button(top, bg = finaltrenes[pos].color, command = elegirColorTren)
	colorTren.place(x = 10, y = 10)
	
	for ruta in finaltrenes[pos].trayectos:
		rutasActuales.append(ruta[1])

def guardarTren(event = None):
	global idT, finaltrenes, finalciudades, trayectosActuales, nombreLin, rutasActuales, colorTren
	
	if (len(trayectosActuales) < 1): return # Check : la ruta tiene más de una parada
	
	for ruta in trayectosActuales:
		if (len(ruta) < 2):
			print("Hay al menos un horario invalido con insuficientes paradas")
			return # Si hay al menos una ruta con menos de 2 paradas, no se puede guardar visto que no es una ruta valida
	
	for ruta in trayectosActuales:
		for i in range(len(ruta)):
			if (not checkTiempo(ruta[i][2].get("1.0", "end-1c")) or (not checkTiempo(ruta[i][3].get("1.0", "end-1c"))) or (int(ruta[i][2].get("1.0", "end-1c")) >= int(ruta[i][3].get("1.0", "end-1c"))) or (i > 0 and int(ruta[i - 1][3].get("1.0", "end-1c")) >= int(ruta[i][2].get("1.0", "end-1c")))): # Check primero que el formato de tiempo de cada tiempo individual sea correcto, despues mirar que la salida sea despues de la llegada, despues mirar que la llegada a la proxima parada no sea antes que la salida
				print("Hora incorrecta")
				return
	
	temptrayecto = []
	
	for tray in range(len(trayectosActuales)):
		temptrayecto.append([[finalciudades[getCiudad(c[5].get())].id for c in trayectosActuales[tray]], [c[2].get("1.0", 'end-1c') for c in trayectosActuales[tray]], [c[3].get("1.0", 'end-1c') for c in trayectosActuales[tray]]])
		
		temptrayecto[tray].insert(1, [ruta for ruta in rutasActuales[tray]])
	
	posT = getTren(nombreLin.get("1.0", 'end-1c')) # Si el nombre existe, se sobreescribe, sino, se crea uno nuevo
	
	if (posT != None): finaltrenes[posT] = Tren(finaltrenes[posT].id, nombreLin.get("1.0",'end-1c'), colorTren.cget('bg'), copy.deepcopy(temptrayecto))
	else: finaltrenes.append(Tren(idT, nombreLin.get("1.0", 'end-1c'), colorTren.cget('bg'), copy.deepcopy(temptrayecto)))
	
	print("Línea " + nombreLin.get("1.0", 'end-1c') + " guardada")
	
	generarIdTren()
	
	escribirTrenes()
	
	cancelarTren()
	crearLineaTren()
	
def cancelarTren(event = None): # Llamar cuando se cierre la ventana, asi se cancelan los cambios y se resetea todo
	global top, nombreLin, anadirParada, trayectosActuales, posActual, rutasActuales, canvas, lineaRuta, trayectoAnt, trayectoSig, trayectoDel, lineaDel, colorTren
	
	for rutaA in trayectosActuales:
		for linea in rutaA:
			for i in range(4):
				linea[i].destroy() # Destruir los items que se han creado
	
	top.destroy()
	
	if (lineaRuta != None): canvas.delete(lineaRuta)
	
	posActual = 0
	trayectosActuales = [[]] # Vaciar el array
	rutasActuales = [[]]
	lineaRuta = None
	
	top = None
	nombreLin = None
	anadirParada = None
	horarioAct = None
	colorTren = None
	
	trayectoAnt = None
	trayectoSig = None
	trayectoDel = None
	lineaDel = None

def crearLineaTren(): # Se llama cuando se da a la T, crea la ventana y pone el editor en modo crear trenes
	global finaltrenes, top, trayectosActuales, posActual, horarioAct, rutasActuales, lineaRuta, selecLn
	
	if (top != None): cancelarCiudad()
	
	top = Toplevel()
	
	top.geometry("400x600")
	top.title("Crear ruta")
	top.resizable(False, False)
	
	Button(top, text = "Nueva línea", command = nuevoTren).place(x = 150, y = 10)
	
	lins = getLineasDisponibles()
	if (len(lins) > 0):		
		lin = StringVar()
		lin.set("Selecciona una línea")
		
		selecLn = OptionMenu(top, lin, *lins, command = trenElegido)
		selecLn.place(x = 100, y = 50)
	
	posActual = 0
	trayectosActuales = [[]]
	rutasActuales = [[]]
	lineaRuta = None
	
	horarioAct = StringVar()
	horarioAct.set("")
	
	Label(top, textvariable = horarioAct).place(x = 150, y = 75)
	
	top.bind("<Return>", guardarTren)
	top.bind("<Escape>", cancelarTren)
	
	top.protocol("WM_DELETE_WINDOW",  cancelarTren)
	
	top.focus_force()

def escribir(event):
	global top
	
	if (top != None): return # Si hay ventana Pop-up volvemos
	
	escribirCiudades()
	escribirRutas()
	escribirTrenes()

def escribirCiudades():
	global finalciudades
	
	with open(ciudadesF, "w+") as f:
		json.dump([c.__dict__ for c in finalciudades], f, indent = 4)
		f.close()
	print(len(finalciudades), "ciudades guardadas")

def escribirRutas():
	global finalrutas
	
	with open(rutasF, "w+") as f:
		json.dump([r.__dict__ for r in finalrutas], f, indent = 4)
		f.close()
	
	print(len(finalrutas), "rutas guardadas")

def escribirTrenes():
	global finaltrenes
	
	with open(trenesF, "w+") as f:
		json.dump([t.__dict__ for t in finaltrenes], f, indent = 4)
		f.close()
	
	print(len(finaltrenes), "trenes guardados")

def verificarRutas(): # Verificar las rutas que se han cargado
	global finalrutas
	
	error = False
	
	for ruta in finalrutas:
		for i in range(len(ruta.ruta) - 1):
			if (ruta.ruta[i][0] == ruta.ruta[i + 1][0] and ruta.ruta[i][1] == ruta.ruta[i + 1][1]):
				print("Error en ruta", ruta.id, "en posicion", i)
				print(ruta.ruta[i][0], ruta.ruta[i][1])

# --------- BINDS ---------

canvas.pack()

canvas.bind("<ButtonPress-1>", click)

canvas.bind("<ButtonPress-3>", editar)
canvas.bind("<ButtonRelease-3>", soltar)

canvas.bind("<Double-1>", guardarRuta)
canvas.bind("<Motion>", mmove)

root.bind("<C>", lambda event, a = 1 : setModo(a))
root.bind("<R>", lambda event, a = 2 : setModo(a))
root.bind("<T>", lambda event, a = 3 : setModo(a))

root.bind("<c>", lambda event, a = 1 : setModo(a))
root.bind("<r>", lambda event, a = 2 : setModo(a))
root.bind("<t>", lambda event, a = 3 : setModo(a))

root.bind("<BackSpace>", borrarPunto)
root.bind("<Delete>", borrarItem)

root.bind("<Return>", escribir)

canvas.pack()

# --------- INIT FUNCS ---------

def cargarCiudades():
	global canvas, finalciudades, ciudades
	
	print("Cargando ciudades")
	
	try:
		f = open(ciudadesF, 'r')
		data = json.loads(f.read())
		
		for i in data: # Dibujar ciudades
			temp = Ciudad(i['id'], i['nombre'], i['x'], i['y'])
			finalciudades.append(temp)
			
			ciudades.append(CiudadDibujada(temp, canvas.create_rectangle(i['x'] - 2, i['y'] - 2, i['x'] + 2, i['y'] + 2, fill="red", activefill="cyan")))
		
		f.close()
	except JSONDecodeError:
		pass
	
	print(len(finalciudades), "ciudades cargadas")

def cargarRutas():
	global canvas, finalrutas, rutas

	print("Cargando rutas")
	
	try:
		f = open(rutasF, 'r')
		data = json.loads(f.read())
		
		for i in data: # Dibujar rutas
			temp = Ruta(i['id'], i['ruta'], i['paradas'])
			finalrutas.append(temp)
			
			tempC = []
			
			for i in range(len(temp.ruta)):
				if (temp.paradas[i] != -1):
					tempC.append(-1) # Añadir un circulo vacio
					continue
				tempC.append(hacerCirculo(temp.ruta[i][0], temp.ruta[i][1], 3, canvas))
			
			rutas.append(LineaDibujada(temp, canvas.create_line(temp.ruta), tempC))
		
		f.close()
	except JSONDecodeError:
		pass
	
	print(len(finalrutas), "rutas cargadas")

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
		pass
	
	print(len(finaltrenes), "trenes cargados")

# Cargar datos
cargarCiudades()
print()
cargarRutas()
print()
cargarTrenes()
print()
setModo(2)
print()

# Verificar rutas

print("Verificando rutas")
verificarRutas()

# Generar ids
print("Generando ids")
generarIdRuta()
generarIdCiudad()
generarIdTren()

print()

mainloop()