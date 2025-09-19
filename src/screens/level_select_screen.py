import pygame
from src.Constantes import *
from src.core.scene_manager import Scene
from src.UI.button import Button

class LevelSelectScreen(Scene):
    """Pantalla de seleccion de niveles con arquitectura extensible"""
    
    def __init__(self, screen, resource_manager, scene_manager):
        super().__init__(screen, resource_manager, scene_manager)
        
        # Configuracion de niveles - Facil de extender
        self.levels_data = {
            "level_1": {
                "name": "Primer dia de trabajo",
                "description": "Uiabot debe entregar su primer paquete.",
                "background": "level1_bg",
                "available": True,
                "characters": ["character_a", "character_b"],
                "preview_image": "level1_preview"
            },
            "level_2": {
                "name": "Duermen los androides con palomas espias?",
                "description": "Uiabot debe entregar una paloma mensajera sospechosa.",
                "background": "level2_bg", 
                "available": True,
                "characters": ["character_c", "character_a"],  # incluir character_a para que coincida con los diálogos
                "preview_image": "level2_preview"
            }
            "level_3": {
                "name": "The Legend of Mishi",
                "description": "Otra mision con Uiabot, esta vez debe entregar un paquete a un gato famoso.",
                "background": "level3_bg", 
                "available": True,
                "characters": ["character_d", "character_a"],  # incluir character_a para que coincida con los diálogos
                "preview_image": "level2_preview"
            }
            # Facil agregar mas niveles aqui
        }
        
        self.level_keys = list(self.levels_data.keys())
        self.selected_level_index = 0
        self.buttons = []
        
        # Variables para animacion de fondo
        self.background_timer = 0.0
        self.animation_speed = 0.8
        self.current_background = 0
        
        # Configuracion visual de niveles
        self.level_card_width = 670
        self.level_card_height = 370
        self.card_spacing = 50
        
        self._create_buttons()
    
    def on_enter(self):
        """Se ejecuta al entrar en la pantalla"""
        self.resource_manager.play_music("menu", volume=0.4)
    
    def _create_buttons(self):
        """Crea los botones de navegacion"""
        button_width = 200
        button_height = 60
        
        # Botones de navegacion entre niveles
        arrow_size = 80
        arrow_y = ALTO_PANTALLA // 2 - arrow_size // 2
        
        # Flechas para navegar niveles
        left_x = 50
        right_x = ANCHO_PANTALLA - arrow_size - 50
        
        self.left_arrow = Button("<", left_x, arrow_y, arrow_size, arrow_size,
                                self.resource_manager, self._prev_level)
        self.right_arrow = Button(">", right_x, arrow_y, arrow_size, arrow_size,
                                 self.resource_manager, self._next_level)
        
        # Botones principales
        button_y = ALTO_PANTALLA - 120
        button_x_center = ANCHO_PANTALLA // 2
        
        select_x = button_x_center - button_width - 55
        back_x = button_x_center + 20
        
        self.select_button = Button("Seleccionar", select_x, button_y, 
                                   button_width+55, button_height,
                                   self.resource_manager, self._select_level)
        
        self.back_button = Button("Volver", back_x, button_y,
                                 button_width, button_height, 
                                 self.resource_manager, self._go_back)
        
        self.buttons = [self.left_arrow, self.right_arrow, 
                       self.select_button, self.back_button]
    
    def _prev_level(self):
        """Navega al nivel anterior"""
        self.selected_level_index = (self.selected_level_index - 1) % len(self.level_keys)
        self.resource_manager.play_sound("boton_hover")
    
    def _next_level(self):
        """Navega al siguiente nivel"""
        self.selected_level_index = (self.selected_level_index + 1) % len(self.level_keys)
        self.resource_manager.play_sound("boton_hover")
    
    def _select_level(self):
        """Selecciona el nivel actual"""
        current_level_key = self.level_keys[self.selected_level_index]
        current_level = self.levels_data[current_level_key]
        
        if current_level["available"]:
            # Guardar el nivel seleccionado en shared_data
            if hasattr(self.scene_manager, 'game_manager') and self.scene_manager.game_manager:
                if not hasattr(self.scene_manager.game_manager, 'shared_data'):
                    self.scene_manager.game_manager.shared_data = {}
                self.scene_manager.game_manager.shared_data['selected_level'] = current_level_key
                self.scene_manager.game_manager.shared_data['level_data'] = current_level
            
            # Transicion al nivel
            from src.screens.level_screen import LevelScreen
            self.scene_manager.change_scene(LevelScreen)
        else:
            print("Nivel no disponible aun")
    
    def _go_back(self):
        """Vuelve al menu principal"""
        from src.screens.menu_screen import MenuScreen  
        self.scene_manager.change_scene(MenuScreen)
    
    def handle_event(self, event):
        """Maneja los eventos de la pantalla"""
        for button in self.buttons:
            button.handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self._prev_level()
            elif event.key == pygame.K_RIGHT:
                self._next_level()
            elif event.key == pygame.K_RETURN:
                self._select_level()
            elif event.key == pygame.K_ESCAPE:
                self._go_back()
    
    def update(self, dt):
        """Actualiza la pantalla"""
        for button in self.buttons:
            button.update(dt)
        
        # Actualizar animacion de fondo
        self.background_timer += dt
        if self.background_timer >= self.animation_speed:
            self.background_timer = 0.0
            self.current_background = 1 - self.current_background
    
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
    
    def _draw_level_card(self):
        """Dibuja la tarjeta del nivel actual"""
        current_level_key = self.level_keys[self.selected_level_index]
        current_level = self.levels_data[current_level_key]
        
        # Posicion de la tarjeta
        card_x = ANCHO_PANTALLA // 2 - self.level_card_width // 2
        card_y = 200
        
        # Fondo de la tarjeta
        card_rect = pygame.Rect(card_x, card_y, self.level_card_width, self.level_card_height)
        
        # Fondo semi-transparente
        overlay = pygame.Surface((self.level_card_width, self.level_card_height))
        overlay.set_alpha(180)
        overlay.fill((20, 20, 40))
        self.screen.blit(overlay, card_rect)
        
        # Borde de la tarjeta
        pygame.draw.rect(self.screen, COLOR_AMARILLO if current_level["available"] else COLOR_ROJO, 
                        card_rect, 3)
        
        # Imagen de preview del nivel (si existe)
        preview_image = self.resource_manager.get_image(current_level["preview_image"])
        if preview_image:
            # Escalar imagen de preview
            preview_height = 150
            preview_width = int((preview_image.get_width() / preview_image.get_height()) * preview_height)
            scaled_preview = pygame.transform.scale(preview_image, (preview_width, preview_height))
            
            preview_x = card_x + (self.level_card_width - preview_width) // 2
            preview_y = card_y + 20
            
            self.screen.blit(scaled_preview, (preview_x, preview_y))
        else:
            # Placeholder si no hay imagen
            placeholder_rect = pygame.Rect(card_x + 20, card_y + 20, 
                                         self.level_card_width - 40, 120)
            pygame.draw.rect(self.screen, (60, 60, 80), placeholder_rect)
            
            font = self.resource_manager.get_font('subtitulo')
            if font:
                placeholder_text = font.render("Sin Preview", True, COLOR_BLANCO)
                text_rect = placeholder_text.get_rect(center=placeholder_rect.center)
                self.screen.blit(placeholder_text, text_rect)
        
        # Titulo del nivel
        font_titulo = self.resource_manager.get_font('subtitulo')
        if font_titulo:
            title_text = current_level["name"]
            title_surface = font_titulo.render(title_text, True, COLOR_AMARILLO)
            title_rect = title_surface.get_rect()
            title_rect.centerx = card_x + self.level_card_width // 2
            title_rect.y = card_y + 180
            self.screen.blit(title_surface, title_rect)
        
        # Descripcion del nivel
        font_desc = self.resource_manager.get_font('pequeña')
        if font_desc:
            desc_text = current_level["description"]
            desc_surface = font_desc.render(desc_text, True, COLOR_BLANCO)
            desc_rect = desc_surface.get_rect()
            desc_rect.centerx = card_x + self.level_card_width // 2
            desc_rect.y = title_rect.bottom + 20
            self.screen.blit(desc_surface, desc_rect)
        
        # Estado del nivel
        status_text = "Disponible" if current_level["available"] else "Bloqueado"
        status_color = COLOR_VERDE if current_level["available"] else COLOR_ROJO
        
        if font_desc:
            status_surface = font_desc.render(status_text, True, status_color)
            status_rect = status_surface.get_rect()
            status_rect.centerx = card_x + self.level_card_width // 2
            status_rect.y = desc_rect.bottom + 15
            self.screen.blit(status_surface, status_rect)
    
    def draw(self):
        """Dibuja la pantalla de seleccion de niveles"""
        # Fondo animado
        background_name = f"menu_background{self.current_background + 1}"
        background_image = self.resource_manager.get_image(background_name)
        
        if background_image:
            scaled_background = pygame.transform.scale(background_image, (ANCHO_PANTALLA, ALTO_PANTALLA))
            self.screen.blit(scaled_background, (0, 0))
        else:
            self.screen.fill(COLOR_FONDO_BASE)
        
        # Titulo principal
        font_titulo = self.resource_manager.get_font('titulo')
        if font_titulo:
            self._draw_bordered_text(
                "Selecciona Mision",
                font_titulo,
                (ANCHO_PANTALLA // 2, 80),
                COLOR_TITULO,
                (0, 0, 0),
                3
            )
        
        # Indicador de nivel actual
        font_indicador = self.resource_manager.get_font('boton')
        if font_indicador:
            level_indicator = f"{self.selected_level_index + 1} / {len(self.level_keys)}"
            indicator_surface = font_indicador.render(level_indicator, True, COLOR_AMARILLO)
            indicator_rect = indicator_surface.get_rect(center=(ANCHO_PANTALLA // 2, 140))
            self.screen.blit(indicator_surface, indicator_rect)
        
        # Tarjeta del nivel actual
        self._draw_level_card()
        
        # Instrucciones
        font_instrucciones = self.resource_manager.get_font('pequeña')
        if font_instrucciones:
            instructions = "← → para navegar • ENTER para seleccionar • ESC para volver"
            instr_surface = font_instrucciones.render(instructions, True, COLOR_TEXTO_SUTIL_EN_FONDO)
            instr_rect = instr_surface.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA - 40))
            self.screen.blit(instr_surface, instr_rect)
        
        # Botones
        for button in self.buttons:
            button.draw(self.screen)