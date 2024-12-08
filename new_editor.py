import gc
import math
import json
from tkinter import *
from copy import deepcopy
from PIL import Image, ImageTk
from tkinter import colorchooser

# ========= TODO =========

# Bug : Doble click en el mismo lugar hace que se guarde el mismo lugar 2 veces


# Guardar el nombre de la linea de tren antes de guardarla (maybe a check to see if the line we are editing already exists ????)
# We are missing the whole route thingy for the lineas creadas -> tenemos las paradas que deberia hacer y las horas a las que deberia parar por cada parada, pero no sabemos que ruta sigue...
# Boton de Nueva linea sigue accesible -> se deberia eliminar en linea_elegida
# Add funciones boton escape

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

linea_actual = None # Clase Linea de la linea actual que se esta editando

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
lineasF = "Lineas.json"

# --- Datos mapa ---

ciudades = [] # Todas la ciudades en el mapa
rutas = [] # Todas las rutas en el mapa
lineas = [] # Todos las lineas de trenes

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
		
		self.llegadas = llegadas
		self.salidas = salidas

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
	
	def clear(self):
		self.selector.clear()
		self.llegadas.clear()
		self.salidas.clear()

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
	if isinstance(txt, int): txt = str(txt)
	
	return "0" * (4 - len(txt)) + txt # Devuelve la hora con ceros delante

def checkTiempo(txt):
	print(txt)
	if len(txt) != 4 or not txt.isdigit(): # Si no hay 4 chars o todos los chars no son numeros -> No esta bien
		return False
	
	return True

def checkHora(hora):
	h = hora // 100
	m = hora % 100
	
	return (0 <= h < 24) and (0 <= m < 60)

def insertar_linea_actual():
	global linea_actual, botones_paradas, lineas
	
	# --- Actualizar horas ---
	
	# . Llegadas .
	
	for i in range(len(botones_paradas)):
		for j in range(len(botones_paradas[i].llegadas)):
			
			linea_actual.trayectos[i].llegadas[j] = botones_paradas[i].llegadas[j].get("1.0", 'end-1c')
			
			if checkTiempo(linea_actual.trayectos[i].llegadas[j]) == False:
				print(f"La hora de llegada introducida : {linea_actual.trayectos[i].llegadas[j]} no es valida")
				return False
	
	# . Salidas .
	
	for i in range(len(botones_paradas)):
		for j in range(len(botones_paradas[i].salidas)):
			
			linea_actual.trayectos[i].salidas[j] = botones_paradas[i].salidas[j].get("1.0", 'end-1c')
			
			if checkTiempo(linea_actual.trayectos[i].salidas[j]) == False:
				print(f"La hora de salida introducida : {linea_actual.trayectos[i].salidas[j]} no es valida")
				return False
	
	# --- Checks de validez ---
	
	# . Horarios .
	
	# Mirar que todos los horarios tengan el buen formato 0000 -> 2400
	
	trayectos_ok = True
	
	i = 0
	for tray in linea_actual.trayectos:
		ult_salida = -1
		
		j = 0
		for llegada, salida in zip(tray.llegadas, tray.salidas):
			llegada = int(llegada)
			salida = int(salida)
			
			# Verificar que las dos horas son validas
			if checkHora(llegada) * checkHora(salida) == False:
				print(f"El formato de las horas de llegada {beautifyTiempo(llegada)} o salida {beautifyTiempo(salida)} no es correcto. Tray {i} , parada {j}")
				trayectos_ok = False
				break
			
			# Verificar que la hora de llegada es despues de la ultima hora de salida
			if ult_salida > llegada:
				print(f"La hora de llegada es inferior a la ultima salida : {beautifyTiempo(llegada)} < {beautifyTiempo(ult_salida)}. Tray {i} , parada {j}")
				trayectos_ok = False
				break
			
			# Verificar que la hora de salida es despues de la hora de llegada
			if llegada > salida:
				print(f"La hora de llegada es superior a la de salida : {beautifyTiempo(llegada)} > {beautifyTiempo(salida)}. Tray {i} , parada {j}")
				trayectos_ok = False
				break
			
			j += 1
			ult_salida = salida # Actualizar la ultima hora de salida
		
		i += 1
		if trayectos_ok == False: break
	
	if trayectos_ok == False:
		return False
	
	# . Numero de paradas .
	
	# --- Insertar linea_actual ---
	
	for i in range(len(lineas)):
		if lineas[i].id == linea_actual.id:
			lineas[i] = deepcopy(linea_actual)
			return
	
	lineas.append(linea_actual)
	
	return True # No ha habido problemas

def RGB2hex(color):
    rgb_array = [max(0, min(255, int(x))) for x in color]
	
    return '#{:02x}{:02x}{:02x}'.format(rgb_array[0], rgb_array[1], rgb_array[2])

# . Calcular distancias .

def calcular_distancia(coords1, coords2):
	return math.sqrt( (coords1[0] - coords2[0])**2 + (coords1[1] - coords2[1])**2 )

def calcular_distancia_punto(punto1, punto2, coord):
	return abs( (punto2[1] - punto1[1])*coord[0] - (punto2[0] - punto1[0])*coord[1] + punto2[0]*punto1[1] - punto2[1]*punto1[0] ) / ( math.sqrt( (punto2[1] - punto1[1])**2 + (punto2[0] - punto1[0])**2 ) + 1e-16 )

# . Posiciones en arrays .

def get_posicion_ciudad(id_c):
	global ciudades
	
	for i in range(len(ciudades)):
		if ciudades[i].id == id_c:
			return i
	
	return None

# . Route finder .

def ciudades_accesibles(nombre_ciudad): # TODO : AQUI SEGURO QUE SE PUEDE OPTIMIZAR PRE-COMPILANDO LOS SETS -> LOOKUP TABLE
	global rutas, ciudades
	
	if nombre_ciudad == None: return [c.nombre for c in ciudades] # Si id_ciudad es None -> devolver todas las ciudades
	
	id_ciudad = get_id_ciudad_con_nombre(nombre_ciudad)
	
	ciudades_acc = set() # Ciudades accesibles
	
	for r in rutas:
		temp_set = set() # Set con las ciudades que pasan por la ruta r
		add_set = False # Añadimos temp_set a ciudades_acc ?
		
		for parada in r.puntos:
			if parada.id_ciudad == None: continue # Si el punto de la ruta no es una parada -> ignorar
			
			if parada.id_ciudad == id_ciudad: add_set = True
			else: temp_set.add( parada.id_ciudad )
		
		if add_set: ciudades_acc = ciudades_acc.union(temp_set)
	
	ciudades_acc = list(ciudades_acc)
	
	return [get_nombre_ciudad_con_id(c) for c in ciudades_acc]

def get_nombre_ciudad_con_id(id_ciudad):
	global ciudades
	
	for c in ciudades:
		if c.id == id_ciudad: return c.nombre
	
	return None

def get_id_ciudad_con_nombre(nombre_ciudad):
	global ciudades
	
	for c in ciudades:
		if nombre_ciudad == c.nombre: return c.id
	
	return None

def get_posicion_linea(nombre_linea):
	global lineas
	
	for i in range(len(nombre_linea)):
		if lineas[i].nombre == nombre_linea: return i
	
	return None

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
	global lineasF, lineas, linea_actual, estado_linea # TODO : CON ESTADO LINEA HACER LA DIFERENCIA ENTRE MODIFICAR Y CREAR NUEVA LINEA
	
	if linea_actual != None:
		if insertar_linea_actual() == False:
			print("Error : no se ha podido guardar la linea de tren")
			return
	
	with open(lineasF, "w+") as f:
		json.dump([l.__dict__ for l in lineas], f, indent = 4, default=lambda o: o.__dict__)
		f.close()
	
	print(f"{len(lineas)} lineas guardadas")

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

def cargar_lineas(): # TODO : FINISH
	global lineas, lineasF, linea_actual
	
	with open(lineasF, "r") as f:
		data = json.load(f)
		
		lineas = []
		for linea_data in data:
			trayectos = []
			
			for trayecto_data in linea_data['trayectos']:
				puntos = [Punto(**punto_data) for punto_data in trayecto_data['puntos']]
				trayecto = Trayecto(puntos=puntos, salidas=trayecto_data['salidas'], llegadas=trayecto_data['llegadas'])
				trayectos.append(trayecto)
			
			linea = Linea(id=linea_data['id'], nombre=linea_data['nombre'], color=linea_data['color'], trayectos = trayectos)
			lineas.append(linea)

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
			print("Se esta creando o editando una linea")
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
	global canvas, ciudades, puntos_ciudades
	
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
	
	# . Sanity check #
	
	if ventana_nombre != None: return
	
	# . Coger coords .
	
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
	
	if calcular_distancia(coords, ruta_actual.puntos[-1].coords) < 5: return
	
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

def borrar_punto_ruta():
	global ruta_actual, ruta_moviendo, punto_moviendo, rutas, estado_ruta
	
	# . Sanity check .
	
	if estado_ruta != 2: return
	
	# --- Quitar punto de la lista ---
	
	del ruta_actual.puntos[punto_moviendo]
	
	rutas.insert(ruta_moviendo, [])
	rutas[ruta_moviendo] = deepcopy(ruta_actual)
	
	# --- Resetear estado ---
	
	estado_ruta = 0 # Estado ruta -> Nada
	
	ruta_actual = Ruta(0, []) # Resetear ruta actual
	
	# --- Redibujar ---
	
	borrar_ruta_actual()
	
	borrar_rutas()
	dibujar_rutas()

def borrar_ruta():
	global ruta_actual, estado_ruta
	
	# . Sanity check .
	
	if estado_ruta != 2: return
	
	# --- Resetear estado ---
	
	estado_ruta = 0 # Estado ruta -> Nada
	
	ruta_actual = Ruta(0, []) # Resetear ruta actual
	
	# --- Redibujar ---
	
	borrar_ruta_actual()
	
	borrar_rutas()
	dibujar_rutas()

def borrar_ciudad(): # TODO : HANDLE IF CIUDAD PART OF RUTA
	global canvas, ciudades, pos_ciudad, moviendo_ciudad, canvas, texto_ciudad, puntos_ciudades
	
	# --- Mirar que ciudad se está modificando ---
	
	if pos_ciudad == None: return # Si no se está modificando ninguna ciudad -> return
	
	# --- Borrar el punto visual ---
	
	canvas.delete(puntos_ciudades[pos_ciudad])
	del puntos_ciudades[pos_ciudad]
	
	# --- Borrar la ciudad de la lista de ciudades ---
	
	del ciudades[pos_ciudad]
	
	# --- Resetear todo	---
	
	# . Vriables .
	
	pos_ciudad = None
	
	moviendo_ciudad = False
	
	# . Redibujar .
	
	canvas.delete(texto_ciudad)
	texto_ciudad = None
	
	moviendo_ciudad = False
	
	print(len(puntos_ciudades))

def borrar(event = None): # Backspace # TODO : FINISH LINEA
	global status
	
	if status == 0: # Estamos modificando una ciudad
		borrar_ciudad()
	elif status == 1: # Estamos modificando una ruta
		borrar_punto_ruta()
	else: # Estamos en la ventana modificando una linea
		return
	
	return

def suprimir(event = None): # Delete # TODO : FINISH LINEA
	global status
	
	if status == 0: # Estamos modificando una ciudad
		borrar_ciudad()
	elif status == 1: # Estamos modificando una ruta
		borrar_ruta()
	else : # Estamos en la ventana modificando una linea
		return
	
	return

def escape(event = None): # Escape # TODO : FINISH CIUDADES, RUTAS Y LINEA
	global status
	
	if status == 0: # Estamos modificando una ciudad
		return
	elif status == 1: # Estamos modificando una ruta
		return
	else : # Estamos en la ventana modificando una linea
		return
	
	return

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

def borrarTrayecto():
	global linea_actual, pos_trayecto, botones_paradas
	
	if len(linea_actual.trayectos) == 1: # Solo hay un trayecto -> cancelar la linea
		cancelar_linea()
		return
	
	# --- Borrar botones ---
	
	# . Parte visual .
	
	for i in range(len(botones_paradas[pos_trayecto].selector)):
		botones_paradas[pos_trayecto].selector[i].destroy()
		botones_paradas[pos_trayecto].llegadas[i].destroy()
		botones_paradas[pos_trayecto].salidas[i].destroy()
	
	botones_paradas[pos_trayecto].quitar.destroy()
	
	# . Parte datos .
	
	del botones_paradas[pos_trayecto]
	
	# --- Borrar datos ---
	
	del linea_actual.trayectos[pos_trayecto]
	
	# --- Refresh ---
	
	if pos_trayecto > 0: pos_trayecto -= 1
	cambiarTrayecto(0)
	
	return

def cambiarTrayecto(dir, copiar = True, auto = False):
	global top_lin, linea_actual, pos_trayecto, botones_paradas, trayecto_actual, anadirParada, trayectoAnt, trayectoSig, trayectoDel, lineaDel
	
	if dir == 0: return
	
	# --- Esconder los elementos del trayecto actual ---
	
	for i in range(len(botones_paradas[pos_trayecto].selector)):
		botones_paradas[pos_trayecto].selector[i].place(x = 1000)
		botones_paradas[pos_trayecto].llegadas[i].place(x = 1000)
		botones_paradas[pos_trayecto].salidas[i].place(x = 1000)
	
	botones_paradas[pos_trayecto].quitar.place(x = 1000)
	
	# --- Actualizar pos_trayecto ---
	
	pos_trayecto += dir
	
	# --- Auto management ---
	
	if auto:
		botones_paradas.append(Parada_visual([], [], [], None)) # Añadir la lista de botones
		return
	
	# --- Crear o mover ---
	
	if pos_trayecto >= 0 and pos_trayecto < len(linea_actual.trayectos): # No hay que crear nada, solo cargar el horario
		
		# . Reaparecer los elementos del nuevo trayecto .
		
		dX = [10, 30, 250, 325]
		
		for i in range(len(botones_paradas[pos_trayecto].selector)):
			botones_paradas[pos_trayecto].selector[i].place(x = dX[1])
			botones_paradas[pos_trayecto].llegadas[i].place(x = dX[2])
			botones_paradas[pos_trayecto].salidas[i].place(x = dX[3])
		
		botones_paradas[pos_trayecto].quitar.place(x = dX[0])
		
		# . Poner los botones para cambiar de trayecto .
		
		length = len(linea_actual.trayectos[pos_trayecto].puntos)
		
		if (anadirParada != None):
			
			# Nueva parada
			
			anadirParada.destroy()
			
			# Cambiar de trayecto
			
			trayectoAnt.destroy()
			trayectoSig.destroy()
			trayectoDel.destroy()
			
			# Borrar linea
			
			lineaDel.destroy()
		
		anadirParada = Button(top_lin, text = "Añadir parada", command = addParada)
		anadirParada.place(x = 10, y = 95 + (length * 30))
		
		trayectoAnt = Button(top_lin, text = "Anterior", command = lambda : cambiarTrayecto(-1))
		trayectoAnt.place(x = 110, y = 95 + (length * 30))
		
		trayectoSig = Button(top_lin, text = "Siguiente", command = lambda : cambiarTrayecto(1))
		trayectoSig.place(x = 175, y = 95 + (length * 30))
		
		trayectoDel = Button(top_lin, text = "Borrar horario", command = borrarTrayecto)
		trayectoDel.place(x = 240, y = 95 + (length * 30))
		
		lineaDel = Button(top_lin, text = "Borrar linea", command = cancelar_linea)
		lineaDel.place(x = 330, y = 95 + (length * 30))
		
	else: # Hay que crear un nuevo trayecto
		if pos_trayecto < 0:
			pos_trayecto = 0
			
			linea_actual.trayectos.insert(0, Trayecto([], [], []))
			botones_paradas.insert(0, Parada_visual([], [], [], None))
		else:
			linea_actual.trayectos.append(Trayecto([], [], []))
			botones_paradas.append(Parada_visual([], [], [], None))
		
		if copiar:
			for i in range(len(linea_actual.trayectos[pos_trayecto - dir].puntos)):
				addParada( get_nombre_ciudad_con_id(linea_actual.trayectos[pos_trayecto - dir].puntos[i].id_ciudad) , linea_actual.trayectos[pos_trayecto - dir].llegadas[i], linea_actual.trayectos[pos_trayecto - dir].salidas[i])
			
			linea_actual.trayectos[pos_trayecto] = deepcopy(linea_actual.trayectos[pos_trayecto - dir])
	
	# --- Actualizar el label ---
	
	trayecto_actual.set("Horario " + str(pos_trayecto + 1) + '/' + str(len(linea_actual.trayectos)))

def paradaSeleccionada(parada):
	global linea_actual, pos_trayecto, botones_paradas
	
	# --- Actualizar eleccion ---
	
	linea_actual.trayectos[pos_trayecto].puntos[-1].id_ciudad = get_id_ciudad_con_nombre(parada)

def quitarParada():
	global linea_actual, pos_trayecto, anadirParada, trayectoAnt, trayectoSig, trayectoDel, lineaDel, botones_paradas
	
	# --- Sanity check ---
	
	if len(linea_actual.trayectos[pos_trayecto].puntos) == 1: # Si solo hay 1 parada en el trayecto
		if len(linea_actual.trayectos) > 1: # Hay varios trayectos
			borrarTrayecto()
		else:							   # Solo hay un trayecto
			cancelar_linea()
		return
	
	# --- Quitar la ultima ---
	
	# . Quitar de la parte datos .
	
	del linea_actual.trayectos[pos_trayecto].puntos[-1]
	del linea_actual.trayectos[pos_trayecto].salidas[-1]
	del linea_actual.trayectos[pos_trayecto].llegadas[-1]
	
	# --- Visual ---
	
	# . Quitar los inputs de la ultima parada .
	
	botones_paradas[pos_trayecto].selector[-1].destroy()
	botones_paradas[pos_trayecto].llegadas[-1].destroy()
	botones_paradas[pos_trayecto].salidas[-1].destroy()
	
	# . Borrar del array .
	
	del botones_paradas[pos_trayecto].selector[-1]
	del botones_paradas[pos_trayecto].llegadas[-1]
	del botones_paradas[pos_trayecto].salidas[-1]
	
	# . Activar el ultimo selector y mover la X .
	
	botones_paradas[pos_trayecto].selector[-1].configure(state = "normal")
	
	length = len(linea_actual.trayectos[pos_trayecto].puntos) - 1
	
	dX = [10, 30, 250, 325]
	dY = [93 + (length * 30), 90 + (length * 30), 95 + (length * 30), 95 + (length * 30)]
	
	botones_paradas[pos_trayecto].quitar.place(x = 10, y = 93 + (length * 30))
	
	anadirParada.place(x = 10, y = 125 + (length * 30))
	trayectoAnt.place(x = 110, y = 125 + (length * 30))
	trayectoSig.place(x = 175, y = 125 + (length * 30))
	trayectoDel.place(x = 240, y = 125 + (length * 30))
	
	lineaDel.place(x = 330, y = 125 + (length * 30))

def addParada(parada = None, lleg = "0000", sali = "0005"):
	global top_lin, linea_actual, pos_trayecto, anadirParada, trayectoAnt, trayectoSig, trayectoDel, lineaDel, botones_paradas
	
	# --- Es un nuevo trayecto o uno viejo ---
	
	ciudades_acc = None
	
	if len(botones_paradas[pos_trayecto].selector) > 0: # Si ya hay varias
		ciudades_acc = ciudades_accesibles( get_nombre_ciudad_con_id(linea_actual.trayectos[pos_trayecto].puntos[-1].id_ciudad) )
		
		# . Bloquear el selector del anterior .
		
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
	
	length = len(botones_paradas[pos_trayecto].selector)
	
	dX = [10, 30, 250, 325]
	dY = [93 + (length * 30), 90 + (length * 30), 95 + (length * 30), 95 + (length * 30)]
	
	posId = 2 * length
	
	# --- Añadir texto nueva parada ---
	
	# . Añadir los botones para la parada actual .
	
	botones_paradas[pos_trayecto].selector.append(OptionMenu(top_lin, ciud, *ciudades_acc, command = lambda a = posId : paradaSeleccionada(a)))
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
	
	# TODO : HAVING AN INVALID HOUR MAKES IT SO THAT THE int() FUNCTION DOESNT WORK HERE
	
	if len(botones_paradas[pos_trayecto].llegadas) > 1 and len(botones_paradas[pos_trayecto].salidas) > 1 and lleg == "0000" and sali == "0005":
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
	
	lineaDel = Button(top_lin, text = "Borrar linea", command = cancelar_linea)
	lineaDel.place(x = 330, y = 125 + (length * 30))
	
	# --- Añadir una nueva parada en el trayecto actual ---
	
	if lleg == "0000" and sali == "0005":
		linea_actual.trayectos[pos_trayecto].puntos.append(Punto([0, 0], True, get_id_ciudad_con_nombre(ciud.get())))
		linea_actual.trayectos[pos_trayecto].llegadas.append(botones_paradas[pos_trayecto].llegadas[-1].get("1.0",'end-1c'))
		linea_actual.trayectos[pos_trayecto].salidas.append(botones_paradas[pos_trayecto].salidas[-1].get("1.0",'end-1c'))

# . Ventana management .

def cambiar_color_actual():
	global colorLinea
	
	colorLinea.configure(bg = colorchooser.askcolor(title ="Elige un color")[1])

def nueva_linea(nombre_linea = None, color = [255, 0, 0]):
	global top_lin, estado_linea, linea_actual, nombreLin, selecLn, colorLinea, horarioAct, trayecto_actual, botones_paradas
	
	# --- Actualizar el estado ---
	
	estado_linea = 1
	
	# --- Borrar pantalla anterior ---
	
	if (selecLn != None): selecLn.destroy()
	
	# --- Dibujar nueva pantalla ---
	
	# . Nombre de la linea .
	
	nombreLin = Text(top_lin, height = 1, width = 15) 
	nombreLin.place(x = 125, y = 50)
	
	if nombre_linea == None: nombreLin.insert(END, "Linea " + str(linea_actual.id))
	else:                    nombreLin.insert(END, nombre_linea)
	
	# . Boton guardar .
	
	Button(top_lin, text = "Guardar", command = guardar).place(x = 175, y = 575)
	
	# . Color linea picker .
	
	colorLinea = Button(top_lin, bg = RGB2hex(color), command = cambiar_color_actual)
	colorLinea.place(x = 10, y = 10)
	
	# . Texto trayecto actual .
	
	trayecto_actual.set("Horario " + str(pos_trayecto + 1) + '/' + str(len(linea_actual.trayectos)))
	
	# ^^^ Si estamos modificando una parada y no  ^^^
	
	if nombre_linea is not None: return # Si la linea tiene nombre => no hay que crear desde 0
	
	# --- Crear nueva linea vacia ---
	
	botones_paradas = [Parada_visual()]
	linea_actual = Linea(0, "Nombre", [255, 0, 0], [Trayecto([], [], [])])
	
	# --- Añadir la primera parada ---
	
	addParada()

def resetear_variables():
	global linea_actual, pos_trayecto, botones_paradas
	
	# .  Nuevo estado linea .
	
	estado_linea = 0
	
	# . Borrar viejas variables .
	
	linea_actual = None
	pos_trayecto = 0
	
	# . Borrar botones .
	
	if botones_paradas is not None:	
		for botones in botones_paradas:
			for i in range(len(botones.selector)):
				botones.selector[i].destroy()
				botones.llegadas[i].destroy()
				botones.salidas[i].destroy()
			
			botones.quitar.destroy()
		
		for i in range(len(botones_paradas)):
			botones_paradas[ len(botones_paradas) - 1 - i ].clear()
		
		botones_paradas = None
	
	gc.collect()

def cerrar_ventana(event = None, new_s = 0):
	global top_lin, estado_linea, botones_paradas
	
	# --- Resete variables ---
	
	if botones_paradas != None: resetear_variables()
	
	# --- Destruir ventana ---
	
	top_lin.destroy()
	del top_lin
	
	# --- Cambiar el estatus a modificar ciudades ---
	
	estado_linea = 0
	
	change_status(new_s)

def cancelar_linea(event = None):
	global estado_linea
	
	# --- Resete variables ---
	
	resetear_variables()
	
	# --- Borrar datos anteriores ---
	
	if estado_linea == 0: return # Sanity check
	
	# --- Cerrar la ventana ---
	
	cerrar_ventana(0)
	
	# --- Reabrir ---
	
	change_status(2)

def linea_elegida(nombre_linea): # TODO : FINISH
	global lineas, linea_actual, estado_linea, botones_paradas, pos_trayecto
	
	# --- Actualizar el estado ---
	
	pos_linea = get_posicion_linea(nombre_linea)
	
	# --- Crear la pantalla con nueva parada ---
	
	# . Crear pantalla .
	
	nueva_linea(lineas[pos_linea].nombre, lineas[pos_linea].color)
	
	# . Traer la linea a linea_actual .
	
	botones_paradas = [Parada_visual()]
	linea_actual = deepcopy(lineas[pos_linea])
	
	# . Resetear el estado_linea .
	
	estado_linea = 2
	
	# --- Añadir los trayectos ---
	
	pos_trayecto = 0
	for trayecto in linea_actual.trayectos: # For each trayecto
		for i in range(len(trayecto.puntos)):
			addParada(parada = get_nombre_ciudad_con_id(trayecto.puntos[i].id_ciudad), lleg = trayecto.llegadas[i], sali = trayecto.salidas[i])
		
		if pos_trayecto < len(linea_actual.trayectos) - 1:
			cambiarTrayecto(1, copiar = False, auto = True)
	
	cambiarTrayecto(-len(linea_actual.trayectos) + 1)
	
	return

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
	linea_actual = Linea(new_id_linea, "Nueva Linea", [255, 0, 0], [Trayecto([], [], [])])
	
	# --- Binds ---
	
	top_lin.bind("<Return>", guardar)
	top_lin.bind("<Escape>", cancelar_linea) # TODO : SI LE DA A ESCAPE PERO NO HA EMPEZADO A CREAR UNA RUTA -> CERRAR
	
	top_lin.protocol("WM_DELETE_WINDOW",  cerrar_ventana)
	
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

root.bind("<BackSpace>", borrar)

root.bind("<Delete>", suprimir)

root.bind("<Escape>", escape)

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
cargar_lineas() # TODO : ACTIVATE WHEN FINISHED

# . Mainloop .

mainloop()