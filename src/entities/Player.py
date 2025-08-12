import pygame
from typing import Callable, List, Optional
from src.Constantes import *

#TODO: Añadir animaciones: Dash
#TODO: Añadir particulas

# Constantes de movimiento del jugador
JUMP_STRENGTH = -17
DASH_SPEED = 15
DASH_DURATION_SECONDS = 0.2
DASH_COOLDOWN_SECONDS = 0.5
RETURN_TO_ORIGIN_SPEED = 5.0
MAX_DISTANCE_FROM_ORIGIN = 200
POSITION_TOLERANCE = 10 

class Player:
    """Jugador UAIBOT que puede saltar y hacer dash para esquivar autos"""
    
    def __init__(self, initial_x: int, initial_y: int, gravity: float, resource_manager):
        """
        Args:
            initial_x: Posicion inicial X
            initial_y: Posicion inicial Y  
            gravity: Fuerza de gravedad a aplicar
            resource_manager: Gestor de recursos para sprites y sonidos
        """
        
        self.rect = pygame.Rect(initial_x, initial_y, 32, 32)
        self.resource_manager = resource_manager
        
        # Posicion original para volver tras el dash
        self.original_position_x = initial_x
        self.original_position_y = initial_y
        
        # Variables de fisica y movimiento
        self._init_physics(gravity)
        
        # Sistema de animacion
        self._init_animation_system()
        
        # Sistema de dash
        self._init_dash_system()
        
        # Cargar sprites y preparar animacion
        self._load_animation_frames()
        self.current_sprite = None
        self._update_sprite()
        
    def _init_physics(self, gravity: float):
        """Inicializa las variables de fisica del jugador"""
        self.velocity_y = 0
        self.gravity = gravity
        self.jump_strength = JUMP_STRENGTH
        self.on_ground = True
        
    def _init_animation_system(self):
        """Inicializa el sistema de animacion del sprite"""
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.08
        self.animation_frames: List[pygame.Surface] = []
    
    def _init_dash_system(self):
        """Inicializa el sistema de dash del jugador"""
        self.dash_speed = DASH_SPEED
        self.dash_duration = DASH_DURATION_SECONDS
        self.dash_timer = 0
        self.is_dashing = False
        self.dash_cooldown = DASH_COOLDOWN_SECONDS
        self.dash_cooldown_timer = 0
        
        # Sistema de retorno a posicion original
        self.return_to_origin_speed = RETURN_TO_ORIGIN_SPEED
        self.max_distance_from_origin = MAX_DISTANCE_FROM_ORIGIN
        
    def _load_animation_frames(self):
        """Carga los frames de animacion del jugador desde el spritesheet"""
        spritesheet = self.resource_manager.get_spritesheet("UIAbot_walk")
        
        if spritesheet:
            self.animation_frames = self.resource_manager.get_animation_frames(
                "UIAbot_walk", 0, 4, 0
            )
        
        # Si no hay frames disponibles, crear placeholder
        if not self.animation_frames:
            placeholder = self.resource_manager.create_fallback_image(
                (32, 32), (0, 100, 255)
            )
            self.animation_frames = [placeholder]
    
    def jump(self):
        """Hace saltar al jugador si esta en el suelo"""
        if self.on_ground:
            self.velocity_y = self.jump_strength
            self.on_ground = False
            self.resource_manager.play_sound("salto")
    
    def dash(self, energy_callback: Callable[[float], bool]) -> bool:
        """
        Ejecuta dash si hay energia y no esta en cooldown
        
        Args:
            energy_callback: Funcion para consumir energia
            
        Returns:
            True si el dash fue exitoso, False si no se pudo hacer
        """
        if self._can_perform_dash() and energy_callback(DASH_ENERGIA_COSTO):
            self._start_dash()
            return True
        return False
    
    def _can_perform_dash(self) -> bool:
        """Verifica si el jugador puede hacer dash"""
        return (not self.is_dashing and 
                self.dash_cooldown_timer <= 0)
    
    def _start_dash(self):
        """Inicia el dash del jugador"""
        self.is_dashing = True
        self.dash_timer = self.dash_duration
        self.dash_cooldown_timer = self.dash_cooldown
        self.resource_manager.play_sound("salto")
    
    def can_dash(self) -> bool:
        """Verifica si el jugador puede hacer dash (metodo publico)"""
        return self._can_perform_dash()
        
    def update(self, delta_time: float = 1/60):
        """
        Actualiza la fisica y animacion del jugador
        
        Args:
            delta_time: Tiempo transcurrido desde el ultimo frame
        """
        self._update_cooldowns(delta_time)
        self._update_dash_movement(delta_time)
        self._update_return_to_origin(delta_time)
        self._update_vertical_physics(delta_time)
        self._update_animation_if_grounded(delta_time)
    
    def _update_cooldowns(self, delta_time: float):
        """Actualiza los timers de cooldown"""
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= delta_time
    
    def _update_dash_movement(self, delta_time: float):
        """Maneja el movimiento durante el dash"""
        if self.is_dashing:
            self.dash_timer -= delta_time
            # Mover al jugador hacia adelante durante el dash
            self.rect.x += self.dash_speed
            
            if self.dash_timer <= 0:
                self.is_dashing = False
    
    def _update_return_to_origin(self, delta_time: float):
        """Maneja el retorno gradual a la posicion original"""
        if not self.is_dashing:
            distance_from_origin = self.rect.x - self.original_position_x
            
            # Solo retornar si se alejo demasiado de la posicion original
            if abs(distance_from_origin) > POSITION_TOLERANCE:
                self._move_towards_origin(distance_from_origin)
    
    def _move_towards_origin(self, distance_from_origin: float):
        """Mueve al jugador gradualmente hacia su posicion original"""
        if distance_from_origin > 0:
            # Esta muy a la derecha, mover hacia la izquierda
            return_speed = min(self.return_to_origin_speed, distance_from_origin)
            self.rect.x -= return_speed
        else:
            # Esta muy a la izquierda, mover hacia la derecha
            return_speed = min(self.return_to_origin_speed, abs(distance_from_origin))
            self.rect.x += return_speed
    
    def _update_vertical_physics(self, delta_time: float):
        """Actualiza la fisica vertical (gravedad y colision con suelo)"""
        # Aplicar gravedad
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
        
        # Verificar colision con el suelo
        if self.rect.y >= self.original_position_y:
            self._land_on_ground()
    
    def _land_on_ground(self):
        """Maneja el aterrizaje del jugador en el suelo"""
        self.rect.y = self.original_position_y
        self.velocity_y = 0
        self.on_ground = True
    
    def _update_animation_if_grounded(self, delta_time: float):
        """Actualiza la animacion solo si esta en el suelo"""
        if self.on_ground:
            self._update_animation(delta_time)
    
    def _update_sprite(self):
        """Actualiza el sprite actual basado en el frame de animacion"""
        if self.animation_frames:
            frame_index = int(self.animation_frame) % len(self.animation_frames)
            self.current_sprite = self.animation_frames[frame_index]
    
    def _update_animation(self, delta_time: float):
        """Actualiza el frame de animacion actual"""
        self.animation_timer += delta_time
        
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % len(self.animation_frames)
            self._update_sprite()