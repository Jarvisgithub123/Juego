import pygame
from typing import List, Optional
from src.Constantes import *
from abc import ABC, abstractmethod

class Collectible(pygame.sprite.Sprite, ABC):
    """Clase base para todos los objetos coleccionables del juego"""
    
    def __init__(self, resource_manager, image_name: str, *groups, 
                 width: int = DEFAULT_PILAS_WIDTH, height: int = DEFAULT_PILAS_HEIGHT):
        # ACEPTAR llamadas donde width/height pueden haber sido pasados como últimos elementos en *groups.
        groups_list = list(groups)
        # Si los dos últimos elementos son ints, asumir que son width, height (en ese orden).
        if len(groups_list) >= 2 and isinstance(groups_list[-1], int) and isinstance(groups_list[-2], int):
            # Extraer height y width desde el final
            height = groups_list.pop()
            width = groups_list.pop()
        
        # Llamar a pygame.sprite.Sprite.__init__ con los grupos correctos (sin ints)
        super().__init__(*groups_list)
        
        self.resource_manager = resource_manager
        
        # Cargar imagen
        collectible_image = resource_manager.get_image(image_name)
        if collectible_image:
            # Si la imagen existe, asegurarse de tener un tamaño consistente
            self.image = collectible_image.convert_alpha()
            # Opcional: ajustar rect al tamaño actual de la imagen (mantener original si se quiere)
            self.rect = self.image.get_rect()
        else:
            # Crear imagen placeholder si no se encuentra (usar width/height correctamente)
            self.image = pygame.Surface((width, height), pygame.SRCALPHA)
            self.image.fill((255, 255, 0))  # Amarillo por defecto
            self.rect = self.image.get_rect()
        
        # Estado del objeto coleccionable
        self.collected = False
        self.speed = 8
        self.effect_duration = 0.0  # Para efectos temporales
        
    def update(self):
        """Actualiza la posicion del objeto coleccionable"""
        if not self.collected:
            self.rect.x -= self.speed
    
    def collect(self, robot):
        """Método para recolectar el objeto - debe ser implementado por las subclases
        
        Args:
            robot: El robot que recolecta el objeto
        """
        if not self.collected:
            self.collected = True
            self._apply_effect(robot)
            self._play_collection_sound()
    
    @abstractmethod
    def _apply_effect(self, robot):
        """Aplica el efecto específico del objeto - debe ser implementado por subclases"""
        pass
    
    @abstractmethod
    def _play_collection_sound(self):
        """Reproduce el sonido de recolección - debe ser implementado por subclases"""
        pass
    
    def is_active(self) -> bool:
        """Verifica si el objeto sigue activo (no recolectado y en pantalla)"""
        return not self.collected
        
    def get_effect_info(self) -> str:
        """Retorna información sobre el efecto del objeto"""
        return "Objeto coleccionable base"