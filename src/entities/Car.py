import pygame
from typing import List, Optional
from src.Constantes import *
import random

# Constantes para los autos - movidas desde numeros magicos

ANIMATION_SPEED = 0.1
SPRITESHEET_START_COLUMN = 0
SPRITESHEET_END_COLUMN = 2
SPRITESHEET_ROW = 0

# Nuevas constantes para evitar numeros magicos
CAR_SPEED_THRESHOLD_FAST = 18
CAR_SPEED_THRESHOLD_SLOW = 12
FAST_CAR_RED_WEIGHT = 80
FAST_CAR_BLUE_WEIGHT = 20
SLOW_CAR_BLUE_WEIGHT = 80
SLOW_CAR_RED_WEIGHT = 20
ANIMATION_SPEED_DIVISOR = 13.0

class Car(pygame.sprite.Sprite):
    """Auto enemigo optimizado con soporte para object pooling"""
    
    CAR_TYPES = ["Auto_azul", "Auto_rojo"]
    
    def __init__(self, initial_x: int, initial_y: int, resource_manager, 
                 speed: int = 15, 
                 width: int = DEFAULT_CAR_WIDTH, 
                 height: int = DEFAULT_CAR_HEIGHT):
        super().__init__()
        self.resource_manager = resource_manager
        self.width = width
        self.height = height
        
        # Pool support
        self.active = True
        
        # Crear rect una sola vez y reutilizar
        self.rect = pygame.Rect(initial_x, initial_y, width, height)
        
        # Cache para frames de animacion (se carga una vez por tipo de auto)
        self.animation_frames: List[pygame.Surface] = []
        
        # Variables de animacion
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = ANIMATION_SPEED
        
        self.current_sprite: Optional[pygame.Surface] = None
        
        # Inicializar con los parametros dados
        self._initialize_car(initial_x, initial_y, speed)
    
    def _initialize_car(self, x: int, y: int, speed: int):
        """Inicializa o reinicializa el auto con nuevos parametros"""
        self.rect.x = x
        self.rect.y = y
        self.movement_speed = speed
        
        # Elegir tipo basado en velocidad
        self.car_type = self._choose_car_type_by_speed(speed)
        
        # Ajustar velocidad de animacion
        self.animation_speed = ANIMATION_SPEED * (ANIMATION_SPEED_DIVISOR / max(speed, 8))
        
        # Resetear animacion
        self.animation_frame = 0
        self.animation_timer = 0
        
        # Cargar frames si no estan cacheados para este tipo
        if not self.animation_frames or getattr(self, '_cached_car_type', None) != self.car_type:
            self._load_animation_frames()
            self._cached_car_type = self.car_type
        
        self._update_sprite()
    
    def reset_for_reuse(self, x: int, y: int, speed: int):
        """Resetea el auto para reutilizacion desde el pool"""
        self._initialize_car(x, y, speed)
        self.active = True
    
    def _choose_car_type_by_speed(self, speed: int) -> str:
        """Autos rojos = mas rapidos, azules = mas lentos"""
        if speed >= CAR_SPEED_THRESHOLD_FAST:
            # Autos rapidos: 80% rojos
            return random.choices(
                ["Auto_rojo", "Auto_azul"], 
                weights=[FAST_CAR_RED_WEIGHT, FAST_CAR_BLUE_WEIGHT], 
                k=1
            )[0]
        elif speed <= CAR_SPEED_THRESHOLD_SLOW:
            # Autos lentos: 80% azules  
            return random.choices(
                ["Auto_azul", "Auto_rojo"], 
                weights=[SLOW_CAR_BLUE_WEIGHT, SLOW_CAR_RED_WEIGHT], 
                k=1
            )[0]
        else:
            # Velocidad media: 50/50
            return random.choice(self.CAR_TYPES)
    
    def _load_animation_frames(self):
        """Carga los frames de animacion"""
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
        """Actualiza el sprite actual - optimizado para evitar calculos innecesarios"""
        if self.animation_frames:
            frame_index = int(self.animation_frame) % len(self.animation_frames)
            new_sprite = self.animation_frames[frame_index]
            
            # Solo actualizar si el sprite cambio
            if self.current_sprite != new_sprite:
                self.current_sprite = new_sprite
                self.image = self.current_sprite
    
    def update(self, delta_time: float = 1/60):
        """Actualiza posicion y animacion - solo si esta activo"""
        if not self.active:
            return
            
        # Movimiento horizontal
        self.rect.x -= self.movement_speed
        
        # Animacion
        self.animation_timer += delta_time
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            old_frame = self.animation_frame
            self.animation_frame = (self.animation_frame + 1) % len(self.animation_frames)
            
            # Solo actualizar sprite si el frame cambio
            if old_frame != self.animation_frame:
                self._update_sprite()
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el auto - solo si esta activo"""
        if not self.active:
            return
            
        if self.current_sprite:
            screen.blit(self.current_sprite, self.rect)
        else:
            # Fallback
            color = (255, 50, 50) if self.car_type == "Auto_rojo" else (50, 50, 255)
            pygame.draw.rect(screen, color, self.rect)
    
    def get_position(self) -> tuple:
        """Retorna posicion actual"""
        return (self.rect.x, self.rect.y)
    
    def get_speed(self) -> int:
        """Retorna velocidad actual"""
        return self.movement_speed
    
    def set_speed(self, new_speed: int):
        """Cambia velocidad y reajusta animacion"""
        self.movement_speed = max(1, new_speed)
        # Reajustar velocidad de animacion
        self.animation_speed = ANIMATION_SPEED * (ANIMATION_SPEED_DIVISOR / max(new_speed, 8))