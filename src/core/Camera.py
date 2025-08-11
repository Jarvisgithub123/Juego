import pygame
from src.Constantes import *

class Camera:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
     
        self.x = 0  
        self.y = 0  
        # Posición original del jugador en pantalla (donde debería aparecer visualmente)
        self.player_original_x = 100  
        
        # Configuración de suavizado
        self.follow_speed = 8.0
        
    def update(self, dt, player_rect):
        player_deviation = player_rect.x - self.player_original_x
        
        if abs(player_deviation) > 10: 
            target_camera_x = player_deviation
            self.x += (target_camera_x - self.x) * self.follow_speed * dt
        else:
            self.x += (0 - self.x) * self.follow_speed * dt
    
    def apply_to_rect(self, rect):
        """Aplica la transformación de camara a un rect"""
        return pygame.Rect(rect.x - self.x, rect.y - self.y, rect.width, rect.height)
    
    def apply_to_pos(self, x, y):
        """Aplica la transformación de camara a una posición"""
        return (x - self.x, y - self.y)
    
    def get_offset(self):
        """Obtiene el offset actual de la camara"""
        return (self.x, self.y)