import pygame
from src.Constantes import *
from src.core.scene_manager import Scene
from src.UI.button import Button

class MenuScreen(Scene):
    """Pantalla del menu principal"""
    
    def __init__(self, screen, resource_manager, scene_manager):
        super().__init__(screen, resource_manager,scene_manager)
        self.scene_manager = scene_manager
        self.sound_enabled = True
        self.buttons = []
        
        # Variables para animacion de fondo
        self.background_timer = 0.0
        self.animation_speed = 0.5  
        self.current_background = 0  
        
        self._create_buttons()
    
    def on_enter(self):
        """Se ejecuta al entrar en la pantalla del menu"""
        self.resource_manager.play_music("menu", volume=0.5)
    
    def _create_buttons(self):
        """Crea los botones del menu - POSICIONADOS A LA DERECHA"""
        button_width = 250
        button_height = 75
        spacing = 30
        total_height = 3 * button_height + 2 * spacing
        start_y = (ALTO_PANTALLA - total_height) // 2 + 60
        
        # POSICIoN CORREGIDA: Posicionar botones a la derecha
        margin_from_right = 150  # Margen desde el borde derecho
        start_x = button_width - margin_from_right  # Formula correcta
        
        self.buttons = [
            Button("Jugar", start_x, start_y, button_width, button_height, 
                self.resource_manager, self._start_game),
            Button("Ajustes", start_x, start_y + button_height + spacing, 
                button_width, button_height, self.resource_manager, self._show_settings),
            Button("Salir", start_x, start_y + 2 * (button_height + spacing), 
                button_width, button_height, self.resource_manager, self._quit_game)
        ]
    
    def _start_game(self):
        """Inicia el juego"""
        if self.scene_manager:
            from src.screens.character_screen import CharacterScreen
            self.scene_manager.change_scene(CharacterScreen)

    
    def _show_settings(self):
        """Muestra las opciones"""
        if self.scene_manager:
            from src.screens.settings_screen import SettingsScreen
            self.scene_manager.change_scene(SettingsScreen)
    
    def _quit_game(self):
        """Sale del juego"""
        pygame.quit()
        exit()
    
    def handle_event(self, event):
        """Maneja los eventos del menu"""
        for button in self.buttons:
            button.handle_event(event)
    
    def update(self, dt):
        """Actualiza el menu"""
        # Actualizar botones
        for button in self.buttons:
            button.update(dt)
        
        # ACTUALIZAR ANIMACIoN DE FONDO
        self.background_timer += dt
        if self.background_timer >= self.animation_speed:
            self.background_timer = 0.0
            self.current_background = 1 - self.current_background  # Alternar entre 0 y 1
    
    def _draw_bordered_text(self, text: str, font: pygame.font.Font, pos: tuple, 
                           text_color: tuple, border_color: tuple, border_size: int = 4):
        """Dibuja texto con borde"""
        x, y = pos
        # Dibujar el borde
        for dx, dy in [(dx, dy) for dx in range(-border_size, border_size + 1) 
                                for dy in range(-border_size, border_size + 1)
                                if dx*dx + dy*dy <= border_size*border_size]:
            text_surface = font.render(text, True, border_color)
            text_rect = text_surface.get_rect(center=(x + dx, y + dy))
            self.screen.blit(text_surface, text_rect)
        
        # Dibujar el texto principal
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def draw(self):
        """Dibuja el menu con fondo animado"""
        # DIBUJAR FONDO ANIMADO
        background_name = f"menu_background{self.current_background + 1}"
        background_image = self.resource_manager.get_image(background_name)
        
        if background_image:
            # Escalar la imagen al tamaño de la pantalla
            scaled_background = pygame.transform.scale(background_image, (ANCHO_PANTALLA, ALTO_PANTALLA))
            self.screen.blit(scaled_background, (0, 0))

        else:
            # Si no hay imagen, usar color de fondo por defecto
            self.screen.fill(COLOR_FONDO_BASE)
        
        # Titulo con borde
        font_titulo = self.resource_manager.get_font('titulo')
        if font_titulo:
            self._draw_bordered_text(
                "Go UAIBOT",
                font_titulo,
                (ANCHO_PANTALLA // 5, 120),
                COLOR_TITULO,
                (0, 0, 0),  # Color del borde (negro)
                3  # Grosor del borde
            )
        
        # Botones (ya posicionados a la derecha)
        for button in self.buttons:
            button.draw(self.screen)