import pygame
from src.Constantes import *
from src.core.scene_manager import Scene
from src.UI.button import Button

class SettingsScreen(Scene):
    """Pantalla de configuracion"""
    
    def __init__(self, screen, resource_manager):
        super().__init__(screen, resource_manager)
        self.buttons = []
        self._create_buttons()
    
    def _create_buttons(self):
        """Crea los botones de configuracion"""
        button_width = 400
        button_height = 70
        spacing = 20
        center_x = ANCHO_PANTALLA // 2
        start_y = ALTO_PANTALLA // 2 - 100
        
        music_enabled = getattr(self.resource_manager, 'music_enabled', True)
        
        self.buttons = [
            Button(f"Musica: {'Activada' if music_enabled else 'Desactivada'}", 
                   center_x - button_width // 2, start_y,
                   button_width, button_height, self.resource_manager, self._toggle_sound),
            Button("Volver al Menu", 
                   center_x - button_width // 2, start_y + button_height + spacing,
                   button_width, button_height, self.resource_manager, self._return_to_menu)
        ]
    
    def _toggle_sound(self):
        """Alterna el sonido"""
        current_state = getattr(self.resource_manager, 'music_enabled', True)
        new_state = not current_state
        
        # Cambiar el estado global de música
        self.resource_manager.enable_music(new_state)
        
        if new_state:
            # Si se activa la música, reproducir la música actual o la del menú
            current_music = self.resource_manager.get_current_music()
            if current_music:
                self.resource_manager.unpause_music()
            else:
                # Si no hay música reproduciéndose, iniciar la música del menú
                self.resource_manager.play_music("menu")
        
        # Actualizar texto del botón
        self.buttons[0].text = f"Musica: {'Activada' if new_state else 'Desactivada'}"
    
    def _return_to_menu(self):
        """Regresa al menu principal"""
        from src.screens.menu_screen import MenuScreen
        self.scene_manager.change_scene(MenuScreen)
    
    def handle_event(self, event):
        """Maneja los eventos de la pantalla de configuracion"""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._return_to_menu()
        
        for button in self.buttons:
            button.handle_event(event)
    
    def update(self, dt):
        """Actualiza la pantalla de configuracion"""
        for button in self.buttons:
            button.update(dt)
        
        music_enabled = getattr(self.resource_manager, 'music_enabled', True)
        expected_text = f"Musica: {'Activada' if music_enabled else 'Desactivada'}"
        if self.buttons[0].text != expected_text:
            self.buttons[0].text = expected_text
    
    def draw(self):
        """Dibuja la pantalla de configuracion"""
        self.screen.fill(COLOR_FONDO_BASE)
        
        # Título
        font_titulo = self.resource_manager.get_font('titulo')
        if font_titulo:
            title_surface = font_titulo.render("Opciones", True, COLOR_TEXTO_EN_FONDO)
            title_rect = title_surface.get_rect(center=(ANCHO_PANTALLA // 2, 120))
            self.screen.blit(title_surface, title_rect)
        
        # Ayuda
        font_pequeña = self.resource_manager.get_font('pequeña')
        if font_pequeña:
            help_surface = font_pequeña.render("Presiona ESC para volver", True, COLOR_TEXTO_SUTIL_EN_FONDO)
            help_rect = help_surface.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2 - 150))
            self.screen.blit(help_surface, help_rect)
        
        # Botones
        for button in self.buttons:
            button.draw(self.screen)
