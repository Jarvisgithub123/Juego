import pygame
from typing import List
from src.Constantes import *
from src.entities.Car import Car
from src.entities.Player import Player
from src.entities.Pilas import pilas
import random
class GameRenderer:
    """Maneja todo el sistema de renderizado del juego"""  
    def __init__(self, screen: pygame.Surface, resource_manager):
        self.screen = screen
        self.resource_manager = resource_manager
        self.world_scroll_x = 0
        self.world_scroll_speed = 30
        self.color_reiniciar = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255) #Color aleatorio para el texto de reiniciar la partida
        self._init_background_system()
    
    def _init_background_system(self):
        """Carga las capas del fondo con diferentes velocidades(parallax)."""
        self.bg_layers = []
        background_configs = [
            ("bg_sky", 0),      # Fondo estatico
            ("bg_mid", 2),    # Capa media
            ("bg_front", 3.6)     # Capa frontal
        ]
        
        for layer_name, parallax_factor in background_configs:
            image = self.resource_manager.get_image(layer_name)
            if image:
                scaled_image = pygame.transform.scale(image, (PANTALLA_ANCHO, PANTALLA_ALTO))
            else:
                scaled_image = pygame.Surface((PANTALLA_ANCHO, PANTALLA_ALTO))
                scaled_image.fill((30, 30, 30))
            
            self.bg_layers.append({
                "image": scaled_image,
                "parallax_factor": parallax_factor,
                "width": scaled_image.get_width()
            })
    
    def update(self, delta_time: float):
        """Actualiza el sistema de renderizado"""
        self.world_scroll_x += self.world_scroll_speed * delta_time
    
        # ---------------- FONDOS ----------------

    def draw_background(self, camera_x: float):
        """Dibuja el fondo con efecto parallax"""
        for layer in self.bg_layers:
            image = layer["image"]
            parallax_factor = layer["parallax_factor"]
            layer_width = layer["width"]
            
            # Calcula cuanto se tiene que correr la capa
            total_offset_x = (self.world_scroll_x * parallax_factor + 
                             camera_x * parallax_factor * 0.1)
            offset_x = -(total_offset_x % layer_width)
            
            # Dibujar multiples copias para scroll infinito
            positions = [offset_x - layer_width, offset_x]
            if offset_x > -layer_width:
                positions.append(offset_x + layer_width)
            
            for pos in positions:
                self.screen.blit(image, (pos, 0))

     # ---------------- PISO ----------------
    def draw_floor(self):
        """Dibuja el piso del juego"""
        floor_height = PANTALLA_ALTO - PISO_POS_Y
        floor_rect = pygame.Rect(0, PISO_POS_Y, PANTALLA_ANCHO, floor_height)
        pygame.draw.rect(self.screen, COLOR_FONDO, floor_rect)
        pygame.draw.line(self.screen, COLOR_LINEA_PISO, 
                        (0, PISO_POS_Y), (PANTALLA_ANCHO, PISO_POS_Y), 3)
     # ---------------- JUGADOR ----------------
    def draw_player(self, player: Player, camera_x: float):
        """Dibuja el jugador con efectos visuales"""
        screen_x = player.rect.x - camera_x
        screen_y = player.rect.y
        
        if player.current_sprite:
            self._draw_player_sprite(player, screen_x, screen_y)
        else:
            self._draw_player_fallback(player, screen_x, screen_y)
    
    def _draw_player_sprite(self, player: Player, screen_x: float, screen_y: float):
        """Dibuja el sprite del jugador"""
        sprite_rect = player.current_sprite.get_rect()
        sprite_rect.center = (screen_x + player.rect.width // 2, 
                             screen_y + player.rect.height // 2)
        
        if player.is_dashing:
            self._draw_dash_trail(player.current_sprite, sprite_rect)
        
        self.screen.blit(player.current_sprite, sprite_rect)
    
    def _draw_dash_trail(self, sprite: pygame.Surface, sprite_rect: pygame.Rect):
        """Dibuja la estela del dash"""
        trail_surface = sprite.copy()
        trail_surface.set_alpha(150)
        
        for i in range(3):
            trail_rect = sprite_rect.copy()
            trail_rect.x -= i * 10
            if trail_rect.right >= 0:
                self.screen.blit(trail_surface, trail_rect)
    
    def _draw_player_fallback(self, player: Player, screen_x: float, screen_y: float):
        """Dibuja rectangulo de respaldo para el jugador"""
        color = COLOR_AMARILLO if player.is_dashing else (0, 100, 255)
        rect = pygame.Rect(screen_x, screen_y, player.rect.width, player.rect.height)
        pygame.draw.rect(self.screen, color, rect)
    
        # ---------------- AUTOS ----------------
    def draw_cars(self, cars: List[Car], camera_x: float):
        """Dibuja todos los autos visibles"""
        for car in cars:
            screen_x = car.rect.x - camera_x
            if self._is_car_visible(screen_x, car.rect.width):
                self._draw_single_car(car, screen_x)
    
    
    
    def _is_car_visible(self, screen_x: float, car_width: int) -> bool:
        """Verifica si un auto esta visible en pantalla"""
        # Margen mas generoso para evitar parpadeos
        margin = 100
        return -margin <= screen_x <= PANTALLA_ANCHO + margin
    
    def _draw_single_car(self, car: Car, screen_x: float):
        """Dibuja un auto individual"""
        if car.current_sprite:
            self.screen.blit(car.current_sprite, (screen_x, car.rect.y))
        else:
            # Rectangulo de respaldo
            rect = pygame.Rect(screen_x, car.rect.y, car.rect.width, car.rect.height)
            pygame.draw.rect(self.screen, (0, 0, 255), rect)
    
    
    # ---------------- PILAS ----------------
    
    def draw_pilas(self, pilas: List[pilas], camera_x: float):
        """Dibuja las pilas en la pantalla"""
        for pila in pilas:
            screen_x = pila.rect.x - camera_x
            
            # Solo dibujar si está en pantalla
            if -pila.rect.width <= screen_x <= PANTALLA_ANCHO:
                # Dibujar la pila
                self.screen.blit(pila.image, (screen_x, pila.rect.y))
                
    
    
    
    # ---------------- PANTALLAS DE ESTADO ----------------

    def draw_game_over_screen(self):
        """Dibuja la pantalla de game over"""
        self._draw_overlay((0, 0, 0), 128)
        
        font_large = self.resource_manager.get_font('titulo')
        font_normal = self.resource_manager.get_font('pequeña')
        
        if font_large:
            self._draw_centered_text("JUEGO TERMINADO", font_large, COLOR_ROJO, 
                                   PANTALLA_ALTO // 2 - 100)
        if font_normal:
            self._draw_centered_text("Presiona [R] para reiniciar", 
                                   font_normal, self.color_reiniciar, PANTALLA_ALTO // 2 - 50)
            self._draw_centered_text("Presiona [ESCAPE] para volver al menu", 
                                   font_normal, COLOR_BLANCO, PANTALLA_ALTO // 2 - 20)
    
    def draw_victory_screen(self):
        """Dibuja la pantalla de victoria"""
        self._draw_overlay((0, 50, 0), 128)
        
        font_large = self.resource_manager.get_font('titulo')
        font_normal = self.resource_manager.get_font('pequeña')
        
        if font_large:
            self._draw_centered_text("¡VICTORIA!", font_large, COLOR_TEXTO_VICTORIA, 
                                   PANTALLA_ALTO // 2 - 100)
        if font_normal:
            self._draw_centered_text("¡El paquete fue entregado con exito!", 
                                   font_normal, COLOR_TEXTO_VICTORIA, 
                                   PANTALLA_ALTO // 2 - 50)
            self._draw_centered_text("Presiona [ESCAPE] para volver al menu", 
                                   font_normal, COLOR_BLANCO, PANTALLA_ALTO // 2 - 20)
            
            # Primero dibujamos el fondo gris
            reiniciar_rect = self._draw_centered_text("Presiona [R] para reiniciar el juego", 
                                font_normal, self.color_reiniciar, PANTALLA_ALTO // 2 + 20)
            bg_rect = reiniciar_rect.inflate(20, 10)  # Hacer el fondo un poco más grande
            pygame.draw.rect(self.screen, (90, 80, 80), bg_rect)  # Color gris
            
            reiniciar_rect = self._draw_centered_text("Presiona [R] para reiniciar el juego", 
                                font_normal, self.color_reiniciar, PANTALLA_ALTO // 2 + 20)
        
        # ---------------- FUNCIONES AUXILIARES ----------------
    def _draw_overlay(self, color: tuple, alpha: int):
        """Dibuja una superposicion semitransparente"""
        overlay = pygame.Surface((PANTALLA_ANCHO, PANTALLA_ALTO))
        overlay.set_alpha(alpha)
        overlay.fill(color)
        self.screen.blit(overlay, (0, 0))
    
    def _draw_centered_text(self, text: str, font: pygame.font.Font, 
                           color: tuple, y_position: int):
        """Dibuja texto centrado horizontalmente"""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(PANTALLA_ANCHO // 2, y_position))

        
        self.screen.blit(text_surface, text_rect)
        return text_rect