import pygame
from typing import Callable, List, Optional, Dict
from src.Constantes import *

#TODO: Añadir animaciones: Dash
#TODO: Añadir particulas

# Constantes de movimiento del jugador

RETURN_TO_ORIGIN_SPEED = 5.0
MAX_DISTANCE_FROM_ORIGIN = 200
POSITION_TOLERANCE = 10 

class Player:
    """Jugador UAIBOT que puede saltar y hacer dash para esquivar autos"""
    
    def __init__(self, initial_x: int, initial_y: int, gravity: float, resource_manager, initial_character: str = 'UIAbot'):
        """
        Args:
            initial_x: Posicion inicial X
            initial_y: Posicion inicial Y  
            gravity: Fuerza de gravedad a aplicar
            resource_manager: Gestor de recursos para sprites y sonidos
        """
        
        self.rect = pygame.Rect(initial_x, initial_y, 32, 32)
        self.resource_manager = resource_manager
        
        # Posicion original para volver tras el dash
        self.original_position_x = initial_x
        self.original_position_y = initial_y
        
        self.personajes = ["UIAbot", "UAIBOTA", "UAIBOTINA", "UAIBOTINO"]
        self.stats = {
        "UIAbot": {  
            "jump_strength": -19, "dash_speed": 12, "dash_duration": 0.18, "dash_cooldown": 0.5, "autonomia": 20},
        "UAIBOTA": {  
            "jump_strength": -21, "dash_speed": 10, "dash_duration": 0.3, "dash_cooldown": 1.5, "autonomia":10},
        "UAIBOTINA": {  
            "jump_strength": -17, "dash_speed": 15, "dash_duration": 0.2, "dash_cooldown": 0.4, "autonomia": 30},
        "UAIBOTINO": {  
            "jump_strength": -17, "dash_speed": 14, "dash_duration": 0.2, "dash_cooldown": 0.45, "autonomia": 30}
    }

        

        for i, personaje in enumerate(self.personajes):
            if personaje == initial_character:  
                self.personaje_actual = i
                break

        print(f"Player iniciado con personaje: {self.personajes[self.personaje_actual]} (índice: {self.personaje_actual})")
        self.on_ground = True  
        
        # Variable para detectar tecla C presionada (evitar spam)
        self.c_key_pressed = False

        # Variables de fisica y movimiento
        self._init_physics(gravity)
        
        # Sistema de animacion
        self._init_animation_system()
        
        # Sistema de dash
        self._init_dash_system()
        
        # Cargar sprites y preparar animacion
        self._load_animation_frames()
        self.current_sprite = None
        self._update_sprite()
    

    def obtener_autonomia_maxima(self) -> int:
        """Retorna la autonomia maxima de todos los personajes"""
        pj_actual = self.get_current_character()
        return self.stats[pj_actual]["autonomia"]
        
    
    
    
    def _init_physics(self, gravity: float):
        """Inicializa las variables de fisica del jugador"""
        self.velocity_y = 0
        self.gravity = gravity
        self.on_ground = True
        current_character = self.personajes[self.personaje_actual]
        self.jump_strength = self.stats[current_character]["jump_strength"]

        
    def _init_animation_system(self):
        """Inicializa el sistema de animacion del sprite"""
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.08
        self.animation_frames: List[pygame.Surface] = []
        self.has_animation = False  # flag para saber si tiene animación o imagen estática
    
    def _init_dash_system(self):
        """Inicializa el sistema de dash del jugador"""
        current_character = self.personajes[self.personaje_actual]
        stats = self.stats[current_character]

        self.dash_speed = stats["dash_speed"]
        self.dash_duration = stats["dash_duration"]
        self.dash_timer = 0
        self.is_dashing = False
        self.dash_cooldown = stats["dash_cooldown"]
        self.dash_cooldown_timer = 0
        
        # sistema de retorno a posicion original
        self.return_to_origin_speed = RETURN_TO_ORIGIN_SPEED
        self.max_distance_from_origin = MAX_DISTANCE_FROM_ORIGIN
        
    def _load_animation_frames(self):
        """Carga los frames de animación directamente desde resource_manager"""
        current_character_name = self.personajes[self.personaje_actual]
        spritesheet_name = f"{current_character_name}_walk"


        print(f"Cargando animacion para personaje: {current_character_name}")
        
        # intentar cargar spritesheet con animación
        spritesheet = self.resource_manager.get_spritesheet(spritesheet_name)
        
        if spritesheet:
            # si es q tiene la  animación
            frames = self.resource_manager.get_animation_frames(spritesheet_name, 0, 5, 0)
            self.animation_frames = frames
            self.has_animation = True
        else:
            # intenta cargar  la imagen estática
            character_image = self.resource_manager.get_image(spritesheet_name)
            if character_image:
                scaled_image = pygame.transform.scale(character_image, (64, 86))
                self.animation_frames = [scaled_image]
                self.has_animation = False
            else:
                # crear placeholder si no se encuentra la imagen
                placeholder = pygame.Surface((64, 86))
                placeholder.fill((255, 0, 255))  # Magenta para debug
                self.animation_frames = [placeholder]
                self.has_animation = False

    def jump(self):
        """Hace saltar al jugador si esta en el suelo"""
        if self.on_ground:
            self.velocity_y = self.jump_strength
            self.on_ground = False
            self.resource_manager.play_sound("salto")
    
    def dash(self, energy_callback: Callable[[float], bool]) -> bool:
        """
        Ejecuta dash si hay energia y no esta en cooldown
        
        Args:
            energy_callback: Funcion para consumir energia
            
        Returns:
            True si el dash fue exitoso, False si no se pudo hacer
        """
        if self._can_perform_dash() and energy_callback(DASH_ENERGIA_COSTO):
            self._start_dash()
            return True
        return False
    
    def _can_perform_dash(self) -> bool:
        """Verifica si el jugador puede hacer dash"""
        return (not self.is_dashing and 
                self.dash_cooldown_timer <= 0)
    
    def _start_dash(self):
        """Inicia el dash del jugador"""
        self.is_dashing = True
        self.dash_timer = self.dash_duration
        self.dash_cooldown_timer = self.dash_cooldown
        self.resource_manager.play_sound("dash")
    
    def can_dash(self) -> bool:
        """Verifica si el jugador puede hacer dash (metodo publico)"""
        return self._can_perform_dash()
    
    def handle_character_change_input(self, keys_pressed: dict):
        """
        Maneja la entrada para cambio de personaje
        
        Args:
            keys_pressed: Diccionario con las teclas presionadas
        """
        if keys_pressed[pygame.K_c]:
            if not self.c_key_pressed and self.on_ground:
                self.change_character()
            self.c_key_pressed = True
        else:
            self.c_key_pressed = False
        
    def update(self, delta_time: float = 1/60, keys_pressed = None):    
        """
        Actualiza la fisica y animacion del jugador
        
        Args:
            delta_time: Tiempo transcurrido desde el ultimo frame
            keys_pressed: Diccionario con las teclas presionadas (opcional)
        """
        self._update_cooldowns(delta_time)
        self._update_dash_movement(delta_time)
        self._update_return_to_origin(delta_time)
        self._update_vertical_physics(delta_time)
        self._update_animation_if_grounded(delta_time)
        
        if keys_pressed:
            self.handle_character_change_input(keys_pressed)
    

    def change_character(self):
        """Cambia el personaje del jugador cargando directamente desde resource_manager"""
        self.personaje_actual = (self.personaje_actual + 1) % len(self.personajes)
        current_character = self.personajes[self.personaje_actual]
        stats = self.stats[current_character]

   
        self.jump_strength = stats["jump_strength"]
        self.dash_speed = stats["dash_speed"]
        self.dash_duration = stats["dash_duration"]
        self.dash_cooldown = stats["dash_cooldown"]
      
    
        self.current_sprite = None
        self._load_animation_frames()
        
        self.animation_frame = 0
        self._update_sprite()
        
        self.resource_manager.play_sound("cambio_personaje")

    def get_current_character(self):
        """Retorna el nombre del personaje actual"""
        return self.personajes[self.personaje_actual]
        
    def _update_cooldowns(self, delta_time: float):
        """Actualiza los timers de cooldown"""
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer -= delta_time
    
    def _update_dash_movement(self, delta_time: float):
        """Maneja el movimiento durante el dash"""
        if self.is_dashing:
            self.dash_timer -= delta_time
            self.rect.x += self.dash_speed
            
            if self.dash_timer <= 0:
                self.is_dashing = False
    
    def _update_return_to_origin(self, delta_time: float):
        """Maneja el retorno gradual a la posicion original"""
        if not self.is_dashing:
            distance_from_origin = self.rect.x - self.original_position_x
            
            if abs(distance_from_origin) > POSITION_TOLERANCE:
                self._move_towards_origin(distance_from_origin)
    
    def _move_towards_origin(self, distance_from_origin: float):
        """Mueve al jugador gradualmente hacia su posicion original"""
        if distance_from_origin > 0:
            return_speed = min(self.return_to_origin_speed, distance_from_origin)
            self.rect.x -= return_speed
        else:
            return_speed = min(self.return_to_origin_speed, abs(distance_from_origin))
            self.rect.x += return_speed
    
    def _update_vertical_physics(self, delta_time: float):
        """Actualiza la fisica vertical (gravedad y colision con suelo)"""
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y
        
        if self.rect.y >= self.original_position_y:
            self._land_on_ground()
    
    def _land_on_ground(self):
        """Maneja el aterrizaje del jugador en el suelo"""
        self.rect.y = self.original_position_y
        self.velocity_y = 0
        self.on_ground = True
    
    def _update_animation_if_grounded(self, delta_time: float):
        """Actualiza la animacion solo si esta en el suelo"""
        if self.on_ground:
            self._update_animation(delta_time)
    
    def _update_sprite(self):
        """Actualiza el sprite actual"""
        if self.animation_frames and len(self.animation_frames) > 0:
            if self.has_animation:
                frame_index = int(self.animation_frame) % len(self.animation_frames)
                self.current_sprite = self.animation_frames[frame_index]
            else:
                self.current_sprite = self.animation_frames[0]
        else:
            self.current_sprite = pygame.Surface((64, 86))
            self.current_sprite.fill((255, 0, 255))  # rosa para debug
    
    def _update_animation(self, delta_time: float):
        """Actualiza el frame de animación solo si tiene animación"""
        if self.has_animation and len(self.animation_frames) > 1:
            self.animation_timer += delta_time
            
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % len(self.animation_frames)
                self._update_sprite()
        else:
            if not self.current_sprite and self.animation_frames:
                self._update_sprite()
            elif self.animation_frames and len(self.animation_frames) == 1:
                expected_sprite = self.animation_frames[0]
                if self.current_sprite != expected_sprite:
                    self._update_sprite()
                elif not self.current_sprite:
                    self._update_sprite()
            
            if not self.current_sprite and self.animation_frames:
                self.current_sprite = self.animation_frames[0]
