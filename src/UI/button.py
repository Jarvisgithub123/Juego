import pygame
from src.Constantes import *

class Button:    
    def __init__(self, text, x, y, width, height, resource_manager, callback=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.resource_manager = resource_manager
        self.callback = callback
        self.is_hovered = False
        self.hover_scale = 1.0
        self.target_scale = 1.0
        
        # Cache de texto
        self._text = text
        self._text_dirty = True
        self._normal_text_surface = None
        self._hover_text_surface = None
        self._normal_text_rect = None
        self._hover_text_rect = None
        
        # Pre-renderizar texto inicial
        self._update_text_cache()
    
    @property
    def text(self):
        """Getter para el texto"""
        return self._text
    
    @text.setter 
    def text(self, value):
        """Setter que marca el cache como dirty cuando cambia el texto"""
        if self._text != value:
            self._text = value
            self._text_dirty = True
    
    def _update_text_cache(self):
        """Actualiza el cache de texto solo cuando es necesario"""
        if not self._text_dirty:
            return
            
        font = self.resource_manager.get_font('boton')
        if font:
            # Renderizar texto normal
            self._normal_text_surface = font.render(self._text, True, COLOR_TEXTO_EN_BOTON)
            self._normal_text_rect = self._normal_text_surface.get_rect()
            
            # Renderizar texto hover (con color diferente si se desea)
            self._hover_text_surface = font.render(self._text, True, COLOR_AMARILLO)
            self._hover_text_rect = self._hover_text_surface.get_rect()
        
        self._text_dirty = False
    
    def handle_event(self, event):
        """Maneja los eventos del botón"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                    self.resource_manager.play_sound("boton_hover")
        
        elif event.type == pygame.MOUSEMOTION:
            # OPTIMIZACIÓN: Solo cambiar estado si es necesario
            was_hovered = self.is_hovered
            self.is_hovered = self.rect.collidepoint(event.pos)
            
            # Solo reproducir sonido cuando empieza el hover
            if self.is_hovered and not was_hovered:
                self.resource_manager.play_sound("boton_hover")
    
    def update(self, dt):
        """Actualiza la animación del botón"""
        # Actualizar cache si es necesario
        self._update_text_cache()
        
        # Animación de escala suave
        self.target_scale = 1.1 if self.is_hovered else 1.0
        scale_diff = self.target_scale - self.hover_scale
        self.hover_scale += scale_diff * 8 * dt  # Velocidad de animación
    
    def draw(self, screen):
        """Dibuja el botón con texto cacheado"""
        # Calcular tamaño y posición con escala
        scaled_width = int(self.rect.width * self.hover_scale)
        scaled_height = int(self.rect.height * self.hover_scale)
        
        #Reutilizar rect para el botón escalado
        if not hasattr(self, '_scaled_rect'):
            self._scaled_rect = pygame.Rect(0, 0, 0, 0)
        
        self._scaled_rect.width = scaled_width
        self._scaled_rect.height = scaled_height
        self._scaled_rect.center = self.rect.center
        
        # Dibujar fondo del botón
        color = COLOR_SECUNDARIO if self.is_hovered else COLOR_PRIMARIO
        pygame.draw.rect(screen, color, self._scaled_rect)
        pygame.draw.rect(screen, COLOR_BLANCO, self._scaled_rect, 2)
        
        # Dibujar texto cacheado
        if self.is_hovered and self._hover_text_surface:
            text_surface = self._hover_text_surface
            text_rect = self._hover_text_rect
        elif self._normal_text_surface:
            text_surface = self._normal_text_surface
            text_rect = self._normal_text_rect
        else:
            return  # No hay texto para mostrar
        
        # Centrar el texto en el botón escalado
        text_rect.center = self._scaled_rect.center
        screen.blit(text_surface, text_rect)