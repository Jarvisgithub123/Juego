import pygame
import random
from typing import List
from src.Constantes import *
from src.entities.Car import Car

class CarSpawner:
    """Maneja la generación y limpieza de autos enemigos"""
    
    # Constantes de configuración
    MIN_SPAWN_INTERVAL = 2.5
    MAX_SPAWN_INTERVAL = 5.0
    MIN_CAR_DISTANCE = 320
    MAX_VISIBLE_CARS = 2
    MIN_SPAWN_DISTANCE_FROM_PLAYER = 400
    CAR_CLEANUP_MARGIN = 500  # Aumentado para dar más margen
    
    def __init__(self, resource_manager):
        self.resource_manager = resource_manager
        self.cars: List[Car] = []
        self.spawn_timer = 0.0
        self.next_spawn_time = 2.0
        self._spawn_initial_car()
    
    def _spawn_initial_car(self):
        """Genera el primer auto para que aparezca inmediatamente"""
        first_car = Car(PANTALLA_ANCHO, PISO_POS_Y - 86, 
                       self.resource_manager, speed=VELOCIDAD_AUTO_BASE)
        self.cars.append(first_car)
    
    def update(self, delta_time: float, camera_x: float, player_x: float):
        """Actualiza el sistema de spawn de autos"""
        self._update_spawn_timer(delta_time)
        self._try_spawn_car(camera_x, player_x)
        self._cleanup_distant_cars(camera_x)
        self._update_cars(delta_time)
    
    def _update_spawn_timer(self, delta_time: float):
        """Actualiza el timer de spawn"""
        self.spawn_timer += delta_time
    
    def _try_spawn_car(self, camera_x: float, player_x: float):
        """Intenta spawnear un nuevo auto si es posible"""
        if self.spawn_timer >= self.next_spawn_time:
            if self._can_spawn_car(camera_x, player_x):
                self._spawn_car(camera_x)
                self._reset_spawn_timer()
            else:
                self._adjust_spawn_timer_for_retry()
    
    def _can_spawn_car(self, camera_x: float, player_x: float) -> bool:
        """Verifica si se puede spawnear un auto sin ser injusto"""
        spawn_x = self._calculate_spawn_position(camera_x)
        return (self._has_safe_distance(spawn_x) and 
                self._not_too_many_visible(camera_x) and 
                self._safe_from_player(spawn_x, player_x))
    
    def _calculate_spawn_position(self, camera_x: float) -> int:
        """Calcula donde aparecerá el próximo auto"""
        return camera_x + PANTALLA_ANCHO + random.randint(200, 500)
    
    def _has_safe_distance(self, spawn_x: int) -> bool:
        """Verifica distancia segura entre autos"""
        return all(abs(car.rect.x - spawn_x) >= self.MIN_CAR_DISTANCE 
                  for car in self.cars)
    
    def _not_too_many_visible(self, camera_x: float) -> bool:
        """Verifica que no haya demasiados autos visibles"""
        # Margen más generoso para contar autos visibles
        margin = 150  # Aumentado desde 100
        visible_count = sum(1 for car in self.cars 
                           if -margin <= car.rect.x - camera_x <= PANTALLA_ANCHO + margin)
        return visible_count < self.MAX_VISIBLE_CARS
    
    def _safe_from_player(self, spawn_x: int, player_x: float) -> bool:
        """Verifica distancia segura del jugador"""
        return spawn_x - player_x >= self.MIN_SPAWN_DISTANCE_FROM_PLAYER
    
    def _spawn_car(self, camera_x: float):
        """Crea un nuevo auto en posición segura"""
        spawn_x = self._calculate_spawn_position(camera_x)
        speed = self._generate_car_speed()
        new_car = Car(spawn_x, PISO_POS_Y - 86, self.resource_manager, speed=speed)
        self.cars.append(new_car)
    
    def _generate_car_speed(self) -> int:
        """Genera velocidad balanceada para el auto"""
        variation = min(VELOCIDAD_AUTO_VARIACION, 3)
        speed = VELOCIDAD_AUTO_BASE + random.randint(-variation, variation)
        return max(6, min(speed, VELOCIDAD_AUTO_BASE + 4))
    
    def _reset_spawn_timer(self):
        """Reinicia el timer con nuevo intervalo aleatorio"""
        self.spawn_timer = 0
        self.next_spawn_time = random.uniform(self.MIN_SPAWN_INTERVAL, self.MAX_SPAWN_INTERVAL)
    
    def _adjust_spawn_timer_for_retry(self):
        """Ajusta timer para reintentar spawn más rápido"""
        retry_delay = random.uniform(0.5, 1.0)
        self.spawn_timer = max(0, self.next_spawn_time - retry_delay)
    
    def _cleanup_distant_cars(self, camera_x: float):
        """Elimina autos lejanos para liberar memoria"""
        # Los autos se eliminan cuando están completamente fuera del borde izquierdo
        # con un margen generoso para evitar eliminación prematura
        cleanup_threshold = camera_x - self.CAR_CLEANUP_MARGIN
        cars_before = len(self.cars)
        self.cars = [car for car in self.cars if car.rect.right > cleanup_threshold]
        
        # Debug opcional: mostrar cuando se eliminan autos
        cars_removed = cars_before - len(self.cars)
        if cars_removed > 0:
            print(f"DEBUG: Eliminados {cars_removed} autos. Threshold: {cleanup_threshold}")
    
    def _update_cars(self, delta_time: float):
        """Actualiza todos los autos"""
        for car in self.cars:
            car.update(delta_time)
    
    def check_collisions(self, player_rect: pygame.Rect) -> bool:
        """Verifica colisiones entre jugador y autos"""
        player_hitbox = player_rect.inflate(-8, -8)
        return any(player_hitbox.colliderect(car.rect.inflate(-5, -20)) 
                  for car in self.cars)
    
    def get_cars(self) -> List[Car]:
        """Obtiene la lista de autos"""
        return self.cars