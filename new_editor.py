import math
import json
from tkinter import *
from copy import deepcopy
from PIL import Image, ImageTk
from tkinter import colorchooser

# ========= VARIABLES =========

# --- Ventana ---

# . Top level stuff .

top = None # Ventana extra para informaciones

fondo = "Mapa_paradas.png"

# . Lineas, puntos y circulos .

puntos_ciudades = []

lineas_rutas = []
lineas_ruta_actual = []

# . Ciudades .

pos_ciudad = None # Posicion de la ciudad que se esta moviendo en el array ciudades

moviendo_ciudad = False # Moviendo ciudad ?

max_radio_ciudad = 5 # Radio de busqueda de ciudades despues de un click derecho

size_rectangulo = 3 # Tamaño rectangulos ciudades

new_ciudad_coords = [] # Coordenadas nueva ciudad

texto_ciudad = None # Texto que dice la ciudad que estamos moviendo

ventana_nombre = None # Ventana que tiene lel text box input_nombre
input_nombre = None # Text box donde se mete el nombre de la nueva ciudad

# . Rutas .

max_radio_linea = 5 # Distancia maxima entre linea lugar de click

ruta_moviendo = None # Posicion de la ruta que se esta moviendo en rutas
punto_moviendo = None # Posicion del punto que se esta moviendo en la lista ruta_actual.puntos

ruta_actual = None # Ruta actual que se esta creando o modificando

estado_ruta = 0 # 0 = nada ; 1 = creando ruta ; 2 = modificar ruta

linea_temp = None # Linea temp

rutas_con_ciudad = [] # Cuando se mueve una ciudad que tiene rutas -> aqui se guardan la posicion en rutas de las rutas que incluyen a la ciudad
posicion_en_ruta = [] # Same, pero aqui se guarda la posicion de la ciudad que se esta moviendo en cada array rutas[rutas_con_ciudad].puntos

# . Lineas .

estado_linea = 0 # 0 = nada ; 1 = creando linea ; 2 = modificando linea

linea_actual = None # Linea actual que se esta editando

top_lin = None # Ventana de linea

pos_trayecto = 0 # Posicion del trayecto en linea.trayectos[pos_trayecto] que se esta editando

lin = None # String Var de las lineas disponibles
selecLn = None # Dropdown menu para seleccionar linea existente
nombreLin = None # Textbox con el nombre de la linea (nueva o existente)
colorLinea = None # Colorpicker para el color de la linea
trayecto_actual = None # Label con el numero del trayecto que estamos editando

anadirParada = None # Boton añadir parada
trayectoAnt = None # Boton trayecto anterior
trayectoSig = None # Boton trayecto siguiente
trayectoDel = None # Boton borrar trayecto
lineaDel = None # Boton borrar linea

botones_paradas = None # Clase en la que se guardaaran todos los botones

# --- Status ---

status = 0 # 0 = ciudades ; 1 = rutas ; 2 = trayectos

texto_status = None # Texto que indica que se esta haciendo ahora : modificar ciudades, rutas o trayectos

# --- Archivos para leer ---

ciudadesF = "Ciudades.json"
rutasF = "Rutas.json"
trenesF = "Trenes.json"

# --- Datos mapa ---

ciudades = [] # Todas la ciudades en el mapa
rutas = [] # Todas las rutas en el mapa
lineas = [] # Todos los trayectos de trenes

# --- Editor ---

new_id_ciudad = -1 # Id para la proxima ciudad
new_id_ruta = -1 # Id para la proxima ruta
new_id_linea = -1 # Id para la proxima linea

# ========= CLASES =========

# . Data structures .

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
		
		self.salidas = salidas
		self.llegadas = llegadas

class Linea:
	def __init__(self, id, nombre, color, trayectos):
		self.id = id
		self.nombre = nombre
		self.color = color
		
		self.trayectos = trayectos

# . Clases visuales .

class Parada_visual:
	def __init__(self, selector = [], llegadas = [], salidas = [], quitar = None):
		self.selector = selector
		
		self.llegadas = llegadas
		self.salidas = salidas
		
		self.quitar = quitar

# ========= FUNCIONES =========

# --- Set-up ---

root = Tk()
root.title("Editor de rutas")

canvas = Canvas(width = 1920, height = 1080, bg = 'black') # Create the canvas with the image size

myimg = ImageTk.PhotoImage(Image.open(fondo))
canvas.create_image(0, 0, image = myimg, anchor = NW) # Put the image in the frame

canvas.create_text(50, 50, text = "Creador de rutas", fill = "black", font = ('Helvetica 15'), justify = "left", anchor="w")
canvas.create_text(50, 75, text = "C : Añadir / modificar ciudades  R : Crear / modificar rutas  L : Crear / modificar lineas", fill = "black", font = ('Helvetica 15'), justify = "left", anchor="w")
texto_status = canvas.create_text(50, 100, text = "Actualmente : editando ciudades", fill = "black", font = ('Helvetica 15'), justify = "left", anchor="w")

root.resizable(False, False)

canvas.pack()

# --- Funciones de base ---

def beautifyTiempo(txt):
	return "0" * (4 - len(txt)) + txt # Devuelve la hora con ceros delante

# . Calcular distancias .

def calcular_distancia(coords1, coords2):
	return math.sqrt( (coords1[0] - coords2[0])**2 + (coords1[1] - coords2[1])**2 )

def calcular_distancia_punto(punto1, punto2, coord):
	return abs( (punto2[1] - punto1[1])*coord[0] - (punto2[0] - punto1[0])*coord[1] + punto2[0]*punto1[1] - punto2[1]*punto1[0] ) / math.sqrt( (punto2[1] - punto1[1])**2 + (punto2[0] - punto1[0])**2 )

# . Posiciones en arrays .

def get_posicion_ciudad(id_c):
	global ciudades
	
	for i in range(len(ciudades)):
		if ciudades[i].id == id_c:
			return i
	
	return None

# . Route finder .

def ciudades_accesibles(id_ciudad): # TODO : AQUI SEGURO QUE SE PUEDE OPTIMIZAR PRE-COMPILANDO LOS SETS -> LOOKUP TABLE
	global rutas, ciudades
	
	if id_ciudad == None: return [c.id for c in ciudades] # Si id_ciudad es None -> devolver todas las ciudades
	
	ciudades_acc = set() # Ciudades accesibles
	
	for r in rutas:
		temp_set = set() # Set con las ciudades que pasan por la ruta r
		add_set = False # Añadimos temp_set a ciudades_acc ?
		
		for parada in r.puntos:
			print(parada.id_ciudad)
			
			if parada.id_ciudad == None: continue # Si el punto de la ruta no es una parada -> ignorar
			
			if parada.id_ciudad == id_ciudad: add_set = True
			else: temp_set.add(parada.id_ciudad)
		
		if add_set: ciudades_acc = ciudades_acc.union(temp_set)
	
	return list(ciudades_acc)

# --- IDs managers ---

def generar_nuevo_id_ciudad():
	global ciudades, new_id_ciudad
	
	i = 0
	while True:
		salir = True
		
		for c in ciudades:
			if c.id == i:
				salir = False
				break
		
		if salir: break
		else: i += 1
	
	new_id_ciudad = i

def generar_nuevo_id_ruta():
	global ciudades, new_id_ruta
	
	i = 0
	while True:
		salir = True
		
		for r in rutas:
			if r.id == i:
				salir = False
				break
		
		if salir: break
		else: i += 1
	
	new_id_ciudad = i

def generar_nuevo_id_linea():
	global lineas, new_id_linea
	
	i = 0
	while True:
		salir = True
		
		for l in lineas:
			if l.id == i:
				salir = False
				break
		
		if salir: break
		else: i += 1
	
	new_id_linea = i

# --- Funciones para guardar ---

def guardar_ciudades():
	global ciudades, ciudadesF
	
	with open(ciudadesF, "w+") as f:
		json.dump([c.__dict__ for c in ciudades], f, indent = 4)
		f.close()
	
	print(f"{len(ciudades)} ciudades guardadas")

def guardar_rutas():
    global rutas, rutasF
    
    with open(rutasF, "w") as f:
        # Convert Ruta objects to dictionaries, ensuring Punto objects are also converted to dictionaries
        rutas_serializadas = []
        for ruta in rutas:
            ruta_dict = ruta.__dict__.copy()  # Copy Ruta dictionary
            ruta_dict['puntos'] = [p.__dict__ for p in ruta.puntos]  # Convert each Punto to a dictionary
            rutas_serializadas.append(ruta_dict)
        
        # Dump the serialized list to the JSON file
        json.dump(rutas_serializadas, f, indent=4)
    
    print(f"{len(rutas)} rutas guardadas")

def guardar_lineas():
	return # TODO : FINISH

# --- Funciones para cargar ---

def cargar_ciudades():
	global ciudadesF, ciudades
	
	try:
		f = open(ciudadesF, 'r')
		data = json.loads(f.read())
		
		for i in data: # Cargar ciudades
			ciudades.append( Ciudad(i['id'], i['nombre'], i['coords']) )
		
		dibujar_ciudades()
		
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
		
		dibujar_rutas()
		
	except JSONDecodeError:
		pass

def cargar_lineas():
	return # TODO : FINISH

# --- Status manager ---

def change_status(new_s):
	global status, input_nombre, moviendo_ciudad, pos_ciudad, new_ciudad_coords, ventana_nombre, input_nombre, estado_ruta, ruta_actual, linea_temp, estado_linea
	
	if new_s == status: return # Si queremos cambiar al mismo modo del que estamos -> don't
	
	# --- Mirar si es posible cambiar el modo ---
	
	if status == 0:	 # . Ciudad -> new_s .
		if input_nombre == None and moviendo_ciudad == False: # Si no se esta creando una nueva ciudad AND no se esta moviendo una ciudad -> cambiar de estatus
			status = new_s
			
			pos_ciudad = None
			
			new_ciudad_coords = []
			
			ventana_nombre = None
			input_nombre = None
		else:
			print("No se puede cambiar de modo porque se esta creando una nueva ciudad o se esta moviendo una ciudad ya existente")
			return
	elif status == 1: # . Ruta -> new_s .
		if estado_ruta == 0: # No estamos haciendo nada -> se puede cambiar de modo
			status = new_s
			
			linea_temp = None
			ruta_actual = Ruta(0, [])
		else:
			print("Se esta creando o editando una ruta")
			return
	elif status == 2: # . Lineas -> new_s .
		if estado_linea == 0: # No estamos haciendo nada -> se puede cambiar de modo
			status = new_s
		else:
			print("Se esta creando o editando una ruta")
			return
	
	# . Trayecto -> new_s .
	
	if status == 2: # Si el nuevo estatus es Lineas -> abrir la ventana
		abrir_ventana_lineas()
	
	# --- Indicar el cambio de modo ---
	
	txts = ["Actualmente : editando ciudades", "Actualmente : editando rutas", "Actualmente : editando lineas"]
	canvas.itemconfig(texto_status, text = txts[new_s])

# --- Funciones dibujar ---

# . Ciudades .

def borrar_ciudades():
	global canvas, puntos_ciudades
	
	for c in puntos_ciudades:
		canvas.delete(c)
	
	puntos_ciudades	= []

def dibujar_ciudades():
	global ciudades, puntos_ciudades
	
	for c in ciudades:
		puntos_ciudades.append(canvas.create_rectangle(c.coords[0] - size_rectangulo, c.coords[1] - size_rectangulo, c.coords[0] + size_rectangulo, c.coords[1] + size_rectangulo, fill = 'red', activefill = 'cyan'))

# . Rutas .

def borrar_rutas():
	global canvas, lineas_rutas
	
	for l in lineas_rutas:
		for linea in l:
			canvas.delete(linea)
	
	lineas_rutas = []

def dibujar_rutas():
	global rutas, canvas, lineas_rutas
	
	for r in rutas:
		lineas_rutas.append([])
		for i in range(len(r.puntos) - 1):
			lin = canvas.create_line(r.puntos[i].coords[0], r.puntos[i].coords[1], r.puntos[i + 1].coords[0], r.puntos[i + 1].coords[1])
			lineas_rutas[-1].append(lin)

def borrar_ruta_actual():
	global canvas, lineas_ruta_actual
	
	for linea in lineas_ruta_actual:
		canvas.delete(linea)
	
	lineas_ruta_actual = []

def dibujar_ruta_actual():
	global canvas, ruta_actual, lineas_ruta_actual
	
	for i in range(len(ruta_actual.puntos) - 1):
		lineas_ruta_actual.append(canvas.create_line(ruta_actual.puntos[i].coords[0], ruta_actual.puntos[i].coords[1], ruta_actual.puntos[i + 1].coords[0], ruta_actual.puntos[i + 1].coords[1]))

# --- Funciones clicks ---

def registrarCiudad(event = None):
	global ventana_nombre, input_nombre, new_ciudad_coords, ciudades
	
	nuevo_nombre = input_nombre.get("1.0", "end-1c")
	
	# --- Check nombre ---
	
	if len(nuevo_nombre) < 2 or len(nuevo_nombre) > 15:
		print("El nombre es demasiado corto o largo (min : 2 max : 15)")
		return
	
	if (nuevo_nombre[-1] == '\n'): nuevo_nombre = nuevo_nombre[0:-1]
	
	for c in ciudades:
		if c.nombre == nuevo_nombre:
			print(f"La ciudad {nuevo_nombre} ya existe")
			return
	
	# --- Crear nueva ciudad ---
	
	nueva_ciudad = Ciudad(new_id_ciudad, nuevo_nombre, new_ciudad_coords)
	ciudades.append(nueva_ciudad)
	generar_nuevo_id_ciudad()
	
	# --- Add punto ---
	
	borrar_ciudades()
	dibujar_ciudades()
	
	# --- Borrar la ventana de texto ---
	
	ventana_nombre.destroy()
	ventana_nombre = None
	input_nombre = None # Resetear la variable input_nombre para decir que ya se ha acabado de editar la nueva ciudad

def cancelarCiudad(event = None):
	global ventana_nombre, input_nombre
	
	# --- Borrar la ventana de texto ---
	
	ventana_nombre.destroy()
	ventana_nombre = None
	input_nombre = None # Resetear la variable input_nombre para decir que ya se ha acabado de editar la nueva ciudad

# --- Funciones click ---

# . Click izquierdo .

def click_ciudad(event):
	global ventana_nombre, input_nombre, new_ciudad_coords
	
	new_ciudad_coords = [event.x, event.y]
	
	# --- Preguntar nombre ---
	
	ventana_nombre = Toplevel()
	ventana_nombre.title("Crear ciudad")
	ventana_nombre.resizable(False, False)
	
	input_nombre = Text(ventana_nombre, height = 1, width = 15)
	input_nombre.focus()
	input_nombre.pack()
	
	Button(ventana_nombre, text = "Aceptar", command = registrarCiudad).pack()
	
	Button(ventana_nombre, text = "Cancelar", command = cancelarCiudad).pack()
	
	ventana_nombre.bind("<Return>", registrarCiudad)
	ventana_nombre.bind("<Escape>", cancelarCiudad)
	
	ventana_nombre.protocol("WM_DELETE_WINDOW",  cancelarCiudad)
	
	ventana_nombre.focus_force()

def click_ruta(event):
	global ciudades, rutas, max_radio_ciudad, estado_ruta
	
	if estado_ruta == 2: return # Sanity check
	
	estado_ruta = 1 # Estamos creando una ruta si estamos aqui
	
	# --- Buscar ciudad cercana ---
	
	coords = [event.x, event.y]
	
	click_ciudad = None
	for c in ciudades:
		if calcular_distancia(coords, c.coords) < max_radio_ciudad:
			click_ciudad = c.id
			coords = c.coords
	
	# --- Añadir punto a la ruta actual ---
	
	ruta_actual.puntos.append(Punto(coords, False, click_ciudad)) # Add el punto, si hay una ciudad -> click_ciudad ; si no ciudad -> None
	
	# --- Redibujar ---
	
	borrar_ruta_actual()
	dibujar_ruta_actual()

# . Click derecho .

def editar_ciudad(event):
	global ciudades, max_radio_ciudad, pos_ciudad, moviendo_ciudad, canvas, ciudades, texto_ciudad, rutas_con_ciudad, posicion_en_ruta
	
	coords = [event.x, event.y]
	
	# --- Buscar la ciudad la mas cercana con un radio max ---
	
	pos_ciudad = None
	for c in ciudades:
		if calcular_distancia(coords, c.coords) < max_radio_ciudad:
			pos_ciudad = get_posicion_ciudad(c.id)
			break
	
	if (pos_ciudad == None): return
	
	# --- Mover la ciudad ---
	
	moviendo_ciudad = True
	
	# --- Redibujar ---
	
	texto_ciudad = canvas.create_text(50, 125, text = f"Moviendo : {ciudades[pos_ciudad].nombre}", fill = "black", font = ('Helvetica 15'), justify = "left", anchor="w")
	
	# --- Buscar rutas que usan la ciudad ---
	
	rutas_con_ciudad = []
	posicion_en_ruta = []
	
	id_ciudad_actual = ciudades[pos_ciudad].id
	
	j = -1
	for r in rutas:
		j += 1
		for i in range( len(r.puntos) ):
			if id_ciudad_actual == r.puntos[i].id_ciudad:
				rutas_con_ciudad.append(j)
				posicion_en_ruta.append(i)
	
	borrar_ciudades()
	dibujar_ciudades()

def soltar_ciudad(event):
	global ciudades, ciudades, moviendo_ciudad, pos_ciudad, canvas, texto_ciudad
	
	coords = [event.x, event.y]
	
	# --- Guardar el nuevo lugar ---
	
	ciudades[pos_ciudad].coords = coords
	
	# --- Redibujar ---
	
	borrar_ciudades()
	dibujar_ciudades()
	
	# --- Quitar el texto ---
	
	canvas.delete(texto_ciudad)
	texto_ciudad = None
	
	moviendo_ciudad = False
	pos_ciudad = None

def acabar_ruta(event):
	global ruta_actual, rutas, estado_ruta, new_id_ruta, canvas, linea_temp
	
	# --- Guardar ruta ---
	
	ruta_actual.id = new_id_ruta # Darle el id
	rutas.append(deepcopy(ruta_actual)) # Guardar la ruta actual
	
	generar_nuevo_id_ruta() # Regenerar un id
	
	# --- Cambiar estado_ruta ---
	
	estado_ruta = 0 # Nuevo estado -> nada
	
	# --- Borrar ruta actual ---
	
	borrar_ruta_actual()
	ruta_actual = Ruta(0, []) # Resetear ruta actual
	
	# --- Redibujar ---
	
	canvas.delete(linea_temp)
	linea_temp = None
	
	borrar_rutas()
	dibujar_rutas()

def empezar_mover_ruta(event):
	global rutas, max_radio_ciudad, ruta_actual, punto_moviendo, estado_ruta, ruta_moviendo, canvas, max_radio_linea
	
	coords = [event.x, event.y]
	
	punto_moviendo = None
	j = -1
	for r in rutas:
		j += 1
		for i in range(len(r.puntos)):
			if calcular_distancia(coords, r.puntos[i].coords) < max_radio_ciudad:
				ruta_actual = deepcopy(r)
				ruta_moviendo = j
				punto_moviendo = i
	
	# --- Moving point ---
	
	if punto_moviendo != None: # Se esta modificando un punto ya existente
		
		if rutas[ruta_moviendo].puntos[punto_moviendo].id_ciudad != None:
			print("Para mover una ciudad hay que estar en el modo ciudad")
			return
		
		# . Actualizar estado .
		
		estado_ruta = 2
		
		# . Borrar ruta .
		
		for l in lineas_rutas[ruta_moviendo]:
			canvas.delete(l)
		
		del rutas[ruta_moviendo]
		del lineas_rutas[ruta_moviendo]
		
		# . Redibujar la ruta que se esta editando .
		
		borrar_ruta_actual()
		dibujar_ruta_actual()
		
		return
	
	# --- Moving line ---
	
	punto_moviendo = None
	j = -1
	for r in rutas:
		j += 1
		for i in range(len(r.puntos) - 1):
			if calcular_distancia_punto(r.puntos[i].coords, r.puntos[i + 1].coords, coords) < max_radio_linea:
				ruta_actual = deepcopy(r)
				ruta_moviendo = j
				
				ruta_actual.puntos.insert(i + 1, Punto(coords, False, None))
				punto_moviendo = i + 1
	
	if punto_moviendo != None:
		
		# . Actualizar estado .
		
		estado_ruta = 2
		
		# . Borrar ruta .
		
		for l in lineas_rutas[ruta_moviendo]:
			canvas.delete(l)
		
		del rutas[ruta_moviendo]
		del lineas_rutas[ruta_moviendo]
		
		# . Redibujar la ruta que se esta editando .
		
		borrar_ruta_actual()
		dibujar_ruta_actual()
		
		return

def dejar_mover_ruta(event):
	global estado_ruta, rutas, ruta_actual
	
	# --- Reincluir la ruta en rutas y vacias ruta_actual ---
	
	rutas.append(deepcopy(ruta_actual))
	
	ruta_actual = Ruta(0, [])
	
	# --- Cambiar estado_ruta ---
	
	estado_ruta = 0 # Nuevo estado -> nada
	
	# --- Redibujar rutas ---
	
	borrar_ruta_actual()
	
	borrar_rutas()
	dibujar_rutas()

# . Movimiento raton .

def mover_ciudad(event):
	global ciudades, rutas, pos_ciudad, rutas_con_ciudad, posicion_en_ruta
	
	# --- Actualizar ciudad ---
	
	coords = [event.x, event.y] # Coger coordenadas
	
	ciudades[pos_ciudad].coords = coords # Actualizar la posicion
	
	# --- Actualizar rutas ---
	
	# Despues, en la funcion mover se alterna la ruta_actual con las rutas que hay que modificar y se actualizan
	for ruta, pos in zip(rutas_con_ciudad, posicion_en_ruta):
		rutas[ruta].puntos[pos].coords = coords
	
	# --- Redibujar ---
	
	borrar_rutas()
	dibujar_rutas()
	
	borrar_ciudades()
	dibujar_ciudades()

def proximo_punto_ruta(event):
	global canvas, linea_temp, ruta_actual
	
	canvas.delete(linea_temp)
	
	linea_temp = canvas.create_line(ruta_actual.puntos[-1].coords[0], ruta_actual.puntos[-1].coords[1], event.x, event.y)

def mover_punto_ruta(event):
	global ruta_actual, punto_moviendo
	
	# --- Mover el punto que se esta editando ---
	
	ruta_actual.puntos[punto_moviendo].coords = [event.x, event.y]
	
	# --- Redibujar la ruta actual ---
	
	# TODO : BORRAR RUTA QUE SE ESTA EDITANDO
	
	borrar_ruta_actual()
	dibujar_ruta_actual()

def mmove(event):
	global status, moviendo_ciudad, estado_ruta
	
	if status == 0 and moviendo_ciudad:
		mover_ciudad(event)
	elif status == 1 and estado_ruta == 1:
		proximo_punto_ruta(event)
	elif status == 1 and estado_ruta == 2:
		mover_punto_ruta(event)

# . Borrar .

# TODO : DO

# --- Click managers ---

def click(event):
	global status
	
	if (status == 0):
		click_ciudad(event)
	elif (status == 1):
		click_ruta(event)

def editar(event):
	global status, estado_ruta
	
	if (status == 0):
		editar_ciudad(event)
	elif status == 1 and estado_ruta == 0:
		empezar_mover_ruta(event)

def soltar(event):
	global status, moviendo_ciudad, estado_ruta
	
	if status == 0 and moviendo_ciudad:
		soltar_ciudad(event)
	elif status == 1 and estado_ruta == 1:
		acabar_ruta(event)
	elif status == 1 and estado_ruta == 2:
		dejar_mover_ruta(event)

# --- Lineas ---

# . Creacion / editado de lineas / trayectos .

def borrarLinea():
	return # TODO : FINISH

def borrarTrayecto():
	return # TODO : FINISH

def cambiarTrayecto(mover):
	return # TODO : FINISH

def paradaSeleccionada(parada):
	return # TODO : FINISH

def quitarParada(a = None):
	return # TODO : FINISH

def addParada(parada = None, lleg = "0000", sali = "0005"):
	global top_lin, linea_actual, pos_trayecto, anadirParada, trayectoAnt, trayectoSig, trayectoDel, lineaDel, botones_paradas
	
	# --- Es un nuevo trayecto o uno viejo ---
	
	ciudades_acc = None
	if len(linea_actual.trayectos[pos_trayecto].puntos) > 0: # Si ya hay varias 
		ciudades_acc = ciudades_accesibles(linea_actual.trayectos[pos_trayecto].puntos[-1].id_ciudad)
		
		# Bloquear el selector del anterior
		botones_paradas[pos_trayecto].selector[-1].configure(state = "disabled")
	else:
		ciudades_acc = ciudades_accesibles(None)
	
	if len(ciudades_acc) < 1:
		print("No hay suficientes ciudades")
		cancelar_linea()
		return
	
	# --- Datos para visualizar ---
	
	ciud = StringVar()
	if parada == None: ciud.set(ciudades_acc[0])
	else: ciud.set(parada)
	
	length = len(linea_actual.trayectos[pos_trayecto].puntos)
	
	dX = [10, 30, 250, 325]
	dY = [93 + (length * 30), 90 + (length * 30), 95 + (length * 30), 95 + (length * 30)]
	
	posId = length + len(linea_actual.trayectos[pos_trayecto].puntos)
	
	print(dY[0])
	
	# --- Añadir texto nueva parada ---
	
	# . Añadir los botones para la parada actual .
	
	botones_paradas[pos_trayecto].selector.append(OptionMenu(top_lin, ciud, *ciudades_acc, command = lambda a = posId : paradaSeleccionada(a, False)))
	botones_paradas[pos_trayecto].llegadas.append(Text(top_lin, heigh = 1, width = 4))
	botones_paradas[pos_trayecto].salidas.append(Text(top_lin, heigh = 1, width = 4))
	
	# . Actualizar la posicion del boton para quitar la ultima parada .
	
	if botones_paradas[pos_trayecto].quitar == None: botones_paradas[pos_trayecto].quitar = Button(top_lin, text = "X", command = quitarParada) # Si no hay boton de quitar -> Lo añadimos
	
	# . Mover los botones viejos
	
	botones_paradas[pos_trayecto].quitar.place(x = dX[0], y = dY[0])
	
	botones_paradas[pos_trayecto].selector[-1].place(x = dX[1], y = dY[1])
	botones_paradas[pos_trayecto].llegadas[-1].place(x = dX[2], y = dY[2])
	botones_paradas[pos_trayecto].salidas[-1].place(x = dX[3], y = dY[3])
	
	# . Poner la hora de la parada .
	
	if len(linea_actual.trayectos[pos_trayecto].puntos) > 0 and lleg == "0000" and sali == "0005":
		botones_paradas[pos_trayecto].llegadas[-1].insert(END, beautifyTiempo(str(int(botones_paradas[pos_trayecto].llegadas[-2].get("1.0",'end-1c')) + 100)))
		botones_paradas[pos_trayecto].salidas[-1].insert(END, beautifyTiempo(str(int(botones_paradas[pos_trayecto].salidas[-2].get("1.0",'end-1c')) + 100)))
	else:
		botones_paradas[pos_trayecto].llegadas[-1].insert(END, beautifyTiempo(lleg))
		botones_paradas[pos_trayecto].salidas[-1].insert(END, beautifyTiempo(sali))
	
	# --- Mover botones ---
	
	# . Borrar viejos botones .
	
	if (anadirParada != None):
		
		# Nueva parada
		
		anadirParada.destroy()
		
		# Cambiar de trayecto
		
		trayectoAnt.destroy()
		trayectoSig.destroy()
		trayectoDel.destroy()
		
		# Borrar linea
		
		lineaDel.destroy()
	
	# . Añadir botones en la buena posicion .
	
	anadirParada = Button(top_lin, text = "Añadir parada", command = addParada)
	anadirParada.place(x = 10, y = 125 + (length * 30))
	
	trayectoAnt = Button(top_lin, text = "Anterior", command = lambda : cambiarTrayecto(-1))
	trayectoAnt.place(x = 110, y = 125 + (length * 30))
	
	trayectoSig = Button(top_lin, text = "Siguiente", command = lambda : cambiarTrayecto(1))
	trayectoSig.place(x = 175, y = 125 + (length * 30))
	
	trayectoDel = Button(top_lin, text = "Borrar horario", command = borrarTrayecto)
	trayectoDel.place(x = 240, y = 125 + (length * 30))
	
	lineaDel = Button(top_lin, text = "Borrar linea", command = borrarLinea)
	lineaDel.place(x = 330, y = 125 + (length * 30))
	
	# --- Añadir una nueva parada en el trayecto actual ---
	
	linea_actual.trayectos[pos_trayecto].puntos.append(Punto([0, 0], True, int(ciud.get())))
	linea_actual.trayectos[pos_trayecto].llegadas.append(botones_paradas[pos_trayecto].llegadas[-1].get("1.0",'end-1c'))
	linea_actual.trayectos[pos_trayecto].salidas.append(botones_paradas[pos_trayecto].salidas[-1].get("1.0",'end-1c'))
	
	#trayectosActuales[posActual].append([]) # Crear una nueva parada
	
	#trayectosActuales[posActual][-1].append(Button(top, text = "X"))
	
	return

# . Ventana management .

def cambiar_color_actual():
	global colorLinea
	
	colorLinea.configure(bg = colorchooser.askcolor(title ="Elige un color")[1])

def nueva_linea():
	global top_lin, linea_actual, nombreLin, selecLn, colorLinea, horarioAct, trayecto_actual, botones_paradas
	
	# --- Borrar pantalla anterior ---
	
	if (selecLn != None): selecLn.destroy()
	
	# --- Dibujar nueva pantalla ---
	
	# . Nombre de la linea .
	
	nombreLin = Text(top_lin, height = 1, width = 15) 
	nombreLin.place(x = 125, y = 50)
	nombreLin.insert(END, "Linea " + str(linea_actual.id))
	
	# . Boton guardar .
	
	Button(top_lin, text = "Guardar", command = guardar_lineas).place(x = 175, y = 575)
	
	# . Color linea picker .
	
	colorLinea = Button(top_lin, bg = "#ff0000", command = cambiar_color_actual)
	colorLinea.place(x = 10, y = 10)
	
	# . Texto trayecto actual .
	
	trayecto_actual.set("Horario " + str(pos_trayecto + 1) + '/' + str(len(linea_actual.trayectos)))
	
	# --- Crear nueva linea vacia ---
	
	botones_paradas = [Parada_visual()]
	linea_actual = Linea(0, [255, 0, 0], "Nombre", [Trayecto([], [], [])])
	
	# --- Añadir la primera parada ---
	
	addParada()

def cancelar_linea(event = None):
	global top_lin
	
	# --- Destruir ventana ---
	
	top_lin.destroy()
	
	# --- Cambiar el estatus a modificar ciudades ---
	
	change_status(0)
	
	return # TODO : FINISH

def linea_elegida():
	return # TODO : FINISH

def abrir_ventana_lineas():
	global lineas, estado_linea, top_lin, lin, selecLn, pos_trayecto, trayecto_actual, linea_actual, nombreLin, new_id_linea
	
	# --- Reset estado linea ---
	
	estado_linea = 0
	
	# --- Crear ventana ---
	
	top_lin = Toplevel()
	
	top_lin.geometry("400x600")
	top_lin.title("Crear ruta")
	top_lin.resizable(False, False)
	
	# . Nueva linea .
	
	Button(top_lin, text = "Nueva línea", command = nueva_linea).place(x = 150, y = 10)
	
	# . Elegir linea existente .
	
	if (len(lineas) > 0):		
		lin = StringVar()
		lin.set("Selecciona una línea")
		
		tras = [t.nombre for t in lineas]
		selecLn = OptionMenu(top_lin, lin, *tras, command = linea_elegida)
		selecLn.place(x = 100, y = 50)
	
	# . Texto trayecto actual .
	
	trayecto_actual = StringVar()
	trayecto_actual.set("")
	
	Label(top_lin, textvariable = trayecto_actual).place(x = 150, y = 75)
	
	# --- Resetear variables lineas ---
	
	# . Nombre de la linea .
	
	nombreLin = None
	
	# . Linea y trayecto actual .
	
	pos_trayecto = 0
	linea_actual = Linea(new_id_linea, [255, 0, 0], "Nueva Linea", [Trayecto([], [], [])])
	
	# --- Binds ---
	
	top_lin.bind("<Return>", guardar)
	top_lin.bind("<Escape>", cancelar_linea)
	
	top_lin.protocol("WM_DELETE_WINDOW",  cancelar_linea)
	
	top_lin.focus_force()

# --- Tecla managers ---

def guardar(event = None):
	guardar_ciudades()
	guardar_rutas()
	guardar_lineas()

# --- Binds ---

# . Clicks .

canvas.bind("<ButtonPress-1>", click)

canvas.bind("<ButtonPress-3>", editar)
canvas.bind("<ButtonRelease-3>", soltar)

# . Movimiento .

canvas.bind("<Motion>", mmove)

# . Cambiar modo .

root.bind("<C>", lambda event, a = 0 : change_status(a))
root.bind("<R>", lambda event, a = 1 : change_status(a))
root.bind("<L>", lambda event, a = 2 : change_status(a))

root.bind("<c>", lambda event, a = 0 : change_status(a))
root.bind("<r>", lambda event, a = 1 : change_status(a))
root.bind("<l>", lambda event, a = 2 : change_status(a))

# . Teclas .

root.bind("<s>", guardar)
root.bind("<S>", guardar)

# --- Iniciar programa ---

change_status(0) # Init status -> Ciudades

# . Generar ids .

generar_nuevo_id_ciudad()
generar_nuevo_id_ruta()
generar_nuevo_id_linea()

# . Init ruta actual .

ruta_actual = Ruta(0, [])

# . Cargar datos precedentes .

cargar_ciudades()
cargar_rutas()

# . Mainloop .

mainloop()