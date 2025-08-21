import pygame
import os
from typing import Dict, Optional

class SpriteSheet:
    """Maneja una hoja de sprites: calcula columnas/filas y recorta frames."""
    def __init__(self, surface, frame_width, frame_height):
        self.sheet = surface
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.columns = self.sheet.get_width() // frame_width
        self.rows = self.sheet.get_height() // frame_height

    def get_frame(self, col, row):
        """Devuelve un frame por (col, row)."""
        x = col * self.frame_width
        y = row * self.frame_height
        return self.sheet.subsurface((x, y, self.frame_width, self.frame_height))

    def get_row(self, row):
        """Devuelve todos los frames de una fila (para animaciones simples)."""
        return [self.get_frame(col, row) for col in range(self.columns)]
    
    def get_animation_frames(self, start_col, end_col, row):
        """Devuelve un rango de frames (col inicial→final) de una fila."""
        frames = []
        for col in range(start_col, end_col + 1):
            if col < self.columns:
                frames.append(self.get_frame(col, row))
        return frames


class ResourceManager:
    """Gestor central de recursos: imagenes, sonidos, fuentes, musica y sprites."""
    def __init__(self):
        # Colecciones por tipo de recurso (acceso por nombre/clave).
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.sprite_sheets: Dict[str, SpriteSheet] = {}
        
        # Sistema de musica .
        self.music_loaded = None          # ultima pista registrada
        self.music_tracks: Dict[str, str] = {}
        self.current_music_track = None
        self.music_volume = 0.7
        self.music_enabled = True
        
        # Fuentes por defecto .
        self._load_default_fonts()
    
    def _load_default_fonts(self):
        """Fuentes base para titulos, botones, HUD, etc."""
        self.fonts['titulo'] = pygame.font.Font("Assets/Fuentes/C&C Red Alert [INET].ttf", 90)
        self.fonts['subtitulo'] = pygame.font.Font("Assets/Fuentes/C&C Red Alert [INET].ttf", 40)
        self.fonts['boton'] = pygame.font.Font("Assets/Fuentes/C&C Red Alert [INET].ttf", 55)
        self.fonts['pequeña'] = pygame.font.Font("Assets/Fuentes/C&C Red Alert [INET].ttf", 32)
        self.fonts['hud'] = pygame.font.Font("Assets/Fuentes/C&C Red Alert [INET].ttf", 32)
        self.fonts['instrucciones'] = pygame.font.Font("Assets/Fuentes/C&C Red Alert [INET].ttf", 36)

    # ===== IMaGENES =====
    def load_image(self, name: str, path: str, convert_alpha: bool = True) -> bool:
        """Carga imagen desde disco y la registra con 'name' ."""
        try:
            if os.path.exists(path):
                image = pygame.image.load(path)
                image = image.convert_alpha() if convert_alpha else image.convert()
                self.images[name] = image
                return True
            else:
                print(f"Advertencia: No se encontro la imagen en {path}")
                return False
        except Exception as e:
            print(f"Error cargando imagen {path}: {e}")
            return False
    
    def get_image(self, name: str) -> Optional[pygame.Surface]:
        """Obtiene una imagen por nombre (o none si no existe)."""
        return self.images.get(name)
    
    def get_scaled_image(self, name: str, size: tuple) -> Optional[pygame.Surface]:
        """Devuelve una copia escalada si la imagen existe."""
        image = self.get_image(name)
        if image:
            return pygame.transform.scale(image, size)
        return None

    # ===== SPRITE SHEETS =====
    def load_spritesheet(self, name: str, path: str, frame_width: int, frame_height: int) -> bool:
        """Carga una hoja de sprites. Si falta, crea placeholder magenta (debug)."""
        try:
            if os.path.exists(path):
                image = pygame.image.load(path).convert_alpha()
                self.sprite_sheets[name] = SpriteSheet(image, frame_width, frame_height)
                print(f"Sprite sheet '{name}' cargado exitosamente: {self.sprite_sheets[name].columns}x{self.sprite_sheets[name].rows} frames")
                return True
            else:
                print(f"Advertencia: No se encontro el sprite sheet en {path}")
                placeholder = pygame.Surface((frame_width, frame_height))
                placeholder.fill((255, 0, 255))  # magenta = recurso faltante
                self.sprite_sheets[name] = SpriteSheet(placeholder, frame_width, frame_height)
                return False
        except Exception as e:
            print(f"Error cargando sprite sheet {path}: {e}")
            placeholder = pygame.Surface((frame_width, frame_height))
            placeholder.fill((255, 0, 255))
            self.sprite_sheets[name] = SpriteSheet(placeholder, frame_width, frame_height)
            return False
    
    def get_spritesheet(self, name: str) -> Optional[SpriteSheet]:
        """Obtiene la hoja de sprites por nombre."""
        return self.sprite_sheets.get(name)
    
    def get_sprite_frame(self, sheet_name: str, col: int, row: int) -> Optional[pygame.Surface]:
        """Atajo: devuelve un frame de una hoja si existe."""
        spritesheet = self.get_spritesheet(sheet_name)
        if spritesheet:
            return spritesheet.get_frame(col, row)
        return None
    
    def get_sprite_row(self, sheet_name: str, row: int) -> list:
        """Atajo: devuelve todos los frames de una fila."""
        spritesheet = self.get_spritesheet(sheet_name)
        if spritesheet:
            return spritesheet.get_row(row)
        return []
    
    def get_animation_frames(self, sheet_name: str, start_col: int, end_col: int, row: int) -> list:
        """Atajo: devuelve un rango de frames para animar."""
        spritesheet = self.get_spritesheet(sheet_name)
        if spritesheet:
            return spritesheet.get_animation_frames(start_col, end_col, row)
        return []

    # ===== SONIDOS  =====
    def load_sound(self, name: str, path: str) -> bool:
        """Carga un efecto de sonido y lo registra con 'name'."""
        try:
            if os.path.exists(path):
                sound = pygame.mixer.Sound(path)
                self.sounds[name] = sound
                return True
            else:
                print(f"Advertencia: No se encontro el sonido en {path}")
                return False
        except Exception as e:
            print(f"Error cargando sonido {path}: {e}")
            return False
    
    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Obtiene un sonido por nombre (o None)."""
        return self.sounds.get(name)
    
    def play_sound(self, name: str) -> bool:
        """Reproduce un sonido si esta cargado."""
        sound = self.get_sound(name)
        if sound:
            sound.play()
            return True
        return False

    # ===== MUSICA =====
    def load_music(self, name: str, path: str) -> bool:
        """Registra la ruta de una pista para reproducirla luego."""
        try:
            if os.path.exists(path):
                self.music_tracks[name] = path
                self.music_loaded = name  # recuerda la ultima
                print(f"Musica '{name}' registrada: {path}")
                return True
            else:
                print(f"Advertencia: No se encontro la musica en {path}")
                return False
        except Exception as e:
            print(f"Error registrando musica {path}: {e}")
            return False
    
    def play_music(self, name: str = None, loops: int = -1, volume: float = None, fade_ms: int = 0):
        """Reproduce una pista por nombre (con loops, volumen y fade opcionales)."""
        # Respeta el switch global de musica.
        if not getattr(self, 'music_enabled', True):
            print("Musica desactivada - no se reproducira")
            return False
            
        if volume is None:
            volume = getattr(self, 'music_volume', 0.7)
            
        # si no se pasa nombre, usa la actual o la uutima cargada.
        if name is None:
            if getattr(self, 'current_music_track', None):
                name = self.current_music_track
            elif self.music_loaded:
                name = self.music_loaded
                
        if name and name in self.music_tracks:
            try:
                current_track = getattr(self, 'current_music_track', None)

                # Solo recarga si es diferente o no hay musica sonando.
                if current_track != name or not pygame.mixer.music.get_busy():
                    path = self.music_tracks[name]
                    
                    # Si hay fade de salida, aplicarlo antes de cargar la nueva.
                    if pygame.mixer.music.get_busy() and fade_ms > 0:
                        pygame.mixer.music.fadeout(fade_ms)
                        pygame.time.wait(fade_ms)
                    
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.set_volume(volume)
                    pygame.mixer.music.play(loops)
                    self.current_music_track = name
                    print(f"Reproduciendo musica: {name}")
                    return True
                else:
                    # Si es la misma pista, solo ajusta el volumen.
                    pygame.mixer.music.set_volume(volume)
                    return True
            except Exception as e:
                print(f"Error reproduciendo musica {name}: {e}")
                return False
        elif name is None and self.music_tracks:
            # Sin nombre: reproduce la primera disponible.
            first_track = list(self.music_tracks.keys())[0]
            return self.play_music(first_track, loops, volume, fade_ms)
        else:
            print(f"Musica '{name}' no encontrada. Disponibles: {list(self.music_tracks.keys())}")
            return False
    
    def switch_music(self, name: str, fade_out_ms: int = 1000, fade_in_ms: int = 1000):
        """Cambia a otra pista aplicando un fade-out corto antes."""
        if name in self.music_tracks:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(fade_out_ms)
                pygame.time.wait(fade_out_ms)
            # Nota: el fade-in lo maneja play_music con volumen inicial si se quiere.
            self.play_music(name)
    
    def stop_music(self, fade_ms: int = 0):
        """Detiene la musica (con fade opcional)."""
        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()
        self.current_music_track = None
    
    def pause_music(self):
        """Pausa la reproduccion actual."""
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        """Reanuda la reproduccion si la musica esta habilitada."""
        if getattr(self, 'music_enabled', True):
            pygame.mixer.music.unpause()
            print("Musica reanudada")
        else:
            print("Musica desactivada - no se puede reanudar")
    
    def set_music_volume(self, volume: float):
        """Fija el volumen global de musica (0.0–1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def get_music_volume(self) -> float:
        """Devuelve el volumen actual de musica."""
        return getattr(self, 'music_volume', 0.7)
    
    def is_music_playing(self) -> bool:
        """Indica si hay musica sonando."""
        return pygame.mixer.music.get_busy()
    
    def get_current_music(self) -> Optional[str]:
        """Nombre de la pista actual (o None)."""
        return getattr(self, 'current_music_track', None)
    
    def get_available_music(self) -> list:
        """Lista de nombres de pistas registradas."""
        return list(self.music_tracks.keys())
    
    def enable_music(self, enabled: bool):
        """Activa/desactiva musica globalmente (detiene si se desactiva)."""
        self.music_enabled = enabled
        if not enabled:
            self.stop_music()
            print("Musica desactivada globalmente")
        else:
            print("Musica activada globalmente")
    
    # ===== FUENTES =====
    def get_font(self, name: str) -> Optional[pygame.font.Font]:
        """Obtiene una fuente por nombre (o None)."""
        return self.fonts.get(name)
    
    def load_font(self, name: str, path: str, size: int) -> bool:
        """Carga una fuente TTF/OTF; si falta, usa una por defecto del sistema."""
        try:
            if os.path.exists(path):
                font = pygame.font.Font(path, size)
                self.fonts[name] = font
                return True
            else:
                print(f"Advertencia: No se encontro la fuente en {path}")
                self.fonts[name] = pygame.font.Font(None, size)
                return False
        except Exception as e:
            print(f"Error cargando fuente {path}: {e}")
            self.fonts[name] = pygame.font.Font(None, size)
            return False
    
    def create_fallback_image(self, size: tuple, color: tuple) -> pygame.Surface:
        """Crea una imagen solida (placeholder o fondos simples)."""
        surface = pygame.Surface(size)
        surface.fill(color)
        return surface
    
    def get_resource_info(self) -> Dict[str, int]:
        """Resumen de recursos cargados (para logs o debug rapido)."""
        return {
            "images": len(self.images),
            "sounds": len(self.sounds),
            "fonts": len(self.fonts),
            "sprite_sheets": len(self.sprite_sheets),
            "music_tracks": len(self.music_tracks),
            "music_loaded": self.music_loaded is not None,
            "current_music": getattr(self, 'current_music_track', None)
        }
    
    def cleanup(self):
        """Limpia todo y detiene musica (para salir del juego ordenado)."""
        self.images.clear()
        self.sounds.clear()
        self.fonts.clear()
        self.sprite_sheets.clear()
        self.music_tracks.clear()
        self.current_music_track = None
        self.music_loaded = None
        pygame.mixer.music.stop()
        print("Recursos limpiados")
