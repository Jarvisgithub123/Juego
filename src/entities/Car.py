import pygame
from src.Constantes import *

class Car(pygame.sprite.Sprite):
    def __init__(self, x, y, resource_manager, speed=15, width=126, height=86):  # VELOCIDAD AUMENTADA
        super().__init__()
        self.resource_manager = resource_manager
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.width = width
        self.height = height
        
        # Variables de animación - MÁS RÁPIDAS
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.1   # Animación más rápida
        self.animation_frames = []
        
        # Cargar frames de animación
        self._load_animation_frames()
        
        # Sprite actual
        self.current_sprite = None
        self._update_sprite()
    
    def _load_animation_frames(self):
        """Carga los frames de animación del auto"""
        spritesheet = self.resource_manager.get_spritesheet("Auto_azul")
        
        if spritesheet:
            # Cargar frames del auto (asumiendo fila 0, columnas 0-2)
            self.animation_frames = self.resource_manager.get_animation_frames("Auto_azul", 0, 2, 0)
        
        # Si no hay frames, usar placeholder
        if not self.animation_frames:
            placeholder = self.resource_manager.create_fallback_image((self.width, self.height), (0, 0, 255))
            self.animation_frames = [placeholder]
            print("Usando placeholder para el auto")
    
    def _update_sprite(self):
        """Actualiza el sprite actual basado en el frame de animación"""
        if self.animation_frames:
            frame_index = int(self.animation_frame) % len(self.animation_frames)
            self.current_sprite = self.animation_frames[frame_index]
            # Actualizar la imagen para compatibilidad con pygame.sprite.Sprite
            self.image = self.current_sprite
    
    def _update_animation(self, dt):
        """Actualiza el frame de animación actual"""
        self.animation_timer += dt
        
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % len(self.animation_frames)
            self._update_sprite()
    
    def update(self, dt=1/60):
        """Actualiza la posición y animación del auto"""
        # Movimiento
        self.rect.x -= self.speed
        
        # Si sale de la pantalla, reiniciar posición
        if self.rect.right < 0:
            self.rect.left = PANTALLA_ANCHO
        
        # Actualizar animación
        self._update_animation(dt)
    
    def draw(self, screen):
        """Dibuja el auto en la pantalla"""
        if self.current_sprite:
            screen.blit(self.current_sprite, self.rect)
        else:
            # Fallback: dibujar rectángulo
            pygame.draw.rect(screen, (0, 0, 255), self.rect)