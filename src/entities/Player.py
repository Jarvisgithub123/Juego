import pygame
from src.Constantes import *

class Player:
    def __init__(self, x, y, gravity, resource_manager):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.resource_manager = resource_manager
        
        # Variables de física - MÁS DINÁMICAS
        self.vel_y = 0
        self.gravity = gravity * 2.5  # Gravedad más fuerte
        self.jump_strength = -12      # Salto más potente
        self.on_ground = True
        self.original_y = y
        
        # Variables de animación simplificadas - MÁS RÁPIDAS
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.08   # Animación más rápida
        self.animation_frames = []
        
        # Cargar frames de animación
        self._load_animation_frames()
        
        # Sprite actual
        self.current_sprite = None
        self._update_sprite()
    
    def _load_animation_frames(self):
        """Carga los frames de animación del jugador"""
        spritesheet = self.resource_manager.get_spritesheet("UIAbot_walk")
        
        if spritesheet:
            # Cargar frames de caminar (fila 0, columnas 0-4)
            self.animation_frames = self.resource_manager.get_animation_frames("UIAbot_walk", 0, 4, 0)
        
        # Si no hay frames, usar placeholder
        if not self.animation_frames:
            placeholder = self.resource_manager.create_fallback_image((32, 32), (0, 100, 255))
            self.animation_frames = [placeholder]
            print("Usando placeholder para el jugador")
    
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
        # Física
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
    
    def draw(self, screen):
        """Dibuja el jugador en la pantalla"""
        if self.current_sprite:
            # Centrar el sprite en el rect del jugador
            sprite_rect = self.current_sprite.get_rect()
            sprite_rect.center = self.rect.center
            screen.blit(self.current_sprite, sprite_rect)
        else:
            # Fallback: dibujar rectángulo
            pygame.draw.rect(screen, (0, 100, 255), self.rect)