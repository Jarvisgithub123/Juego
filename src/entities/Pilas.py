import pygame
from typing import List, Optional
from src.Constantes import *


class pilas(pygame.sprite.Sprite):
    def __init__(self, resource_manager, *groups, width: int = DEFAULT_PILAS_WIDTH, height: int = DEFAULT_PILAS_HEIGHT):
        super().__init__(*groups)
        
        # Cargar imagen directamente en lugar de usar spritesheet
        pila_image = resource_manager.get_image("pila")  
        self.rect = self.image.get_rect()
        # Estado de la pila
        self.collected = False
        self.speed = 8
    
    def update(self):
        """Actualiza la posicion de la pila"""
        if not self.collected:
            self.rect.x -= self.speed
        
    
    def collect(self, robot):
        """ Método para recolectar la pila y dar energia al robot
        
        Args:
            robot: El robot que recolecta la pila
        """
        if not self.collected:
            energia_anterior = robot.energia if hasattr(robot, 'energia') else 0
            
            # Aumentar la energia del robot sin exceder su maximo
            if hasattr(robot, 'energia_maxima'):
                nueva_energia = min(robot.energia + ENERGIA_PILA, robot.energia_maxima)
                robot.energia = nueva_energia
                print(f"Energia del robot: {energia_anterior} -> {nueva_energia}")
            
            self.collected = True
            print(f"¡Pila recolectada! +{ENERGIA_PILA} segundos de energia")
    
    def is_active(self) -> bool:
        """Verifica si la pila sigue activa (no recolectada y en pantalla)"""
        return not self.collected
