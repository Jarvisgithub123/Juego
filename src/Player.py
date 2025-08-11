import pygame
from Constantes import *
class Personaje(pygame.sprite.Sprite):
        """Clase que representa al personaje principal UAIBOT"""
        def __init__(self, x, y, scale):
            super().__init__()
            
            # Cargar imagen del personaje UAIBOT
            try:
                imagen = pygame.image.load("Assets/Imagenes/UAIBOT.png").convert_alpha()
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
                self.vel_y = -30
                self.en_el_aire = True
                sonido_salto.play()

        def actualizar(self):
            """Actualiza la fisica del personaje (gravedad y posicion)"""
            # Aplicar gravedad
            self.vel_y += GRAVEDAD
            
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
                self.vel_y = 0
                sonido_salto.stop()