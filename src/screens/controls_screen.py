import pygame
from src.Constantes import *
from src.core.scene_manager import Scene
from src.UI.button import Button

class ControlsScreen(Scene):
    """Pantalla que muestra los controles del juego"""
    
    def __init__(self, screen, resource_manager):
        super().__init__(screen, resource_manager)
        self.buttons = []
        
        # Variables para animacion de fondo
        self.background_timer = 0.0
        self.animation_speed = 0.5 
        self.current_background = 0 
        
        # Crear los elementos de texto de controles
        self._create_control_elements()
        self._create_buttons()
    
    def _create_control_elements(self):
        """Crea los elementos de texto que muestran los controles"""
        self.control_elements = []
        
        # Obtener fuentes
        font_titulo_controles = self.resource_manager.get_font('subtitulo')
        font_controles = self.resource_manager.get_font('boton')
        font_descripcion = self.resource_manager.get_font('pequena')
        
        # Posicion base para los controles
        start_x = ANCHO_PANTALLA // 2
        start_y = 180
        spacing_y = 80
        
        # Lista de controles con sus descripciones
        controles = [
            ("ESPACIO", "Saltar", "Presiona para hacer que UAIBOT salte sobre obstaculos"),
            ("Z", "Dash", "Realiza un dash rapido (consume energia)"),
            ("P", "Pausar", "Pausa o reanuda el juego"),
            ("ESC", "Menu", "Regresa al menu principal (en pausa)")
        ]
        
        for i, (tecla, accion, descripcion) in enumerate(controles):
            y_pos = start_y + (i * spacing_y)
            
            # Crear superficie para la tecla
            if font_controles:
                tecla_surface = font_controles.render(f"[{tecla}]", True, COLOR_AMARILLO)
                tecla_rect = tecla_surface.get_rect(center=(start_x - 200, y_pos))
                
                # Crear superficie para la accion
                accion_surface = font_controles.render(accion, True, COLOR_BLANCO)
                accion_rect = accion_surface.get_rect(center=(start_x, y_pos))
                
                # Crear superficie para la descripcion
                if font_descripcion:
                    desc_surface = font_descripcion.render(descripcion, True, COLOR_TEXTO_SUTIL_EN_FONDO)
                    desc_rect = desc_surface.get_rect(center=(start_x, y_pos + 25))
                    
                    self.control_elements.extend([
                        (tecla_surface, tecla_rect),
                        (accion_surface, accion_rect),
                        (desc_surface, desc_rect)
                    ])
    
    def _create_buttons(self):
        """Crea el boton para volver"""
        button_width = 300
        button_height = 70
        
        # Posicionar boton en la parte inferior
        start_x = (ANCHO_PANTALLA - button_width) // 2
        start_y = ALTO_PANTALLA - 100
        
        self.buttons = [
            Button("Volver", 
                   start_x, start_y,
                   button_width, button_height, 
                   self.resource_manager, self._return_to_settings)
        ]
    
    def _return_to_settings(self):
        """Regresa a la pantalla de configuracion"""
        from src.screens.settings_screen import SettingsScreen
        self.scene_manager.change_scene(SettingsScreen)
    
    def handle_event(self, event):
        """Maneja los eventos de la pantalla de controles"""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._return_to_settings()
        
        for button in self.buttons:
            button.handle_event(event)
    
    def update(self, dt):
        """Actualiza la pantalla de controles"""
        # Actualizar botones
        for button in self.buttons:
            button.update(dt)
        
        # Actualizar animacion de fondo
        self.background_timer += dt
        if self.background_timer >= self.animation_speed:
            self.background_timer = 0.0
            self.current_background = 1 - self.current_background  # Alternar entre 0 y 1
    
    def draw(self):
        """Dibuja la pantalla de controles con fondo animado"""
        # Dibujar fondo animado
        background_name = f"menu_background{self.current_background + 1}"
        background_image = self.resource_manager.get_image(background_name)
        
        if background_image:
            # Escalar la imagen al tamaño de la pantalla
            scaled_background = pygame.transform.scale(background_image, (ANCHO_PANTALLA, ALTO_PANTALLA))
            self.screen.blit(scaled_background, (0, 0))
        else:
            # Si no hay imagen, usar color de fondo por defecto
            self.screen.fill(COLOR_FONDO_BASE)
        
        # Titulo principal
        font_titulo = self.resource_manager.get_font('titulo')
        if font_titulo:
            title_surface = font_titulo.render("Controles", True, COLOR_AMARILLO)
            title_rect = title_surface.get_rect(center=(ANCHO_PANTALLA // 2, 80))
            self.screen.blit(title_surface, title_rect)
        
        # Dibujar fondo semi-transparente para mejor legibilidad
        overlay = pygame.Surface((ANCHO_PANTALLA - 100, 400))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        overlay_rect = overlay.get_rect(center=(ANCHO_PANTALLA // 2, 320))
        self.screen.blit(overlay, overlay_rect)
        
        # Dibujar elementos de control
        for surface, rect in self.control_elements:
            self.screen.blit(surface, rect)
        
        # Ayuda
        font_pequeña = self.resource_manager.get_font('pequena')
        if font_pequeña:
            help_surface = font_pequeña.render("Presiona ESC para volver", True, COLOR_TEXTO_SUTIL_EN_FONDO)
            help_rect = help_surface.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA - 40))
            self.screen.blit(help_surface, help_rect)
        
        # Botones
        for button in self.buttons:
            button.draw(self.screen)