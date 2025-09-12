
# CONFIGURACION DE PANTALLA Y VENTANA
ANCHO_PANTALLA = 1200  # Ancho de ventana principal
ALTO_PANTALLA = 800    # Alto de ventana principal
# Configuracion de renderizado
PANTALLA_ANCHO = 1280  # Ancho del area de juego
PANTALLA_ALTO = 720    # Alto del area de juego
FPS = 60               # Frames por segundo objetivo

# COLORES DEL JUEGO

# Colores de interfaz y fondo
COLOR_FONDO_BASE = (10, 0, 30)           # Azul-purpura muy oscuro para fondo
COLOR_PRIMARIO = (99, 155, 255) 
COLOR_SECUNDARIO = (205, 13, 137)        # Verde mas claro
COLOR_FONDO = (198, 118, 118)            # Color del piso del juego

# Colores de texto
COLOR_TEXTO_EN_FONDO = (220, 230, 240)     # Gris/azul para texto principal
COLOR_TEXTO_SUTIL_EN_FONDO = (150, 160, 170)  # Gris/azul sutil
COLOR_TEXTO_EN_BOTON = (245, 250, 245)     # Blanco para botones
COLOR_TEXTO_VICTORIA = (0, 255, 0)         # Verde brillante para victoria
COLOR_TITULO = (99, 155, 255)                

# Colores basicos
COLOR_BLANCO = (255, 255, 255)
COLOR_NEGRO = (0, 0, 0)
COLOR_ROJO = (200, 0, 0)
COLOR_AZUL = (0, 0, 200)
COLOR_VERDE = (0, 200, 0)
COLOR_AMARILLO = (255, 255, 0)
COLOR_LINEA_PISO = (244,202,202)
# Colores de elementos de juego
COLOR_INSTRUCCION_FONDO = (50, 50, 50)
COLOR_BARRA_ENERGIA = (100, 255, 100)
COLOR_BARRA_FONDO = (50, 50, 50)


# FISICA Y MOVIMIENTO

# Fisica del jugador
GRAVEDAD = 1                    # Fuerza de gravedad aplicada al jugador
PISO_POS_Y = 650               # Posicion Y del piso donde aterriza el jugador

# Configuracion de dash del jugador
DASH_ENERGIA_COSTO = 2         # Costo en energia por cada dash

# MECANICAS DE JUEGO

# Sistema de energia y objetivos
DURACION_ENERGIA = 20               # Segundos totales de energia
KILOMETROS_OBJETIVO = 1.0          # Kilometros que debe recorrer UAIBOT
DECREMENTO_KM_POR_SEGUNDO = 0.03      # Velocidad de avance en km/s

# Velocidades de elementos
VELOCIDAD_FONDO = 4              # Velocidad del scroll de fondo
VELOCIDAD_AUTO_BASE = 13         # Velocidad base de los autos enemigos
VELOCIDAD_AUTO_VARIACION = 1    # Variacion maxima de velocidad de autos



# RUTAS DE RECURSOS (DEPRECADO - USAR RESOURCE_MANAGER)

RUTA_ARCHIVO_FONDO = "Assets\\Imagenes\\ciudad.jpg"  # Ruta legacy del fondo

# CONFIGURACIONES DE DEBUG Y DESARROLLO

DEBUG_MODE = False              # Activar modo debug
SHOW_HITBOXES = False          # Mostrar hitboxes de colision
ENABLE_CONSOLE_LOGS = True     # Habilitar logs en consola

ENERGIA_PILA = 10 
