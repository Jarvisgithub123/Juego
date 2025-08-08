import pygame
import sys
import os
import math
import Constantes

pygame.init()

# Configuracion de archivos y colores
RUTA_ARCHIVO_FONDO = "Recursos\Imagenes\ciudad.jpg" 
COLOR_BLANCO = (255, 255, 255)
COLOR_NEGRO = (0, 0, 0)
COLOR_ROJO = (200, 0, 0)
COLOR_AZUL = (0, 0, 200)
COLOR_VERDE = (0, 200, 0)
COLOR_INSTRUCCION_FONDO = (50, 50, 50)
COLOR_BARRA_ENERGIA = (100, 255, 100)  # Verde claro para la energia
COLOR_BARRA_FONDO = (50, 50, 50)       # Gris oscuro para el fondo de barras
COLOR_TEXTO_VICTORIA = (0, 255, 0)     # Verde para mensaje de victoria
COLOR_AMARILLO = (255, 255, 0)         # Amarillo para contador kilometros

# Configuracion de pantalla
PANTALLA_ANCHO = 1280
PANTALLA_ALTO = 720
PISO_POS_Y = 650
clock = pygame.time.Clock()
FPS = 60

# Variables del juego
DURACION_ENERGIA = 60  # 60 segundos de energia
KILOMETROS_OBJETIVO = 1.0  # 1 kilometro objetivo
DECREMENTO_KM_POR_SEGUNDO = 0.03  # 0.03km por segundo

pantalla = pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
pygame.display.set_caption("OFIRCA 2025 - Ronda 1 Inicio")

# Cargar imagen de fondo
if os.path.exists(RUTA_ARCHIVO_FONDO):
    img_fondo = pygame.image.load(RUTA_ARCHIVO_FONDO)
    img_fondo = pygame.transform.scale(img_fondo, (PANTALLA_ANCHO, PANTALLA_ALTO))
else:
    img_fondo = None

# Configuracion de fuentes
font_TxtInstrucciones = pygame.font.SysFont(None, 36)
font_TxtGameOver = pygame.font.SysFont(None, 100)
font_TxtVictoria = pygame.font.SysFont(None, 80)
font_HUD = pygame.font.SysFont(None, 32)  # Fuente para interfaz de usuario

# Textos de instrucciones
txtInstrucciones = font_TxtInstrucciones.render("Usa la barra espaciadora para saltar", True, COLOR_BLANCO)
txtInstrucciones_desplazamiento = 10
txtInstrucciones_rect = txtInstrucciones.get_rect()
txtInstrucciones_rect.topleft = (10, 10)
fondo_rect = pygame.Rect(txtInstrucciones_rect.left - txtInstrucciones_desplazamiento,
                        txtInstrucciones_rect.top - txtInstrucciones_desplazamiento,
                        txtInstrucciones_rect.width + 2 * txtInstrucciones_desplazamiento,
                         txtInstrucciones_rect.height + 2 * txtInstrucciones_desplazamiento)

# Textos de game over y victoria
txtGameOver = font_TxtGameOver.render("JUEGO TERMINADO", True, COLOR_ROJO)
txtGameOver_rect = txtGameOver.get_rect(center=(PANTALLA_ANCHO // 2, (PANTALLA_ALTO // 2)-200))

txtVictoria = font_TxtVictoria.render("¡El paquete fue entregado con exito!", True, COLOR_TEXTO_VICTORIA)
txtVictoria_rect = txtVictoria.get_rect(center=(PANTALLA_ANCHO // 2, (PANTALLA_ALTO // 2)-200))

# Variables del robot
robot_tamaño = 50
robot_x = 100
robot_y = PISO_POS_Y - robot_tamaño

# Variables del auto
auto_ancho = 100
auto_alto = 40
auto_x = PANTALLA_ANCHO
auto_y = PISO_POS_Y - auto_alto
auto_vel_x = 7

# Variables de estado del juego
juegoEnEjecucion = True
game_over = False
victoria = False

# Variables para animacion del fondo
fondo_x1 = 0
fondo_x2 = PANTALLA_ANCHO
velocidad_fondo = 2  # Velocidad de desplazamiento del fondo

# Variables de tiempo y energia
tiempo_inicio = pygame.time.get_ticks()
energia_restante = DURACION_ENERGIA
kilometros_restantes = KILOMETROS_OBJETIVO

class Personaje(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        super().__init__()
        
        # Cargar imagen del personaje UAIBOT
        try:
            imagen = pygame.image.load("Recursos/Imagenes/UAIBOT.png").convert_alpha()
        except:
            # Si no encuentra la imagen, crear un rectangulo azul como respaldo
            imagen = pygame.Surface((64, 64))
            imagen.fill(COLOR_AZUL)
        
        # Escalar la imagen segun el parametro scale
        ancho = int(imagen.get_width() * scale)
        alto = int(imagen.get_height() * scale)
        self.image = pygame.transform.scale(imagen, (ancho, alto))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
        # Variables de fisica del personaje
        self.vel_y = 0
        self.en_el_aire = False
        self.y = y

    def saltar(self):
        """Hace que el personaje salte si esta en el suelo"""
        if not self.en_el_aire:
            self.vel_y = -15  # Velocidad inicial del salto (negativa = hacia arriba)
            self.en_el_aire = True

    def actualizar(self):
        """Actualiza la fisica del personaje (gravedad y posicion)"""
        # Aplicar gravedad
        self.vel_y += Constantes.GRAVEDAD
        
        # Limitar velocidad maxima de caida
        if self.vel_y > 10:
            self.vel_y = 10

        # Actualizar posicion vertical
        self.rect.y += self.vel_y
        self.y = self.rect.y

        # Verificar colision con el suelo
        if self.rect.bottom >= PISO_POS_Y:
            self.rect.bottom = PISO_POS_Y
            self.en_el_aire = False
            self.vel_y = 0  # Detener velocidad vertical al tocar el suelo

    def dibujar(self, pantalla):
        """Dibuja el personaje en la pantalla"""
        pantalla.blit(self.image, self.rect)

def dibujar_barra_energia(pantalla, energia_actual, energia_maxima):
    """Dibuja la barra de energia en la parte superior derecha de la pantalla"""
    # Calcular porcentaje de energia restante
    porcentaje = (energia_actual / energia_maxima) * 100
    
    # Posicion y dimensiones de la barra
    barra_ancho = 200
    barra_alto = 20
    barra_x = PANTALLA_ANCHO - barra_ancho - 20
    barra_y = 20
    
    # Dibujar fondo de la barra (gris oscuro)
    pygame.draw.rect(pantalla, COLOR_BARRA_FONDO, (barra_x, barra_y, barra_ancho, barra_alto))
    
    # Calcular ancho de la barra de energia segun porcentaje
    ancho_energia = int((energia_actual / energia_maxima) * barra_ancho)
    
    # Cambiar color segun nivel de energia
    if porcentaje > 60:
        color_energia = COLOR_BARRA_ENERGIA  
    elif porcentaje > 30:
        color_energia = COLOR_AMARILLO       
    else:
        color_energia = COLOR_ROJO          
    
    # Dibujar barra de energia
    if ancho_energia > 0:
        pygame.draw.rect(pantalla, color_energia, (barra_x, barra_y, ancho_energia, barra_alto))
    
    # Dibujar borde de la barra
    pygame.draw.rect(pantalla, COLOR_BLANCO, (barra_x, barra_y, barra_ancho, barra_alto), 2)
    
    # Dibujar texto con porcentaje
    texto_energia = font_HUD.render(f"Energia: {porcentaje:.0f}%", True, COLOR_BLANCO)
    pantalla.blit(texto_energia, (barra_x, barra_y - 25))

def dibujar_contador_kilometros(pantalla, km_restantes):
    """Dibuja el contador de kilometros en la parte superior izquierda"""
    # Posicion del contador
    contador_x = 20
    contador_y = 60
    
    # Crear texto con kilometros restantes
    texto_km = font_HUD.render(f"Kilometros restantes: {km_restantes:.2f} km", True, COLOR_AMARILLO)
    
    # Dibujar fondo semi-transparente para el texto
    texto_rect = texto_km.get_rect()
    texto_rect.topleft = (contador_x, contador_y)
    
    fondo_contador = pygame.Rect(texto_rect.left - 5, texto_rect.top - 5, 
                                texto_rect.width + 10, texto_rect.height + 10)
    pygame.draw.rect(pantalla, COLOR_INSTRUCCION_FONDO, fondo_contador)
    
    # Dibujar el texto
    pantalla.blit(texto_km, (contador_x, contador_y))

def dibujar_fondo_animado(pantalla, img_fondo, fondo_x1, fondo_x2):
    """Dibuja el fondo animado para crear sensacion de movimiento"""
    if img_fondo:
        # Dibujar dos copias del fondo para crear loop continuo
        pantalla.blit(img_fondo, (fondo_x1, -(PANTALLA_ALTO - PISO_POS_Y)))
        pantalla.blit(img_fondo, (fondo_x2, -(PANTALLA_ALTO - PISO_POS_Y)))
    else:
        # Si no hay imagen, llenar con color blanco
        pantalla.fill(COLOR_BLANCO)

def verificar_colision(rect_personaje, rect_auto):
    """Verifica si hay colision entre el personaje y el auto"""
    return rect_personaje.colliderect(rect_auto)

def actualizar_tiempo_y_distancia(tiempo_inicio):
    """Actualiza el tiempo transcurrido y calcula kilometros restantes"""
    tiempo_actual = pygame.time.get_ticks()
    tiempo_transcurrido = (tiempo_actual - tiempo_inicio) / 1000  # Convertir a segundos
    
    # Calcular energia restante
    energia_actual = max(0, DURACION_ENERGIA - tiempo_transcurrido)
    
    # Calcular kilometros restantes
    km_recorridos = tiempo_transcurrido * DECREMENTO_KM_POR_SEGUNDO
    km_restantes = max(0, KILOMETROS_OBJETIVO - km_recorridos)
    
    return energia_actual, km_restantes, tiempo_transcurrido

# Crear instancia del personaje
personaje = Personaje(100, PISO_POS_Y - 64, scale=0.2)

# Bucle principal del juego
while juegoEnEjecucion:
    clock.tick(FPS)
    
    # Actualizar tiempo, energia y distancia
    if not game_over and not victoria:
        energia_restante, kilometros_restantes, tiempo_transcurrido = actualizar_tiempo_y_distancia(tiempo_inicio)
        
        # Verificar condiciones de victoria o derrota
        if energia_restante <= 0:
            game_over = True
        elif kilometros_restantes <= 0:
            victoria = True
    
    # Animar fondo (mover hacia la izquierda para simular movimiento)
    if not game_over and not victoria:
        fondo_x1 -= velocidad_fondo
        fondo_x2 -= velocidad_fondo
        
        # Reiniciar posiciones cuando salen de pantalla
        if fondo_x1 <= -PANTALLA_ANCHO:
            fondo_x1 = PANTALLA_ANCHO
        if fondo_x2 <= -PANTALLA_ANCHO:
            fondo_x2 = PANTALLA_ANCHO
    
    # Dibujar fondo animado
    dibujar_fondo_animado(pantalla, img_fondo, fondo_x1, fondo_x2)
    
    # Dibujar el piso (linea verde)
    piso_altura = PANTALLA_ALTO - PISO_POS_Y
    piso_rect = pygame.Rect(0, PISO_POS_Y, PANTALLA_ANCHO, piso_altura)
    pygame.draw.rect(pantalla, COLOR_VERDE, piso_rect)
    pygame.draw.line(pantalla, COLOR_NEGRO, (0, PISO_POS_Y), (PANTALLA_ANCHO, PISO_POS_Y), 3)

    # Manejar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            juegoEnEjecucion = False
        
        # Si el juego termino, cualquier tecla cierra el juego
        if game_over or victoria:
            if event.type == pygame.KEYDOWN:
                juegoEnEjecucion = False

    # Logica del juego (solo si no ha terminado)
    if not game_over and not victoria:
        # Manejar input del jugador
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            personaje.saltar()
  
        # Mover el auto hacia la izquierda
        auto_x -= auto_vel_x
        
        # Si el auto sale de pantalla, reiniciar posicion (consigna 4)
        if auto_x < -auto_ancho:
            auto_x = PANTALLA_ANCHO

    # Actualizar y dibujar personaje
    personaje.actualizar()
    personaje.dibujar(pantalla)
    
    # Dibujar auto
    auto_rect = pygame.Rect(auto_x, auto_y, auto_ancho, auto_alto)
    pygame.draw.rect(pantalla, COLOR_ROJO, auto_rect)
    
    # Verificar colision entre personaje y auto
    if not game_over and not victoria:
        if verificar_colision(personaje.rect, auto_rect):
            game_over = True
    
    # Dibujar interfaz de usuario (HUD)
    if not game_over and not victoria:
        # Dibujar instrucciones
        pygame.draw.rect(pantalla, COLOR_INSTRUCCION_FONDO, fondo_rect)
        pantalla.blit(txtInstrucciones, txtInstrucciones_rect)
        
        # Dibujar barra de energia
        dibujar_barra_energia(pantalla, energia_restante, DURACION_ENERGIA)
        
        # Dibujar contador de kilometros
        dibujar_contador_kilometros(pantalla, kilometros_restantes)
    
    # Mostrar mensaje de game over o victoria
    if game_over:
        pantalla.blit(txtGameOver, txtGameOver_rect)
        # Texto adicional para reiniciar
        texto_reinicio = font_HUD.render("Presiona cualquier tecla para salir", True, COLOR_BLANCO)
        rect_reinicio = texto_reinicio.get_rect(center=(PANTALLA_ANCHO // 2, (PANTALLA_ALTO // 2)-150))
        pantalla.blit(texto_reinicio, rect_reinicio)
    
    elif victoria:
        pantalla.blit(txtVictoria, txtVictoria_rect)
        # Texto adicional para salir
        texto_salir = font_HUD.render("Presiona cualquier tecla para salir", True, COLOR_BLANCO)
        rect_salir = texto_salir.get_rect(center=(PANTALLA_ANCHO // 2, (PANTALLA_ALTO // 2)-150))
        pantalla.blit(texto_salir, rect_salir)

    # Actualizar pantalla
    pygame.display.flip()

# Cerrar pygame y salir
pygame.quit()
sys.exit()