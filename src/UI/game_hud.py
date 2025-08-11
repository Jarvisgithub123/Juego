import pygame
from src.Constantes import *


#TODO: Añadir iconos
#TODO: Mejorar interfaz
class GameHUD:
    """Interfaz de usuario del juego (HUD)"""
    
    def __init__(self, resource_manager):
        self.resource_manager = resource_manager
        
        # Crear textos estaticos
        font_instructions = self.resource_manager.get_font('instrucciones')
        if font_instructions:
            self.instructions_text = font_instructions.render(
                "Usa la barra espaciadora para saltar", True, COLOR_BLANCO)
            self.instructions_rect = self.instructions_text.get_rect()
            self.instructions_rect.topleft = (10, 10)
            
            # Configurar fondo de instrucciones
            padding = 10
            self.instructions_bg = pygame.Rect(
                self.instructions_rect.left - padding,
                self.instructions_rect.top - padding,
                self.instructions_rect.width + 2 * padding,
                self.instructions_rect.height + 2 * padding
            )
    
    def draw(self, screen, current_energy, max_energy, km_remaining):
        """Dibuja todos los elementos del HUD"""
        self._draw_instructions(screen)
        self._draw_energy_bar(screen, current_energy, max_energy)
        self._draw_km_counter(screen, km_remaining)
    
    def _draw_instructions(self, screen):
        """Dibuja las instrucciones en pantalla"""
        if hasattr(self, 'instructions_bg'):
            pygame.draw.rect(screen, COLOR_INSTRUCCION_FONDO, self.instructions_bg)
            screen.blit(self.instructions_text, self.instructions_rect)
    
    def _draw_energy_bar(self, screen, current_energy, max_energy):
        """Dibuja la barra de energía en la parte superior derecha"""
        percentage = (current_energy / max_energy) * 100
        
        # Configuracion de la barra
        bar_width = 200
        bar_height = 20
        bar_x = PANTALLA_ANCHO - bar_width - 20
        bar_y = 20
        
        # Dibujar fondo de la barra
        pygame.draw.rect(screen, COLOR_BARRA_FONDO, (bar_x, bar_y, bar_width, bar_height))
        
        # Calcular ancho segun energía restante
        energy_width = int((current_energy / max_energy) * bar_width)
        
        if percentage > 60:
            energy_color = COLOR_BARRA_ENERGIA
        elif percentage > 30:
            energy_color = COLOR_AMARILLO
        else:
            energy_color = COLOR_ROJO
        
        # Dibujar barra de energía
        if energy_width > 0:
            pygame.draw.rect(screen, energy_color, (bar_x, bar_y, energy_width, bar_height))
        pygame.draw.rect(screen, COLOR_BLANCO, (bar_x, bar_y, bar_width, bar_height), 2)
        
        font_hud = self.resource_manager.get_font('hud')
        if font_hud:
            energy_text = font_hud.render(f"Energía: {percentage:.0f}%", True, COLOR_BLANCO)
            screen.blit(energy_text, (bar_x, bar_y - 25))
    
    def _draw_km_counter(self, screen, km_remaining):
        """Dibuja el contador de kilometros en la parte superior izquierda"""
        counter_x = 20
        counter_y = 60
        
        # Crear texto
        font_hud = self.resource_manager.get_font('hud')
        if font_hud:
            km_text = font_hud.render(f"Kilometros restantes: {km_remaining:.2f} km", True, COLOR_AMARILLO)
            
            # Crear fondo para el texto
            text_rect = km_text.get_rect()
            text_rect.topleft = (counter_x, counter_y)
            
            bg_counter = pygame.Rect(text_rect.left - 5, text_rect.top - 5,
                                   text_rect.width + 10, text_rect.height + 10)
            pygame.draw.rect(screen, COLOR_INSTRUCCION_FONDO, bg_counter)
      
            screen.blit(km_text, (counter_x, counter_y))