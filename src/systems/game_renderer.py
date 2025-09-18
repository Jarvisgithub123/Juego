import pygame
from typing import List
from src.Constantes import *
from src.entities.Car import Car
from src.entities.Player import Player
from src.entities.Pilas import pilas
import random
import math

class GameRenderer:
    """Maneja todo el sistema de renderizado del juego"""  
    def __init__(self, screen: pygame.Surface, resource_manager):
        self.screen = screen
        self.resource_manager = resource_manager
        self.world_scroll_x = 0
        self.world_scroll_speed = 30
        self.color_reiniciar = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        
        # Cache para superficies escaladas
        self.scaled_backgrounds = {}
        self.cached_text_surfaces = {}
        
        # Config para cambio aleatorio del front
        self.front_options = []                     # ...se llenará con nombres disponibles...
        self.current_front_name = None
        # Mantenemos un mapa de tiles para la capa frontal: index -> variant_name
        self.front_tile_map = {}                    # tile_index -> "bg_front"|"bg_front2"
        self.front_change_chance = 0.5              # probabilidad de cambiar a otro fondo en el siguiente tile
        # REDUCIDO: cambiar con más frecuencia mientras avanzas (antes PANTALLA_ANCHO)
        self.front_change_distance = max(200, PANTALLA_ANCHO // 3)  # configurable (ajustable)
        self.last_front_segment = -1
        
        self._init_background_system()
        self._prerender_static_texts()
    
    def _init_background_system(self):
        """Carga las capas del fondo con diferentes velocidades (parallax)"""
        self.bg_layers = []
        # capas base (se preescalan como antes)
        base_layers = [("bg_sky", 0), ("bg_mid", 2)]
        for layer_name, parallax_factor in base_layers:
            # Verificar si ya tenemos la imagen escalada en cache
            if layer_name not in self.scaled_backgrounds:
                image = self.resource_manager.get_image(layer_name)
                if image:
                    #guardar en cache
                    scaled_image = pygame.transform.scale(image, (PANTALLA_ANCHO, PANTALLA_ALTO))
                    scaled_image = scaled_image.convert_alpha()  # Optimizar blitting
                else:
                    scaled_image = pygame.Surface((PANTALLA_ANCHO, PANTALLA_ALTO))
                    scaled_image.fill((30, 30, 30))
                    scaled_image = scaled_image.convert()
                
                self.scaled_backgrounds[layer_name] = scaled_image
            
            self.bg_layers.append({
                "name": layer_name,
                "image": self.scaled_backgrounds[layer_name],
                "parallax_factor": parallax_factor,
                "width": self.scaled_backgrounds[layer_name].get_width()
            })
        
        # PRE-CARGAR OPCIONES DE FRONT (bg_front y bg_front2 si existen)
        candidates = ["bg_front", "bg_front2"]
        for name in candidates:
            if name not in self.scaled_backgrounds:
                image = self.resource_manager.get_image(name)
                if image:
                    scaled = pygame.transform.scale(image, (PANTALLA_ANCHO, PANTALLA_ALTO)).convert_alpha()
                else:
                    # fallback simple si no existe la imagen
                    scaled = pygame.Surface((PANTALLA_ANCHO, PANTALLA_ALTO))
                    scaled.fill((40, 40, 40))
                    scaled = scaled.convert()
                self.scaled_backgrounds[name] = scaled
            # si la imagen real fue cargada en resource_manager, la consideramos opción
            if self.resource_manager.get_image(name):
                self.front_options.append(name)
        # Si no hay opciones reales, usar al menos 'bg_front' como opción disponible
        if not self.front_options:
            self.front_options = ["bg_front"]
        
        # Elegir variante inicial aleatoria
        self.current_front_name = random.choice(self.front_options)
        front_image = self.scaled_backgrounds[self.current_front_name]
        self.bg_layers.append({
            "name": "front_dynamic",
            "image": front_image,               # valor por defecto (se ignorará por tile)
            "parallax_factor": 3.6,
            "width": front_image.get_width()
        })
        # Guardar algunos datos útiles para la capa frontal
        self.front_parallax_factor = 3.6
        self.front_tile_width = front_image.get_width()
        # inicializar segmento para evitar cambio inmediato
        self.last_front_segment = -1

    def _prerender_static_texts(self):
        """Pre-renderiza textos que no cambian durante el juego"""
        font_large = self.resource_manager.get_font('titulo')
        font_normal = self.resource_manager.get_font('pequeña')
        
        if font_large:
            # Textos de game over
            self.cached_text_surfaces['game_over'] = font_large.render(
                "JUEGO TERMINADO", True, COLOR_ROJO
            )
            self.cached_text_surfaces['victory'] = font_large.render(
                "¡VICTORIA!", True, COLOR_TEXTO_VICTORIA
            )
        
        if font_normal:
            # Textos de instrucciones
            self.cached_text_surfaces['escape_menu'] = font_normal.render(
                "Presiona [ESCAPE] para volver al menu", True, COLOR_BLANCO
            )
            self.cached_text_surfaces['victory_msg'] = font_normal.render(
                "¡El paquete fue entregado con exito!", True, COLOR_TEXTO_VICTORIA
            )
            # Texto de reiniciar (con color aleatorio)
            self.cached_text_surfaces['restart'] = font_normal.render(
                "Presiona [R] para reiniciar el juego", True, self.color_reiniciar
            )
    
    def update(self, delta_time: float):
        """Actualiza el sistema de renderizado"""
        self.world_scroll_x += self.world_scroll_speed * delta_time
    
    def _maybe_update_front_by_camera(self, camera_x: float):
        """Cambia la variante frontal aleatoriamente cuando se avanza suficiente en el mundo."""
        # Si no hay al menos 2 opciones, no hacemos nada
        if not self.front_options or len(self.front_options) == 1:
            return
        # Usar el scroll global del mundo para decidir el segmento (más fiable que solo camera_x)
        seg = int(self.world_scroll_x // self.front_change_distance)
        if seg != self.last_front_segment:
            # elegir una variante distinta a la actual cuando sea posible
            choices = [c for c in self.front_options if c != self.current_front_name]
            if not choices:
                choices = self.front_options
            new_front = random.choice(choices)
            self.current_front_name = new_front
            # actualizar la capa frontal
            for layer in self.bg_layers:
                if layer.get("name") == "front_dynamic":
                    layer["image"] = self.scaled_backgrounds[self.current_front_name]
                    layer["width"] = self.scaled_backgrounds[self.current_front_name].get_width()
                    break
            self.last_front_segment = seg
            # Depuración mínima para verificar cambios (puedes quitar)
            print(f"[GameRenderer] front cambiado a {self.current_front_name} en segmento {seg}")

    # Nuevo helper para obtener/crear la variante de un tile
    def _get_front_variant_for_tile(self, tile_index: int) -> str:
        """Retorna la variante asignada para tile_index; la genera si no existe.
        Se intenta (con cierta probabilidad) cambiar respecto al tile anterior para que
        la transición ocurra en la línea entre tiles."""
        if tile_index in self.front_tile_map:
            return self.front_tile_map[tile_index]

        # Intentar mantener continuidad: mirar versión anterior
        prev = self.front_tile_map.get(tile_index - 1, self.current_front_name)
        # Decidir si cambiamos
        if random.random() < self.front_change_chance:
            # elegir una variante distinta si es posible
            options = [o for o in self.front_options if o != prev]
            if not options:
                options = self.front_options
            chosen = random.choice(options)
        else:
            chosen = prev

        self.front_tile_map[tile_index] = chosen
        return chosen

    def draw_background(self, camera_x: float):
        """OPTIMIZADO: fondo con parallax - version mejorada pero funcional"""
        # APLICAR CAMBIO DE FRONT SI CORRESPONDE
        self._maybe_update_front_by_camera(camera_x)
        
        # Cache para evitar recalculos cuando la camara no se mueve mucho
        if not hasattr(self, 'last_camera_x'):
            self.last_camera_x = 0
        
        # Solo recalcular si hay cambio significativo
        camera_moved = abs(camera_x - self.last_camera_x) > 5
        
        for layer in self.bg_layers:
            # Si es la capa frontal dinámica, dibujar por tiles con variantes por índice
            if layer.get("name") == "front_dynamic":
                layer_width = layer["width"]
                parallax_factor = layer["parallax_factor"]

                # total_offset_x define qué tile está en pantalla (puede ser flotante)
                total_offset_x = (self.world_scroll_x * parallax_factor +
                                  camera_x * parallax_factor * BACKGROUND_PARALLAX_CAMERA_FACTOR)
                # índice del tile más a la izquierda que debería dibujarse
                start_tile_index = int(math.floor(total_offset_x / layer_width))
                # offset_x para dibujar el primer tile en coordenadas de pantalla
                offset_x = -(total_offset_x % layer_width)

                # calcular cuántos tiles necesitamos para cubrir la pantalla
                tiles_needed = int(math.ceil((PANTALLA_ANCHO - offset_x) / layer_width)) + 1

                for i in range(tiles_needed):
                    tile_index = start_tile_index + i
                    variant_name = self._get_front_variant_for_tile(tile_index)
                    tile_image = self.scaled_backgrounds.get(variant_name)
                    if tile_image:
                        pos_x = offset_x + i * layer_width
                        self.screen.blit(tile_image, (pos_x, 0))
                continue  # ya dibujamos la capa frontal, pasar a la siguiente capa

            image = layer["image"]
            parallax_factor = layer["parallax_factor"]
            layer_width = layer["width"]
            
            # Calcular offset solo una vez por capa
            total_offset_x = (self.world_scroll_x * parallax_factor + 
                            camera_x * parallax_factor * BACKGROUND_PARALLAX_CAMERA_FACTOR)
            offset_x = -(total_offset_x % layer_width)
            
            # OPTIMIZACIoN: Reducir cantidad de blits calculando posiciones exactas
            positions_needed = []
            
            # Calcular solo las posiciones que realmente necesitamos
            start_x = offset_x
            while start_x < PANTALLA_ANCHO:
                if start_x + layer_width > 0:  # Solo si es visible
                    positions_needed.append(start_x)
                start_x += layer_width
            
            # Dibujar solo las posiciones necesarias
            for pos in positions_needed:
                self.screen.blit(image, (pos, 0))
        
        # Actualizar cache de posicion de camara
        if camera_moved:
            self.last_camera_x = camera_x
    
    def draw_floor(self):
        """Dibuja el piso del juego"""
        # Usar una superficie cacheada para el piso si es posible
        floor_height = PANTALLA_ALTO - PISO_POS_Y
        floor_rect = pygame.Rect(0, PISO_POS_Y, PANTALLA_ANCHO, floor_height)
        pygame.draw.rect(self.screen, COLOR_FONDO, floor_rect)
        pygame.draw.line(self.screen, COLOR_LINEA_PISO, 
                        (0, PISO_POS_Y), (PANTALLA_ANCHO, PISO_POS_Y), 3)
    
    def draw_player(self, player: Player, camera_x: float):
        """Dibuja el jugador con efectos visuales """
        screen_x = player.rect.x - camera_x
        screen_y = player.rect.y
        
        if player.current_sprite:
            self._draw_player_sprite(player, screen_x, screen_y)
        else:
            self._draw_player_fallback(player, screen_x, screen_y)
    
    def _draw_player_sprite(self, player: Player, screen_x: float, screen_y: float):
        """Dibuja el sprite del jugador"""
        # Reutilizar rect existente en lugar de crear uno nuevo para mejor performance
        player.current_sprite_rect = getattr(player, 'current_sprite_rect', None)
        if player.current_sprite_rect is None:
            player.current_sprite_rect = player.current_sprite.get_rect()
        
        player.current_sprite_rect.center = (screen_x + player.rect.width // 2, 
                                           screen_y + player.rect.height // 2)
        
        if player.is_dashing:
            self._draw_dash_trail(player.current_sprite, player.current_sprite_rect)
        
        self.screen.blit(player.current_sprite, player.current_sprite_rect)
    
    def _draw_dash_trail(self, sprite: pygame.Surface, sprite_rect: pygame.Rect):
        """Dibuja la estela del dash"""
        # Cache de la superficie de estela
        if not hasattr(self, 'trail_surface') or self.trail_surface_sprite != sprite:
            self.trail_surface = sprite.copy()
            self.trail_surface.set_alpha(150)
            self.trail_surface_sprite = sprite
        
        # Reutilizar rect para la estela
        if not hasattr(self, 'trail_rect'):
            self.trail_rect = sprite_rect.copy()
        
        for i in range(3):
            self.trail_rect.x = sprite_rect.x - i * 10
            self.trail_rect.y = sprite_rect.y
            if self.trail_rect.right >= 0:
                self.screen.blit(self.trail_surface, self.trail_rect)
    
    def _draw_player_fallback(self, player: Player, screen_x: float, screen_y: float):
        """Dibuja rectangulo de respaldo para el jugador"""
        color = COLOR_AMARILLO if player.is_dashing else (0, 100, 255)
        # Reutilizar rect existente
        if not hasattr(self, 'fallback_rect'):
            self.fallback_rect = pygame.Rect(0, 0, player.rect.width, player.rect.height)
        
        self.fallback_rect.x = screen_x
        self.fallback_rect.y = screen_y
        pygame.draw.rect(self.screen, color, self.fallback_rect)
    
    def draw_cars(self, cars: List[Car], camera_x: float):
        """Dibuja todos los autos visibles"""
        for car in cars:
            screen_x = car.rect.x - camera_x
            if self._is_car_visible(screen_x, car.rect.width):
                self._draw_single_car(car, screen_x)
    
    def _is_car_visible(self, screen_x: float, car_width: int) -> bool:
        """Verifica si un auto esta visible en pantalla"""
        margin = 100
        return -margin <= screen_x <= PANTALLA_ANCHO + margin
    
    def _draw_single_car(self, car: Car, screen_x: float):
        """Dibuja un auto individual"""
        if car.current_sprite:
            # Usar posicion directa en lugar de crear rect
            self.screen.blit(car.current_sprite, (screen_x, car.rect.y))
        else:
            # Rectangulo de respaldo - reutilizar rect
            if not hasattr(car, 'fallback_rect'):
                car.fallback_rect = pygame.Rect(0, 0, car.rect.width, car.rect.height)
            car.fallback_rect.x = screen_x
            car.fallback_rect.y = car.rect.y
            pygame.draw.rect(self.screen, (0, 0, 255), car.fallback_rect)
    
    def draw_pilas(self, pilas: List[pilas], camera_x: float):
        """Dibuja las pilas en la pantalla"""
        for pila in pilas:
            screen_x = pila.rect.x - camera_x
            
            # Solo dibujar si esta en pantalla
            if -pila.rect.width <= screen_x <= PANTALLA_ANCHO:
                self.screen.blit(pila.image, (screen_x, pila.rect.y))
    
    def draw_game_over_screen(self):
        """Dibuja la pantalla de game over"""
        self._draw_overlay((0, 0, 0), 128)
        
        # Usar textos pre-renderizados
        if 'game_over' in self.cached_text_surfaces:
            text_rect = self.cached_text_surfaces['game_over'].get_rect(
                center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 - 100)
            )
            self.screen.blit(self.cached_text_surfaces['game_over'], text_rect)
        
        if 'escape_menu' in self.cached_text_surfaces:
            text_rect = self.cached_text_surfaces['escape_menu'].get_rect(
                center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 - 50)
            )
            self.screen.blit(self.cached_text_surfaces['escape_menu'], text_rect)
        
        if 'restart' in self.cached_text_surfaces:
            # Dibujar fondo para el texto de reiniciar
            restart_rect = self.cached_text_surfaces['restart'].get_rect(
                center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 + 20)
            )
            bg_rect = restart_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (50, 50, 50), bg_rect)
            self.screen.blit(self.cached_text_surfaces['restart'], restart_rect)
    
    def draw_victory_screen(self):
        """Dibuja la pantalla de victoria"""
        self._draw_overlay((0, 50, 0), 128)
        
        # Usar textos pre-renderizados
        if 'victory' in self.cached_text_surfaces:
            text_rect = self.cached_text_surfaces['victory'].get_rect(
                center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 - 100)
            )
            self.screen.blit(self.cached_text_surfaces['victory'], text_rect)
        
        if 'victory_msg' in self.cached_text_surfaces:
            text_rect = self.cached_text_surfaces['victory_msg'].get_rect(
                center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 - 50)
            )
            self.screen.blit(self.cached_text_surfaces['victory_msg'], text_rect)
        
        if 'escape_menu' in self.cached_text_surfaces:
            text_rect = self.cached_text_surfaces['escape_menu'].get_rect(
                center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 - 20)
            )
            self.screen.blit(self.cached_text_surfaces['escape_menu'], text_rect)
        
        if 'restart' in self.cached_text_surfaces:
            restart_rect = self.cached_text_surfaces['restart'].get_rect(
                center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 + 20)
            )
            bg_rect = restart_rect.inflate(20, 10)
            pygame.draw.rect(self.screen, (50, 50, 50), bg_rect)
            self.screen.blit(self.cached_text_surfaces['restart'], restart_rect)
    
    def _draw_overlay(self, color: tuple, alpha: int):
        # Cache de overlay
        overlay_key = f"{color}_{alpha}"
        if overlay_key not in self.cached_text_surfaces:
            overlay = pygame.Surface((PANTALLA_ANCHO, PANTALLA_ALTO))
            overlay.set_alpha(alpha)
            overlay.fill(color)
            overlay = overlay.convert_alpha()
            self.cached_text_surfaces[overlay_key] = overlay
        
        self.screen.blit(self.cached_text_surfaces[overlay_key], (0, 0))
    
    def _draw_centered_text(self, text: str, font: pygame.font.Font, 
                           color: tuple, y_position: int):
        """Dibuja texto centrado horizontalmente"""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(PANTALLA_ANCHO // 2, y_position))
        self.screen.blit(text_surface, text_rect)
        return text_rect