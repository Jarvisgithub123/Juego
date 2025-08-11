import pygame
from src.Constantes import *

class Player:
    def __init__(self, x, y, gravity, resource_manager):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.resource_manager = resource_manager
        
        # Variables de física
        self.vel_y = 0
        self.gravity = gravity 
        self.jump_strength = -17
        self.on_ground = True
        self.original_y = y
        self.original_x = x  
        
        # Variables de animación
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.08
        self.animation_frames = []
        
        self.dash_speed = 15
        self.dash_duration = 0.2
        self.dash_timer = 0
        self.is_dashing = False
        self.dash_cooldown = 0.5
        self.dash_cooldown_timer = 0
        
        # Variable para controlar el retorno gradual a posición original
        self.return_to_origin_speed = 5.0  
        self.max_distance_from_origin = 200  
        
        # Cargar animación y sprite actual
        self._load_animation_frames()
        self.current_sprite = None
        self._update_sprite()
        
    def dash(self, energy_callback):
        """Ejecuta dash si hay energía y no está en cooldown"""
        if (not self.is_dashing and 
            self.dash_cooldown_timer <= 0 and 
            energy_callback(DASH_ENERGIA_COSTO)):
            
            self.is_dashing = True
            self.dash_timer = self.dash_duration
            self.dash_cooldown_timer = self.dash_cooldown
            self.resource_manager.play_sound("salto")
            return True
        return False
        
    def _load_animation_frames(self):
        """Carga los frames de animación del jugador"""
        spritesheet = self.resource_manager.get_spritesheet("UIAbot_walk")
        
        if spritesheet:
            self.animation_frames = self.resource_manager.get_animation_frames("UIAbot_walk", 0, 4, 0)
        
        # Fallback si no hay frames
        if not self.animation_frames:
            placeholder = self.resource_manager.create_fallback_image((32, 32), (0, 100, 255))
            self.animation_frames = [placeholder]
    
    def jump(self):
        """Hace saltar al jugador si está en el suelo"""
        if self.on_ground:
            self.vel_y = self.jump_strength
            self.on_ground = False
            self.resource_manager.play_sound("salto")
    
    def _update_sprite(self):
        """Actualiza el sprite actual basado en el frame de animación"""
        if self.animation_frames:
            frame_index = int(self.animation_frame) % len(self.animation_frames)
            self.current_sprite = self.animation_frames[frame_index]
    
    def update(self, dt=1/60):
        """Actualiza la física y animación del jugador"""
        # Actualizar cooldowns
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= dt
        
        # Manejar dash - RESTAURADO CON MEJORAS
        if self.is_dashing:
            self.dash_timer -= dt
            # SÍ movemos al jugador durante el dash
            self.rect.x += self.dash_speed
            
            if self.dash_timer <= 0:
                self.is_dashing = False
        
        # NUEVA LÓGICA: Retorno gradual a la posición original cuando no hace dash
        if not self.is_dashing:
            distance_from_origin = self.rect.x - self.original_x
            
            # Solo retornar si se alejó demasiado
            if abs(distance_from_origin) > 10:  # Pequeño margen
                if distance_from_origin > 0:
                    # Está muy a la derecha, mover hacia la izquierda
                    return_speed = min(self.return_to_origin_speed, distance_from_origin)
                    self.rect.x -= return_speed
                else:
                    # Está muy a la izquierda, mover hacia la derecha
                    return_speed = min(self.return_to_origin_speed, abs(distance_from_origin))
                    self.rect.x += return_speed
        
        # Física vertical (sin cambios)
        self.vel_y += self.gravity
        self.rect.y += self.vel_y
        
        # Verificar colisión con el suelo
        if self.rect.y >= self.original_y:
            self.rect.y = self.original_y
            self.vel_y = 0
            self.on_ground = True
            
        # Animación (solo si está en el suelo)
        if self.on_ground:
            self._update_animation(dt)
            
    def _update_animation(self, dt):
        """Actualiza el frame de animación actual"""
        self.animation_timer += dt
        
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % len(self.animation_frames)
            self._update_sprite()
    
    def can_dash(self):
        """Verifica si el jugador puede hacer dash"""
        return not self.is_dashing and self.dash_cooldown_timer <= 0