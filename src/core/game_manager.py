import pygame
import sys
from src.Constantes import *
from src.core.resource_manager import ResourceManager
from src.core.scene_manager import SceneManager
from src.screens.menu_screen import MenuScreen

class GameManager:
    """Gestor principal del juego"""
    def __init__(self):
        # Configurar pantalla
        self.screen = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
        pygame.display.set_caption("Go UAIBOT")
        self.clock = pygame.time.Clock()
        
        # Inicializar gestores
        self.resource_manager = ResourceManager()
        self.scene_manager = SceneManager(self.screen, self.resource_manager)
        
        # Cargar recursos iniciales
        self._load_initial_resources()
        
        # Configurar escena inicial
        self.scene_manager.change_scene(MenuScreen)
        
        self.running = True
    
    def _load_initial_resources(self):
        """Carga los recursos iniciales del juego"""
        # Imágenes
        self.resource_manager.load_image("uaibot", "Assets/Imagenes/UAIBOT.png")
        self.resource_manager.load_image("auto", "Assets/Imagenesauto.png")
        self.resource_manager.load_image("fondo_ciudad", "Assets/Imagenes/ciudad.jpg")
        
        # Sonidos
        self.resource_manager.load_sound("boton_hover", "Assets/Music/mixkit-arcade-game-jump-coin-216.mp3")
        self.resource_manager.load_sound("salto", "Assets/Music/Jump.mp3")
        self.resource_manager.load_sound("game_over", "Assets/Music/Game-over.mp3")
        self.resource_manager.load_sound("victoria", "Assets/Music/Win.mp3")
        
        # Música
        self.resource_manager.load_music("menu", "Assets/Music/wwd.mp3juice.blog - Aventura - Los Infieles (192 KBps).mp3")
    
    def handle_events(self):
        """Maneja los eventos globales del juego"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                # Pasar eventos a la escena actual
                self.scene_manager.handle_event(event)
    
    def update(self, dt):
        """Actualiza la lógica del juego"""
        self.scene_manager.update(dt)
    
    def draw(self):
        """Dibuja todo en pantalla"""
        self.screen.fill(COLOR_FONDO_BASE)
        self.scene_manager.draw()
        pygame.display.flip()
    
    def run(self):
        """Bucle principal del juego"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time en segundos
            
            self.handle_events()
            self.update(dt)
            self.draw()