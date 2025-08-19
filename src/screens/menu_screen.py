import pygame
from src.Constantes import *
from src.core.scene_manager import Scene
from src.UI.button import Button

class MenuScreen(Scene):
    """Pantalla del menu principal"""
    
    def __init__(self, screen, resource_manager):
        super().__init__(screen, resource_manager)
        self.sound_enabled = True
        self.buttons = []
        self._create_buttons()
    
    def on_enter(self):
        """Se ejecuta al entrar en la pantalla del menu"""
        self.resource_manager.play_music("menu", volume=0.5)
    
    def _create_buttons(self):
        """Crea los botones del menu"""
        button_width = 250
        button_height = 75
        spacing = 30
        total_height = 3 * button_height + 2 * spacing
        start_y = (ALTO_PANTALLA - total_height) // 2 + 60
        start_x = ANCHO_PANTALLA - button_width - 480
        
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
        from src.screens.game_screen import GameScreen
        self.resource_manager.stop_music()
        self.scene_manager.change_scene(GameScreen)
    
    def _show_settings(self):
        """Muestra las opciones"""
        from src.screens.settings_screen import SettingsScreen
        self.scene_manager.change_scene(SettingsScreen, self.sound_enabled)
    
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
        for button in self.buttons:
            button.update(dt)
    
    def draw(self):
        """Dibuja el menu"""
        self.screen.fill(COLOR_FONDO_BASE)
        
        # Título
        font_titulo = self.resource_manager.get_font('titulo')
        if font_titulo:
            title_surface = font_titulo.render("Go UAIBOT", True, COLOR_TEXTO_EN_FONDO)
            title_rect = title_surface.get_rect(center=(ANCHO_PANTALLA // 2, 120))
            self.screen.blit(title_surface, title_rect)
        
        # Subtítulo
        font_subtitulo = self.resource_manager.get_font('subtitulo')
        if font_subtitulo:
            subtitle_surface = font_subtitulo.render(":)", True, COLOR_TEXTO_SUTIL_EN_FONDO)
            subtitle_rect = subtitle_surface.get_rect(center=(ANCHO_PANTALLA // 2, 180))
            self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Botones
        for button in self.buttons:
            button.draw(self.screen)