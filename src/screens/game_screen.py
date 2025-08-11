import pygame
import os
from src.Constantes import *
from src.core.scene_manager import Scene
from src.entities.Player import Player
from src.entities.Car import Car
from src.UI.game_hud import GameHUD

class GameScreen(Scene):
    """Pantalla principal del juego"""
    
    def __init__(self, screen, resource_manager):
        super().__init__(screen, resource_manager)
        
        # Inicializar componentes del juego
        self.player = Player(100, PISO_POS_Y - 64, 0.2, resource_manager)
        self.cars = [Car(PANTALLA_ANCHO, PISO_POS_Y - 40, resource_manager)]
        self.hud = GameHUD(resource_manager)
        
        # Estados del juego
        self.game_over = False
        self.victory = False
        
        # Variables de tiempo y distancia
        self.start_time = pygame.time.get_ticks()
        self.energy_remaining = DURACION_ENERGIA
        self.km_remaining = KILOMETROS_OBJETIVO
        
        # Variables para animación del fondo
        self.background_x1 = 0
        self.background_x2 = PANTALLA_ANCHO
        self.background_speed = 2
        
        # Cargar fondo
        self._load_background()
    
    def _load_background(self):
        """Carga la imagen de fondo"""
        bg_image = self.resource_manager.get_image("fondo_ciudad")
        if bg_image:
            self.background_image = pygame.transform.scale(bg_image, (PANTALLA_ANCHO, PANTALLA_ALTO))
        else:
            self.background_image = None
    
    def handle_event(self, event):
        """Maneja los eventos del juego"""
        keys = pygame.key.get_pressed()
        
        # Control del jugador durante el juego
        if not self.game_over and not self.victory:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.player.jump()
        
        # Controles en game over o victoria
        if self.game_over or self.victory:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE]:
                    self._restart_game()
                elif event.key == pygame.K_ESCAPE:
                    self._return_to_menu()
    
    def _restart_game(self):
        """Reinicia el juego"""
        from src.screens.game_screen import GameScreen
        self.scene_manager.change_scene(GameScreen)
    
    def _return_to_menu(self):
        """Regresa al menú principal"""
        from src.screens.menu_screen import MenuScreen
        self.scene_manager.change_scene(MenuScreen)
    
    def update(self, dt):
        """Actualiza la lógica del juego"""
        if not self.game_over and not self.victory:
            # Actualizar tiempo y distancia
            self._update_time_and_distance()
            
            # Actualizar entidades
            self.player.update()
            for car in self.cars:
                car.update()
            
            # Verificar colisiones
            self._check_collisions()
            
            # Verificar condiciones de fin
            self._check_end_conditions()
            
            # Animar fondo
            self._update_background()
    
    def _update_time_and_distance(self):
        """Actualiza el tiempo transcurrido y calcula kilómetros restantes"""
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - self.start_time) / 1000
        
        # Calcular energía restante
        self.energy_remaining = max(0, DURACION_ENERGIA - elapsed_time)
        
        # Calcular kilómetros restantes
        km_traveled = elapsed_time * DECREMENTO_KM_POR_SEGUNDO
        self.km_remaining = max(0, KILOMETROS_OBJETIVO - km_traveled)
    
    def _check_collisions(self):
        """Verifica las colisiones"""
        for car in self.cars:
            if self.player.rect.colliderect(car.rect):
                self.game_over = True
                self.resource_manager.play_sound("game_over")
                return
    
    def _check_end_conditions(self):
        """Verifica las condiciones de fin de juego"""
        # Verificar si se agotó la energía
        if self.energy_remaining <= 0:
            self.game_over = True
            self.resource_manager.play_sound("game_over")
            return
        
        # Verificar victoria
        if self.km_remaining <= 0:
            self.victory = True
            self.resource_manager.play_sound("victoria")
            return
    
    def _update_background(self):
        """Actualiza la animación del fondo"""
        self.background_x1 -= self.background_speed
        self.background_x2 -= self.background_speed
        
        # Reiniciar posiciones del fondo
        if self.background_x1 <= -PANTALLA_ANCHO:
            self.background_x1 = PANTALLA_ANCHO
        if self.background_x2 <= -PANTALLA_ANCHO:
            self.background_x2 = PANTALLA_ANCHO
    
    def draw(self):
        """Dibuja todos los elementos del juego"""
        # Dibujar fondo animado
        self._draw_background()
        
        # Dibujar piso
        self._draw_floor()
        
        # Dibujar entidades
        self.player.draw(self.screen)
        for car in self.cars:
            car.draw(self.screen)
        
        # Dibujar HUD
        if not self.game_over and not self.victory:
            self.hud.draw(self.screen, self.energy_remaining, DURACION_ENERGIA, self.km_remaining)
        
        # Dibujar pantallas de fin
        if self.game_over:
            self._draw_game_over()
        elif self.victory:
            self._draw_victory()
    
    def _draw_background(self):
        """Dibuja el fondo animado"""
        if self.background_image:
            y_offset = -(PANTALLA_ALTO - PISO_POS_Y)
            self.screen.blit(self.background_image, (self.background_x1, y_offset))
            self.screen.blit(self.background_image, (self.background_x2, y_offset))
        else:
            self.screen.fill(COLOR_BLANCO)
    
    def _draw_floor(self):
        """Dibuja el piso del juego"""
        floor_height = PANTALLA_ALTO - PISO_POS_Y
        floor_rect = pygame.Rect(0, PISO_POS_Y, PANTALLA_ANCHO, floor_height)
        pygame.draw.rect(self.screen, COLOR_VERDE, floor_rect)
        pygame.draw.line(self.screen, COLOR_NEGRO, (0, PISO_POS_Y), (PANTALLA_ANCHO, PISO_POS_Y), 3)
    
    def _draw_game_over(self):
        """Dibuja la pantalla de game over"""
        # Fondo semitransparente
        overlay = pygame.Surface((PANTALLA_ANCHO, PANTALLA_ALTO))
        overlay.set_alpha(128)
        overlay.fill(COLOR_NEGRO)
        self.screen.blit(overlay, (0, 0))
        
        # Texto de game over
        font_large = self.resource_manager.get_font('titulo')
        font_normal = self.resource_manager.get_font('pequena')
        
        if font_large:
            game_over_text = font_large.render("JUEGO TERMINADO", True, COLOR_ROJO)
            game_over_rect = game_over_text.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 - 100))
            self.screen.blit(game_over_text, game_over_rect)
        
        if font_normal:
            restart_text = font_normal.render("Presiona [ENTER] o [ESPACIO] para reiniciar", True, COLOR_VERDE)
            restart_rect = restart_text.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 - 50))
            self.screen.blit(restart_text, restart_rect)
            
            menu_text = font_normal.render("Presiona [ESCAPE] para volver al menú", True, COLOR_BLANCO)
            menu_rect = menu_text.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 - 20))
            self.screen.blit(menu_text, menu_rect)
    
    def _draw_victory(self):
        """Dibuja la pantalla de victoria"""
        # Fondo semitransparente
        overlay = pygame.Surface((PANTALLA_ANCHO, PANTALLA_ALTO))
        overlay.set_alpha(128)
        overlay.fill((0, 50, 0))  # Verde oscuro
        self.screen.blit(overlay, (0, 0))
        
        # Texto de victoria
        font_large = self.resource_manager.get_font('titulo')
        font_normal = self.resource_manager.get_font('pequena')
        
        if font_large:
            victory_text = font_large.render("¡VICTORIA!", True, COLOR_TEXTO_VICTORIA)
            victory_rect = victory_text.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 - 100))
            self.screen.blit(victory_text, victory_rect)
        
        if font_normal:
            success_text = font_normal.render("¡El paquete fue entregado con éxito!", True, COLOR_TEXTO_VICTORIA)
            success_rect = success_text.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 - 50))
            self.screen.blit(success_text, success_rect)
            
            menu_text = font_normal.render("Presiona [ESCAPE] para volver al menú", True, COLOR_BLANCO)
            menu_rect = menu_text.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 - 20))
            self.screen.blit(menu_text, menu_rect)