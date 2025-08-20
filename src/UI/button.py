import pygame
from src.Constantes import *

class Button:
    """Boton mejorado con efectos y sonidos"""
    
    def __init__(self, text: str, x: int, y: int, width: int, height: int, 
                 resource_manager, action=None):   
        """Inicializa el botón con tamaño, posición, colores, efectos y acción"""

        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.action = action
        self.resource_manager = resource_manager
        
        # Colores y estados
        self.color = COLOR_PRIMARIO
        self.color_hover = COLOR_SECUNDARIO
        self.color_text = COLOR_TEXTO_EN_BOTON
        self.was_hovering = False
        self.is_pressed = False
        
        # Efectos del hover
        self.hover_scale = 1.0
        self.target_scale = 1.0
        self.scale_speed = 8.0
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Maneja los eventos del boton"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.is_pressed = True
                if self.action:
                    self.action()
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_pressed = False
        
        return False
    
    def update(self, dt: float):
        """Actualiza el estado del boton"""
        # --- Comprobar si el mouse está sobre el botón ---
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = self.rect.collidepoint(mouse_pos)
        
        # Reproducir sonido de hover
        if is_hovering and not self.was_hovering:
            self.resource_manager.play_sound("boton_hover")
        
        self.was_hovering = is_hovering
        
        # Actualizar escala para efecto hover
        self.target_scale = 1.05 if is_hovering else 1.0
        self.hover_scale += (self.target_scale - self.hover_scale) * self.scale_speed * dt
    
    def draw(self, surface: pygame.Surface):
        """Dibuja el boton"""
        # Calcular rectangulo escalado
        if self.hover_scale != 1.0:
            center = self.rect.center
            scaled_size = (int(self.rect.width * self.hover_scale), 
                          int(self.rect.height * self.hover_scale))
            draw_rect = pygame.Rect(0, 0, *scaled_size)
            draw_rect.center = center
        else:
            draw_rect = self.rect
        
        # Color actual
        current_color = self.color_hover if self.was_hovering else self.color
        if self.is_pressed:
            # Oscurecer si esta presionado
            current_color = tuple(max(0, c - 30) for c in current_color)
        
        # Dibujar boton
        pygame.draw.rect(surface, current_color, draw_rect, border_radius=8)
        
        # Dibujar texto
        font = self.resource_manager.get_font('boton')
        if font:
            text_surface = font.render(self.text, True, self.color_text)
            text_rect = text_surface.get_rect(center=draw_rect.center)
            surface.blit(text_surface, text_rect)