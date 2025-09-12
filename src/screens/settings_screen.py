import pygame
from src.Constantes import *
from src.core.scene_manager import Scene
from src.UI.button import Button

class SettingsScreen(Scene):
    """Pantalla de configuracion"""
    
    def __init__(self, screen, resource_manager,scene_manager):
        super().__init__(screen, resource_manager,scene_manager)
        self.buttons = []
        
        # Variables para animacion de fondo
        self.background_timer = 0.0
        self.animation_speed = 0.5 
        self.current_background = 0 
        
        self._create_buttons()
    
    def _create_buttons(self):
        """Crea los botones de configuracion - POSICIONADOS A LA DERECHA"""
        button_width = 400
        button_height = 70
        spacing = 20
        
        # CAMBIO: Posicionar botones a la derecha
        margin_from_right = 350  # Margen desde el borde derecho
        start_x =  button_width - margin_from_right
        start_y = ALTO_PANTALLA // 2 - 80  # Ajustado para 3 botones
        
        music_enabled = getattr(self.resource_manager, 'music_enabled', True)
        
        self.buttons = [
            Button(f"Musica: {'Activada' if music_enabled else 'Desactivada'}", 
                   start_x, start_y,
                   button_width, button_height, self.resource_manager, self._toggle_sound),
            Button("Controles", 
                   start_x, start_y + button_height + spacing,
                   button_width, button_height, self.resource_manager, self._show_controls),
            Button("Volver al Menu", 
                   start_x, start_y + 2 * (button_height + spacing),
                   button_width, button_height, self.resource_manager, self._return_to_menu)
        ]
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
    def _toggle_sound(self):
        """Alterna el sonido"""
        current_state = getattr(self.resource_manager, 'music_enabled', True)
        new_state = not current_state
        
        # Cambiar el estado global de musica
        self.resource_manager.enable_music(new_state)
        
        if new_state:
            # Si se activa la musica, reproducir la musica actual o la del menu
            current_music = self.resource_manager.get_current_music()
            if current_music:
                self.resource_manager.unpause_music()
            else:
                # Si no hay musica reproduciendose, iniciar la musica del menu
                self.resource_manager.play_music("menu")
        
        # Actualizar texto del boton
        self.buttons[0].text = f"Musica: {'Activada' if new_state else 'Desactivada'}"
    
    def _show_controls(self):
        """Muestra la pantalla de controles"""
        from src.screens.controls_screen import ControlsScreen
        self.scene_manager.change_scene(ControlsScreen)
    
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
        # Actualizar botones
        for button in self.buttons:
            button.update(dt)
        
        # ACTUALIZAR ANIMACIoN DE FONDO
        self.background_timer += dt
        if self.background_timer >= self.animation_speed:
            self.background_timer = 0.0
            self.current_background = 1 - self.current_background  # Alternar entre 0 y 1
        
        # Actualizar texto del boton de musica si es necesario
        music_enabled = getattr(self.resource_manager, 'music_enabled', True)
        expected_text = f"Musica: {'Activada' if music_enabled else 'Desactivada'}"
        if self.buttons[0].text != expected_text:
            self.buttons[0].text = expected_text
    
    def draw(self):
        """Dibuja la pantalla de configuracion con fondo animado"""
        # DIBUJAR FONDO ANIMADO
        background_name = f"menu_background{self.current_background + 1}"
        background_image = self.resource_manager.get_image(background_name)
        
        if background_image:
            # Escalar la imagen al tamaño de la pantalla
            scaled_background = pygame.transform.scale(background_image, (ANCHO_PANTALLA, ALTO_PANTALLA))
            self.screen.blit(scaled_background, (0, 0))
            
            fade_duration = 0.5  
            if self.background_timer <= fade_duration:
                # Mostrar la imagen anterior con fade out
                other_bg_name = f"settings_bg{(1 - self.current_background) + 1}"
                other_bg = self.resource_manager.get_image(other_bg_name)
                if other_bg:
                    alpha = int(255 * (1 - self.background_timer / fade_duration))
                    other_bg_scaled = pygame.transform.scale(other_bg, (ANCHO_PANTALLA, ALTO_PANTALLA))
                    other_bg_scaled.set_alpha(alpha)
                    self.screen.blit(other_bg_scaled, (0, 0))
        else:
            # Si no hay imagen, usar color de fondo por defecto
            self.screen.fill(COLOR_FONDO_BASE)
        
        # Titulo - posicionado a la izquierda para balancear
        font_titulo = self.resource_manager.get_font('titulo')
        if font_titulo:
            self._draw_bordered_text(
                "Opciones",
                font_titulo,
                (ANCHO_PANTALLA // 5, 120),
                COLOR_TITULO,
                (0, 0, 0),  # Color del borde (negro)
                3  # Grosor del borde
            )
        
        # Ayuda - tambien a la izquierda
        font_pequeña = self.resource_manager.get_font('pequeña')
        if font_pequeña:
            help_surface = font_pequeña.render("Presiona ESC para volver", True, COLOR_TEXTO_SUTIL_EN_FONDO)
            help_rect = help_surface.get_rect(center=(ANCHO_PANTALLA // 5, 180))
            self.screen.blit(help_surface, help_rect)
        
        # Informacion de la animacion (opcional, para debug)
        if font_pequeña:
            anim_info = f"Fondo: {self.current_background + 1}/2"
            anim_surface = font_pequeña.render(anim_info, True, COLOR_TEXTO_SUTIL_EN_FONDO)
            self.screen.blit(anim_surface, (10, ALTO_PANTALLA - 30))
        
        # Botones (ya posicionados a la derecha)
        for button in self.buttons:
            button.draw(self.screen)