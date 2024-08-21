import math
import json
from tkinter import *
from PIL import Image, ImageTk

# ========= VARIABLES =========

# --- Ventana ---

# . Top level stuff .

top = None # Ventana extra para informaciones

fondo = "Mapa.png"

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

ruta_actual = None # Ruta actual que se esta creando o modificando

estado_ruta = 0 # 0 = nada ; 1 = creando ruta ; 2 = modificar ruta

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
trayectos = []

# --- Editor ---

new_id_ciudad = -1 # Id para la proxima ciudad
new_id_rutas = -1 # Id para la proxima ruta

# ========= CLASES =========

class Ciudad:
	def __init__(self, id, nombre, coords):
		self.id = id
		self.nombre = nombre
		self.coords = coords

class Punto:
	def __init__(self, coords, parada, id_ciudad): # Cuando es usado para ruta, parada siempre es False y ciudad = None siu no hay ciudad
		self.coords = coords
		self.parada = parada
		self.id_ciudad = id_ciudad

class Ruta:
	def __init__(self, id, puntos):
		self.id = id
		self.puntos = puntos

class Trayecto:
	def __init__(self, id, punto, salidas, llegadas, color, nombre):
		self.id = id
		self.punto = punto
		
		self.salidas = salidas
		self.llegadas = llegadas
		
		self.color = color
		self.nombre = nombre

# ========= FUNCIONES =========

# --- Set-up ---

root = Tk()
root.title("Editor de rutas")

canvas = Canvas(width = 1920, height = 1080, bg = 'black') # Create the canvas with the image size

myimg = ImageTk.PhotoImage(Image.open(fondo))
canvas.create_image(0, 0, image = myimg, anchor = NW) # Put the image in the frame

canvas.create_text(50, 50, text = "Creador de rutas", fill = "black", font = ('Helvetica 15'), justify = "left", anchor="w")
canvas.create_text(50, 75, text = "C : Añadir / modificar ciudades  R : Crear / modificar rutas  T : Crear / modificar trayectos", fill = "black", font = ('Helvetica 15'), justify = "left", anchor="w")
texto_status = canvas.create_text(50, 100, text = "Actualmente : editando ciudades", fill = "black", font = ('Helvetica 15'), justify = "left", anchor="w")

root.resizable(False, False)

canvas.pack()

# --- Low-level functions ---

def calcular_distancia(coords1, coords2):
	return math.sqrt( (coords1[0] - coords2[0])**2 + (coords1[1] - coords2[1])**2 )

def get_posicion_ciudad(id_c):
	global ciudades
	
	for i in range(len(ciudades)):
		if ciudades[i].id == id_c:
			return i
	
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

# --- Status manager ---

def change_status(new_s):
	global status, input_nombre, moviendo_ciudad, pos_ciudad, new_ciudad_coords, ventana_nombre, input_nombre
	
	if new_s == status: return # Si queremos cambiar al mismo modo del que estamos -> don't
	
	# --- Mirar si es posible cambiar el modo ---
	
	# . Ciudad -> new_s .
	
	if status == 0 and input_nombre == None and moviendo_ciudad == False: # Si no se esta creando una nueva ciudad AND no se esta moviendo una ciudad -> cambiar de estatus
		status = new_s
		
		pos_ciudad = None
		
		new_ciudad_coords = []
		
		ventana_nombre = None
		input_nombre = None
	else:
		print("No se puede cambiar de modo porque se esta creando una nueva ciudad o se esta moviendo una ciudad ya existente")
		return
	
	# . Ruta -> new_s .
	
	# . Trayecto -> new_s .
	
	# --- Indicar el cambio de modo ---
	
	txts = ["Actualmente : editando ciudades", "Actualmente : editando rutas", "Actualmente : editando trayectos"]
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
		canvas.create_line(ruta_actual.puntos[i].coords[0], ruta_actual.puntos[i].coords[1], ruta_actual.puntos[i + 1].coords[0], ruta_actual.puntos[i + 1].coords[1])

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
	
	# --- Añadir punto a la ruta actual ---
	
	ruta_actual.puntos.append(Punto(coords, None, click_ciudad)) # Add el punto, si hay una ciudad -> click_ciudad ; si no ciudad -> None
	
	# --- Redibujar ---
	
	borrar_ruta_actual()
	dibujar_ruta_actual()

# . Click derecho .

def editar_ciudad(event):
	global ciudades, max_radio_ciudad, pos_ciudad, moviendo_ciudad, canvas, ciudades, texto_ciudad
	
	coords = [event.x, event.y]
	
	# --- Buscar la ciudad la mas cercana con un radio max ---
	
	pos_ciudad = None
	for c in ciudades:
		if calcular_distancia(coords, c.coords) < max_radio_ciudad:
			pos_ciudad = get_posicion_ciudad(c.id)
			break
	
	if (pos_ciudad == None): return
	
	# Check si la ciudad forma parte de una ruta
	# Problema : si la ciudad esta conectada a una ruta -> actualizar
	
	# --- Mover la ciudad ---
	
	moviendo_ciudad = True
	
	# --- Redibujar ---
	
	texto_ciudad = canvas.create_text(50, 125, text = f"Moviendo : {ciudades[pos_ciudad].nombre}", fill = "black", font = ('Helvetica 15'), justify = "left", anchor="w")
	
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
	global ruta_actual, rutas, estado_ruta
	
	# Guardar ruta
	
	# --- Cambiar estado_ruta ---
	
	estado_ruta = 0 # Nuevo estado -> nada
	
	# --- Borrar ruta actual ---
	
	borrar_ruta_actual()
	ruta_actual = []
	
	# --- Redibujar ---
	
	borrar_rutas()
	dibujar_rutas()
	
	return

def dejar_mover_ruta(event):
	return

# . Movimiento raton .

def mover_ciudad(event):
	global ciudades, pos_ciudad
	
	# --- Actualizar coordenadas ---
	
	coords = [event.x, event.y] # Coger coordenadas
	
	ciudades[pos_ciudad].coords = coords # Actualizar la posicion
	
	# --- Redibujar ---
	
	borrar_ciudades()
	dibujar_ciudades()

def mmove(event):
	global moviendo_ciudad
	
	if moviendo_ciudad:
		mover_ciudad(event)

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
	elif status == 1 and estado_ruta = 2:
		

def soltar(event):
	global status, moviendo_ciudad, estado_ruta
	
	if status == 0 and moviendo_ciudad:
		soltar_ciudad(event)
	elif status == 1 and estado_ruta == 1:
		acabar_ruta(event)
	elif status == 1 and estado_ruta == 2:
		dejar_mover_ruta(event)

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
root.bind("<T>", lambda event, a = 2 : change_status(a))

root.bind("<c>", lambda event, a = 0 : change_status(a))
root.bind("<r>", lambda event, a = 1 : change_status(a))
root.bind("<t>", lambda event, a = 2 : change_status(a))

# --- Iniciar programa ---

# . Generar ids .

generar_nuevo_id_ciudad()
generar_nuevo_id_ruta()

# . Init ruta actual .

ruta_actual = Ruta(0, [])

# . Mainloop .

mainloop()