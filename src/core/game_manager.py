import pygame
import sys
from src.Constantes import *
from src.core.resource_manager import ResourceManager
from src.core.scene_manager import SceneManager
from src.screens.menu_screen import MenuScreen

class GameManager:
    """Gestor principal del juego se encarga de inicializar,
    cargar recursos, manejar escenas y controlar el bucle.
    """
    def __init__(self):
        # Configurar pantalla
        self.screen = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
        pygame.display.set_caption("Go UAIBOT")
        self.clock = pygame.time.Clock()
        
        # Inicializar gestores
        self.resource_manager = ResourceManager()
        self.scene_manager = SceneManager(self.screen, self.resource_manager)
        self.scene_manager.game_manager = self  # Pasa la  referencia al game_manager
        # Cargar recursos iniciales
        self._load_initial_resources()
        
        # Configurar escena inicial
        self.scene_manager.change_scene(MenuScreen)
        
        self.running = True
        self.shared_data = {
            'selected_character': 'UIAbot'  
        }

    def _load_initial_resources(self):
        """Carga los recursos iniciales del juego"""
        # imagenes estaticas
        self.resource_manager.load_image("menu_background1","Assets/Imagenes/menubackground1.png")
        self.resource_manager.load_image("menu_background2","Assets/Imagenes/menubackground2.png")
        self.resource_manager.load_image("bg_sky", "Assets/Imagenes/bg_sky.png")
        self.resource_manager.load_image("bg_mid", "Assets/Imagenes/bg_mid.png")
        self.resource_manager.load_image("bg_front", "Assets/Imagenes/bg_front.png")
        self.resource_manager.load_image("pila", "Assets/Imagenes/MONSTER.png")
        self.resource_manager.load_image("cartel", "Assets/Imagenes/billboard.png")
        self.resource_manager.load_image("personaje1", "Assets/Imagenes/prueba.png")
        self.resource_manager.load_image("personaje2", "Assets/Imagenes/personaje2.png")
        
        # PERSONAJES 
        # UIAbot: tiene spritesheet con animacion
        self.resource_manager.load_spritesheet("UIAbot_walk", "Assets/Sprites/uiabot2.png", 64, 86)
        
        # otros personajes: por ahora imagenes estaticas 
        #self.resource_manager.load_image("UAIBOTA_walk", "Assets/Sprites/UAIBOTA.png")
        #self.resource_manager.load_image("UAIBOTINA_walk", "Assets/Sprites/UAIBOTINA.png")
        #self.resource_manager.load_image("UAIBOTINO_walk", "Assets/Sprites/UAIBOTINO.png")
        self.resource_manager.load_spritesheet("UAIBOTA_walk", "Assets/Sprites/Uiabota.png", 64, 86)
        self.resource_manager.load_spritesheet("UAIBOTINA_walk", "Assets/Sprites/Uiabotina.png", 64, 86)
        self.resource_manager.load_spritesheet("UAIBOTINO_walk", "Assets/Sprites/Uibotino.png", 64, 86)
        
        # spritesheets de autos
        self.resource_manager.load_spritesheet("Auto_azul", "Assets/Sprites/Autos/Auto-azul.png", 126, 86)
        self.resource_manager.load_spritesheet("Auto_rojo", "Assets/Sprites/Autos/Auto-rojo.png", 126, 86)
        
        # sonidos
        self.resource_manager.load_sound("boton_hover", "Assets/Music/mixkit-arcade-game-jump-coin-216.mp3")
        self.resource_manager.load_sound("salto", "Assets/Music/Jump.mp3")
        self.resource_manager.load_sound("dash", "Assets/Music/dash.mp3")
        self.resource_manager.load_sound("game_over", "Assets/Music/Game-over.mp3")
        self.resource_manager.load_sound("victoria", "Assets/Music/Win.mp3")
        self.resource_manager.load_sound("cambio_personaje", "Assets/Music/cambio_personaje.mp3")
        
        # musica
        self.resource_manager.load_music("menu", "Assets/Music/Music-menu.mp3")
        self.resource_manager.load_music("game_music", "Assets/Music/Game-music.mp3")
        
        # Debug: mostrar cantidad de recursos cargados
        info = self.resource_manager.get_resource_info()
        print(f"Recursos cargados: {info}")
    
    def handle_events(self):
        """Maneja los eventos globales del juego"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            else:
                # Pasar todos los eventos a la escena actual
                self.scene_manager.handle_event(event)

    def update(self, dt):
        """Actualiza la logica del juego"""
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
        
        # Limpiar recursos al salir
        self.resource_manager.cleanup()