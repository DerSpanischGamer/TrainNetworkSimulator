# En este programa se puede abrir una imagen en la que se selecciona si se quiere crear una ruta o poner ciudades y crea los archivos .json que lo acompañan

# Teclas: R = Ruta ; C = Ciudad ; T = Tren ; BACKSPACE = Borrar

# TODO : ACEPTAR COMO INPUT DEL USUARIO LOS ARCHIVOS PARA UTILIZAR
# TODO : AÑADIR ZOOM
# TODO : CREAR Y EDITAR LINEAS DE TREN CON DIFERENTES HORARIOS (NO RUTAS)
# TODO : AÑADIR UN TEXT HOLDER DONDE SE PUEDAN PONER INFORMACIONES

import copy
import math
import json
from tkinter import *
from tkinter.constants import *
from PIL import Image, ImageTk

# --------- VARIABLES ---------

top = None # Ventana extra para informaciones
textBox = None # Textbox con el nombre de la ciudad que se esta creando
nombreLin = None # Textbox con el nombre de la linea que se esta creando
anadirParada = None # Boton de añadir parada

ciudad = False # Estamos en modo ciudad ?
eraCiudad = False # Estamos moviendo un punto que era una ciudad ?

ciudadesF = "Ciudades.json"
rutasF = "Rutas.json"
trenesF = "Trenes.json"

moviendo = [] # Vacio cuando no se mueve una ruta, cuando se mueve una ruta [ruta_conectada , pos_ocupaba_ciudad]
moviendoC = [-1] # Guarda la informacion de lo que hay que mover cuando se mueve una ciudad [id_ciudad , [ruta_conectada , pos_ocupaba_ciudad], ...]

finalciudades = [] # Guarda las clases Ciudad
ciudades = [] # Guarda las ciudades que son dibujadas

finalrutas = [] # Guarda las clases Ruta que seran las que se escribiran en el json
rutas = [] # Guarda las rutas que son dibujadas

trayectosActuales = [] # Guarda todos los rutaActual
rutaActual = [] # Guarda [botonQuitar, ciudad, salida, llegada, id] del tren que se esta modificando ahora bajo la forma de los items en la pantalla
finaltrenes = [] # Guarda las classes Tren que seran las que se escribiran en el json

idR = -1 # Id para la proxima ruta
idC = -1 # Id para la proxima ciudad
idT = -1 # Id para el proximo tren

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
	def __init__(self, id, nombre, x, y):
		self.id = id
		self.nombre = nombre
		self.x = x
		self.y = y

class Tren:
	def __init__(self, id, nombre, trayecto):
		self.id = id
		self.nombre = nombre
		
		self.ruta = ruta
		
		self.trayecto = trayecto # [ [paradas, ruta, llegadas , salidas], ... ] Array de arrays contiene las pardas, la ruta a seguir, llegadas y salidas de cada tren (pueden haber varios a la vez con rutas diferentes)

# --------- SETUP ---------

root = Tk()
root.title("Editor de rutas")

canvas = Canvas(width=5914, height=3691, bg='black') # Create the canvas with the image size

myimg = ImageTk.PhotoImage(Image.open('smol.jpg'))
canvas.create_image(0, 0, image=myimg, anchor=NW) # Put the image in the frame

texto = canvas.create_text(300, 50, text="Creador de rutas", fill="black", font=('Helvetica 15'))

# --------- FUNCIONES ---------

def create_circle(x, y, r, canvas): # Dibujar un circulo con coords centro y radio
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

def distPointLine(p, pos0, pos1): # Distancia entre un punto y una recta designada por dos puntos
	rc = math.sqrt( (pos1[0] - pos0[0])**2 + (pos1[1] - pos0[1])**2 )
	if (rc == 0):
		return 0
	return abs( (pos1[0] - pos0[0])*(pos0[1] - p[1]) - (pos0[0] - p[0])*(pos1[1] - pos0[1]) ) / rc

def setModo(modo): # 1 = CIUDADES ; 2 = RUTAS ; 3 = TREN
	global texto, ciudad, linea, top, moviendo, moviendoC
	
	if (top != None or linea != None or len(moviendo) > 0 or moviendoC[0] != -1): # No cambiar de modo si se esta creando una nueva ciudad, una nueva linea. Editando una ruta o una ciudad 
		return
	
	if (modo == 1):
		if (linea != None): # Check que no se esten editando rutas
			return
		
		ciudad = True
		canvas.itemconfig(texto, text="Creador de ciudades")
	elif (modo == 2):
		ciudad = False
		canvas.itemconfig(texto, text="Creador de rutas")
	else:
		crearLineaTren()

def existeNombre(nombre): # Check si existe el nombre de la ciudad o no
	for n in finalciudades:
		if (nombre == n.nombre):
			return True
	return False

def getLineasDisponibles(): # Devuelve el nombre de todas las lineas de tren disponibles para modificar
	return [t.nombre for t in finaltrenes]

def getRuta(id): # Devuelve la posicion de la Ruta en finalrutas
	
	for i in range(len(finalrutas)):
		if (finalrutas[i].id == id):
			return i
	
	return None

def getTren(nombre): # Devuelve la posicion de la Ciudad en finalciudades
	global finaltrenes
	
	for i in range(len(finaltrenes)):
		if (finaltrenes.nombre == nombre):
			return i
	return None

def getRutasPorCiudad(idC): # Rutas que pasan por una ciudad
	temp = [] # Ciudades 

	for r in finalrutas:
		if (idC in r.paradas and not r.id in temp):
			temp.append(r.id)

	return temp

def getCiudadId(id): # Devuelve la posicion de la Ciudad en finalciudades
	for i in range(len(finalciudades)):
		if (finalciudades[i].id == id):
			return i
	
	return None

def getCiudad(nombre): # Devuelve la posicion de la Ciudad en finalciudades
	global finalciudades
	
	for i in range(len(finalciudades)):
		if (finalciudades[i].nombre == nombre):
			return i
	
	return None

def getCiudades(idC = None): # Devuelve la lista de todas las ciudades disponibles para que pase un tren
	if (idC == None):
		return [c.nombre for c in finalciudades]
	
	previo = [idC] # Lista con ids de las paradas que hay que escanear
	after = [] # Lista con ids de las paradas que han sido escaneadas
	
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
	
	after.remove(idC) # Quitar la ciudad de origen
	
	return [finalciudades[getCiudadId(c)].nombre for c in after] # Quitar la ciudad que se nos ha dado

def getRutaPuntos(origen, destino): # Devuelve una ruta (serie de puntos) entre dos puntos (origen, destino) TODO : HACER QUE MUESTRE TODAS LAS RUTAS POSIBLES
	return None

def beautifyTiempo(txt):
	return "0"*(4 - len(txt)) + txt

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
	
	if (top != None):
		return
	
	lineas = [event.x, event.y]
	
	top = Toplevel()
	top.title("Crear ciudad	")
	
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
	
	if (len(moviendo) == 2 or top != None): # Si se esta moviendo o haciendo una linea de tren
		return
	
	coords = [event.x, event.y]
	
	paradas.append(-1)
	circulos.append(create_circle(event.x, event.y, 3, canvas)) # Añadir circulo del lugar actual
	
	for i in range(len(finalciudades)): # Detectar si el click ha sido cerca de una ciudad para registrarlo como una parada
		if (distancia(coords, [finalciudades[i].x, finalciudades[i].y]) < 5):
			canvas.delete(circulos[-1])
			circulos[-1] = -1 # Mantener algo por si acaso se borrara la estacion
			
			coords = [finalciudades[i].x, finalciudades[i].y]
			paradas[-1] = finalciudades[i].id
			break
	
	lineas.append(coords) # Si no se ha seleccionado una ciudad, entonces se crea un circulo para poder mover (no pasa con lineas nuevas)
	
	dibujarLinea()

def editarCiudad(coords):
	global finalciudades, ciudades, moviendoC
	
	for i in range(len(finalciudades)): # Coger ciudad
		if (distancia([finalciudades[i].x, finalciudades[i].y], coords) < 4):
			moviendoC = [i]
			
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
	
	if (linea != None or len(rutas) == 0): # Si esta creando una linea o no hay lineas que editar, se vuelve
		return
	
	for r in range(len(finalrutas)): # Detectar si el click ha sido en un punto de inflexion de la ruta para moverlo
		for i in range(len(finalrutas[r].ruta)):
			if (distancia(finalrutas[r].ruta[i], coords) < 5):
				moviendo = [r, i]
				
				eraCiudad = False
				
				if (finalrutas[r].paradas[i] != -1): # El punto que se ha seleccionado es una parada
					rutas[r].circulos[i] = create_circle(event.x, event.y, 3, canvas) # Crear un circulo visto que ya no es una parada, si no un punto de inflexion de la ruta
					
					finalrutas[r].paradas[i] = -1 # Decir que la parada anterior ya no es una parada
					
					eraCiudad = True

				return
	
	if (len(moviendo) > 0): # Si ya se está moviendo un punto de inflexion, volver
		return
	
	for r in range(len(finalrutas)): # Añadir puntos en una recta
		for i in range(len(finalrutas[r].ruta) - 1):
			if (distPointLine(coords, finalrutas[r].ruta[i], finalrutas[r].ruta[i + 1]) < 5):
				
				finalrutas[r].ruta.insert(i+1, [event.x, event.y]) # Insertar la posicion actual en la lista
				finalrutas[r].paradas.insert(i+1, -1) # Decir que el punto que acabamos de insertar no es una parada
				
				rutas[r].circulos.insert(i+1, create_circle(event.x, event.y, 3, canvas)) # Poner un ciculo visto que no es una parada
				
				moviendo = [r, i+1] # Indicar el punto que estamos moviendo visto que ya ha sido integrado en la lista
				
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
		return
	
	if (len(moviendo) == 0): # Si no se esta moviendo nada : return
		return
	
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
		
		rutas[moviendo[0]].circulos[moviendo[1]] = create_circle(event.x, event.y, 3, canvas)
		
		dibujarLinea()
		
		if (eraCiudad): # Si era ciudad, no hay que mirar que este cerca de una parada ya que detectara la ciudad en la que estaba
			return
		
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
		canvas.delete(circulos[0])
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

def borrarPunto(event):
	global ciudad, moviendo, canvas, rutas, finalrutas, lineas, linea
	
	if (ciudad or len(moviendo) != 2): # Si se estan editando las ciudades o no se esta editando una recta -> return
		return
	
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
		for c in circulos:
			canvas.delete(c)
		
		lineas = []
		circulos = []
		paradas = []
		
		canvas.delete(linea)
		linea = None

def elegirCiudad(value):
	global rutaActual
	
	print(value)

def quitarParada(par):
	global rutaActual, anadirParada
	
	pos = -1
	
	for i in range(len(rutaActual)):
		if (rutaActual[i][4] == par):
			pos = i
			break
	
	if (pos == -1): # Sanity check
		return
	
	for i in range(len(rutaActual[pos]) - 2):
		rutaActual[pos][i].destroy()
	
	dX = [10, 30, 150, 220]
	
	for i in range(pos + 1, len(rutaActual)):
		dY = [43 + i*30, 40 + i*30, 45 + i*30, 45 + i*30]
		for j in range(4):
			rutaActual[i][j].place(x = dX[j], y = dY[j])
	
	del rutaActual[pos]
	
	anadirParada.destroy()
	anadirParada = Button(top, text = "Añadir parada", command = addParada)
	anadirParada.place(x = 10, y = 75 + len(rutaActual)*30)

def addParada(pos = "None", lleg = "0000", sali = "0005"): # TODO : CAMBIAR A ESTRUCTURA DE rutaActual para acomodar los horarios (mismo tren que puede pasar varias veces)
	global top, rutaActual, anadirParada
	
	if (len(rutaActual) > 0):
		ciuds = getCiudades(finalciudades[getCiudad(rutaActual[-1][5].get())].id)
	else:
		ciuds = getCiudades(None)
	
	ciud = StringVar()
	
	if (pos == "None"):
		ciud.set(ciuds[0])
	else:
		ciud.set(pos)
	
	length = len(rutaActual)
	
	dX = [10, 30, 250, 325]
	dY = [73 + length*30, 70 + length*30, 75 + length*30, 75 + length*30]
	
	temp = []
	
	temp.append(Button(top, text = "X", command = lambda a = length : quitarParada(a)))
	temp.append(OptionMenu(top, ciud, *ciuds))
	temp.append(Text(top, heigh = 1, width = 4))
	temp.append(Text(top, heigh = 1, width = 4))
	temp.append(length)
	temp.append(ciud)
	
	for i in range(4):
		temp[i].place(x = dX[i], y = dY[i])
	
	rutaActual.append(temp)
	
	if (len(rutaActual) > 1 and lleg == "0000" and sali == "0005"):
		rutaActual[-1][2].insert(END, beautifyTiempo(str(int(rutaActual[-2][2].get("1.0",'end-1c')) + 100)))
		rutaActual[-1][3].insert(END, beautifyTiempo(str(int(rutaActual[-2][3].get("1.0",'end-1c')) + 100)))
	else:
		rutaActual[-1][2].insert(END, beautifyTiempo(lleg))
		rutaActual[-1][3].insert(END, beautifyTiempo(sali))
	
	if (anadirParada != None): anadirParada.destroy()
	anadirParada = Button(top, text = "Añadir parada", command = addParada)
	anadirParada.place(x = 10, y = 105 + length*30)

def nuevoTren():
	global top, rutaActual, finalciudades, nombreLin, idT
	
	for i in range(len(rutaActual)): # Resetear por si se estaba haciendo una ruta y se pincha en nueva otra vez
		for j in range(4):
			top.delete(rutaActual[i][j])
	
	rutaActual = []
	
	if (nombreLin == None): nombreLin = Text(top, height = 1, width = 15)
	nombreLin.place(x = 175, y = 50)
	nombreLin.insert(END, "Linea " + str(idT))
	nombreLin.focus()
	
	addParada()
	
def trenElegido(value):
	global top, rutaActual, finaltrenes, nombreLin
	
	pos = getTren(value)
	
	for i in range(len(rutaActual)): # Resetear por si se estaba haciendo una ruta y se pincha en nueva otra vez
		for j in range(4):
			top.delete(rutaActual[i][j])
	
	rutaActual = []
	
	if (nombreLin == None): nombreLin = Text(top, height = 1, width = 15)
	nombreLin.place(x = 175, y = 50)
	nombreLin.insert(END, value)
	nombreLin.focus()
	
	for i in range(finaltrenes[pos].paradas):
		addParada(finaltrenes[pos].paradas[i], finaltrenes[pos].llegadas[i], finaltrenes[pos].salidas[i])
	
	print(value)

def guardarTren(event = None):
	global idT, finaltrenes, finalciudades, rutaActual, nombreLin
	
	if (len(rutaActual) < 2): # Check : la ruta tiene más de una parada
		return
	
	for t in finaltrenes: # Check : nombre nuevo
		if (t.nombre == nombreLin.get("1.0",'end-1c')):
			return
	
	for i in range(len(rutaActual)):
		if (not checkTiempo(rutaActual[i][2].get("1.0", "end-1c")) or (not checkTiempo(rutaActual[i][3].get("1.0", "end-1c"))) or (int(rutaActual[i][2].get("1.0", "end-1c")) >= int(rutaActual[i][3].get("1.0", "end-1c"))) or (i > 0 and int(rutaActual[i - 1][3].get("1.0", "end-1c")) >= int(rutaActual[i][2].get("1.0", "end-1c")))): # Check primero que el formato de tiempo de cada tiempo individual sea correcto, despues mirar que la salida sea despues de la llegada, despues mirar que la llegada a la proxima parada no sea antes que la salida
			print("Hora incorrecta")
			return
	
	temptrayecto = [[finalciudades[getCiudad(c[5].get())].id for c in rutaActual], ,[c[2].get("1.0", "end-1c") for c in rutaActual], [c[3].get("1.0", "end-1c") for c in rutaActual]]
	
	finaltrenes.append(Tren(idT, nombreLin.get("1.0",'end-1c'), ))
	
	generarIdTren()
	
	escribirTrenes()
	
	print("Línea de tren guardada")

def cancelarTren(evenet = None):
	global top, nombreLin, anadirParada, rutaActual
	
	top.destroy()
	
	rutaActual = []
	
	top = None
	nombreLin = None
	anadirParada = None

def crearLineaTren():
	global finaltrenes, top
	
	top = Toplevel()
	top.geometry("400x400")
	top.title("Crear ruta")
	
	Button(top, text = "Nueva línea", command = nuevoTren).pack()
	
	lins = getLineasDisponibles()
	lin = StringVar()
	lin.set("Selecciona una línea")
	if (len(lins) > 0):
		OptionMenu(top, lin, *lins, command = trenElegido).pack()
	
	Button(top, text = "Guardar", command = guardarTren).place(x = 175, y = 375)
	
	top.bind("<Return>", guardarTren)
	top.bind("<Return>", cancelarTren)
	
	top.protocol("WM_DELETE_WINDOW",  cancelarTren)
	
	top.focus_force()

def escribir(event):
	global top
	
	if (top != None): # Si hay ventana Pop-up volvemos
		return
	
	escribirCiudades()
	escribirRutas()
	escribirTrenes()

def escribirCiudades():
	global finalciudades
	
	with open(ciudadesF, "w+") as f:
		json.dump([c.__dict__ for c in finalciudades], f, indent=4)
		f.close()
	print(len(finalciudades), "ciudades guardadas")

def escribirRutas():
	global finalrutas
	
	with open(rutasF, "w+") as f:
		json.dump([r.__dict__ for r in finalrutas], f, indent=4)
		f.close()
	
	print(len(finalrutas), "rutas guardadas")

def escribirTrenes():
	global finaltrenes
	
	with open(trenesF, "w+") as f:
		json.dump([t.__dict__ for t in finaltrenes], f, indent=4)
		f.close()
	
	print(len(finaltrenes), " trenes guardados")

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

def do_zoom(event):
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    factor = 1.001 ** event.delta
    canvas.scale(ALL, x, y, factor, factor)

# TEST : FUNCIONA - PROBLEMA LA IMAGEN DE FONDO Y LAS RUTAS NO ESCALAN
# canvas.bind("<MouseWheel>", do_zoom)
# canvas.bind('<ButtonPress-1>', lambda event: canvas.scan_mark(event.x, event.y))
# canvas.bind("<B1-Motion>", lambda event: canvas.scan_dragto(event.x, event.y, gain=1))


# --------- INIT FUNCS ---------

def cargarCiudades():
	global canvas, finalciudades, ciudades
	
	print("Cargando ciudades")
	
	f = open(ciudadesF, 'r')
	data = json.loads(f.read())
	
	for i in data: # Dibujar ciudades
		temp = Ciudad(i['id'], i['nombre'], i['x'], i['y'])
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
				tempC.append(-1) # Añadir un circulo vacio
				continue
			tempC.append(create_circle(temp.ruta[i][0], temp.ruta[i][1], 3, canvas))
		
		rutas.append(LineaDibujada(temp, canvas.create_line(temp.ruta), tempC))
	
	f.close()
	
	print(len(finalrutas), "rutas cargadas")

def cargarTrenes():
	global finaltrenes
	
	print("Cargando trenes")
	
	f = open(trenesF, 'r')
	data = json.loads(f.read())
	
	for i in data: # Meter trenes en la lista
		finaltrenes.append(Tren(i['id'], i['nombre'], i['ruta'], i['paradas'], i['horarios']))
	
	f.close()
	
	print(len(finaltrenes), "trenes cargados")

cargarCiudades()
print()
cargarRutas()
print()
cargarTrenes()
print()
setModo(2)
print()
print("Generando ids")
generarIdRuta()
generarIdCiudad()
generarIdTren()
print()

mainloop()