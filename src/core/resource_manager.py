import pygame
import os
from typing import Dict, Optional

class ResourceManager:
    """Gestor de recursos del juego (imágenes, sonidos, música, etc.)"""
    
    def __init__(self):
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.music_loaded = None
        
        # Cargar fuentes por defecto
        self._load_default_fonts()
    
    def _load_default_fonts(self):
        """Carga las fuentes por defecto"""
        self.fonts['titulo'] = pygame.font.Font(None, 90)
        self.fonts['subtitulo'] = pygame.font.Font(None, 40)
        self.fonts['boton'] = pygame.font.Font(None, 55)
        self.fonts['pequena'] = pygame.font.Font(None, 32)
        self.fonts['hud'] = pygame.font.SysFont(None, 32)
        self.fonts['instrucciones'] = pygame.font.SysFont(None, 36)
    
    def load_image(self, name: str, path: str, convert_alpha: bool = True) -> bool:
        """Carga una imagen y la almacena con el nombre dado"""
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
        """Obtiene una imagen por su nombre"""
        return self.images.get(name)
    
    def get_scaled_image(self, name: str, size: tuple) -> Optional[pygame.Surface]:
        """Obtiene una imagen escalada"""
        image = self.get_image(name)
        if image:
            return pygame.transform.scale(image, size)
        return None
    
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
    
    def get_font(self, name: str) -> Optional[pygame.font.Font]:
        """Obtiene una fuente por su nombre"""
        return self.fonts.get(name)
    
    def create_fallback_image(self, size: tuple, color: tuple) -> pygame.Surface:
        """Crea una imagen de respaldo"""
        surface = pygame.Surface(size)
        surface.fill(color)
        return surface