import pygame
import random
from src.Constantes import *
from src.core.scene_manager import Scene
from src.entities.Player import Player
from src.entities.Car import Car
from src.UI.game_hud import GameHUD
from src.core.Camera import Camera

#TODO: Hacer que el fondo se mueva con diferentes paralax
#TODO: Hacer que sea mas justo el juego 
#TODO: Añadir plataformas
#TODO: Añadir musica
#TODO: Objetos interactivos, como energia o monedas o como Escudo (bloquea 1 golpe).Turbo (aumenta velocidad por unos segundos).
#TODO: Eventos aleatorios (lluvia,autos raros, etc)
#TODO: Dia / Noche
#TODO: Variación de terreno Rutas elevadas vs subterráneas (puentes, túneles). Rampas que te impulsan. Zonas con menos gravedad (salto más alto). Secciones con piso que resbala.
#TODO: Best Score
class GameScreen(Scene):
    def __init__(self, screen, resource_manager):
        super().__init__(screen, resource_manager)
        
        # Sistema de cámara
        self.camera = Camera(PANTALLA_ANCHO, PANTALLA_ALTO)
        
        # Inicializar jugador
        self.player = Player(100, PISO_POS_Y - 64, GRAVEDAD, resource_manager)
        
        # Sistema de spawn de autos
        self.cars = []
        self.spawn_timer = 0
        self.min_spawn_interval = 1.5
        self.max_spawn_interval = 4.0
        self.next_spawn_time = 2.0
        self.world_position = 0
        # Generar primer auto
        self.cars.append(Car(PANTALLA_ANCHO, PISO_POS_Y - 86, resource_manager, speed=VELOCIDAD_AUTO_BASE))
        
        self.hud = GameHUD(resource_manager)
        self.dash_distance_bonus = 0
        # Estados del juego
        self.game_over = False
        self.victory = False
        
        # Variables de energía y distancia
        self.energy_remaining = DURACION_ENERGIA
        self.km_remaining = KILOMETROS_OBJETIVO
        
        # Variables para fondo animado (vuelve al sistema original)
        self.background_x1 = 0
        self.background_x2 = PANTALLA_ANCHO
        self.background_speed = VELOCIDAD_FONDO
        
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
        if not self.game_over and not self.victory:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.jump()
                elif event.key == pygame.K_z:
                    self.player.dash(self._consume_energy)
        
        # Controles en game over o victoria
        if self.game_over or self.victory:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE]:
                    self._restart_game()
                elif event.key == pygame.K_ESCAPE:
                    self._return_to_menu()
    

    def _spawn_new_car_if_needed(self, dt):
        """Sistema de spawn de autos - VERSIÓN ESTABILIZADA"""
        self.spawn_timer += dt
        
        if self.spawn_timer >= self.next_spawn_time:
            # LÓGICA SIMPLE: Spawn basado en una posición fija relativa a la pantalla
            # Ignora completamente la posición del jugador para el spawn
            base_spawn_x = PANTALLA_ANCHO + random.randint(150, 400)
            
            # Verificar distancia mínima con otros autos
            can_spawn = True
            min_distance = 280  # Distancia mínima entre autos
            
            for car in self.cars:
                if abs(car.rect.x - base_spawn_x) < min_distance:
                    can_spawn = False
                    break
            
            # VERIFICACIÓN ADICIONAL: No spawnear si hay muchos autos cercanos al borde derecho
            cars_near_edge = sum(1 for car in self.cars if car.rect.x > PANTALLA_ANCHO - 100)
            if cars_near_edge >= 2:  # No más de 2 autos cerca del borde
                can_spawn = False
            
            if can_spawn:
                speed = VELOCIDAD_AUTO_BASE + random.randint(-VELOCIDAD_AUTO_VARIACION, VELOCIDAD_AUTO_VARIACION)
                speed = max(8, speed)
                
                new_car = Car(base_spawn_x, PISO_POS_Y - 86, self.resource_manager, speed=speed)
                self.cars.append(new_car)
                
                # Reset del timer
                self.spawn_timer = 0
                self.next_spawn_time = random.uniform(self.min_spawn_interval, self.max_spawn_interval)
                
                print(f"Auto spawneado en x={base_spawn_x} (total autos activos: {len(self.cars)})")
            else:
                # Reintentar más rápido si no se pudo spawnear
                self.spawn_timer = max(0, self.next_spawn_time - 0.3)
                print(f"Spawn bloqueado - reintentar pronto (autos activos: {len(self.cars)})")
    
    def _restart_game(self):
        """Reinicia el juego"""
        from src.screens.game_screen import GameScreen
        self.scene_manager.change_scene(GameScreen)
    
    def _return_to_menu(self):
        """Regresa al menu principal"""
        from src.screens.menu_screen import MenuScreen
        self.scene_manager.change_scene(MenuScreen)
    
    def update(self, dt):
        """Actualiza la lógica del juego"""
        if not self.game_over and not self.victory:
            # Actualizar tiempo y distancia
            self._update_time_and_distance(dt)
            
            # Actualizar jugador
            self.player.update(dt)
            
            # CÁMARA SIMPLIFICADA: Solo seguir cuando el jugador se aleja mucho
            target_camera_x = max(0, self.player.rect.x - 100)  # Mantener jugador cerca de x=100 en pantalla
            camera_diff = target_camera_x - self.camera.x
            if abs(camera_diff) > 20:  # Solo mover cámara si hay diferencia significativa
                self.camera.x += camera_diff * 0.1  # Movimiento suave y lento
            
            # Sistema de spawn
            self._spawn_new_car_if_needed(dt)
            
            # Limpiar autos que están muy atrás
            self.cars = [car for car in self.cars if car.rect.right > -200]
            
            for car in self.cars:
                car.update(dt)
            
            # Verificar colisiones
            self._check_collisions()
            
            # Verificar condiciones de fin
            self._check_end_conditions()
            
            # Animar fondo
            self._update_background()
            
    def _update_time_and_distance(self, dt):
        """Actualiza el tiempo y distancia"""
        if not self.player.is_dashing:
            self.energy_remaining -= dt
        
        km_traveled = (DURACION_ENERGIA - self.energy_remaining) * DECREMENTO_KM_POR_SEGUNDO
        self.km_remaining = max(0, KILOMETROS_OBJETIVO - km_traveled)
    
    def _check_collisions(self):
        """Verifica colisiones entre jugador y autos"""
        player_hitbox = self.player.rect.inflate(-8, -8)
        for car in self.cars:
            car_hitbox = car.rect.inflate(-5, -20)
            if player_hitbox.colliderect(car_hitbox):
                self.game_over = True
                self.resource_manager.play_sound("game_over")
                return
    
    def _consume_energy(self, amount):
        """Consume energía si hay suficiente"""
        if self.energy_remaining >= amount:
            self.energy_remaining -= amount
            return True
        return False
    
    def _check_end_conditions(self):
        """Verifica condiciones de fin del juego"""
        if self.energy_remaining <= 0:
            self.game_over = True
            self.resource_manager.play_sound("game_over")
        elif self.km_remaining <= 0:
            self.victory = True
            self.resource_manager.play_sound("victoria")
    
    def _update_background(self):
        """Actualiza la animación del fondo (sistema original restaurado)"""
        self.background_x1 -= self.background_speed
        self.background_x2 -= self.background_speed
        
        # Reiniciar posiciones del fondo
        if self.background_x1 <= -PANTALLA_ANCHO:
            self.background_x1 = PANTALLA_ANCHO
        if self.background_x2 <= -PANTALLA_ANCHO:
            self.background_x2 = PANTALLA_ANCHO
    
    def draw(self):
        """Dibuja todo en pantalla"""
        # Dibujar fondo animado
        self._draw_background()
        
        # Dibujar piso 
        self._draw_floor()
        
        # Dibujar entidades 
        self._draw_entities()
        
        # Dibujar HUD 
        if not self.game_over and not self.victory:
            self.hud.draw(self.screen, self.energy_remaining, DURACION_ENERGIA, self.km_remaining)
            
        # Pantallas de fin
        if self.game_over:
            self._draw_game_over()
        elif self.victory:
            self._draw_victory()
    
    def _draw_background(self):
        if self.background_image:
            y_offset = -(PANTALLA_ALTO - PISO_POS_Y)
            self.screen.blit(self.background_image, (self.background_x1, y_offset))
            self.screen.blit(self.background_image, (self.background_x2, y_offset))
        else:
            self.screen.fill(COLOR_BLANCO)
    
    def _draw_floor(self):
        floor_height = PANTALLA_ALTO - PISO_POS_Y
        floor_rect = pygame.Rect(0, PISO_POS_Y, PANTALLA_ANCHO, floor_height)
        pygame.draw.rect(self.screen, COLOR_FONDO, floor_rect)
        pygame.draw.line(self.screen, COLOR_NEGRO, (0, PISO_POS_Y), (PANTALLA_ANCHO, PISO_POS_Y), 3)
    
    def _draw_entities(self):
        self._draw_player()
        
        # Dibujar autos
        for car in self.cars:
            self._draw_car(car)
    
    def _draw_player(self):
        """Dibuja el jugador aplicando offset de cámara suave"""
        # Aplicar offset de cámara al jugador
        camera_offset = self.camera.get_offset()
        player_screen_pos = (self.player.rect.x - camera_offset[0], self.player.rect.y - camera_offset[1])
        
        if self.player.current_sprite:
            sprite_rect = self.player.current_sprite.get_rect()
            sprite_rect.center = (player_screen_pos[0] + self.player.rect.width // 2, 
                                player_screen_pos[1] + self.player.rect.height // 2)
            
            # Efecto de dash mejorado
            if self.player.is_dashing:
                dash_surface = self.player.current_sprite.copy()
                dash_surface.set_alpha(150)
                for i in range(3):
                    offset_rect = sprite_rect.copy()
                    offset_rect.x -= i * 10
                    if offset_rect.right >= 0:
                        self.screen.blit(dash_surface, offset_rect)
            
            self.screen.blit(self.player.current_sprite, sprite_rect)
        else:
            # Fallback rect
            color = (255, 255, 0) if self.player.is_dashing else (0, 100, 255)
            player_rect = pygame.Rect(player_screen_pos[0], player_screen_pos[1], 
                                    self.player.rect.width, self.player.rect.height)
            pygame.draw.rect(self.screen, color, player_rect)

    
    def _draw_car(self, car):
        """Dibuja un auto aplicando offset de cámara"""
        camera_offset = self.camera.get_offset()
        car_screen_pos = (car.rect.x - camera_offset[0], car.rect.y - camera_offset[1])
        
        # Solo dibujar si está visible en pantalla
        if car_screen_pos[0] + car.rect.width >= -50 and car_screen_pos[0] <= PANTALLA_ANCHO + 50:
            if car.current_sprite:
                self.screen.blit(car.current_sprite, car_screen_pos)
            else:
                # Fallback rect
                car_rect = pygame.Rect(car_screen_pos[0], car_screen_pos[1], 
                                    car.rect.width, car.rect.height)
                pygame.draw.rect(self.screen, (0, 0, 255), car_rect)
    def _draw_game_over(self):
        """Dibuja la pantalla de game over"""
        overlay = pygame.Surface((PANTALLA_ANCHO, PANTALLA_ALTO))
        overlay.set_alpha(128)
        overlay.fill(COLOR_NEGRO)
        self.screen.blit(overlay, (0, 0))
        
        font_large = self.resource_manager.get_font('titulo')
        font_normal = self.resource_manager.get_font('pequeña')
        
        if font_large:
            game_over_text = font_large.render("JUEGO TERMINADO", True, COLOR_ROJO)
            game_over_rect = game_over_text.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 - 100))
            self.screen.blit(game_over_text, game_over_rect)
        
        if font_normal:
            restart_text = font_normal.render("Presiona [ENTER] o [ESPACIO] para reiniciar", True, COLOR_VERDE)
            restart_rect = restart_text.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 - 50))
            self.screen.blit(restart_text, restart_rect)
            
            menu_text = font_normal.render("Presiona [ESCAPE] para volver al menu", True, COLOR_BLANCO)
            menu_rect = menu_text.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 - 20))
            self.screen.blit(menu_text, menu_rect)
    
    def _draw_victory(self):
        """Dibuja la pantalla de victoria"""
        overlay = pygame.Surface((PANTALLA_ANCHO, PANTALLA_ALTO))
        overlay.set_alpha(128)
        overlay.fill((0, 50, 0))
        self.screen.blit(overlay, (0, 0))
        
        font_large = self.resource_manager.get_font('titulo')
        font_normal = self.resource_manager.get_font('pequeña')
        
        if font_large:
            victory_text = font_large.render("¡VICTORIA!", True, COLOR_TEXTO_VICTORIA)
            victory_rect = victory_text.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 - 100))
            self.screen.blit(victory_text, victory_rect)
        
        if font_normal:
            success_text = font_normal.render("¡El paquete fue entregado con éxito!", True, COLOR_TEXTO_VICTORIA)
            success_rect = success_text.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 - 50))
            self.screen.blit(success_text, success_rect)
            
            menu_text = font_normal.render("Presiona [ESCAPE] para volver al menu", True, COLOR_BLANCO)
            menu_rect = menu_text.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 - 20))
            self.screen.blit(menu_text, menu_rect)