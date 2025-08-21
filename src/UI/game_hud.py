import pygame
from src.Constantes import *


#TODO: Añadir iconos
#TODO: Mejorar interfaz
class GameHUD:
    """Interfaz de usuario del juego (HUD)"""
    
    def __init__(self, resource_manager):
        self.resource_manager = resource_manager
        
        # Crear textos estaticos
        font_instrucciones = self.resource_manager.get_font('instrucciones')
        self.instructions = []
        if font_instrucciones:
            textos = [
                ("Presiona 'Espacio' para saltar", (20, 60)),
                ("Presiona 'Z' para dashear", (20,  90)),
                ("Presiona 'P' para pausar",(20,  120)),
            ]
            
            for texto, pos in textos:
                txt_surface = font_instrucciones.render(texto, True, COLOR_BLANCO)
                rect = txt_surface.get_rect(topleft=pos)
                self.instructions.append((txt_surface, rect))
    
    def draw(self, screen, current_energy, max_energy, km_remaining):
        """Dibuja todos los elementos del HUD"""
        self._draw_instructions(screen)
        self._draw_energy_bar(screen, current_energy, max_energy)
        self._draw_km_counter(screen, km_remaining)
    
    def _draw_instructions(self, screen):
        """Dibuja todas las instrucciones en pantalla"""
        for txt_surface, rect in self.instructions:
            # Dibujar fondo
            bg = pygame.Rect(rect.left - 5, rect.top - 5,rect.width + 10, rect.height + 10)
            pygame.draw.rect(screen, COLOR_INSTRUCCION_FONDO, bg)
            # Dibujar texto
            screen.blit(txt_surface, rect)
        
    def _draw_energy_bar(self, screen, current_energy, max_energy):
        """Dibuja la barra de energia en la parte superior derecha"""
        percentage = (current_energy / max_energy) * 100
        
        # Configuracion de la barra
        bar_width = 200
        bar_height = 20
        bar_x = PANTALLA_ANCHO - bar_width - 100
        bar_y = 50
    
        # Dibujar fondo de la barra
        pygame.draw.rect(screen, COLOR_BARRA_FONDO, (bar_x, bar_y, bar_width, bar_height))
        
        # Calcular ancho segun energia restante
        energy_width = int((current_energy / max_energy) * bar_width)
        
        if percentage > 60:
            energy_color = COLOR_BARRA_ENERGIA
        elif percentage > 30:
            energy_color = COLOR_AMARILLO
        else:
            energy_color = COLOR_ROJO
        
        # Dibujar barra de energia
        if energy_width > 0:
            pygame.draw.rect(screen, energy_color, (bar_x, bar_y, energy_width, bar_height))
        pygame.draw.rect(screen, COLOR_NEGRO, (bar_x, bar_y, bar_width, bar_height), 2)
        
        font_hud = self.resource_manager.get_font('hud')
        if font_hud:
            energy_text = font_hud.render(f"Energia: {percentage:.0f}%", True, COLOR_NEGRO)
            screen.blit(energy_text, (bar_x, bar_y - 25))
    
    def _draw_km_counter(self, screen, km_remaining):
        """Dibuja el contador de kilometros en la parte superior izquierda"""
        counter_x = 20
        counter_y = 30
        
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