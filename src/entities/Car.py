import pygame
from typing import List, Optional
from src.Constantes import *

#TODO: Añadir diferentes tipos de vehiculos

# Constantes para los autos
DEFAULT_CAR_WIDTH = 126
DEFAULT_CAR_HEIGHT = 86
DEFAULT_CAR_SPEED = 15
ANIMATION_SPEED = 0.1
SPRITESHEET_START_COLUMN = 0
SPRITESHEET_END_COLUMN = 2
SPRITESHEET_ROW = 0

class Car(pygame.sprite.Sprite):
    """Auto enemigo que se mueve hacia el jugador"""
    
    def __init__(self, initial_x: int, initial_y: int, resource_manager, 
                 speed: int = DEFAULT_CAR_SPEED, 
                 width: int = DEFAULT_CAR_WIDTH, 
                 height: int = DEFAULT_CAR_HEIGHT):
        """
        Inicializa un auto enemigo
        
        Args:
            initial_x: Posicion inicial X
            initial_y: Posicion inicial Y
            resource_manager: Gestor de recursos para sprites
            speed: Velocidad de movimiento del auto
            width: Ancho del auto
            height: Alto del auto
        """
        super().__init__()
        self.resource_manager = resource_manager
        self.rect = pygame.Rect(initial_x, initial_y, width, height)
        self.movement_speed = speed
        self.width = width
        self.height = height
        
        # Sistema de animacion del auto
        self._init_animation_system()
        
        # Cargar frames de animacion
        self._load_animation_frames()
        
        # Configurar sprite inicial
        self.current_sprite: Optional[pygame.Surface] = None
        self._update_sprite()
    
    def _init_animation_system(self):
        """Inicializa las variables del sistema de animacion"""
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = ANIMATION_SPEED
        self.animation_frames: List[pygame.Surface] = []
    
    def _load_animation_frames(self):
        """Carga los frames de animacion del auto desde el spritesheet"""
        spritesheet = self.resource_manager.get_spritesheet("Auto_azul")
        
        if spritesheet:
            # Cargar frames del auto desde el spritesheet
            self.animation_frames = self.resource_manager.get_animation_frames(
                "Auto_azul", 
                SPRITESHEET_START_COLUMN, 
                SPRITESHEET_END_COLUMN, 
                SPRITESHEET_ROW
            )
        
        # Si no hay frames, usar imagen placeholder
        if not self.animation_frames:
            placeholder = self._create_placeholder_sprite()
            self.animation_frames = [placeholder]
            print("Usando placeholder para el auto")
    
    def _create_placeholder_sprite(self) -> pygame.Surface:
        """Crea un sprite placeholder azul si no hay spritesheet"""
        return self.resource_manager.create_fallback_image(
            (self.width, self.height), (0, 0, 255)
        )
    
    def _update_sprite(self):
        """Actualiza el sprite actual basado en el frame de animacion"""
        if self.animation_frames:
            frame_index = int(self.animation_frame) % len(self.animation_frames)
            self.current_sprite = self.animation_frames[frame_index]
            # Actualizar la imagen para compatibilidad con pygame.sprite.Sprite
            self.image = self.current_sprite
    
    def update(self, delta_time: float = 1/60):
        """
        Actualiza la posicion y animacion del auto
        
        Args:
            delta_time: Tiempo transcurrido desde el ultimo frame
        """
        self._update_horizontal_movement()
        self._handle_screen_wrapping()
        self._update_animation(delta_time)
    
    def _update_horizontal_movement(self):
        """Actualiza el movimiento horizontal del auto"""
        self.rect.x -= self.movement_speed
    
    def _handle_screen_wrapping(self):
        """Reinicia la posicion del auto cuando sale de pantalla"""
        if self.rect.right < 0:
            self.rect.left = PANTALLA_ANCHO
    
    def _update_animation(self, delta_time: float):
        """Actualiza el frame de animacion actual"""
        self.animation_timer += delta_time
        
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % len(self.animation_frames)
            self._update_sprite()
    
    def draw(self, screen: pygame.Surface):
        """
        Dibuja el auto en la pantalla
        
        Args:
            screen: Superficie donde dibujar
        """
        if self.current_sprite:
            screen.blit(self.current_sprite, self.rect)
        else:
            # Fallback: dibujar rectangulo azul
            pygame.draw.rect(screen, (0, 0, 255), self.rect)
    
    def get_position(self) -> tuple:
        """Retorna la posicion actual del auto como tupla (x, y)"""
        return (self.rect.x, self.rect.y)
    
    def get_speed(self) -> int:
        """Retorna la velocidad actual del auto"""
        return self.movement_speed
    
    def set_speed(self, new_speed: int):
        """
        Cambia la velocidad del auto
        
        Args:
            new_speed: Nueva velocidad a asignar
        """
        self.movement_speed = max(1, new_speed)  # Velocidad minima de 1