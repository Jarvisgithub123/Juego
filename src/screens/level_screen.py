import pygame
import math
from src.Constantes import *
from src.core.scene_manager import Scene

class LevelScreen(Scene):
    """Pantalla de nivel con sistema de dialogos dinamico"""
    
    def __init__(self, screen, resource_manager, scene_manager):
        super().__init__(screen, resource_manager, scene_manager)
        
        # Configuracion de dialogos por nivel - Facil de extender
        self.dialogs_data = {
            "level_1": [
                {
                    "speaker": "character_a",
                    "name": "ARIA",
                    "text": "¡Por fin despiertas! Pense que no lo lograrias...",
                    "position": "left"
                },
                {
                    "speaker": "character_b", 
                    "name": "NEXUS",
                    "text": "El sistema de energia esta fallando. Necesitamos encontrar las baterias perdidas antes de que sea demasiado tarde.",
                    "position": "right"
                },
                {
                    "speaker": "character_a",
                    "name": "ARIA", 
                    "text": "¿Estas listo para esta mision, UAIBOT? El destino de nuestra ciudad digital depende de ti.",
                    "position": "left"
                },
                {
                    "speaker": "character_b",
                    "name": "NEXUS",
                    "text": "Recuerda: salta con ESPACIO, usa el dash con Z cuando tengas energia, y cambia entre nosotros con C si necesitas ayuda.",
                    "position": "right"
                }
            ],
            "level_2": [
                {
                    "speaker": "character_c",
                    "name": "ZARA",
                    "text": "Los datos que recuperaste revelan algo inquietante... hay mas de lo que pensabamos.",
                    "position": "left"
                },
                {
                    "speaker": "character_d",
                    "name": "CIPHER", 
                    "text": "La corrupcion se extiende mas alla de nuestra red. Debemos actuar rapido.",
                    "position": "right"
                },
                {
                    "speaker": "character_c",
                    "name": "ZARA",
                    "text": "Esta mision sera mas peligrosa. Los obstaculos han evolucionado. ¿Estas preparado?",
                    "position": "left"
                }
            ]
        }
        
        # Estado del dialogo
        self.current_dialog_index = 0
        self.dialog_finished = False
        self.text_animation_progress = 0
        self.text_animation_speed = 50  # caracteres por segundo
        self.waiting_for_input = False
        
        # Configuracion visual
        self.dialog_box_height = 200
        self.character_size = (150, 200)
        self.text_margin = 40
        
        # Obtener datos del nivel seleccionado
        self._load_level_data()
        
        # Timer para animacion de texto
        self.text_timer = 0
        
        # Estado de entrada para evitar spam
        self.enter_pressed = False
    
    def _load_level_data(self):
        """Carga los datos del nivel seleccionado"""
        self.level_key = 'level_1'  # Default
        self.level_data = {
            "background": "level1_bg", 
            "characters": ["character_a", "character_b"]
        }
        
        # Intentar obtener datos del level seleccionado
        try:
            if (hasattr(self.scene_manager, 'game_manager') and 
                self.scene_manager.game_manager and
                hasattr(self.scene_manager.game_manager, 'shared_data')):
                
                shared_data = self.scene_manager.game_manager.shared_data
                if 'selected_level' in shared_data:
                    self.level_key = shared_data['selected_level']
                if 'level_data' in shared_data:
                    self.level_data = shared_data['level_data']
                    
        except Exception as e:
            print(f"Error cargando datos del nivel: {e}")
        
        # Obtener dialogos para este nivel
        self.current_dialogs = self.dialogs_data.get(self.level_key, [])
    
    def on_enter(self):
        """Se ejecuta al entrar en la pantalla del nivel"""
        self.resource_manager.play_music("menu", volume=0.3)
    
    def handle_event(self, event):
        """Maneja los eventos de la pantalla"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if not self.enter_pressed:
                    self._advance_dialog()
                self.enter_pressed = True
            elif event.key == pygame.K_ESCAPE:
                self._skip_to_character_select()
        
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_RETURN:
                self.enter_pressed = False
    
    def _advance_dialog(self):
        """Avanza al siguiente dialogo o termina la secuencia"""
        if not self.waiting_for_input:
            # Si el texto aun se esta animando, completarlo instantaneamente
            if self.text_animation_progress < len(self._get_current_dialog_text()):
                self.text_animation_progress = len(self._get_current_dialog_text())
                self.waiting_for_input = True
            return
        
        # Avanzar al siguiente dialogo
        self.current_dialog_index += 1
        
        if self.current_dialog_index >= len(self.current_dialogs):
            # Terminar dialogos
            self.dialog_finished = True
            self._go_to_character_select()
        else:
            # Resetear animacion para el siguiente dialogo
            self.text_animation_progress = 0
            self.text_timer = 0
            self.waiting_for_input = False
    
    def _get_current_dialog_text(self):
        """Obtiene el texto del dialogo actual"""
        if (self.current_dialog_index < len(self.current_dialogs)):
            return self.current_dialogs[self.current_dialog_index]["text"]
        return ""
    
    def _get_current_dialog_data(self):
        """Obtiene todos los datos del dialogo actual"""
        if (self.current_dialog_index < len(self.current_dialogs)):
            return self.current_dialogs[self.current_dialog_index]
        return None
    
    def _go_to_character_select(self):
        """Transicion a la pantalla de seleccion de personajes"""
        from src.screens.character_screen import CharacterScreen
        self.scene_manager.change_scene(CharacterScreen)
    
    def _skip_to_character_select(self):
        """Saltar directamente a seleccion de personajes"""
        self._go_to_character_select()
    
    def update(self, dt):
        """Actualiza la logica de la pantalla"""
        if not self.dialog_finished and not self.waiting_for_input:
            # Actualizar animacion de texto
            self.text_timer += dt
            current_text = self._get_current_dialog_text()
            
            # Calcular progreso de animacion
            chars_to_show = int(self.text_timer * self.text_animation_speed)
            self.text_animation_progress = min(chars_to_show, len(current_text))
            
            # Marcar como esperando input cuando termine la animacion
            if self.text_animation_progress >= len(current_text):
                self.waiting_for_input = True
    
    def _draw_diamond_dialog_box(self):
        """Dibuja una caja de dialogo en forma de paralelogramo (antes rombo)"""
        box_width = ANCHO_PANTALLA - 100
        box_height = self.dialog_box_height
        box_x = 50
        box_y = ALTO_PANTALLA - box_height - 30

        # Crear superficie para el paralelogramo con transparencia
        dialog_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)

        # Desplazamiento para el slant del paralelogramo (ajustable)
        slant = max(20, int(box_width * 0.03))  # p.ej. 3% del ancho o al menos 20px

        # Puntos del paralelogramo (top-left hacia la derecha respecto al bottom-left)
        parallelogram_points = [
            (slant, 0),                 # Punto superior izquierdo (desplazado a la derecha)
            (box_width, 0),             # Punto superior derecho
            (box_width - slant, box_height),  # Punto inferior derecho (desplazado a la izquierda)
            (0, box_height)             # Punto inferior izquierdo
        ]

        # Dibujar sombra del paralelogramo (desplazada y con alpha)
        shadow_offset = 5
        shadow_points = [(x + shadow_offset, y + shadow_offset) for x, y in parallelogram_points]
        pygame.draw.polygon(dialog_surface, (0, 0, 0, 100), shadow_points)

        # Dibujar paralelogramo principal (fondo semi-transparente)
        pygame.draw.polygon(dialog_surface, (20, 25, 45, 220), parallelogram_points)

        # Dibujar borde del paralelogramo
        pygame.draw.polygon(dialog_surface, COLOR_AMARILLO, parallelogram_points, 3)

        # Aplicar la superficie a la pantalla
        self.screen.blit(dialog_surface, (box_x, box_y))

        return pygame.Rect(box_x, box_y, box_width, box_height)
    
    def _draw_dialog_text(self, dialog_rect):
        """Dibuja el texto del dialogo con animacion"""
        dialog_data = self._get_current_dialog_data()
        if not dialog_data:
            return
        
        # area de texto dentro del rombo
        text_area_width = dialog_rect.width - (self.text_margin * 2)
        text_area_height = dialog_rect.height - (self.text_margin * 2)
        text_x = dialog_rect.x + self.text_margin
        text_y = dialog_rect.y + self.text_margin
        
        # Nombre del hablante
        font_name = self.resource_manager.get_font('boton')
        if font_name:
            name_surface = font_name.render(dialog_data["name"], True, COLOR_AMARILLO)
            self.screen.blit(name_surface, (text_x, text_y))
        
        # Texto del dialogo (con animacion)
        font_dialog = self.resource_manager.get_font('pequeña')
        if font_dialog:
            # Obtener texto hasta el progreso actual
            full_text = dialog_data["text"]
            displayed_text = full_text[:self.text_animation_progress]
            
            # Dividir en lineas para texto multilinea
            words = displayed_text.split(' ')
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + word + " "
                test_surface = font_dialog.render(test_line, True, COLOR_BLANCO)
                
                if test_surface.get_width() <= text_area_width - 40:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line.strip())
                        current_line = word + " "
                    else:
                        lines.append(word)
                        current_line = ""
            
            if current_line:
                lines.append(current_line.strip())
            
            # Dibujar lineas
            line_height = font_dialog.get_height() + 5
            start_y = text_y + 50  # Debajo del nombre
            
            for i, line in enumerate(lines):
                if line.strip():
                    line_surface = font_dialog.render(line, True, COLOR_BLANCO)
                    self.screen.blit(line_surface, (text_x, start_y + i * line_height))
        
        # Indicador de "presiona Enter"
        if self.waiting_for_input:
            font_small = self.resource_manager.get_font('pequeña')
            if font_small:
                # Crear efecto de parpadeo
                alpha = int(127 * (1 + math.sin(pygame.time.get_ticks() * 0.005)))
                
                continue_text = "Presiona ENTER para continuar..."
                continue_surface = font_small.render(continue_text, True, COLOR_AMARILLO)
                continue_surface.set_alpha(alpha)
                
                continue_x = dialog_rect.right - continue_surface.get_width() - 30
                continue_y = dialog_rect.bottom - continue_surface.get_height() - 15
                self.screen.blit(continue_surface, (continue_x, continue_y))
    
    def _draw_characters(self):
        """Dibuja los personajes en pantalla (izquierda / derecha) con efecto segun quien hable"""
        dialog_data = self._get_current_dialog_data()
        if not dialog_data:
            return

        # Posiciones de los personajes
        left_char_x = 100
        right_char_x = ANCHO_PANTALLA - 250
        char_y = ALTO_PANTALLA - 400

        speaker_position = dialog_data.get("position", "left")

        # Obtener nombres de recursos para personajes desde level_data (fallback a keys conocidas)
        chars = self.level_data.get("characters", ["character_a", "character_b"])
        left_key = chars[0] if len(chars) > 0 else "character_a"
        right_key = chars[1] if len(chars) > 1 else "character_b"

        # Cargar y escalar imagenes (si estan disponibles)
        left_img = self.resource_manager.get_image(left_key)
        right_img = self.resource_manager.get_image(right_key)

        # Dibujar izquierdo
        if left_img:
            try:
                scaled_left = pygame.transform.smoothscale(left_img, self.character_size)
            except Exception:
                scaled_left = pygame.transform.scale(left_img, self.character_size)
            if speaker_position == "left":
                # brillo al hablar
                self.screen.blit(scaled_left, (left_char_x, char_y))
                glow = pygame.Surface(self.character_size, pygame.SRCALPHA)
                glow.fill((255, 255, 120, 40))
                self.screen.blit(glow, (left_char_x, char_y))
            else:
                # oscurecer si no habla
                dark = pygame.Surface(self.character_size, pygame.SRCALPHA)
                dark.fill((0, 0, 0, 120))
                self.screen.blit(scaled_left, (left_char_x, char_y))
                self.screen.blit(dark, (left_char_x, char_y))
        else:
            # placeholder
            placeholder_rect = pygame.Rect(left_char_x, char_y, *self.character_size)
            color = COLOR_AMARILLO if speaker_position == "left" else (100, 100, 100)
            pygame.draw.rect(self.screen, color, placeholder_rect)
            font = self.resource_manager.get_font('pequeña')
            if font:
                text = font.render("CHAR A", True, COLOR_BLANCO)
                text_rect = text.get_rect(center=placeholder_rect.center)
                self.screen.blit(text, text_rect)

        # Dibujar derecho
        if right_img:
            try:
                scaled_right = pygame.transform.smoothscale(right_img, self.character_size)
            except Exception:
                scaled_right = pygame.transform.scale(right_img, self.character_size)
            if speaker_position == "right":
                self.screen.blit(scaled_right, (right_char_x, char_y))
                glow = pygame.Surface(self.character_size, pygame.SRCALPHA)
                glow.fill((255, 255, 120, 40))
                self.screen.blit(glow, (right_char_x, char_y))
            else:
                dark = pygame.Surface(self.character_size, pygame.SRCALPHA)
                dark.fill((0, 0, 0, 120))
                self.screen.blit(scaled_right, (right_char_x, char_y))
                self.screen.blit(dark, (right_char_x, char_y))
        else:
            placeholder_rect = pygame.Rect(right_char_x, char_y, *self.character_size)
            color = COLOR_AMARILLO if speaker_position == "right" else (100, 100, 100)
            pygame.draw.rect(self.screen, color, placeholder_rect)
            font = self.resource_manager.get_font('pequeña')
            if font:
                text = font.render("CHAR B", True, COLOR_BLANCO)
                text_rect = text.get_rect(center=placeholder_rect.center)
                self.screen.blit(text, text_rect)
    
    def draw(self):
        """Dibuja la pantalla del nivel"""
        # Fondo del nivel
        background_image = self.resource_manager.get_image(self.level_data["background"])
        if background_image:
            try:
                scaled_background = pygame.transform.smoothscale(background_image, (ANCHO_PANTALLA, ALTO_PANTALLA))
            except Exception:
                scaled_background = pygame.transform.scale(background_image, (ANCHO_PANTALLA, ALTO_PANTALLA))
            self.screen.blit(scaled_background, (0, 0))
        else:
            # Fondo gradiente como fallback
            for y in range(ALTO_PANTALLA):
                color_intensity = int(30 + (y / ALTO_PANTALLA) * 50)
                color = (color_intensity, color_intensity // 2, color_intensity + 20)
                pygame.draw.line(self.screen, color, (0, y), (ANCHO_PANTALLA, y))
        # Dibujar personajes
        self._draw_characters()
        # Dibujar caja de dialogo
        if not self.dialog_finished:
            dialog_rect = self._draw_diamond_dialog_box()
            self._draw_dialog_text(dialog_rect)
