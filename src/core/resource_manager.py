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
        self.music_loaded = None
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
    
    # ===== MÉTODOS PARA MÚSICA =====
    def load_music(self, name: str, path: str) -> bool:
        """Carga música de fondo"""
        try:
            if os.path.exists(path):
                pygame.mixer.music.load(path)
                self.music_loaded = name
                return True
            else:
                print(f"Advertencia: No se encontró la música en {path}")
                return False
        except Exception as e:
            print(f"Error cargando música {path}: {e}")
            return False
    
    def play_music(self, loops: int = -1, volume: float = 0.7):
        """Reproduce la música cargada"""
        if self.music_loaded:
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
    
    def stop_music(self):
        """Detiene la música"""
        pygame.mixer.music.stop()
    
    def pause_music(self):
        """Pausa la música"""
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        """Reanuda la música"""
        pygame.mixer.music.unpause()
    
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
            "music_loaded": self.music_loaded is not None
        }
    
    def cleanup(self):
        """Limpia todos los recursos cargados"""
        self.images.clear()
        self.sounds.clear()
        self.fonts.clear()
        self.sprite_sheets.clear()
        self.music_loaded = None
        print("Recursos limpiados")