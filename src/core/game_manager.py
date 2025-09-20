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
            'selected_character': 'UIAbot',
            'music_volume': DEFAULT_MUSIC_VOLUME,
            'sound_volume': 0.7  # NUEVO: Volumen de efectos por defecto  
        }

         # Aplicar configuración inicial de audio
        self.resource_manager.set_music_volume(DEFAULT_MUSIC_VOLUME)
        self.resource_manager.set_sound_volume(0.7)
        
    def _load_initial_resources(self):
        """Carga los recursos iniciales del juego"""
        # imagenes estaticas
        self.resource_manager.load_image("menu_background1","Assets/Imagenes/menubackground1.png")
        self.resource_manager.load_image("menu_background2","Assets/Imagenes/menubackground2.png")
        
        self.resource_manager.load_image("bg_sky", "Assets/Imagenes/Background/bg_sky.png")
        self.resource_manager.load_image("bg_mid", "Assets/Imagenes/Background/bg_mid.png")
        self.resource_manager.load_image("bg_front", "Assets/Imagenes/Background/bg_front1.png")
        self.resource_manager.load_image("bg_front2", "Assets/Imagenes/Background/bg_front2.png")
        
        self.resource_manager.load_image("bg_sky_night", "Assets/Imagenes/Background/background_back_night.png")
        self.resource_manager.load_image("bg_mid_night", "Assets/Imagenes/Background/background_mid_night.png")
        self.resource_manager.load_image("bg_front_night", "Assets/Imagenes/Background/background_front_night.png")
        self.resource_manager.load_image("bg_front_night_2", "Assets/Imagenes/Background/backgorund_front_nigth_2.png")
        
        
        self.resource_manager.load_image("pila", "Assets/Imagenes/bateria.png")
        self.resource_manager.load_image("escudo", "Assets/Imagenes/escudo.png")
        self.resource_manager.load_image("cartel", "Assets/Imagenes/Background/billboard.png")
        self.resource_manager.load_image("cartel_uaibot", "Assets/Imagenes/cartel_uaibot.png")
        self.resource_manager.load_image("cartel_uaibotina", "Assets/Imagenes/cartel_uaibotina.png")
        self.resource_manager.load_image("cartel_uaibota", "Assets/Imagenes/cartel_uaibota.png")
        self.resource_manager.load_image("cartel_uaibotino", "Assets/Imagenes/cartel_uaibotino.png")
        self.resource_manager.load_image("avion", "Assets/Imagenes/avion_publicidad.png")
        
        # PERSONAJES 
        # UIAbot: tiene spritesheet con animacion
        self.resource_manager.load_spritesheet("UIAbot_walk", "Assets/Sprites/uiabot2.png", 64, 86)
        self.resource_manager.load_spritesheet("UAIBOTA_walk", "Assets/Sprites/Uiabota.png", 64, 86)
        self.resource_manager.load_spritesheet("UAIBOTINA_walk", "Assets/Sprites/Uiabotina.png", 64, 86)
        self.resource_manager.load_spritesheet("UAIBOTINO_walk", "Assets/Sprites/Uibotino.png", 64, 86)
        
        
        #MISIONES
        
        #NPCS
        self.resource_manager.load_spritesheet("character_a", "Assets/Sprites/Misiones/Uiabot_talk.png",450, 780)      
        self.resource_manager.load_spritesheet("character_b", "Assets/Sprites/Misiones/npc_1.png",450, 780)      
        
        self.resource_manager.load_spritesheet("character_c", "Assets/Sprites/Misiones/npc_2.png",450, 780)
        self.resource_manager.load_spritesheet("character_d", "Assets/Sprites/Misiones/npc_3.png",450, 780)
        self.resource_manager.load_spritesheet("character_e", "Assets/Sprites/Misiones/npc_4.png",450, 780)
        
        #FONDOS DE MISIONES
        self.resource_manager.load_image("level1_bg", "Assets/Imagenes/Background/fondo_mision_1.png")
        self.resource_manager.load_image("level2_bg", "Assets/Imagenes/Background/fondo_mision_2.png")
        self.resource_manager.load_image("level3_bg", "Assets/Imagenes/Background/fondo_mision_3.png")
        self.resource_manager.load_image("level4_bg", "Assets/Imagenes/Background/fondo_mision_4.png")
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
        self.resource_manager.load_music("level_music", "Assets/Music/Mission_music.mp3")
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