import pygame
import os
from typing import Dict, Optional

class SpriteSheet:
    def __init__(self, surface, frame_width, frame_height):
        self.sheet = surface
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.columns = self.sheet.get_width() // frame_width
        self.rows = self.sheet.get_height() // frame_height

    def get_frame(self, col, row):
        """Obtiene un frame específico por columna y fila"""
        x = col * self.frame_width
        y = row * self.frame_height
        return self.sheet.subsurface((x, y, self.frame_width, self.frame_height))

    def get_row(self, row):
        return [self.get_frame(col, row) for col in range(self.columns)]
    
    def get_animation_frames(self, start_col, end_col, row):
        frames = []
        for col in range(start_col, end_col + 1):
            if col < self.columns:
                frames.append(self.get_frame(col, row))
        return frames

class ResourceManager:
    """Gestor de recursos del juego (imagenes, sonidos, música, sprite sheets, etc.)"""
    def __init__(self):
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.sprite_sheets: Dict[str, SpriteSheet] = {}
        
        # Mantener compatibilidad con código existente
        self.music_loaded = None
        
        # Nuevo sistema para manejar múltiples músicas
        self.music_tracks: Dict[str, str] = {}
        self.current_music_track = None
        self.music_volume = 0.7
        self.music_enabled = True
        
        self._load_default_fonts()
    
    def _load_default_fonts(self):
        self.fonts['titulo'] = pygame.font.Font(None, 90)
        self.fonts['subtitulo'] = pygame.font.Font(None, 40)
        self.fonts['boton'] = pygame.font.Font(None, 55)
        self.fonts['pequena'] = pygame.font.Font(None, 32)
        self.fonts['hud'] = pygame.font.SysFont(None, 32)
        self.fonts['instrucciones'] = pygame.font.SysFont(None, 36)

    def load_image(self, name: str, path: str, convert_alpha: bool = True) -> bool:
        try:
            if os.path.exists(path):
                image = pygame.image.load(path)
                if convert_alpha:
                    image = image.convert_alpha()
                else:
                    image = image.convert()
                self.images[name] = image
                return True
            else:
                print(f"Advertencia: No se encontró la imagen en {path}")
                return False
        except Exception as e:
            print(f"Error cargando imagen {path}: {e}")
            return False
    
    def get_image(self, name: str) -> Optional[pygame.Surface]:
        return self.images.get(name)
    
    def get_scaled_image(self, name: str, size: tuple) -> Optional[pygame.Surface]:
        """Obtiene una imagen escalada"""
        image = self.get_image(name)
        if image:
            return pygame.transform.scale(image, size)
        return None
    
    def load_spritesheet(self, name: str, path: str, frame_width: int, frame_height: int) -> bool:
        """Carga una hoja de sprites y la almacena con el nombre dado"""
        try:
            if os.path.exists(path):
                image = pygame.image.load(path).convert_alpha()
                self.sprite_sheets[name] = SpriteSheet(image, frame_width, frame_height)
                print(f"Sprite sheet '{name}' cargado exitosamente: {self.sprite_sheets[name].columns}x{self.sprite_sheets[name].rows} frames")
                return True
            else:
                print(f"Advertencia: No se encontró el sprite sheet en {path}")
                # Crear placeholder para debug
                placeholder = pygame.Surface((frame_width, frame_height))
                placeholder.fill((255, 0, 255))  # Magenta para debug
                self.sprite_sheets[name] = SpriteSheet(placeholder, frame_width, frame_height)
                return False
        except Exception as e:
            print(f"Error cargando sprite sheet {path}: {e}")
            # Crear placeholder para debug
            placeholder = pygame.Surface((frame_width, frame_height))
            placeholder.fill((255, 0, 255))  # Magenta para debug
            self.sprite_sheets[name] = SpriteSheet(placeholder, frame_width, frame_height)
            return False
    
    def get_spritesheet(self, name: str) -> Optional[SpriteSheet]:
        """Obtiene una hoja de sprites por su nombre"""
        return self.sprite_sheets.get(name)
    
    def get_sprite_frame(self, sheet_name: str, col: int, row: int) -> Optional[pygame.Surface]:
        """Obtiene un frame específico de una sprite sheet"""
        spritesheet = self.get_spritesheet(sheet_name)
        if spritesheet:
            return spritesheet.get_frame(col, row)
        return None
    
    def get_sprite_row(self, sheet_name: str, row: int) -> list:
        """Obtiene toda una fila de frames de una sprite sheet"""
        spritesheet = self.get_spritesheet(sheet_name)
        if spritesheet:
            return spritesheet.get_row(row)
        return []
    
    def get_animation_frames(self, sheet_name: str, start_col: int, end_col: int, row: int) -> list:
        """Obtiene un rango de frames para animación de una sprite sheet"""
        spritesheet = self.get_spritesheet(sheet_name)
        if spritesheet:
            return spritesheet.get_animation_frames(start_col, end_col, row)
        return []
    
    def load_sound(self, name: str, path: str) -> bool:
        """Carga un sonido y lo almacena con el nombre dado"""
        try:
            if os.path.exists(path):
                sound = pygame.mixer.Sound(path)
                self.sounds[name] = sound
                return True
            else:
                print(f"Advertencia: No se encontró el sonido en {path}")
                return False
        except Exception as e:
            print(f"Error cargando sonido {path}: {e}")
            return False
    
    def get_sound(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Obtiene un sonido por su nombre"""
        return self.sounds.get(name)
    
    def play_sound(self, name: str) -> bool:
        """Reproduce un sonido"""
        sound = self.get_sound(name)
        if sound:
            sound.play()
            return True
        return False
    
    # ===== MÉTODOS PARA MÚSICA  =====
    def load_music(self, name: str, path: str) -> bool:
        #Carga una pista de música y la almacena con el nombre dado
        try:
            if os.path.exists(path):
                self.music_tracks[name] = path
                # Mantener compatibilidad: establecer music_loaded al último cargado
                self.music_loaded = name
                print(f"Música '{name}' registrada: {path}")
                return True
            else:
                print(f"Advertencia: No se encontró la música en {path}")
                return False
        except Exception as e:
            print(f"Error registrando música {path}: {e}")
            return False
    
    def play_music(self, name: str = None, loops: int = -1, volume: float = None, fade_ms: int = 0):
        """Reproduce una música específica por nombre"""
        if not getattr(self, 'music_enabled', True):
            print("Música desactivada - no se reproducirá")
            return False
            
        if volume is None:
            volume = getattr(self, 'music_volume', 0.7)
            
        # Compatibilidad: si no se especifica nombre, usar el último cargado
        if name is None:
            if hasattr(self, 'current_music_track') and self.current_music_track:
                name = self.current_music_track
            elif self.music_loaded:
                name = self.music_loaded
                
        if name and name in self.music_tracks:
            try:
                # Solo cambiar música si es diferente a la actual
                current_track = getattr(self, 'current_music_track', None)
                if current_track != name or not pygame.mixer.music.get_busy():
                    path = self.music_tracks[name]
                    
                    # Detener música actual si hay fade
                    if pygame.mixer.music.get_busy() and fade_ms > 0:
                        pygame.mixer.music.fadeout(fade_ms)
                        pygame.time.wait(fade_ms)
                    
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.set_volume(volume)
                    pygame.mixer.music.play(loops)
                    self.current_music_track = name
                    
                    print(f"Reproduciendo música: {name}")
                    return True
                else:
                    # Solo ajustar volumen si es la misma música
                    pygame.mixer.music.set_volume(volume)
                    return True
            except Exception as e:
                print(f"Error reproduciendo música {name}: {e}")
                return False
        elif name is None and self.music_tracks:
            # Reproducir cualquier música disponible si no se especifica
            first_track = list(self.music_tracks.keys())[0]
            return self.play_music(first_track, loops, volume, fade_ms)
        else:
            print(f"Música '{name}' no encontrada. Disponibles: {list(self.music_tracks.keys())}")
            return False
    
    def switch_music(self, name: str, fade_out_ms: int = 1000, fade_in_ms: int = 1000):
        """Cambia de una música a otra con efectos de fade"""
        if name in self.music_tracks:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(fade_out_ms)
                pygame.time.wait(fade_out_ms)
            
            self.play_music(name)
    
    def stop_music(self, fade_ms: int = 0):
        """Detiene la música"""
        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()
        if hasattr(self, 'current_music_track'):
            self.current_music_track = None
    
    def pause_music(self):
        """Pausa la música"""
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        """Reanuda la música"""
        if getattr(self, 'music_enabled', True):
            pygame.mixer.music.unpause()
            print("Música reanudada")
        else:
            print("Música desactivada - no se puede reanudar")
    
    def set_music_volume(self, volume: float):
        """Establece el volumen de la música (0.0 - 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def get_music_volume(self) -> float:
        """Obtiene el volumen actual de la música"""
        return getattr(self, 'music_volume', 0.7)
    
    def is_music_playing(self) -> bool:
        """Verifica si se está reproduciendo música"""
        return pygame.mixer.music.get_busy()
    
    def get_current_music(self) -> Optional[str]:
        """Obtiene el nombre de la música actual"""
        return getattr(self, 'current_music_track', None)
    
    def get_available_music(self) -> list:
        """Obtiene lista de músicas disponibles"""
        return list(self.music_tracks.keys())
    
    def enable_music(self, enabled: bool):
        """Habilita o deshabilita la música"""
        self.music_enabled = enabled
        if not enabled:
            self.stop_music()
            print("Música desactivada globalmente")
        else:
            print("Música activada globalmente")
    
    # ===== MÉTODOS PARA FUENTES =====
    def get_font(self, name: str) -> Optional[pygame.font.Font]:
        """Obtiene una fuente por su nombre"""
        return self.fonts.get(name)
    
    def load_font(self, name: str, path: str, size: int) -> bool:
        """Carga una fuente personalizada"""
        try:
            if os.path.exists(path):
                font = pygame.font.Font(path, size)
                self.fonts[name] = font
                return True
            else:
                print(f"Advertencia: No se encontró la fuente en {path}")
                # Usar fuente por defecto
                self.fonts[name] = pygame.font.Font(None, size)
                return False
        except Exception as e:
            print(f"Error cargando fuente {path}: {e}")
            # Usar fuente por defecto
            self.fonts[name] = pygame.font.Font(None, size)
            return False
    
    # ===== MÉTODOS UTILITARIOS =====
    def create_fallback_image(self, size: tuple, color: tuple) -> pygame.Surface:
        """Crea una imagen de respaldo"""
        surface = pygame.Surface(size)
        surface.fill(color)
        return surface
    
    def get_resource_info(self) -> Dict[str, int]:
        """Obtiene información sobre los recursos cargados"""
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
        """Limpia todos los recursos cargados"""
        self.images.clear()
        self.sounds.clear()
        self.fonts.clear()
        self.sprite_sheets.clear()
        self.music_tracks.clear()
        self.current_music_track = None
        self.music_loaded = None
        pygame.mixer.music.stop()
        print("Recursos limpiados")
