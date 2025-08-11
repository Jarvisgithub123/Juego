import pygame
from src.Constantes import *

class Car(pygame.sprite.Sprite):
    """Clase que representa los autos enemigos"""
    
    def __init__(self, x, y, resource_manager, speed=7, width=100, height=40):
        super().__init__()
        self.resource_manager = resource_manager
        
        # Cargar imagen del auto
        image = self.resource_manager.get_image("auto")
        if image:
            self.image = pygame.transform.scale(image, (width, height))
        else:
            # Crear imagen de respaldo
            self.image = self.resource_manager.create_fallback_image((width, height), COLOR_ROJO)
        
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.width = width
        self.height = height
    
    def update(self):
        """Actualiza la posición del auto moviéndolo hacia la izquierda"""
        self.rect.x -= self.speed
        
        # Si sale de la pantalla, reiniciar posición
        if self.rect.right < 0:
            self.rect.left = PANTALLA_ANCHO
    
    def draw(self, screen):
        """Dibuja el auto en la pantalla"""
        screen.blit(self.image, self.rect)
