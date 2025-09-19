import pygame
from src.Constantes import *
from src.core.scene_manager import Scene
from src.UI.button import Button
from src.systems.ability_system import ability_system  # agregado

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
            },
            "level_2": {
                "name": "Duermen los androides con palomas espias?",
                "description": "Uiabot debe entregar una paloma mensajera sospechosa.",
                "background": "level2_bg", 
                "available": True,
                "characters": ["character_c", "character_a"],  # incluir character_a para que coincida con los dialogos
                
            },
            "level_3": {
                "name": "The Legend of Mishi",
                "description": "Otra mision con Uiabot \n esta vez debe entregar un paquete a un gato famoso.",
                "background": "level3_bg", 
                "available": True,
                "characters": ["character_d", "character_a"],  # incluir character_a para que coincida con los dialogos
                
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
        # Recuadro un poco más grande
        self.level_card_width = 780
        self.level_card_height = 360
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
        
        # Boton para borrar progreso (esquina inferior derecha)
        # Hacer el boton ligeramente mas grande
        delete_w = 360
        delete_h = 60
        delete_x = ANCHO_PANTALLA - delete_w - 5
        delete_y = ALTO_PANTALLA - delete_h - 10
        self.delete_progress_button = Button("Borrar Progreso", delete_x, delete_y, delete_w, delete_h,
                                            self.resource_manager, self._reset_progress)
        self.buttons.append(self.delete_progress_button)
 

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
    
    def _reset_progress(self):
        """Callback para borrar el progreso guardado"""
        try:
            ability_system.reset_progress()
            ability_system.load_progress()
            # feedback audible si existe el sonido
            try:
                self.resource_manager.play_sound("boton_hover")
            except Exception:
                pass
            print("Progreso borrado desde la pantalla de seleccion de niveles.")
        except Exception as e:
            print(f"Error borrando progreso: {e}")
    
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
        
        # Badge "COMPLETADO" si la mision ya fue completada
        completed = current_level_key in ability_system.get_completed_missions()
        if completed:
            badge_w = 160
            badge_h = 36
            badge_x = card_x + self.level_card_width - badge_w - 20
            badge_y = card_y + 20
            # recto sólido y texto blanco
            pygame.draw.rect(self.screen, COLOR_VERDE, (badge_x, badge_y, badge_w, badge_h), border_radius=6)
            font_badge = self.resource_manager.get_font('pequeña')
            if font_badge:
                txt = font_badge.render("COMPLETADO", True, COLOR_BLANCO)
                txt_rect = txt.get_rect(center=(badge_x + badge_w // 2, badge_y + badge_h // 2))
                self.screen.blit(txt, txt_rect)
        
        title_y = card_y + 60
        desc_y = card_y + 140
		
        font_titulo = self.resource_manager.get_font('subtitulo')
        if font_titulo:
            title_text = current_level["name"]
            title_surface = font_titulo.render(title_text, True, COLOR_AMARILLO)
            title_rect = title_surface.get_rect()
            title_rect.centerx = card_x + self.level_card_width // 2
            title_rect.y = title_y
            self.screen.blit(title_surface, title_rect)
        else:
            # fallback rápido por si no hay fuente cargada
            fallback = pygame.font.SysFont(None, 28)
            title_surface = fallback.render(current_level["name"], True, COLOR_AMARILLO)
            title_rect = title_surface.get_rect(center=(card_x + self.level_card_width // 2, title_y))
            self.screen.blit(title_surface, title_rect)
        
        # Descripcion del nivel (soporta '\n' y wrapping)
        font_desc = self.resource_manager.get_font('pequeña')
        if font_desc:
            desc_text = current_level["description"]
            # ancho máximo para las líneas (margen dentro del recuadro)
            max_width = self.level_card_width - 80
            lines = []
            # Primero separar por párrafos (salto explícito '\n')
            for paragraph in desc_text.split('\n'):
                words = paragraph.split(' ')
                current_line = ""
                for word in words:
                    if current_line == "":
                        test_line = word
                    else:
                        test_line = current_line + " " + word
                    # medir ancho de la línea tentativa
                    line_width = font_desc.size(test_line)[0]
                    if line_width <= max_width:
                        current_line = test_line
                    else:
                        if current_line != "":
                            lines.append(current_line)
                        # comenzar nueva línea con la palabra actual
                        current_line = word
                if current_line:
                    lines.append(current_line)
            # Renderizar líneas centradas
            line_height = font_desc.get_height() + 6
            start_y = desc_y
            for i, line in enumerate(lines):
                line_surf = font_desc.render(line, True, COLOR_BLANCO)
                line_rect = line_surf.get_rect(center=(card_x + self.level_card_width // 2, start_y + i * line_height))
                self.screen.blit(line_surf, line_rect)
            # calcular bottom de bloque de texto para posicionar estado
            text_block_bottom = start_y + len(lines) * line_height
        else:
            text_block_bottom = desc_y
        
        # Estado del nivel (Disponible / Bloqueado / Completado)
        if completed:
            status_text = "Completado"
            status_color = COLOR_VERDE
        else:
            status_text = "Disponible" if current_level["available"] else "Bloqueado"
            status_color = COLOR_VERDE if current_level["available"] else COLOR_ROJO
        
        # dibujar estado con fallback si es necesario
        if font_desc:
            status_surface = font_desc.render(status_text, True, status_color)
            status_rect = status_surface.get_rect()
            status_rect.centerx = card_x + self.level_card_width // 2
            status_rect.y = text_block_bottom + 30
            self.screen.blit(status_surface, status_rect)
        else:
            fallback = pygame.font.SysFont(None, 20)
            status_surface = fallback.render(status_text, True, status_color)
            status_rect = status_surface.get_rect(center=(card_x + self.level_card_width // 2, text_block_bottom + 30))
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
        
        # Titulo principal (uso de fallback si falta la fuente)
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
        else:
            fb = pygame.font.SysFont(None, 48)
            txt = fb.render("Selecciona Mision", True, COLOR_TITULO)
            self.screen.blit(txt, txt.get_rect(center=(ANCHO_PANTALLA // 2, 80)))

        # Indicador de nivel actual (usar color contrastante)
        font_indicador = self.resource_manager.get_font('boton')
        if font_indicador:
            level_indicator = f"{self.selected_level_index + 1} / {len(self.level_keys)}"
            indicator_surface = font_indicador.render(level_indicator, True, COLOR_AMARILLO)
            indicator_rect = indicator_surface.get_rect(center=(ANCHO_PANTALLA // 2, 140))
            self.screen.blit(indicator_surface, indicator_rect)
        else:
            fb = pygame.font.SysFont(None, 24)
            level_indicator = f"{self.selected_level_index + 1} / {len(self.level_keys)}"
            indicator_surface = fb.render(level_indicator, True, COLOR_AMARILLO)
            self.screen.blit(indicator_surface, indicator_surface.get_rect(center=(ANCHO_PANTALLA // 2, 140)))
        
        # Tarjeta del nivel actual
        self._draw_level_card()
        
        # Instrucciones (con fallback)
        font_instrucciones = self.resource_manager.get_font('pequeña')
        if font_instrucciones:
            instructions = "← → para navegar • ENTER para seleccionar • ESC para volver"
            instr_surface = font_instrucciones.render(instructions, True, COLOR_TEXTO_SUTIL_EN_FONDO)
            instr_rect = instr_surface.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA - 40))
            self.screen.blit(instr_surface, instr_rect)
        else:
            fb = pygame.font.SysFont(None, 20)
            instr_surface = fb.render("← → para navegar • ENTER para seleccionar • ESC para volver", True, COLOR_TEXTO_SUTIL_EN_FONDO)
            self.screen.blit(instr_surface, instr_surface.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA - 40)))
        
        # Botones: intentar dibujar con la implementación Button; si falla, dibujar fallback para el botón de borrar
        # Intentar dibujar cada botón y detectar si el botón de borrar se dibujó correctamente
        delete_draw_ok = False
        for button in self.buttons:
            if button is self.delete_progress_button:
                try:
                    button.draw(self.screen)
                    delete_draw_ok = True
                except Exception:
                    delete_draw_ok = False
            else:
                try:
                    button.draw(self.screen)
                except Exception:
                    # ignorar error en draw de otros botones
                    pass

        # Solo dibujar fallback para el botón "Borrar Progreso" si su draw() falló o no existe
        if not delete_draw_ok:
            rect = getattr(self, 'delete_progress_rect', None)
            if rect:
                # Dibujar fondo y borde fallback
                pygame.draw.rect(self.screen, (60, 60, 60), rect, border_radius=6)
                pygame.draw.rect(self.screen, (100, 100, 100), rect, 2, border_radius=6)
                # Texto del botón (fallback font)
                fb = pygame.font.SysFont(None, 16)  # texto más pequeño
                label = getattr(self, 'delete_progress_label', "Borrar Progreso")
                txt = fb.render(label, True, COLOR_BLANCO)
                self.screen.blit(txt, txt.get_rect(center=rect.center))
        else:
            # Si el Button.draw se ejecutó correctamente, sobreescribimos la etiqueta
            # con una fuente más pequeña para asegurar el tamaño deseado.
            rect = getattr(self, 'delete_progress_rect', None)
            if rect:
                fb_small = pygame.font.SysFont(None, 16)
                label = getattr(self, 'delete_progress_label', "Borrar Progreso")
                txt = fb_small.render(label, True, COLOR_BLANCO)
                self.screen.blit(txt, txt.get_rect(center=rect.center))