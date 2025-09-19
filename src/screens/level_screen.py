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
                        "name": "UIABOT",
                        "text": """(Primer dia de trabajo, ya siento la electricidad en mis circuitos. Estara la maquina de cafe para robots?)""",
                        "position": "left",
                        "emotion": 1
                    },
                    {
                        "speaker": "character_b",
                        "name": "Supervisor Connor",
                        "text": "Bienvenido UIABOT, Soy Connor, tu supervisor. Te asignaron una entrega sencilla para empezar, nada de lujos.",
                        "position": "right"
                    },
                    {
                        "speaker": "character_a",
                        "name": "UIABOT",
                        "text": "Hola Connor, encantado de conocerte.",
                        "position": "left",
                        "emotion": 0
                    },
                    {
                        "speaker": "character_a",
                        "name": "UIABOT",
                        "text": "(Bien, un paquete misterioso. Ojala sea algo que salve a la humanidad... o al menos que tenga cafe.)",
                        "position": "left",
                        "emotion": 1
                    },
                    {
                        "speaker": "character_b",
                        "name": "Supervisor Connor",
                        "text": "Es un lote sobre stickers de manuales para shampoo. El cliente esta al norte de el distrito 67. Rapido y sin accidentes.",
                        "position": "right"
                    },
                    {
                        "speaker": "character_a",
                        "name": "UIABOT",
                        "text": "Manual de como no quedarse dormido mientras leo. Perfecto, lo entrego y vuelvo por mi cafe supervisor!.",
                        "position": "left"
                    },
                    {
                        "speaker": "character_b",
                        "name": "Supervisor Connor",
                        "text": "Eso si llegas a tiempo... Buena suerte.",
                        "position": "right"
                    },
                    {
                        "speaker": "character_b",
                        "name": "Supervisor Connor",
                        "text": "(Es normal que los robots tomen cafe? Espero que el cafe de la empresa no sea cafe oxidado, podria afectar sus circuitos...)",
                        "position": "right"
                    },
            ],
            "level_2": [
                    {
                        "speaker": "character_c",
                        "name": "Amigo del mago",
                        "text": "Gracias por venir, necesito tu ayuda para que lleves una cosa...",
                        "position": "left",
                        "emotion": 0 
                    },
                    {
                        "speaker": "character_a",
                        "name": "UIAbot",
                        "text": "Claro, ese es mi trabaj... ¿Una paloma robotica? Parece muy real..",
                        "position": "right",
                        "emotion": 0
                    },
                    {
                        "speaker": "character_c",
                        "name": "Amigo del mago",
                        "text": "Es un proyecto especial del club de inventores. Solo llevalo antes del show...",
                        "position": "left",
                        "emotion": 1
                    },
                    {
                        "speaker": "character_a",
                        "name": "UIAbot",
                        "text": "Perfecto, Mision: Entregar una paloma que probablemente tiene camaras instaladas...",
                        "position": "right",
                        "emotion": 3   # emocion 2 -> frames 4 / 5
                    },
                    {
                        "speaker": "character_a",
                        "name": "UIAbot",
                        "text": "(Nota mental: Todas las palomas son asi? deberia investigar en mi base de datos... )",
                        "position": "right",
                        "emotion": 2
                    },
            ],
            "level_3": [
                {
                    "speaker": "character_a",
                    "name": "UIABOT",
                    "text": "Mi segundo encargo oficial es llevar croquetas premium a un gato... robot. Que honor.",
                    "position": "right"
                },
                {
                    "speaker": "character_a",
                    "name": "UIABOT",
                    "text": "(Ojala me hubieran fabricado como un gato robot... y no como un robot repartidor)",
                    "position": "right",
                    "emotion": 1
                    
                },
                {
                    "speaker": "character_d",
                    "name": "Claire Bluefield",
                    "text": "¡No es cualquier gato!",
                    "position": "left"
                },
                {
                    "speaker": "character_d",
                    "name": "Claire Bluefield",
                    "text": "Es MishiBot, la estrella de mis streams. La gente paga por verlo comer, por jugar.",
                    "position": "left",
                    "emotion": 1
                    
                },
                {
                    "speaker": "character_a",
                    "name": "UIABOT",
                    "text": "Genial. Yo entrenando miles de protocolos de precision,salto y termino como repartidor en vez de un felino famoso...",
                    "position": "right",
                    "emotion": 4
                },
                {
                    "speaker": "character_d",
                    "name": "Claire Bluefield",
                    "text": "Apurate! Si tardo en la entrega... pierdo a los viewers del chat. Y sin ellos, no soy nada!!!.",
                    "position": "left"
                },
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
        self.character_size = (450, 780)
        self.text_margin = 40
        
        # Obtener datos del nivel seleccionado
        self._load_level_data()
        
        # Timer para animacion de texto
        self.text_timer = 0
        
        # Estado de entrada para evitar spam
        self.enter_pressed = False
        
        # cache de frames por personaje (frames ya escalados a character_size)
        self._char_frames_cache = {}  # key -> [Surface, Surface, ...]
        # intervalo (ms) entre alternar boca abierta/cerrada mientras habla
        self._talk_frame_interval_ms = 160
    
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
        self.resource_manager.play_music("level_music", volume=0.3)
    
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
            # Asegurar que el modo este configurado como mision
            try:
                if (hasattr(self.scene_manager, 'game_manager') and 
                    self.scene_manager.game_manager and
                    hasattr(self.scene_manager.game_manager, 'shared_data')):
                    
                    if not hasattr(self.scene_manager.game_manager, 'shared_data'):
                        self.scene_manager.game_manager.shared_data = {}
                    
                    # Configurar modo mision
                    self.scene_manager.game_manager.shared_data['game_mode'] = 'mission'
                    print("Modo configurado como mision")
                    
            except Exception as e:
                print(f"Error configurando modo mision: {e}")
                
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
        
        # Definir colores por si no estan en constantes
        color_amarillo = (255, 255, 0)
        color_blanco = (255, 255, 255)
        
        # Nombre del hablante
        font_name = self.resource_manager.get_font('boton')
        if font_name:
            name_surface = font_name.render(dialog_data["name"], True, color_amarillo)
            self.screen.blit(name_surface, (text_x, text_y))
        
        # Texto del dialogo (con animacion)
        font_dialog = self.resource_manager.get_font('pequeña')  # Corregir el caracter especial
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
                test_surface = font_dialog.render(test_line, True, color_blanco)
                
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
                    line_surface = font_dialog.render(line, True, color_blanco)
                    self.screen.blit(line_surface, (text_x, start_y + i * line_height))
        
        # Indicador de "presiona Enter"
        if self.waiting_for_input:
            font_small = self.resource_manager.get_font('pequeña')  # Corregir el caracter especial
            if font_small:
                # Crear efecto de parpadeo
                alpha = int(127 * (1 + math.sin(pygame.time.get_ticks() * 0.005)))
                
                continue_text = "Presiona ENTER para continuar..."
                continue_surface = font_small.render(continue_text, True, color_amarillo)
                continue_surface.set_alpha(alpha)
                
                continue_x = dialog_rect.right - continue_surface.get_width() - 30
                continue_y = dialog_rect.bottom - continue_surface.get_height() - 15
                self.screen.blit(continue_surface, (continue_x, continue_y))
    
    def _get_scaled_frames_for(self, key: str):
        """
        Obtiene lista de frames escalados a self.character_size para 'key'.
        Busca hoja de sprites con resource_manager.get_spritesheet(key) o imagen simple.
        """
        if key in self._char_frames_cache:
            return self._char_frames_cache[key]

        frames = []
        # intentar spritesheet primero (ResourceManager.load_spritesheet guarda en sprite_sheets)
        sheet = None
        try:
            sheet = self.resource_manager.get_spritesheet(key)
        except Exception:
            sheet = None

        if sheet:
            # obtener todos los frames de la primera fila (row 0)
            cols = sheet.columns
            for c in range(cols):
                try:
                    f = sheet.get_frame(c, 0).copy()
                except Exception:
                    continue
                # escalar al tamaño objetivo
                try:
                    f = pygame.transform.smoothscale(f, self.character_size)
                except Exception:
                    f = pygame.transform.scale(f, self.character_size)
                frames.append(f.convert_alpha() if f.get_flags() & pygame.SRCALPHA else f.convert())
        else:
            # fallback: usar imagen estatica si existe
            img = self.resource_manager.get_image(key)
            if img:
                try:
                    f = pygame.transform.smoothscale(img, self.character_size)
                except Exception:
                    f = pygame.transform.scale(img, self.character_size)
                frames = [f.convert_alpha() if f.get_flags() & pygame.SRCALPHA else f.convert()]

        self._char_frames_cache[key] = frames
        return frames

    def _draw_characters(self):
        """Dibuja los personajes en pantalla: usa spritesheet para hablar segÃºn 'emotion'."""
        dialog_data = self._get_current_dialog_data()
        if not dialog_data:
            return

        # Posiciones de los personajes
        left_char_x = 30
        right_char_x = ANCHO_PANTALLA - 450
        char_y = ALTO_PANTALLA - 600

        speaker_position = dialog_data.get("position", "left")

        # Obtener keys de personajes
        chars = self.level_data.get("characters", ["character_a", "character_b"])
        left_key = chars[0] if len(chars) > 0 else "character_a"
        right_key = chars[1] if len(chars) > 1 else "character_b"

        # obtener frames escalados (cache)
        left_frames = self._get_scaled_frames_for(left_key)
        right_frames = self._get_scaled_frames_for(right_key)

        # SOLUCION: Determinar quien habla basado en position y aplicar emotion solo al hablante
        dialog_speaker_key = dialog_data.get("speaker")
        dialog_emotion = dialog_data.get("emotion", 0)
        
        # Solo el hablante recibe la emocion del dialogo
        left_emotion = None
        right_emotion = None
        
        # Determinar quien habla basado en la posicion
        if speaker_position == "left":
            left_emotion = dialog_emotion
            # El personaje de la derecha no habla, no tiene emocion especial
        elif speaker_position == "right":
            right_emotion = dialog_emotion
            # El personaje de la izquierda no habla, no tiene emocion especial

        # Helpers para indices open/closed segun emotion
        def _frame_indices(frames, emotion_idx):
            # Si emotion_idx es None => usar base (0/1) - personaje en reposo
            if not frames:
                return (None, None)
            if emotion_idx is None:
                # personaje no hablante: usar frames de reposo (0/1)
                if len(frames) > 1:
                    return (0, 1)
                return (0, 0)
            # personaje hablante: usar frames segun su emocion
            open_i = emotion_idx * 2
            closed_i = open_i + 1
            # si no hay closed_i, fallback a 0/1 o 0
            if closed_i >= len(frames):
                if len(frames) > 1:
                    return (0, 1)
                else:
                    return (0, 0)
            return (open_i, closed_i)

        # determinar si estamos en fase de hablar (animando texto) -> alternar
        is_animating = not self.waiting_for_input
        now = pygame.time.get_ticks()
        toggle_open = ((now // self._talk_frame_interval_ms) % 2) == 0

        # renderizado para quien habla: alterna entre open/closed mientras animando, termina en closed
        def render_speaking(frames, pos_x, pos_y, emotion_idx):
            if not frames:
                # placeholder si no hay frames
                rect = pygame.Rect(pos_x, pos_y, *self.character_size)
                pygame.draw.rect(self.screen, COLOR_AMARILLO, rect)
                return
            open_i, closed_i = _frame_indices(frames, emotion_idx)
            # elegir Ã­ndice
            if is_animating:
                idx = open_i if toggle_open else closed_i
            else:
                idx = closed_i
            if idx is None or idx >= len(frames):
                idx = 0
            frame = frames[idx]
            self.screen.blit(frame, (pos_x, pos_y))

        # renderizado para quien NO habla: dibuja version reducida y aplica mascara oscurecedora
        def render_not_speaking(frames, pos_x, pos_y, emotion_idx):
            # si hay frames, usar closed frame y reescalar un poco mas chiquito
            target_w, target_h = self.character_size
            scale = 0.90
            small_w = max(1, int(target_w * scale))
            small_h = max(1, int(target_h * scale))
            if frames:
                _, closed_i = _frame_indices(frames, emotion_idx)
                if closed_i is None or closed_i >= len(frames):
                    closed_i = 0
                frame = frames[closed_i]
                try:
                    small_frame = pygame.transform.smoothscale(frame, (small_w, small_h))
                except Exception:
                    small_frame = pygame.transform.scale(frame, (small_w, small_h))
                offset_x = pos_x + (target_w - small_w) // 2
                offset_y = pos_y + (target_h - small_h) // 2
                self.screen.blit(small_frame, (offset_x, offset_y))
                # overlay oscuro usando mascara del sprite reducido
                try:
                    mask = pygame.mask.from_surface(small_frame)
                    mask_surf = mask.to_surface(setcolor=(0,0,0,255), unsetcolor=(0,0,0,0)).convert_alpha()
                    mask_surf.set_alpha(120)
                    self.screen.blit(mask_surf, (offset_x, offset_y))
                except Exception:
                    dark = pygame.Surface((small_w, small_h), pygame.SRCALPHA)
                    dark.fill((0,0,0,120))
                    self.screen.blit(dark, (offset_x, offset_y))
            else:
                # placeholder reducido + oscuro
                offset_x = pos_x + int(self.character_size[0] * 0.05)
                offset_y = pos_y + int(self.character_size[1] * 0.05)
                pygame.draw.rect(self.screen, (100,100,100), (offset_x, offset_y, small_w, small_h))
                dark = pygame.Surface((small_w, small_h), pygame.SRCALPHA)
                dark.fill((0,0,0,120))
                self.screen.blit(dark, (offset_x, offset_y))

        # Dibujar izquierdo / derecho segun quien habla
        if speaker_position == "left":
            render_speaking(left_frames, left_char_x, char_y, left_emotion)
            render_not_speaking(right_frames, right_char_x, char_y, right_emotion)
        else:
            render_not_speaking(left_frames, left_char_x, char_y, left_emotion)
            render_speaking(right_frames, right_char_x, char_y, right_emotion)
    
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