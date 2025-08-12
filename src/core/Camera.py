import pygame
from typing import Tuple
from src.Constantes import *

# Constantes de la camara
DEFAULT_PLAYER_SCREEN_X = 100  # Donde aparece el jugador visualmente
DEFAULT_FOLLOW_SPEED = 8.0
MINIMUM_DEVIATION_THRESHOLD = 10  # Minimo movimiento antes de seguir

class Camera:
    """Sistema de camara que sigue al jugador suavemente"""
    
    def __init__(self, screen_width: int, screen_height: int):
        """
        Inicializa la camara del juego
        
        Args:
            screen_width: Ancho de la pantalla
            screen_height: Alto de la pantalla
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Posicion actual de la camara en el mundo
        self.world_position_x = 0  
        self.world_position_y = 0  
        
        # Donde deberia aparecer el jugador visualmente en pantalla
        self.player_visual_x = DEFAULT_PLAYER_SCREEN_X  
        
        # Configuracion de suavizado del movimiento
        self.follow_speed = DEFAULT_FOLLOW_SPEED
        
    def update(self, delta_time: float, player_rect: pygame.Rect):
        """
        Actualiza la posicion de la camara para seguir al jugador
        
        Args:
            delta_time: Tiempo transcurrido desde el ultimo frame
            player_rect: Rectangulo del jugador a seguir
        """
        player_deviation = self._calculate_player_deviation(player_rect)
        
        if self._should_follow_player(player_deviation):
            self._follow_player_smoothly(player_deviation, delta_time)
        else:
            self._return_to_center_smoothly(delta_time)
    
    def _calculate_player_deviation(self, player_rect: pygame.Rect) -> float:
        """Calcula cuanto se desvio el jugador de su posicion visual ideal"""
        return player_rect.x - self.player_visual_x
    
    def _should_follow_player(self, deviation: float) -> bool:
        """Determina si la camara debe seguir al jugador basado en su desviacion"""
        return abs(deviation) > MINIMUM_DEVIATION_THRESHOLD
    
    def _follow_player_smoothly(self, deviation: float, delta_time: float):
        """Sigue al jugador suavemente hacia su nueva posicion"""
        target_camera_x = deviation
        camera_movement = (target_camera_x - self.world_position_x) * self.follow_speed * delta_time
        self.world_position_x += camera_movement
    
    def _return_to_center_smoothly(self, delta_time: float):
        """Retorna la camara suavemente al centro"""
        center_movement = (0 - self.world_position_x) * self.follow_speed * delta_time
        self.world_position_x += center_movement
    
    def apply_to_rect(self, rect: pygame.Rect) -> pygame.Rect:
        """
        Aplica la transformacion de camara a un rectangulo
        
        Args:
            rect: Rectangulo en coordenadas del mundo
            
        Returns:
            Rectangulo transformado a coordenadas de pantalla
        """
        return pygame.Rect(
            rect.x - self.world_position_x, 
            rect.y - self.world_position_y, 
            rect.width, 
            rect.height
        )
    
    def apply_to_position(self, world_x: float, world_y: float) -> Tuple[float, float]:
        """
        Aplica la transformacion de camara a una posicion
        
        Args:
            world_x: Posicion X en el mundo
            world_y: Posicion Y en el mundo
            
        Returns:
            Tupla con posicion transformada a coordenadas de pantalla
        """
        screen_x = world_x - self.world_position_x
        screen_y = world_y - self.world_position_y
        return (screen_x, screen_y)
    
    def get_offset(self) -> Tuple[float, float]:
        """
        Obtiene el offset actual de la camara
        
        Returns:
            Tupla con el offset (x, y) de la camara
        """
        return (self.world_position_x, self.world_position_y)
    
    def get_world_bounds(self) -> pygame.Rect:
        """
        Obtiene los limites del mundo visible por la camara
        
        Returns:
            Rectangulo que representa el area visible en coordenadas del mundo
        """
        return pygame.Rect(
            self.world_position_x,
            self.world_position_y,
            self.screen_width,
            self.screen_height
        )
    
    def is_visible(self, world_rect: pygame.Rect) -> bool:
        """
        Verifica si un rectangulo esta visible en la camara
        
        Args:
            world_rect: Rectangulo en coordenadas del mundo
            
        Returns:
            True si el rectangulo esta visible, False caso contrario
        """
        camera_bounds = self.get_world_bounds()
        return world_rect.colliderect(camera_bounds)
    
    def set_follow_speed(self, new_speed: float):
        """
        Cambia la velocidad de seguimiento de la camara
        
        Args:
            new_speed: Nueva velocidad de seguimiento
        """
        self.follow_speed = max(0.1, min(new_speed, 20.0))  # Entre 0.1 y 20
    
    def set_player_visual_position(self, visual_x: int):
        """
        Cambia donde aparece visualmente el jugador en pantalla
        
        Args:
            visual_x: Nueva posicion X visual del jugador
        """
        self.player_visual_x = max(50, min(visual_x, self.screen_width - 50))
    
    # Propiedades para compatibilidad con codigo existente
    @property
    def x(self) -> float:
        """Alias para world_position_x"""
        return self.world_position_x
    
    @x.setter 
    def x(self, value: float):
        """Setter para world_position_x"""
        self.world_position_x = value
    
    @property
    def y(self) -> float:
        """Alias para world_position_y"""
        return self.world_position_y
    
    @y.setter
    def y(self, value: float):
        """Setter para world_position_y"""
        self.world_position_y = value