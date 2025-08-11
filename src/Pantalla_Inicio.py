import pygame
import sys
import random
import math
import Constantes
from Ronda1_Inicio import juego

# Inicializar Pygame
pygame.init()

PANTALLA = pygame.display.set_mode((Constantes.ANCHO_PANTALLA, Constantes.ALTO_PANTALLA))
pygame.display.set_caption("Neo-Ciudad Vista - Edición Eco")
pygame.mixer.music.load("src\Recursos\Music\Win.mp3")
pygame.mixer.music.play(-1)  # Reproducir en bucle
sonido_boton=pygame.mixer.Sound("src\Recursos\Music\mixkit-arcade-game-jump-coin-216.mp3")

VOLUMEN_MUSICA = 1.0  # Volumen inicial (0.0 a 1.0)
VOLUMEN_SONIDO = 1.0  # Volumen inicial (0.0 a 1.0)

SALIR = False
# Fuentes
FUENTE_TITULO = pygame.font.Font(None, 90)
FUENTE_SUBTITULO = pygame.font.Font(None, 40)
FUENTE_BOTON = pygame.font.Font(None, 55)
FUENTE_PEQUENA = pygame.font.Font(None, 32)

# --- Clase Barra de Volumen ---
class BarraVolumen:
    def __init__(self, texto, x, y, ancho, volumen_inicial=1.0, callback=None):
        self.texto = texto
        self.x = x
        self.y = y
        self.ancho = ancho
        self.volumen = volumen_inicial
        self.callback = callback
        self.arrastrando = False
        
        # Dimensiones de la barra
        self.barra_y = y + 35
        self.barra_alto = 20
        self.barra_ancho = ancho - 40
        self.barra_x = x + 20
        
    def dibujar(self, superficie):
        
        # Dibujar texto
        texto_surface = FUENTE_PEQUENA.render(self.texto, True, Constantes.COLOR_TEXTO_EN_FONDO)
        superficie.blit(texto_surface, (self.x, self.y))
        
        # Dibujar fondo de la barra
        rect_fondo = pygame.Rect(self.barra_x, self.barra_y, self.barra_ancho, self.barra_alto)
        pygame.draw.rect(superficie, (60, 60, 60), rect_fondo)
        
        # Dibujar barra de progreso
        ancho_progreso = int(self.barra_ancho * self.volumen)
        if ancho_progreso > 0:
            rect_progreso = pygame.Rect(self.barra_x, self.barra_y, ancho_progreso, self.barra_alto)
            pygame.draw.rect(superficie, Constantes.COLOR_PRIMARIO, rect_progreso)
        
        # Dibujar círculo deslizante
        circulo_x = self.barra_x + int(self.barra_ancho * self.volumen)
        pygame.draw.circle(superficie, Constantes.COLOR_SECUNDARIO, (circulo_x, self.barra_y + self.barra_alto // 2), 12)
        pygame.draw.circle(superficie, (255, 255, 255), (circulo_x, self.barra_y + self.barra_alto // 2), 8)
        
        # Mostrar porcentaje
        porcentaje_text = f"{int(self.volumen * 100)}%"
        porcentaje_surface = FUENTE_PEQUENA.render(porcentaje_text, True, Constantes.COLOR_TEXTO_EN_FONDO)
        superficie.blit(porcentaje_surface, (self.x + self.ancho - 60, self.y))
    
    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 1:  # Click izquierdo
                mouse_x, mouse_y = evento.pos
                # Verificar si el click está en la barra
                if (self.barra_x <= mouse_x <= self.barra_x + self.barra_ancho and 
                    self.barra_y <= mouse_y <= self.barra_y + self.barra_alto):
                    self.arrastrando = True
                    self.actualizar_volumen(mouse_x)
        
        elif evento.type == pygame.MOUSEBUTTONUP:
            if evento.button == 1:
                self.arrastrando = False
        
        elif evento.type == pygame.MOUSEMOTION:
            if self.arrastrando:
                mouse_x = evento.pos[0]
                self.actualizar_volumen(mouse_x)
    
    def actualizar_volumen(self, mouse_x):
        # Calcular nuevo volumen basado en la posición del mouse
        volumen_relativo = (mouse_x - self.barra_x) / self.barra_ancho
        self.volumen = max(0.0, min(1.0, volumen_relativo))  # Limitar entre 0 y 1
        
        if self.callback:
            self.callback(self.volumen)

# --- Clase Botón ---
class Boton:
    def __init__(self, texto, x, y, ancho, alto, accion=None):
        self.texto = texto
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.accion = accion
        self.color = Constantes.COLOR_PRIMARIO
        self.color_hover = Constantes.COLOR_SECUNDARIO
        self.color_texto = Constantes.COLOR_TEXTO_EN_BOTON
        self.hover_viejo= False

    def dibujar(self, superficie):
        pos_raton = pygame.mouse.get_pos()
        color_actual = self.color

        esta_en_hover = self.rect.collidepoint(pos_raton)
        if esta_en_hover and not self.hover_viejo and VOLUMEN_SONIDO > 0:
            sonido_boton.set_volume(VOLUMEN_SONIDO)
            sonido_boton.play()
            
        self.hover_viejo = esta_en_hover

        if esta_en_hover:
            color_actual = self.color_hover
            
        pygame.draw.rect(superficie, color_actual, self.rect, border_radius=8) 
        
        superficie_texto = FUENTE_BOTON.render(self.texto, True, self.color_texto)
        rect_texto = superficie_texto.get_rect(center=self.rect.center)
        superficie.blit(superficie_texto, rect_texto)

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(evento.pos) and self.accion:
                self.accion()

# --- Funciones del Menú ---
def Juego():
    musica = pygame.mixer.music.stop()
    juego() 

def ver_opciones():
    ejecutar_menu_opciones() 

def salir_juego():
    pygame.quit()
    sys.exit()

def cambiar_volumen_musica(volumen):
    global VOLUMEN_MUSICA
    VOLUMEN_MUSICA = volumen
    pygame.mixer.music.set_volume(volumen)

def cambiar_volumen_sonido(volumen):
    global VOLUMEN_SONIDO
    VOLUMEN_SONIDO = volumen
    sonido_boton.set_volume(volumen)

# --- Nueva función para el menú de opciones ---
def ejecutar_menu_opciones():
    ancho_control = 400
    alto_control = 70
    espaciado = 30
    
    centro_x = Constantes.ANCHO_PANTALLA // 2
    inicio_y_opciones = Constantes.ALTO_PANTALLA // 2 - 100 
    
    # Barra de volumen de música
    barra_musica = BarraVolumen(
        "Volumen de Música:",
        centro_x - ancho_control // 2,
        inicio_y_opciones,
        ancho_control,
        VOLUMEN_MUSICA,
        cambiar_volumen_musica
    )
    
    # Barra de volumen de sonidos
    barra_sonido = BarraVolumen(
        "Volumen de Efectos:",
        centro_x - ancho_control // 2,
        inicio_y_opciones + alto_control + espaciado,
        ancho_control,
        VOLUMEN_SONIDO,
        cambiar_volumen_sonido
    )

    # Botón volver
    boton_volver = Boton(
        "Volver al Menú",
        centro_x - 200,
        inicio_y_opciones + 2 * (alto_control + espaciado),
        400,
        70,
        lambda: None
    )
    
    ejecutando = True
    
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                salir_juego()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    ejecutando = False 
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_volver.rect.collidepoint(evento.pos):
                    ejecutando = False
            
            # Manejar eventos de las barras de volumen
            barra_musica.manejar_evento(evento)
            barra_sonido.manejar_evento(evento)

        PANTALLA.fill(Constantes.COLOR_FONDO_BASE)
        
        # Título
        superficie_titulo_opciones = FUENTE_TITULO.render("Opciones", True, Constantes.COLOR_TEXTO_EN_FONDO)
        rect_titulo_opciones = superficie_titulo_opciones.get_rect(center=(Constantes.ANCHO_PANTALLA // 2, 120))
        PANTALLA.blit(superficie_titulo_opciones, rect_titulo_opciones)
        
        # Dibujar controles
        barra_musica.dibujar(PANTALLA)
        barra_sonido.dibujar(PANTALLA)
        boton_volver.dibujar(PANTALLA)

        # Texto de ayuda
        texto_volver_ayuda = FUENTE_PEQUENA.render("Presiona ESC para volver", True, Constantes.COLOR_TEXTO_SUTIL_EN_FONDO)
        rect_volver_ayuda = texto_volver_ayuda.get_rect(center=(Constantes.ANCHO_PANTALLA // 2, Constantes.ALTO_PANTALLA // 2 - 150))
        PANTALLA.blit(texto_volver_ayuda, rect_volver_ayuda)

        pygame.display.flip()

def main_menu():
    ancho_boton = 250
    alto_boton = 75
    espaciado = 30
    altura_total_botones = 3 * alto_boton + 2 * espaciado
    inicio_y = (Constantes.ALTO_PANTALLA - altura_total_botones) // 2 + 60
    
    inicio_x = Constantes.ANCHO_PANTALLA - ancho_boton - 480
    
    botones = [
        Boton("Jugar", inicio_x, inicio_y, ancho_boton, alto_boton, Juego),
        Boton("Ajustes", inicio_x, inicio_y + alto_boton + espaciado, ancho_boton, alto_boton, ver_opciones),
        Boton("Salir", inicio_x, inicio_y + 2 * (alto_boton + espaciado), ancho_boton, alto_boton, salir_juego)
    ]
    
    # Establecer volúmenes iniciales
    pygame.mixer.music.set_volume(VOLUMEN_MUSICA)
    sonido_boton.set_volume(VOLUMEN_SONIDO)
    
    ejecutando = True
    
    while ejecutando:
        PANTALLA.fill(Constantes.COLOR_FONDO_BASE)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                salir_juego()
            for boton in botones:
                boton.manejar_evento(evento)
                
        superficie_titulo = FUENTE_TITULO.render("Go UAIBOT", True, Constantes.COLOR_TEXTO_EN_FONDO)
        rect_titulo = superficie_titulo.get_rect(center=(Constantes.ANCHO_PANTALLA // 2, 120))
        PANTALLA.blit(superficie_titulo, rect_titulo)
        
        superficie_subtitulo = FUENTE_SUBTITULO.render(":)", True, Constantes.COLOR_TEXTO_SUTIL_EN_FONDO)
        rect_subtitulo = superficie_subtitulo.get_rect(center=(Constantes.ANCHO_PANTALLA // 2, 180))
        PANTALLA.blit(superficie_subtitulo, rect_subtitulo)
        
        for boton in botones:
            boton.dibujar(PANTALLA)
        pygame.display.flip()

if __name__ == "__main__":
    PANTALLA = pygame.display.set_mode((Constantes.ANCHO_PANTALLA, Constantes.ALTO_PANTALLA))
    pygame.display.set_caption(f"Neo-Ciudad Vista - {Constantes.ANCHO_PANTALLA}x{Constantes.ALTO_PANTALLA}")

    for i in range(20):
        x = random.randint(50, Constantes.ANCHO_PANTALLA - 50)
        y = Constantes.ALTO_PANTALLA - 50

    main_menu()