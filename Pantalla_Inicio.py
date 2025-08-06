import pygame
import sys
import random
import math
import Constantes
# Inicializar Pygame
pygame.init()



PANTALLA = pygame.display.set_mode((Constantes.ANCHO_PANTALLA, Constantes.ALTO_PANTALLA))
pygame.display.set_caption("Neo-Ciudad Vista - Edición Eco")
pygame.mixer.music.load("Recursos\Music\wwd.mp3juice.blog - Aventura - Los Infieles (192 KBps).mp3")
pygame.mixer.music.play(-1)  # Reproducir en bucle
sonido_boton=pygame.mixer.Sound("Recursos\Music\mixkit-arcade-game-jump-coin-216.mp3")

SONIDO_ACTIVADO = True
SALIR = False
# Fuentes
FUENTE_TITULO = pygame.font.Font(None, 90)
FUENTE_SUBTITULO = pygame.font.Font(None, 40)
FUENTE_BOTON = pygame.font.Font(None, 55)
FUENTE_PEQUENA = pygame.font.Font(None, 32)

# --- Clase Ventana  ---
class Ventana:
    def __init__(self, rel_x, rel_y, ancho, alto, es_eco=False):
        self.rect_rel = pygame.Rect(rel_x, rel_y, ancho, alto)
        self.es_eco = es_eco 
        self.esta_encendida = random.random() < (0.2 if es_eco else 0.3)
        self.alfa_actual = 255 if self.esta_encendida else 0
        self.velocidad_desvanecimiento = random.uniform(1.0, 2.5) 
        self.direccion_desvanecimiento = 0
        self.tiempo_cambio_siguiente_estado = pygame.time.get_ticks() + random.randint(2000, 8000) 

    def actualizar(self):
        tiempo_actual = pygame.time.get_ticks()
        if self.direccion_desvanecimiento != 0:
            self.alfa_actual += self.direccion_desvanecimiento * self.velocidad_desvanecimiento
            self.alfa_actual = max(0, min(255, self.alfa_actual))
            if (self.direccion_desvanecimiento == 1 and self.alfa_actual >= 255) or \
               (self.direccion_desvanecimiento == -1 and self.alfa_actual <= 0):
                self.direccion_desvanecimiento = 0
                self.esta_encendida = (self.alfa_actual > 0)
                self.tiempo_cambio_siguiente_estado = tiempo_actual + random.randint(2000, 8000)
        if self.direccion_desvanecimiento == 0 and tiempo_actual >= self.tiempo_cambio_siguiente_estado:
            probabilidad_cambio = 0.03 if self.es_eco else 0.05
            if random.random() < probabilidad_cambio:
                if self.esta_encendida:
                    self.direccion_desvanecimiento = -1
                else:
                    self.direccion_desvanecimiento = 1
                self.tiempo_cambio_siguiente_estado = tiempo_actual + random.randint(2000, 8000)

    def dibujar(self, superficie, abs_x, abs_y, multiplicador_alfa=1.0):
        rect_abs = self.rect_rel.copy()
        rect_abs.x += abs_x
        rect_abs.y += abs_y
        if self.alfa_actual > 0:
            if self.es_eco:
                color_ventana = Constantes.COLOR_VENTANA_ECO + (int(self.alfa_actual * multiplicador_alfa),)
            else:
                color_ventana = Constantes.COLOR_VENTANA_CLARA + (int(self.alfa_actual * multiplicador_alfa),)
            s = pygame.Surface((rect_abs.width, rect_abs.height), pygame.SRCALPHA)
            s.fill(color_ventana)
            superficie.blit(s, (rect_abs.x, rect_abs.y))
        else:
            color_apagado = Constantes.COLOR_VENTANA_APAGADA + (int(255 * multiplicador_alfa),)
            pygame.draw.rect(superficie, color_apagado, rect_abs)



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
        if esta_en_hover and not self.hover_viejo:
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

# --- Función de Dibujo de Fondo Dinámico (Simplificada con árboles) ---


# --- Funciones del Menú ---
def Juego():
    musica = pygame.mixer.music.stop()  # Llamar a la función de inicio del juego desde el módulo Juego


def ver_opciones():
    ejecutar_menu_opciones() 

def salir_juego():
    pygame.quit()
    sys.exit()

            

# --- Nueva función para el menú de opciones ---
def ejecutar_menu_opciones():

    def alternar_sonido():
        global SONIDO_ACTIVADO
        if SONIDO_ACTIVADO:
            pygame.mixer.music.pause() 
            SONIDO_ACTIVADO = False
        else: 
            pygame.mixer.music.unpause()
            SONIDO_ACTIVADO = True
    
    ancho_boton_opcion = 400
    alto_boton_opcion = 70
    espaciado_opcion = 20
    
    centro_x = Constantes.ANCHO_PANTALLA // 2
    inicio_y_opciones = Constantes.ALTO_PANTALLA // 2 - 100 
    
    
    # Botón de Sonido
    boton_sonido = Boton(
        f"Sonido: {'Activado' if SONIDO_ACTIVADO else 'Desactivado'}",
        centro_x - ancho_boton_opcion // 2,
        inicio_y_opciones,
        ancho_boton_opcion,
        alto_boton_opcion,
        alternar_sonido
    )

    boton_volver = Boton(
        "Volver al Menú",
        centro_x - ancho_boton_opcion // 2,
        inicio_y_opciones + 1 * (alto_boton_opcion + espaciado_opcion),
        ancho_boton_opcion,
        alto_boton_opcion,
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
            
            boton_sonido.manejar_evento(evento)

       
        
        superficie_titulo_opciones = FUENTE_TITULO.render("Opciones", True, Constantes.COLOR_TEXTO_EN_FONDO)
        rect_titulo_opciones = superficie_titulo_opciones.get_rect(center=(Constantes.ANCHO_PANTALLA // 2, 120))
        PANTALLA.blit(superficie_titulo_opciones, rect_titulo_opciones)

        # Actualizar el texto de los botones cada frame
        boton_sonido.texto = f"Sonido: {'Activado' if SONIDO_ACTIVADO else 'Desactivado'}"
       
        
        boton_sonido.dibujar(PANTALLA)
        boton_volver.dibujar(PANTALLA)

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
    ejecutando = True
    while ejecutando:
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
