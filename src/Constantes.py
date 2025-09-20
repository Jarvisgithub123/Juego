# ===== CONFIGURACION DE PANTALLA Y VENTANA =====
ANCHO_PANTALLA = 1200  # Ancho de ventana principal
ALTO_PANTALLA = 800    # Alto de ventana principal

# Configuracion de renderizado (usar nombres consistentes)
PANTALLA_ANCHO = 1280  # Ancho del area de juego
PANTALLA_ALTO = 720    # Alto del area de juego
FPS = 100            

# ===== COLORES DEL JUEGO =====

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
COLOR_LINEA_PISO = (244, 202, 202)

# Colores de elementos de juego
COLOR_INSTRUCCION_FONDO = (50, 50, 50)
COLOR_BARRA_ENERGIA = (100, 255, 100)
COLOR_BARRA_FONDO = (50, 50, 50)

# ===== FISICA Y MOVIMIENTO =====

# Fisica del jugador
GRAVEDAD = 0.8                 # Fuerza de gravedad aplicada al jugador
PISO_POS_Y = 650               # Posicion Y del piso donde aterriza el jugador

# Configuracion de dash del jugador
DASH_ENERGIA_COSTO = 2         # Costo en energia por cada dash

# ===== CONSTANTES DE JUGADOR=====

# Constantes de movimiento del jugador
RETURN_TO_ORIGIN_SPEED = 5.0
MAX_DISTANCE_FROM_ORIGIN = 200
POSITION_TOLERANCE = 10

# Constantes de salto por personaje (organizadas)
UAIBOT_JUMP_STRENGTH = -19
UAIBOTA_JUMP_STRENGTH = -21
UAIBOTINA_JUMP_STRENGTH = -17
UAIBOTINO_JUMP_STRENGTH = -17

# Constantes de dash por personaje
UAIBOT_DASH_SPEED = 12
UAIBOT_DASH_DURATION = 0.2
UAIBOT_DASH_COOLDOWN = 2.0
UAIBOT_AUTONOMIA = 20

UAIBOTA_DASH_SPEED = 10
UAIBOTA_DASH_DURATION = 0.3
UAIBOTA_DASH_COOLDOWN = 1.5
UAIBOTA_AUTONOMIA = 10

UAIBOTINA_DASH_SPEED = 15
UAIBOTINA_DASH_DURATION = 0.1
UAIBOTINA_DASH_COOLDOWN = 1.4
UAIBOTINA_AUTONOMIA = 30

UAIBOTINO_DASH_SPEED = 14
UAIBOTINO_DASH_DURATION = 0.2
UAIBOTINO_DASH_COOLDOWN = 1.0
UAIBOTINO_AUTONOMIA = 30

# ===== CONSTANTES DE AUTOS=====

# Dimensiones de autos
DEFAULT_CAR_WIDTH = 126
DEFAULT_CAR_HEIGHT = 86

# Animacion de autos
CAR_ANIMATION_SPEED = 0.1
CAR_ANIMATION_SPEED_DIVISOR = 13.0

# Velocidades de autos
SLOW_CAR_SPEED_MIN = 7
SLOW_CAR_SPEED_MAX = 9
NORMAL_CAR_SPEED_MIN = 10
NORMAL_CAR_SPEED_MAX = 13
FAST_CAR_SPEED_MIN = 14
FAST_CAR_SPEED_MAX = 16
VERY_FAST_CAR_SPEED_MIN = 18
VERY_FAST_CAR_SPEED_MAX = 22

# Pesos de probabilidad para tipos de auto
SLOW_CAR_WEIGHT = 30
NORMAL_CAR_WEIGHT = 40
FAST_CAR_WEIGHT = 30

# Colores de autos por velocidad
FAST_CAR_RED_PROBABILITY = 80
FAST_CAR_BLUE_PROBABILITY = 20
SLOW_CAR_BLUE_PROBABILITY = 80
SLOW_CAR_RED_PROBABILITY = 20

# ===== CONSTANTES DE SPAWN=====

# Configuracion de spawn de autos
DEFAULT_SPAWN_TIME = 2.0
MAX_VISIBLE_CARS = 4
MIN_DISTANCE_TO_PLAYER = 500
MIN_SPACING_BETWEEN_CARS = 250
SPAWN_X_OFFSET_MIN = 300
SPAWN_X_OFFSET_MAX = 500

# Intervalos de spawn
SPAWN_INTERVAL_MIN = 3.0
SPAWN_INTERVAL_MAX = 6.0

# Distancia entre autos cuando spawnan en par
CAR_GAP_MIN = 300
CAR_GAP_MAX = 500

# Probabilidades de spawn
SINGLE_CAR_PROBABILITY = 40
DOUBLE_CAR_PROBABILITY = 60

# ===== CONSTANTES DE COLISIONES=====

# Distancia para considerar colisiones
COLLISION_DISTANCE_THRESHOLD = 150

# Threshold para limpieza de objetos fuera de pantalla
CLEANUP_THRESHOLD_OFFSET = 600


# ===== CONSTANTES DE PILAS =====

# Dimensiones de pilas
DEFAULT_PILAS_WIDTH = 80
DEFAULT_PILAS_HEIGHT = 80

# Spawn de pilas
PILA_SPAWN_INTERVAL = 5.0  # Segundos
PILA_SPEED = 8
ENERGIA_PILA = 10

# Rangos de spawn para pilas
PILA_SPAWN_Y_MIN = PISO_POS_Y - 400
PILA_SPAWN_Y_MAX = PISO_POS_Y - 100
PILA_SPAWN_X_OFFSET = 100

# ===== MECANICAS DE JUEGO =====

# Sistema de energia y objetivos
KILOMETROS_OBJETIVO = 1.0          # Kilometros que debe recorrer UAIBOT
DECREMENTO_KM_POR_SEGUNDO = 0.03      # Velocidad de avance en km/s

# Velocidades de elementos
VELOCIDAD_FONDO = 4              # Velocidad del scroll de fondo
VELOCIDAD_AUTO_BASE = 10         # Velocidad base de los autos enemigos
VELOCIDAD_AUTO_VARIACION = 1    # Variacion maxima de velocidad de autos

# ===== CONSTANTES DE CAMARA=====

# Configuracion de camara
DEFAULT_PLAYER_SCREEN_X = 100  # Donde aparece el jugador visualmente
DEFAULT_FOLLOW_SPEED = 8.0
MINIMUM_DEVIATION_THRESHOLD = 10  # Minimo movimiento antes de seguir
CAMERA_SMOOTH_FACTOR = 0.08  # Factor de suavizado de camara

# ===== CONSTANTES DE ANIMACION =====

# Player animation
PLAYER_ANIMATION_SPEED = 0.08
PLAYER_SPRITE_WIDTH = 64
PLAYER_SPRITE_HEIGHT = 86

# Spritesheet configuration
SPRITESHEET_START_COLUMN = 0
SPRITESHEET_END_COLUMN = 5  # Para UIAbot
SPRITESHEET_ROW = 0

# ===== CONSTANTES DE UI Y RENDERIZADO =====

# Posiciones de elementos UI
BILLBOARD_AREA_X = 225
BILLBOARD_AREA_Y = 160
BILLBOARD_AREA_WIDTH = 575
BILLBOARD_AREA_HEIGHT = 260

# Botones
BUTTON_WIDTH_STANDARD = 250
BUTTON_HEIGHT_STANDARD = 75
BUTTON_SPACING = 30
ARROW_BUTTON_SIZE = 60

# Efectos de texto
TEXT_BORDER_SIZE_DEFAULT = 2
TEXT_BORDER_SIZE_TITLE = 3
TEXT_BORDER_SIZE_LARGE = 4



# ===== CONSTANTES DE BACKGROUND Y PARALLAX =====

# Factores de parallax para capas de fondo
BG_SKY_PARALLAX_FACTOR = 0      # Fondo estatico
BG_MID_PARALLAX_FACTOR = 2      # Capa media
BG_FRONT_PARALLAX_FACTOR = 3.6  # Capa frontal

# Velocidad de scroll del mundo
WORLD_SCROLL_SPEED = 30
BACKGROUND_PARALLAX_CAMERA_FACTOR = 0.1

# Animacion de menu background
MENU_BACKGROUND_ANIMATION_SPEED = 0.5

# ===== CONFIGURACIONES DE DEBUG Y DESARROLLO =====

DEBUG_MODE = False              # Activar modo debug
SHOW_HITBOXES = False          # Mostrar hitboxes de colision
ENABLE_CONSOLE_LOGS = True     # Habilitar logs en consola

# Pool sizes
INITIAL_CAR_POOL_SIZE = 8
MAX_CAR_POOL_SIZE = 15
AVAILABLE_CAR_POOL_LIMIT = 6

ESCUDO_DURACION = 8.0  # Duracion del escudo en segundos
ESCUDO_SPAWN_CHANCE = 0.3  # 30% de probabilidad de generar escudo en lugar de pila

# === CONSTANTES PARA EFECTOS VISUALES ===
SHIELD_EFFECT_DURATION = 300  # Duracion del efecto visual de impacto en milisegundos
COLLISION_FLASH_DURATION = 200  # Duracion del flash al colisionar con escudo
# ===== RUTAS DE RECURSOS (DEPRECADO - USAR RESOURCE_MANAGER) =====

# ===== CONSTANTES DE AUDIO ACTUALIZADAS =====
DEFAULT_SOUND_VOLUME = 0.7      # Volumen por defecto de efectos
MIN_VOLUME = 0.0                # Volumen mínimo
MAX_VOLUME = 1.0                # Volumen máximo

# Volumenes por defecto
DEFAULT_MUSIC_VOLUME = 0.7
MENU_MUSIC_VOLUME = 0.5
GAME_MUSIC_VOLUME = 0.6