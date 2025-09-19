import pygame
from typing import Callable, List, Optional, Dict
from src.Constantes import *

class Player:
    """Player con sistema de escudo integrado"""
    
    def __init__(self, initial_x: int, initial_y: int, gravity: float, resource_manager, initial_character: str = 'UIAbot'):
        """
        Args:
            initial_x: Posicion inicial X
            initial_y: Posicion inicial Y  
            gravity: Fuerza de gravedad a aplicar
            resource_manager: Gestor de recursos para sprites y sonidos
            initial_character: Personaje inicial
        """
        
        self.rect = pygame.Rect(initial_x, initial_y, 32, 32)
        self.resource_manager = resource_manager
        
        # Posicion original para volver tras el dash
        self.original_position_x = initial_x
        self.original_position_y = initial_y
        
        # COMPATIBILIDAD: Mantener la estructura original que espera el codigo existente
        self.personajes = ["UIAbot", "UAIBOTA", "UAIBOTINA", "UAIBOTINO"]
        self.stats = {
            "UIAbot": {  
                "jump_strength": UAIBOT_JUMP_STRENGTH, 
                "dash_speed": UAIBOT_DASH_SPEED, 
                "dash_duration": UAIBOT_DASH_DURATION, 
                "dash_cooldown": UAIBOT_DASH_COOLDOWN, 
                "autonomia": UAIBOT_AUTONOMIA
            },
            "UAIBOTA": {  
                "jump_strength": UAIBOTA_JUMP_STRENGTH, 
                "dash_speed": UAIBOTA_DASH_SPEED, 
                "dash_duration": UAIBOTA_DASH_DURATION, 
                "dash_cooldown": UAIBOTA_DASH_COOLDOWN, 
                "autonomia": UAIBOTA_AUTONOMIA
            },
            "UAIBOTINA": {  
                "jump_strength": UAIBOTINA_JUMP_STRENGTH, 
                "dash_speed": UAIBOTINA_DASH_SPEED, 
                "dash_duration": UAIBOTINA_DASH_DURATION, 
                "dash_cooldown": UAIBOTINA_DASH_COOLDOWN, 
                "autonomia": UAIBOTINA_AUTONOMIA
            },
            "UAIBOTINO": {  
                "jump_strength": UAIBOTINO_JUMP_STRENGTH, 
                "dash_speed": UAIBOTINO_DASH_SPEED, 
                "dash_duration": UAIBOTINO_DASH_DURATION, 
                "dash_cooldown": UAIBOTINO_DASH_COOLDOWN, 
                "autonomia": UAIBOTINO_AUTONOMIA
            }
        }

        # Encontrar indice del personaje inicial
        for i, personaje in enumerate(self.personajes):
            if personaje == initial_character:  
                self.personaje_actual = i
                break
        else:
            self.personaje_actual = 0  # Default a UIAbot si no se encuentra

        print(f"Player iniciado con personaje: {self.personajes[self.personaje_actual]} (indice: {self.personaje_actual})")
        self.on_ground = True  
        
        # Variable para detectar tecla C presionada (evitar spam)
        self.c_key_pressed = False
        self.space_key_pressed = False  #evitar spam de salto
        self.z_key_pressed = False      #evitar spam de dash

        # Variables de fisica y movimiento
        self._init_physics(gravity)
        
        # Sistema de animacion
        self._init_animation_system()
        
        # Sistema de dash
        self._init_dash_system()
        
        #Sistema de escudo
        self._init_shield_system()
        
        # Cargar sprites y preparar animacion
        self._load_animation_frames()
        self.current_sprite = None
        self._update_sprite()
    
    def _init_shield_system(self):
        """Inicializa el sistema de escudo del jugador"""
        self.has_shield = False
        self.shield_time = 0.0
        self.shield_collision_effect_time = 0.0  # Para mostrar efecto cuando se usa el escudo
        self.max_shield_time = ESCUDO_DURACION
        
    def update_shield(self, delta_time: float):
        """Actualiza el estado del escudo"""
        if self.has_shield and self.shield_time > 0:
            self.shield_time -= delta_time
            if self.shield_time <= 0:
                self.has_shield = False
                self.shield_time = 0.0
                print("Escudo desactivado")
        
        # Actualizar efecto de colision del escudo
        if self.shield_collision_effect_time > 0:
            self.shield_collision_effect_time -= delta_time * 1000  # Convertir a milisegundos
    
    def activate_shield_collision_effect(self):
        """Activa el efecto visual cuando el escudo absorbe una colision"""
        if self.has_shield:
            self.shield_collision_effect_time = SHIELD_EFFECT_DURATION
            # Reducir un poco el tiempo de escudo al usarse
            self.shield_time = max(0, self.shield_time - 0.5)
            print("¡Escudo absorbe colisión!")
            
            # Reproducir sonido de impacto del escudo
            self.resource_manager.play_sound("shield_hit")
            return True
        return False
    
    def is_protected(self) -> bool:
        """Verifica si el jugador está protegido por el escudo"""
        return self.has_shield and self.shield_time > 0
    
    def should_show_shield_effect(self) -> bool:
        """Verifica si debe mostrarse el efecto visual del escudo"""
        return self.has_shield and self.shield_time > 0
    
    def should_show_collision_effect(self) -> bool:
        """Verifica si debe mostrarse el efecto de colision del escudo"""
        return self.shield_collision_effect_time > 0
    
    def get_shield_time_remaining(self) -> float:
        """Retorna el tiempo restante de escudo"""
        return self.shield_time if self.has_shield else 0.0
    
    def get_shield_percentage(self) -> float:
        """Retorna el porcentaje de escudo restante (0.0 a 1.0)"""
        if not self.has_shield:
            return 0.0
        return min(1.0, self.shield_time / self.max_shield_time)
    
    def obtener_autonomia_maxima(self) -> int:
        """Retorna la autonomia maxima del personaje actual"""
        pj_actual = self.get_current_character()
        return self.stats[pj_actual]["autonomia"]
    
    def _init_physics(self, gravity: float):
        """Inicializa las variables de fisica del jugador usando constantes"""
        self.velocity_y = 0
        self.gravity = gravity
        self.on_ground = True
        current_character = self.personajes[self.personaje_actual]
        self.jump_strength = self.stats[current_character]["jump_strength"]
    
    def _init_animation_system(self):
        """Inicializa el sistema de animacion del sprite"""
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = PLAYER_ANIMATION_SPEED  # Usar constante
        self.animation_frames: List[pygame.Surface] = []
        self.has_animation = False
        
        # Cache para evitar recargar innecesariamente
        self._cached_character = None
    
    def _init_dash_system(self):
        """Inicializa el sistema de dash del jugador usando constantes"""
        current_character = self.personajes[self.personaje_actual]
        stats = self.stats[current_character]

        self.dash_speed = stats["dash_speed"]
        self.dash_duration = stats["dash_duration"]
        self.dash_timer = 0
        self.is_dashing = False
        self.dash_cooldown = stats["dash_cooldown"]
        self.dash_cooldown_timer = 0
    
    def _load_animation_frames(self):
        """Carga los frames de animacion - optimizado para evitar recargas innecesarias"""
        current_character_name = self.personajes[self.personaje_actual]
        
        # Solo recargar si cambio el personaje
        if self._cached_character == current_character_name:
            return
            
        spritesheet_name = f"{current_character_name}_walk"

        print(f"Cargando animacion para personaje: {current_character_name}")
        
        # intentar cargar spritesheet con animacion
        spritesheet = self.resource_manager.get_spritesheet(spritesheet_name)
        
        if spritesheet:
            frames = self.resource_manager.get_animation_frames(
                spritesheet_name, 
                SPRITESHEET_START_COLUMN, 
                SPRITESHEET_END_COLUMN, 
                SPRITESHEET_ROW
            )
            self.animation_frames = frames
            self.has_animation = True
        else:
            # intenta cargar imagen estatica
            character_image = self.resource_manager.get_image(spritesheet_name)
            if character_image:
                scaled_image = pygame.transform.scale(
                    character_image, 
                    (PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT)
                )
                self.animation_frames = [scaled_image]
                self.has_animation = False
            else:
                # crear placeholder si no se encuentra la imagen
                placeholder = pygame.Surface((PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT))
                placeholder.fill((255, 0, 255))  # Magenta para debug
                self.animation_frames = [placeholder]
                self.has_animation = False
        
        self._cached_character = current_character_name
        self.animation_frame = 0  # Resetear animacion

    def jump(self):
        """Hace saltar al jugador si esta en el suelo"""
        if self.on_ground:
            self.velocity_y = self.jump_strength
            self.on_ground = False
            self.resource_manager.play_sound("salto")
    
    def dash(self, energy_callback: Callable[[float], bool]) -> bool:
        """
        Ejecuta dash si hay energia y no esta en cooldown
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
        """Maneja entrada para cambio de personaje - con anti-spam mejorado"""
        if keys_pressed[pygame.K_c]:
            if not self.c_key_pressed and self.on_ground:
                self.change_character()
            self.c_key_pressed = True
        else:
            self.c_key_pressed = False
    
    def _handle_jump_input(self, keys_pressed: dict):
        """Maneja entrada de salto con anti-spam"""
        if keys_pressed[pygame.K_SPACE]:
            if not self.space_key_pressed:
                self.jump()
            self.space_key_pressed = True
        else:
            self.space_key_pressed = False
    
    def _handle_dash_input(self, keys_pressed: dict, energy_callback: Callable[[float], bool]):
        """Maneja entrada de dash con anti-spam"""
        if keys_pressed[pygame.K_z]:
            if not self.z_key_pressed:
                self.dash(energy_callback)
            self.z_key_pressed = True
        else:
            self.z_key_pressed = False
        
    def update(self, delta_time: float = 1/60, keys_pressed=None, energy_callback: Callable[[float], bool] = None):    
        """
        Actualiza la fisica y animacion del jugador - mejorado con anti-spam y sistema de escudo
        """
        self._update_cooldowns(delta_time)
        self._update_dash_movement(delta_time)
        self._update_return_to_origin(delta_time)
        self._update_vertical_physics(delta_time)
        self._update_animation_if_grounded(delta_time)
        
        #Actualizar sistema de escudo
        self.update_shield(delta_time)
        
        if keys_pressed:
            self.handle_character_change_input(keys_pressed)
            self._handle_jump_input(keys_pressed)
            if energy_callback:
                self._handle_dash_input(keys_pressed, energy_callback)

    def change_character(self):
        """Cambia el personaje del jugador """
        old_character = self.personajes[self.personaje_actual]
        self.personaje_actual = (self.personaje_actual + 1) % len(self.personajes)
        new_character = self.personajes[self.personaje_actual]
        
        # Solo actualizar si realmente cambio
        if old_character != new_character:
            stats = self.stats[new_character]
            
            # Actualizar estadisticas fisicas
            self.jump_strength = stats["jump_strength"]
            self.dash_speed = stats["dash_speed"]
            self.dash_duration = stats["dash_duration"]
            self.dash_cooldown = stats["dash_cooldown"]
        
            # Recargar animacion
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
        """Maneja el retorno gradual a la posicion original usando constantes"""
        if not self.is_dashing:
            distance_from_origin = self.rect.x - self.original_position_x
            
            if abs(distance_from_origin) > POSITION_TOLERANCE:
                self._move_towards_origin(distance_from_origin)
    
    def _move_towards_origin(self, distance_from_origin: float):
        """Mueve al jugador gradualmente hacia su posicion original usando constantes"""
        if distance_from_origin > 0:
            return_speed = min(RETURN_TO_ORIGIN_SPEED, distance_from_origin)
            self.rect.x -= return_speed
        else:
            return_speed = min(RETURN_TO_ORIGIN_SPEED, abs(distance_from_origin))
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
        """Actualiza el sprite actual para evitar updates innecesarios"""
        if not self.animation_frames:
            return
            
        if self.has_animation and len(self.animation_frames) > 1:
            frame_index = int(self.animation_frame) % len(self.animation_frames)
            new_sprite = self.animation_frames[frame_index]
        else:
            new_sprite = self.animation_frames[0]
        
        # Solo actualizar si el sprite cambio 
        if self.current_sprite != new_sprite:
            self.current_sprite = new_sprite
    
    def _update_animation(self, delta_time: float):
        """Actualiza el frame de animacion"""
        if self.has_animation and len(self.animation_frames) > 1:
            self.animation_timer += delta_time
            
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                old_frame = self.animation_frame
                self.animation_frame = (self.animation_frame + 1) % len(self.animation_frames)
                
                # Solo actualizar sprite si el frame cambio
                if old_frame != self.animation_frame:
                    self._update_sprite()
        elif not self.current_sprite and self.animation_frames:
            self._update_sprite()