import pygame
from src.Constantes import *
from src.core.scene_manager import Scene
from src.UI.button import Button

class CharacterScreen(Scene):
    """Pantalla de seleccion de personaje con carrusel manual"""
    
    def __init__(self, screen, resource_manager,scene_manager):
        super().__init__(screen, resource_manager,scene_manager)
        self.selected_character = None
        self.buttons = []
        
        # medidas originales del cartel
        original_width, original_height = 1057, 706
        scale_x = ANCHO_PANTALLA / original_width
        scale_y = ALTO_PANTALLA / original_height

        original_area = pygame.Rect(225, 160, 575, 260)
        self.billboard_area = pygame.Rect(
            int(original_area.x * scale_x),
            int(original_area.y * scale_y),
            int(original_area.width * scale_x),
            int(original_area.height * scale_y)
        )

        # Lista de personajes disponibles (puedes añadir mas)
        self.characters = [
            ("UIAbot", self.resource_manager.get_image("cartel_uaibot")),
            ("UAIBOTA", self.resource_manager.get_image("personaje3")),
            ("UAIBOTINA", self.resource_manager.get_image("cartel_uaibotina")),
            ("UAIBOTINO", self.resource_manager.get_image("UAIBOTINO_walk")),
        ]
        self.current_index = 0

        # primer personaje
        self._update_current_character()
        self._create_buttons()
    
    def on_enter(self):
        """Se ejecuta al entrar en la pantalla de seleccion"""
        self.resource_manager.play_music("menu", volume=0.3)

    def _update_current_character(self):
        """Carga y escala el personaje actual al billboard"""
        name, image = self.characters[self.current_index]
        if image:
            card_rect = image.get_rect()
            scale_ratio = min(
                self.billboard_area.width / card_rect.width,
                self.billboard_area.height / card_rect.height
            )
            new_width = int(card_rect.width * scale_ratio * 1.20)
            new_height = int(card_rect.height * scale_ratio)

            self.character_scaled = pygame.transform.scale(image, (new_width, new_height))
            self.character_rect = self.character_scaled.get_rect(center=self.billboard_area.center)
            self.selected_character = name  
        else:
            self.character_scaled = None
            self.character_rect = None
            self.selected_character = None

    def _create_buttons(self):
        """Crea los botones de la pantalla"""
        button_width = 200
        button_height = 60
        spacing = 20

        # Botones inferiores
        total_width = 2 * button_width + spacing + 50
        start_x = (ANCHO_PANTALLA - total_width) // 2
        button_y = ALTO_PANTALLA - 120

        self.buttons = [
            Button("Seleccionar", start_x-50, button_y, button_width + 60, button_height+5,
                   self.resource_manager, self._select_character),
            Button("Volver", start_x + button_width + spacing, button_y,
                   button_width, button_height, self.resource_manager, self._go_back)
        ]

        # Botones de flechas 
        arrow_size = 60
        arrow_y = self.billboard_area.centery - arrow_size // 2
        left_x = self.billboard_area.left - arrow_size - 20
        right_x = self.billboard_area.right + 20

        self.left_button = Button("<", left_x, arrow_y, arrow_size, arrow_size,
                                  self.resource_manager, self._prev_character)
        self.right_button = Button(">", right_x, arrow_y, arrow_size, arrow_size,
                                   self.resource_manager, self._next_character)

        self.buttons.extend([self.left_button, self.right_button])

    def _next_character(self):
        """Muestra el siguiente personaje"""
        self.current_index = (self.current_index + 1) % len(self.characters)
        self._update_current_character()

    def _prev_character(self):
        """Muestra el personaje anterior"""
        self.current_index = (self.current_index - 1) % len(self.characters)
        self._update_current_character()
    
    def _select_character(self):
        """Confirma la seleccion del personaje y guarda la eleccion"""
        if self.selected_character:
            try:
                if hasattr(self.scene_manager, 'game_manager') and self.scene_manager.game_manager:
                    if not hasattr(self.scene_manager.game_manager, 'shared_data'):
                        self.scene_manager.game_manager.shared_data = {}
                    self.scene_manager.game_manager.shared_data['selected_character'] = self.selected_character
                    print(f"Personaje seleccionado guardado: {self.selected_character}")
                else:
                    print("Warning: No se pudo acceder a game_manager")
            except Exception as e:
                print(f"Error al guardar personaje seleccionado: {e}")
            
            from src.screens.game_screen import GameScreen
            self.resource_manager.stop_music()
            self.scene_manager.change_scene(GameScreen)
        else:
            print("Primero selecciona un personaje")
    
    def _go_back(self):
        """Vuelve al menú principal"""
        from src.screens.menu_screen import MenuScreen
        self.scene_manager.change_scene(MenuScreen)
    
    def handle_event(self, event):
        """Maneja los eventos de la pantalla"""
        for button in self.buttons:
            button.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._go_back()
    
    def update(self, dt):
        """Actualiza la pantalla"""
        for button in self.buttons:
            button.update(dt)
    
    def _draw_bordered_text(self, text: str, font: pygame.font.Font, pos: tuple,
                           text_color: tuple, border_color: tuple, border_size: int = 2):
        """Dibuja texto con borde"""
        x, y = pos
        for dx, dy in [(dx, dy) for dx in range(-border_size, border_size + 1)
                                for dy in range(-border_size, border_size + 1)
                                if dx*dx + dy*dy <= border_size*border_size]:
            text_surface = font.render(text, True, border_color)
            text_rect = text_surface.get_rect(center=(x + dx, y + dy))
            self.screen.blit(text_surface, text_rect)

        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)
    
    def draw(self):
        """Dibuja la pantalla de seleccion de personaje"""
        # Fondo 
        billboard_image = self.resource_manager.get_image("cartel")
        if billboard_image:
            scaled_billboard = pygame.transform.scale(billboard_image, (ANCHO_PANTALLA, ALTO_PANTALLA))
            self.screen.blit(scaled_billboard, (0, 0))
        else:
            self.screen.fill(COLOR_FONDO_BASE)
        
        # Personaje actual
        if self.character_scaled and self.character_rect:
            self.screen.blit(self.character_scaled, self.character_rect.topleft)

        # Titulo
        font_titulo = self.resource_manager.get_font('titulo')
        if font_titulo:
            self._draw_bordered_text(
                "Selecciona tu Personaje",
                font_titulo,
                (ANCHO_PANTALLA // 2, 80),
                COLOR_TITULO,
                (0, 0, 0),
                3
            )

        

        # Botones
        for button in self.buttons:
            button.draw(self.screen)
