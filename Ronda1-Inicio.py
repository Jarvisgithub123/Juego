import pygame
import sys
import os
import Constantes

pygame.init()

RUTA_ARCHIVO_FONDO = "Recursos\Imagenes\ciudad.jpg" 
COLOR_BLANCO = (255, 255, 255)
COLOR_NEGRO = (0, 0, 0)
COLOR_ROJO = (200, 0, 0)
COLOR_AZUL = (0, 0, 200)
COLOR_VERDE = (0, 200, 0)
COLOR_INSTRUCCION_FONDO = (50, 50, 50)
PANTALLA_ANCHO = 1280
PANTALLA_ALTO = 720
PISO_POS_Y = 650
clock = pygame.time.Clock()
FPS = 60

pantalla = pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
pygame.display.set_caption("OFIRCA 2025 - Ronda 1 Inicio")

if os.path.exists(RUTA_ARCHIVO_FONDO):
    img_fondo = pygame.image.load(RUTA_ARCHIVO_FONDO)
    img_fondo = pygame.transform.scale(img_fondo, (PANTALLA_ANCHO, PANTALLA_ALTO))
else:
    img_fondo = None

font_TxtInstrucciones = pygame.font.SysFont(None, 36)
txtInstrucciones = font_TxtInstrucciones.render("Usa la barra espaciadora para saltar", True, COLOR_BLANCO)
txtInstrucciones_desplazamiento = 10
txtInstrucciones_rect = txtInstrucciones.get_rect()
txtInstrucciones_rect.topleft = (10, 10)
fondo_rect = pygame.Rect(txtInstrucciones_rect.left - txtInstrucciones_desplazamiento,
                        txtInstrucciones_rect.top - txtInstrucciones_desplazamiento,
                        txtInstrucciones_rect.width + 2 * txtInstrucciones_desplazamiento,
                         txtInstrucciones_rect.height + 2 * txtInstrucciones_desplazamiento)

font_TxtGameOver = pygame.font.SysFont(None, 100)
txtGameOver = font_TxtGameOver.render("JUEGO TERMINADO", True, COLOR_ROJO)
txtGameOver_rect = txtGameOver.get_rect(center=(PANTALLA_ANCHO // 2, (PANTALLA_ALTO // 2)-200))

robot_tamaño = 50
robot_x = 100
robot_y = PISO_POS_Y - robot_tamaño

auto_ancho = 100
auto_alto = 40
auto_x = PANTALLA_ANCHO
auto_y = PISO_POS_Y - auto_alto
auto_vel_x = 7

juegoEnEjecucion = True
game_over = False


class Personaje(pygame.sprite.Sprite):
    def __init__(self, x, y,scale):
        super().__init__()


        imagen = pygame.image.load("Recursos/Imagenes/UAIBOT.png").convert_alpha()

        ancho = int(imagen.get_width() * scale)
        alto = int(imagen.get_height() * scale)
        self.image = pygame.transform.scale(imagen, (ancho, alto))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.vel_y = 0
        self.en_el_aire = False
        self.y = y  

    def saltar(self):
        if not self.en_el_aire:
            self.vel_y = -15
            self.en_el_aire = True

    def actualizar(self):
        self.vel_y += Constantes.GRAVEDAD
        if self.vel_y > 10:
            self.vel_y = 10

        self.rect.y += self.vel_y
        self.y = self.rect.y  

        if self.rect.bottom >= PISO_POS_Y:
            self.rect.bottom = PISO_POS_Y
            self.en_el_aire = False

    def dibujar(self, pantalla):
        pantalla.blit(self.image, self.rect)


personaje = Personaje(100,PISO_POS_Y - 64, scale=0.2)

while juegoEnEjecucion:
    clock.tick(FPS)
    if img_fondo:
        fondo_desplazamiento_y = -(PANTALLA_ALTO - PISO_POS_Y)
        pantalla.blit(img_fondo, (0, fondo_desplazamiento_y))
    else:
        pantalla.fill(COLOR_BLANCO)

  
    piso_altura = PANTALLA_ALTO - PISO_POS_Y
    piso_rect = pygame.Rect(0, PISO_POS_Y, PANTALLA_ANCHO, piso_altura)
    pygame.draw.rect(pantalla, COLOR_VERDE, piso_rect)

    pygame.draw.line(pantalla, COLOR_NEGRO, (0, PISO_POS_Y), (PANTALLA_ANCHO, PISO_POS_Y), 3)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            juegoEnEjecucion = False
        if game_over:
            if event.type == pygame.KEYDOWN:
                juegoEnEjecucion = False

    if not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            personaje.saltar()
  
        auto_x -= auto_vel_x
        if auto_x < -auto_ancho:
            auto_x = PANTALLA_ANCHO  

        auto_rect = pygame.Rect(auto_x, auto_y, auto_ancho, auto_alto)

    personaje.actualizar()
    personaje.dibujar(pantalla) 
    auto_rect = pygame.Rect(auto_x, auto_y, auto_ancho, auto_alto)
    pygame.draw.rect(pantalla, COLOR_ROJO, auto_rect)

    if not game_over:
        pygame.draw.rect(pantalla, COLOR_INSTRUCCION_FONDO, fondo_rect)
        pantalla.blit(txtInstrucciones, txtInstrucciones_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
