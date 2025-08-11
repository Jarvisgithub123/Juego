import pygame
from src.Constantes import *

class Player(pygame.sprite.Sprite):
    """Clase que representa al personaje principal UAIBOT"""
    
    def __init__(self, x, y, scale, resource_manager):
        super().__init__()
        self.resource_manager = resource_manager
        
        # Cargar imagen del personaje
        image = self.resource_manager.get_image("uaibot")
        if image:
            # Escalar la imagen según el parámetro scale
            width = int(image.get_width() * scale)
            height = int(image.get_height() * scale)
            self.image = pygame.transform.scale(image, (width, height))
        else:
            # Crear imagen de respaldo
            self.image = self.resource_manager.create_fallback_image((64, 64), COLOR_AZUL)
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
        # Variables de física del personaje
        self.vel_y = 0
        self.is_airborne = False
        self.y = y
    
    def jump(self):
        """Hace que el personaje salte si está en el suelo"""
        if not self.is_airborne:
            self.vel_y = -30
            self.is_airborne = True
            self.resource_manager.play_sound("salto")
    
    def update(self):
        """Actualiza la física del personaje (gravedad y posición)"""
        # Aplicar gravedad
        self.vel_y += GRAVEDAD
        
        # Limitar velocidad máxima de caída
        if self.vel_y > 10:
            self.vel_y = 10
        
        # Actualizar posición vertical
        self.rect.y += self.vel_y
        self.y = self.rect.y
        
        # Verificar colisión con el suelo
        if self.rect.bottom >= PISO_POS_Y:
            self.rect.bottom = PISO_POS_Y
            self.is_airborne = False
            self.vel_y = 0
    
    def draw(self, screen):
        """Dibuja el personaje"""
        screen.blit(self.image, self.rect)