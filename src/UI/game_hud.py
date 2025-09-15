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
                ("Presiona 'Espacio' para saltar", (20, 80)),
                ("Presiona 'Z' para dashear", (20,  130)),
                ("Presiona 'P' para pausar",(20,  180)),
            ]
            
            for texto, pos in textos:
                txt_surface = font_instrucciones.render(texto, True, COLOR_BLANCO)
                rect = txt_surface.get_rect(topleft=pos)
                self.instructions.append((txt_surface, rect))
        self.cached_instruction_texts = {}
        self.last_energy_text = None
        self.last_km_text = None
        
        # Configuración para el panel de distancias
        self.distances_panel_width = 300
        self.distances_panel_height = 150
        
        # Cache para superficies de texto (optimización)
        self.cached_text = {}
        
    def draw(self, screen: pygame.Surface, energy_remaining: float, 
             max_energy: float, km_remaining: float, distancias_personajes: dict = None):
        """Versión optimizada con cache de textos"""
        
        # Cache textos de instrucciones (no cambian)
        if not self.cached_instruction_texts:
            font = self.resource_manager.get_font('pequeña')
            if font:
                self.cached_instruction_texts['space'] = font.render(
                    "[ESPACIO] Saltar", True, COLOR_BLANCO)
                self.cached_instruction_texts['z'] = font.render(
                    "[Z] Dash", True, COLOR_BLANCO)
                self.cached_instruction_texts['c'] = font.render(
                    "[C] Cambiar personaje", True, COLOR_BLANCO)
        
        # Renderizar textos dinámicos solo si cambiaron
        font = self.resource_manager.get_font('hud')
        if font:
            # Energy text
            energy_str = f"Energia: {energy_remaining:.1f}s"
            if self.last_energy_text != energy_str:
                self.energy_surface = font.render(energy_str, True, COLOR_BLANCO)
                self.last_energy_text = energy_str
            
            # KM text
            km_str = f"Distancia: {km_remaining:.2f} km"
            if self.last_km_text != km_str:
                self.km_surface = font.render(km_str, True, COLOR_BLANCO)
                self.last_km_text = km_str
        
        # Dibujar todo (usando superficies cacheadas)
        self._draw_energy_bar(screen, energy_remaining, max_energy)
        screen.blit(self.energy_surface, (20, 20))
        screen.blit(self.km_surface, (20, 60))
        self._draw_cached_instructions(screen)
        
        if distancias_personajes:
            self._draw_distances_panel(screen, distancias_personajes)
    def _draw_cached_instructions(self, screen):
        """Dibuja instrucciones usando cache"""
        y_start = PANTALLA_ALTO - 120
        for i, key in enumerate(['space', 'z', 'c']):
            if key in self.cached_instruction_texts:
                screen.blit(self.cached_instruction_texts[key], 
                           (20, y_start + i * 30))
                
    def _draw_distances_panel(self, screen: pygame.Surface, distancias_personajes: dict):
        # Configuración del panel
        panel_width = 280
        panel_height = 180
        panel_x = PANTALLA_ANCHO - panel_width - 86
        panel_y = 100
        
        # Fondo del panel
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        # Fondo semi-transparente (manteniendo el estilo del HUD original)
        overlay = pygame.Surface((panel_width, panel_height))
        overlay.set_alpha(150)
        overlay.fill(COLOR_INSTRUCCION_FONDO)
        screen.blit(overlay, panel_rect)
        
        # Borde del panel
        pygame.draw.rect(screen, COLOR_BLANCO, panel_rect, 2)
        
        # Fuentes
        font_titulo = self.resource_manager.get_font('pequeña')
        font_datos = self.resource_manager.get_font('hud')
        
        if font_titulo and font_datos:
            # Título del panel
            titulo_text = "Distancias Recorridas"
            titulo_surface = font_titulo.render(titulo_text, True, COLOR_AMARILLO)
            titulo_rect = titulo_surface.get_rect()
            titulo_rect.centerx = panel_x + panel_width // 2
            titulo_rect.y = panel_y + 8
            screen.blit(titulo_surface, titulo_rect)
            
            # Datos de cada personaje
            y_offset = titulo_rect.bottom + 10
            line_height = 22
            
            # Personajes en orden fijo
            personajes_ordenados = ["UIAbot", "UAIBOTA", "UAIBOTINA", "UAIBOTINO"]
            
            for i, personaje in enumerate(personajes_ordenados):
                if personaje in distancias_personajes:
                    distancia = distancias_personajes[personaje]
                    
                    # Texto del personaje
                    personaje_text = f"{personaje}:"
                    personaje_surface = font_datos.render(personaje_text, True, COLOR_BLANCO)
                    personaje_rect = personaje_surface.get_rect()
                    personaje_rect.x = panel_x + 10
                    personaje_rect.y = y_offset + (i * line_height)
                    screen.blit(personaje_surface, personaje_rect)
                    
                    # Distancia (alineada a la derecha)
                    distancia_text = f"{distancia:.2f} km"
                    distancia_surface = font_datos.render(distancia_text, True, COLOR_BARRA_ENERGIA)
                    distancia_rect = distancia_surface.get_rect()
                    distancia_rect.right = panel_x + panel_width - 10
                    distancia_rect.y = personaje_rect.y
                    screen.blit(distancia_surface, distancia_rect)
            
            # Línea separadora
            total_y = y_offset + (len(personajes_ordenados) * line_height) + 2
            # Total de la partida
            distancia_total = sum(distancias_personajes.values())
            total_surface = font_datos.render("TOTAL:", True, COLOR_AMARILLO)
            total_rect = total_surface.get_rect()
            total_rect.x = panel_x + 10
            total_rect.y = total_y + 6
            screen.blit(total_surface, total_rect)
            
            total_km_surface = font_datos.render(f"{distancia_total:.2f} km", True, COLOR_AMARILLO)
            total_km_rect = total_km_surface.get_rect()
            total_km_rect.right = panel_x + panel_width - 10
            total_km_rect.y = total_rect.y
            screen.blit(total_km_surface, total_km_rect)      
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