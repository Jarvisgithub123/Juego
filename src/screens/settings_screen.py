import pygame
from src.Constantes import *
from src.core.scene_manager import Scene
from src.UI.button import Button
from src.UI.Slider import Slider
class SettingsScreen(Scene):
    """Pantalla de configuracion"""
    
    def __init__(self, screen, resource_manager,scene_manager):
        super().__init__(screen, resource_manager,scene_manager)
        self.buttons = []
        self.sliders = []
        
        # Variables para animacion de fondo
        self.background_timer = 0.0
        self.animation_speed = 0.5 
        self.current_background = 0 
        
        # Etiquetas para los sliders
        self.slider_labels = ["Volumen Musica", "Volumen Efectos"]
        self.initial_music_volume = self.resource_manager.get_music_volume()
        self.initial_sound_volume = self.resource_manager.get_sound_volume()
        
        self._create_buttons()
    
    def _create_buttons(self):
        """Crea los botones de configuracion - POSICIONADOS A LA DERECHA"""
        button_width = 400
        button_height = 70
        spacing = 20
        
        # CAMBIO: Posicionar botones a la derecha
        margin_from_right = 350  # Margen desde el borde derecho
        start_x =  button_width - margin_from_right
        start_y = ALTO_PANTALLA // 2 - 40
        
        self.sliders = [ 
            Slider((start_x + button_width // 2, start_y - 50), (300, 20), 0.0, 1.0, 
                   self.initial_music_volume, self.resource_manager, self._update_music_volume),
            Slider((start_x + button_width // 2, start_y ), (300, 20), 0.0, 1.0, 
                   self.initial_sound_volume, self.resource_manager, self._update_sound_volume)
        ]
        
        self._update_music_volume(self.initial_music_volume)
        self._update_sound_volume(self.initial_sound_volume)
        
        self.buttons = [
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
    
    # Callbacks para actualizar audio
    def _update_music_volume(self, value):
        """Actualiza volumen de música cuando cambia el slider"""
        self.resource_manager.set_music_volume(value)
        if (self.scene_manager and hasattr(self.scene_manager, 'game_manager') 
            and self.scene_manager.game_manager 
            and hasattr(self.scene_manager.game_manager, 'shared_data')):
            self.scene_manager.game_manager.shared_data['music_volume'] = value
        print(f"Volumen música: {value:.2f}")

    def _update_sound_volume(self, value):
        """Actualiza volumen de efectos cuando cambia el slider"""
        self.resource_manager.set_sound_volume(value)
        if (self.scene_manager and hasattr(self.scene_manager, 'game_manager') 
            and self.scene_manager.game_manager 
            and hasattr(self.scene_manager.game_manager, 'shared_data')):
            self.scene_manager.game_manager.shared_data['sound_volume'] = value
        print(f"Volumen efectos: {value:.2f}")
    
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
        
        for slider in self.sliders:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and slider.container_rect.collidepoint(event.pos):
                    slider.move_slider(event.pos[0])
    
    def update(self, dt):
        """Actualiza la pantalla de configuracion"""
        # Actualizar botones
        for button in self.buttons:
            button.update(dt)
        
        for slider in self.sliders:
            if slider.container_rect.collidepoint(pygame.mouse.get_pos()):
                if pygame.mouse.get_pressed()[0]:
                    slider.move_slider(pygame.mouse.get_pos()[0])
        
        # ACTUALIZAR ANIMACIoN DE FONDO
        self.background_timer += dt
        if self.background_timer >= self.animation_speed:
            self.background_timer = 0.0
            self.current_background = 1 - self.current_background  # Alternar entre 0 y 1
        
    
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
            for i, (slider, label) in enumerate(zip(self.sliders, self.slider_labels)):
                # Etiqueta
                label_surface = font_pequeña.render(label, True, COLOR_AMARILLO)
                label_y = slider.pos[1] - 35
                self.screen.blit(label_surface, (slider.slider_left_pos, label_y))
                
                # Valor actual
                value_text = f"{int(slider.get_value() * 100)}%"
                value_surface = font_pequeña.render(value_text, True, COLOR_AMARILLO)
                value_rect = value_surface.get_rect()
                value_rect.right = slider.slider_right_pos
                value_rect.y = label_y
                self.screen.blit(value_surface, value_rect)
        
        # Botones (ya posicionados a la derecha)
        for button in self.buttons:
            button.draw(self.screen)
        
        for slider in self.sliders:
            slider.draw(self.screen)
