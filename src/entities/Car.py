import pygame
from src.Constantes import *

class Car(pygame.sprite.Sprite):
    def __init__(self, x, y, resource_manager, speed=7, width=126, height=86):
        super().__init__()
        self.resource_manager = resource_manager
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.width = width
        self.height = height
        
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.2 
        self.animation_frames = []
        
        self._load_animation_frames()
        
        self.current_sprite = None
        self._update_sprite()
    
    def _load_animation_frames(self):
        spritesheet = self.resource_manager.get_spritesheet("Auto_azul")
        
        if spritesheet:
            self.animation_frames = self.resource_manager.get_animation_frames("Auto_azul", 0, 3, 0)
        
        if not self.animation_frames:
            placeholder = self.resource_manager.create_fallback_image((self.width, self.height), (0, 0, 255))
            self.animation_frames = [placeholder]
            print("Usando placeholder para el auto")
    
    def _update_sprite(self):
        if self.animation_frames:
            frame_index = int(self.animation_frame) % len(self.animation_frames)
            self.current_sprite = self.animation_frames[frame_index]
            self.image = self.current_sprite
    
    def _update_animation(self, dt):
    
        self.animation_timer += dt
        
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % len(self.animation_frames)
            self._update_sprite()
    
    def update(self, dt=1/60):
        # Movimiento
        self.rect.x -= self.speed
        
        # Si sale de la pantalla, reiniciar posición
        if self.rect.right < 0:
            self.rect.left = PANTALLA_ANCHO
        
        # Actualizar animación
        self._update_animation(dt)
    
    def draw(self, screen):

        if self.current_sprite:
            screen.blit(self.current_sprite, self.rect)
        else:

            pygame.draw.rect(screen, (0, 0, 255), self.rect)