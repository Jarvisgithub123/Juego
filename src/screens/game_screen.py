import pygame
from src.Constantes import *
from src.core.scene_manager import Scene
from src.entities.Player import Player
from src.UI.game_hud import GameHUD
from src.core.Camera import Camera
from src.systems.car_spawner import CarSpawner
from src.systems.game_renderer import GameRenderer

class GameScreen(Scene):
    """Pantalla principal del juego donde UAIBOT corre y esquiva autos"""
    
    def __init__(self, screen: pygame.Surface, resource_manager):
        super().__init__(screen, resource_manager)
        
        # Sistemas principales
        self.camera = Camera(PANTALLA_ANCHO, PANTALLA_ALTO)
        self.player = Player(100, PISO_POS_Y - 60, GRAVEDAD, resource_manager)
        self.car_spawner = CarSpawner(resource_manager)
        self.renderer = GameRenderer(screen, resource_manager)
        self.hud = GameHUD(resource_manager)
        
        # Estado del juego
        self.pause = False
        self.game_over = False
        self.victory = False
        self.energy_remaining = DURACION_ENERGIA
        self.kilometers_remaining = KILOMETROS_OBJETIVO
    
    def handle_event(self, event: pygame.event.Event):
        """Maneja los eventos de entrada del usuario"""
        if not self.game_over and not self.victory:
            self._handle_gameplay_events(event)
        else:
            self._handle_endgame_events(event)
    
    def _handle_gameplay_events(self, event: pygame.event.Event):
        """Maneja eventos durante el juego activo"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.pause:
                self.player.jump()
            elif event.key == pygame.K_z and not self.pause:
                self.player.dash(self._consume_energy)
            if event.key == pygame.K_p: 
                self.pause= not self.pause 
            elif self.pause: 
                if event.key == pygame.K_ESCAPE:
                    self._return_to_menu()
    
    def _handle_endgame_events(self, event: pygame.event.Event):
        """Maneja eventos en pantallas de fin de juego"""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE]:
                self._restart_game()
            elif event.key == pygame.K_ESCAPE:
                self._return_to_menu()
    
    def update(self, delta_time: float):
        """Para que no se reinicie al entrar en pausa"""
        if self.pause:
            return
        """Actualiza toda la logica del juego"""
        if not self.game_over and not self.victory:
            self._update_game_systems(delta_time)
            self._update_entities(delta_time)
            self._check_game_conditions()
    
    def _update_game_systems(self, delta_time: float):
        """Actualiza sistemas del juego"""
        self._update_time_and_distance(delta_time)
        self._update_camera(delta_time)
        self.renderer.update(delta_time)
    
    def _update_camera(self, delta_time: float):
        """Actualiza la camara para seguir al jugador suavemente"""
        target_x = max(0, self.player.rect.x - 150)
        diff = target_x - self.camera.x
        if abs(diff) > 15:
            self.camera.x += diff * 0.08
    
    def _update_entities(self, delta_time: float):
        """Actualiza entidades del juego"""
        self.player.update(delta_time)
        self.car_spawner.update(delta_time, self.camera.x, self.player.rect.x)
    
    def _check_game_conditions(self):
        """Verifica condiciones de fin de juego"""
        # Verificar colisiones
        if self.car_spawner.check_collisions(self.player.rect):
            self._trigger_game_over()
            return
        
        # Verificar condiciones de fin
        if self.energy_remaining <= 0:
            self._trigger_game_over()
        elif self.kilometers_remaining <= 0:
            self._trigger_victory()
    
    def _trigger_game_over(self):
        """Activa el estado de game over"""
        self.game_over = True
        self.resource_manager.play_sound("game_over")
    
    def _trigger_victory(self):
        """Activa el estado de victoria"""
        self.victory = True
        self.resource_manager.play_sound("victoria")
    
    def _update_time_and_distance(self, delta_time: float):
        """Actualiza tiempo de energia y distancia recorrida"""
        # Solo consumir energia si no esta haciendo dash
        if not self.player.is_dashing:
            self.energy_remaining -= delta_time
        
        # Calcular distancia basada en tiempo transcurrido
        km_traveled = (DURACION_ENERGIA - self.energy_remaining) * DECREMENTO_KM_POR_SEGUNDO
        self.kilometers_remaining = max(0, KILOMETROS_OBJETIVO - km_traveled)
    
    def _consume_energy(self, energy_amount: float) -> bool:
        """Consume energia si hay suficiente disponible"""
        if self.energy_remaining >= energy_amount:
            self.energy_remaining -= energy_amount
            return True
        return False
    
    def on_enter(self):
        """Se ejecuta al entrar en la pantalla del juego"""
        
        self.resource_manager.play_music("game_music", volume=0.6)
    
    def on_exit(self):
        """Se ejecuta al salir de la pantalla del juego"""
        # Detener todos los sonidos que puedan estar reproduciéndose
        pygame.mixer.stop()  # Detiene todos los sonidos (no la musica)
        print("Sonidos detenidos al salir del juego")
    
    def _restart_game(self):
        """Reinicia el juego desde el principio"""
        pygame.mixer.stop()
        from src.screens.game_screen import GameScreen
        self.scene_manager.change_scene(GameScreen)
    
    def _return_to_menu(self):
        """Regresa al menu principal"""
        pygame.mixer.stop()
        from src.screens.menu_screen import MenuScreen
        self.scene_manager.change_scene(MenuScreen)
    
    def draw(self):
        """Dibuja todos los elementos visuales"""
        self.renderer.draw_background(self.camera.x)
        self.renderer.draw_floor()
        self.renderer.draw_player(self.player, self.camera.x)
        self.renderer.draw_cars(self.car_spawner.get_cars(), self.camera.x)
        
        # Dibujar UI
        if not self.game_over and not self.victory:
            self.hud.draw(self.screen, self.energy_remaining, 
                         DURACION_ENERGIA, self.kilometers_remaining)
        
        # Dibujar pantallas de fin de juego
        if self.game_over:
            self.renderer.draw_game_over_screen()
        elif self.victory:
            self.renderer.draw_victory_screen()
        if self.pause and not self.game_over and not self.victory:
            overlay = pygame.Surface((PANTALLA_ANCHO, PANTALLA_ALTO))
            overlay.set_alpha(150)  # nivel de transparencia
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            font = pygame.font.SysFont(None, 60)
            text = font.render("Juego Pausado", True, (255, 255, 255))
            rect = text.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2))
            self.screen.blit(text, rect)

            font_small = pygame.font.SysFont(None, 36)
            text2 = font_small.render("Presiona P para continuar o ESC para volver al menu", True, (200, 200, 200))
            rect2 = text2.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 + 60))


            self.screen.blit(text2, rect2)
