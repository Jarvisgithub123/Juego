import pygame
from src.Constantes import *

class Camera:
    """
    Sistema de cámara simple que mantiene al jugador en su posición original
    
    CONCEPTO CLAVE:
    - Los objetos tienen POSICIÓN MUNDIAL (donde realmente están)
    - La cámara solo afecta donde se DIBUJAN en pantalla
    - La lógica del juego (colisiones, spawn, etc.) usa posiciones mundiales
    """
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Offset de la cámara (cuánto se ha movido el "ojo" de la cámara)
        self.x = 0  # Posición X de la cámara en el mundo
        self.y = 0  # Posición Y de la cámara en el mundo
        
        # Posición original del jugador en pantalla (donde debería aparecer visualmente)
        self.player_original_x = 100  
        
        # Configuración de suavizado
        self.follow_speed = 8.0
        
    def update(self, dt, player_rect):
        """
        Actualiza la cámara para mantener al jugador en su posición visual original
        
        LÓGICA:
        1. El jugador debería aparecer en x=100 en pantalla
        2. Si el jugador está en posición mundial x=150, la cámara debe moverse +50
        3. Así el jugador se dibuja en 150-50=100 (su posición visual ideal)
        """
        # Calcular cuánto se ha desviado el jugador de su posición original
        player_deviation = player_rect.x - self.player_original_x
        
        # Solo mover la cámara si el jugador se alejó de su posición original
        if abs(player_deviation) > 10:  # Pequeño margen para evitar jitter
            # La cámara debe compensar la desviación del jugador
            target_camera_x = player_deviation
            
            # Suavizar el movimiento hacia el target
            self.x += (target_camera_x - self.x) * self.follow_speed * dt
        else:
            # Volver suavemente a la posición original si el jugador está cerca
            self.x += (0 - self.x) * self.follow_speed * dt
    
    def apply_to_rect(self, rect):
        """Aplica la transformación de cámara a un rect"""
        return pygame.Rect(rect.x - self.x, rect.y - self.y, rect.width, rect.height)
    
    def apply_to_pos(self, x, y):
        """Aplica la transformación de cámara a una posición"""
        return (x - self.x, y - self.y)
    
    def get_offset(self):
        """Obtiene el offset actual de la cámara"""
        return (self.x, self.y)