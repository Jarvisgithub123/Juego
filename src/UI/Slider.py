import pygame
from src.Constantes import *



class Slider:
    def __init__(self, pos: tuple, size: tuple, min_value, max_value, initial_value: float, resource_manager, callback=None):
        self.pos = pos
        self.size = size
        
        self.slider_left_pos = self.pos[0] - size[0] // 2
        self.slider_right_pos = self.pos[0] + size[0] // 2
        self.slider_top_pos = self.pos[1] - size[1] // 2
        
        self.min_value = min_value
        self.max_value = max_value
        self.callback = callback  # NUEVO: Guardar callback
        
        # CORREGIR: Cálculo correcto de posición inicial
        self.current_value = initial_value
        normalized_value = (initial_value - min_value) / (max_value - min_value)
        button_x_offset = normalized_value * size[0]
        
        self.container_rect = pygame.Rect(self.slider_left_pos, self.slider_top_pos, self.size[0], self.size[1])
        self.button_rect = pygame.Rect(self.slider_left_pos + button_x_offset - 5, self.slider_top_pos, 10, self.size[1])
    
    def draw(self, screen):
        """Dibuja el slider en la pantalla con estilo pixel art que sigue la interfaz del juego"""
        # Fondo del slider (track) - estilo pixel art con bordes
        track_rect = pygame.Rect(self.slider_left_pos, self.slider_top_pos + self.size[1]//3, 
                                self.size[0], self.size[1]//3)
        
        # Sombra del track (efecto 3D pixel art)
        shadow_rect = pygame.Rect(track_rect.x + 2, track_rect.y + 2, track_rect.width, track_rect.height)
        pygame.draw.rect(screen, (100, 100, 100), shadow_rect)
        
        # Track principal con gradiente simple
        pygame.draw.rect(screen, (200, 200, 200), track_rect)
        pygame.draw.rect(screen, COLOR_BLANCO, track_rect, 2)
        
        # Parte llena del slider (progreso) - en azul como los botones del juego
        button_center = self.button_rect.x + 5
        progress_width = max(0, button_center - self.slider_left_pos)
        if progress_width > 0:
            progress_rect = pygame.Rect(self.slider_left_pos, track_rect.y, 
                                      progress_width, track_rect.height)
            pygame.draw.rect(screen, (70, 130, 255), progress_rect)  # Azul del juego
            pygame.draw.rect(screen, (100, 160, 255), progress_rect, 1)  # Borde más claro
        
        # Botón del slider - estilo 3D pixel art
        button_size = self.size[1]
        button_x = self.button_rect.x + 5 - button_size//2
        button_y = self.slider_top_pos
        
        # Sombra del botón
        shadow_button = pygame.Rect(button_x + 2, button_y + 2, button_size, button_size)
        pygame.draw.rect(screen, (80, 80, 80), shadow_button)
        
        # Botón principal
        main_button = pygame.Rect(button_x, button_y, button_size, button_size)
        pygame.draw.rect(screen, COLOR_AMARILLO, main_button)
        
        # Highlight del botón (efecto 3D)
        highlight_rect = pygame.Rect(button_x + 2, button_y + 2, button_size - 4, button_size - 4)
        pygame.draw.rect(screen, (255, 255, 150), highlight_rect, 2)
        
        # Borde exterior del botón
        pygame.draw.rect(screen, COLOR_BLANCO, main_button, 2)
    
    def move_slider(self, mouse_x):
        """Mueve el slider y ejecuta callback si existe"""
        # Calcular donde debería estar el centro del botón
        if mouse_x <= self.slider_left_pos:
            # Centro en el extremo izquierdo
            button_center = self.slider_left_pos
        elif mouse_x >= self.slider_right_pos:
            # Centro en el extremo derecho  
            button_center = self.slider_right_pos
        else:
            # Centro donde está el mouse
            button_center = mouse_x
        
        # Posicionar el botón (esquina izquierda = centro - 5)
        self.button_rect.x = button_center - 5
        
        # Ejecutar callback si existe
        if hasattr(self, 'callback') and self.callback:
            new_value = self.get_value()
            if not hasattr(self, 'current_value'):
                self.current_value = new_value
            if abs(new_value - self.current_value) > 0.01:
                self.current_value = new_value
                self.callback(new_value)

    def get_value(self):
        """Obtiene el valor actual del slider"""
        # El centro del botón es button_rect.x + 5
        button_center = self.button_rect.x + 5
        
        # Calcular posición relativa (0 a size[0])
        relative_pos = button_center - self.slider_left_pos
        
        percentage = relative_pos / self.size[0]
        
        # Permitir que llegue exactamente a 1.0 cuando esté en el extremo derecho
        if percentage >= 0.99:
            percentage = 1.0
        elif percentage <= 0.01:
            percentage = 0.0
        else:
            percentage = max(0.0, min(1.0, percentage))
        
        # Convertir a valor final
        value = self.min_value + (self.max_value - self.min_value) * percentage
        
        return value
