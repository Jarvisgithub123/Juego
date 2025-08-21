import pygame
from typing import List, Optional
from src.Constantes import *
import random

# Constantes para los autos
DEFAULT_CAR_WIDTH = 126
DEFAULT_CAR_HEIGHT = 86
ANIMATION_SPEED = 0.1
SPRITESHEET_START_COLUMN = 0
SPRITESHEET_END_COLUMN = 2
SPRITESHEET_ROW = 0

class Car(pygame.sprite.Sprite):
    """Auto enemigo con velocidades más variadas"""
    
    CAR_TYPES = ["Auto_azul", "Auto_rojo"]
    
    def __init__(self, initial_x: int, initial_y: int, resource_manager, 
                 speed: int = 15, 
                 width: int = DEFAULT_CAR_WIDTH, 
                 height: int = DEFAULT_CAR_HEIGHT):
        super().__init__()
        self.resource_manager = resource_manager
        self.rect = pygame.Rect(initial_x, initial_y, width, height)
        self.movement_speed = speed
        self.width = width
        self.height = height
        
        # Elegir tipo basado en velocidad para coherencia visual
        self.car_type = self._choose_car_type_by_speed(speed)
        
        # Sistema de animación
        self.animation_frame = 0
        self.animation_timer = 0
        # Animación más rápida para autos más rápidos
        self.animation_speed = ANIMATION_SPEED * (13.0 / max(speed, 8))
        self.animation_frames: List[pygame.Surface] = []
        
        # Cargar frames y configurar sprite
        self._load_animation_frames()
        self.current_sprite: Optional[pygame.Surface] = None
        self._update_sprite()
    
    def _choose_car_type_by_speed(self, speed: int) -> str:
        """Autos rojos = más rápidos, azules = más lentos"""
        if speed >= 18:
            # Autos rápidos: 80% rojos
            return random.choices(["Auto_rojo", "Auto_azul"], weights=[80, 20], k=1)[0]
        elif speed <= 12:
            # Autos lentos: 80% azules  
            return random.choices(["Auto_azul", "Auto_rojo"], weights=[80, 20], k=1)[0]
        else:
            # Velocidad media: 50/50
            return random.choice(self.CAR_TYPES)
    
    def _load_animation_frames(self):
        """Carga los frames de animación"""
        spritesheet = self.resource_manager.get_spritesheet(self.car_type)
        
        if spritesheet:
            self.animation_frames = self.resource_manager.get_animation_frames(
                self.car_type, 
                SPRITESHEET_START_COLUMN, 
                SPRITESHEET_END_COLUMN, 
                SPRITESHEET_ROW
            )
        
        # Fallback si no hay frames
        if not self.animation_frames:
            color = (255, 50, 50) if self.car_type == "Auto_rojo" else (50, 50, 255)
            placeholder = self.resource_manager.create_fallback_image((self.width, self.height), color)
            self.animation_frames = [placeholder]
    
    def _update_sprite(self):
        """Actualiza el sprite actual"""
        if self.animation_frames:
            frame_index = int(self.animation_frame) % len(self.animation_frames)
            self.current_sprite = self.animation_frames[frame_index]
            self.image = self.current_sprite
    
    def update(self, delta_time: float = 1/60):
        """Actualiza posición y animación"""
        # Movimiento horizontal
        self.rect.x -= self.movement_speed
        
        # Animación
        self.animation_timer += delta_time
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % len(self.animation_frames)
            self._update_sprite()
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el auto"""
        if self.current_sprite:
            screen.blit(self.current_sprite, self.rect)
        else:
            # Fallback
            color = (255, 50, 50) if self.car_type == "Auto_rojo" else (50, 50, 255)
            pygame.draw.rect(screen, color, self.rect)
    
    def get_position(self) -> tuple:
        return (self.rect.x, self.rect.y)
    
    def get_speed(self) -> int:
        return self.movement_speed
    
    def set_speed(self, new_speed: int):
        self.movement_speed = max(1, new_speed)
        # Reajustar velocidad de animación
        self.animation_speed = ANIMATION_SPEED * (13.0 / max(new_speed, 8))