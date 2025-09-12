import pygame
import random
from typing import List
from src.Constantes import *
from src.entities.Car import Car

class CarSpawner:
    """Sistema de spawn simplificado pero más variado """
    
    def __init__(self, resource_manager):
        self.resource_manager = resource_manager
        self.cars: List[Car] = []
        self.spawn_timer = 0.0
        self.next_spawn_time = 2.0
        
        #Pre-crear rectángulos para colisiones
        self.player_hitbox = pygame.Rect(0, 0, 0, 0)
        self.car_hitbox = pygame.Rect(0, 0, 0, 0)
        
        self._spawn_initial_car()
    
    def _spawn_initial_car(self):
        """Genera el primer auto"""
        first_car = Car(PANTALLA_ANCHO, PISO_POS_Y - 86, 
                       self.resource_manager, speed=self._generate_car_speed())
        self.cars.append(first_car)
    
    def update(self, delta_time: float, camera_x: float, player_x: float):
        """Actualiza el sistema de spawn"""
        self.spawn_timer += delta_time
        
        if self.spawn_timer >= self.next_spawn_time:
            if self._can_spawn_car(camera_x, player_x):
                num_cars = self._decide_spawn_count()
                self._spawn_cars(camera_x, num_cars)
                self._reset_spawn_timer()
        
        self._cleanup_cars(camera_x)
        self._update_cars(delta_time)
    
    def _decide_spawn_count(self) -> int:
        """Decide cuántos autos spawner (1 o 2)"""
        return random.choices([1, 2], weights=[40, 60], k=1)[0]
    
    def _can_spawn_car(self, camera_x: float, player_x: float) -> bool:
        """Verifica si se puede spawner"""
        spawn_x = camera_x + PANTALLA_ANCHO + 300
        
        # No más de 4 autos visibles
        visible_cars = sum(1 for car in self.cars 
                          if car.rect.x - camera_x > -200 and car.rect.x - camera_x < PANTALLA_ANCHO + 200)
        
        return (visible_cars < 4 and
                spawn_x - player_x >= 500 and
                self._safe_distance_from_other_cars(spawn_x))
    
    def _safe_distance_from_other_cars(self, spawn_x: int) -> bool:
        """Verifica distancia minima con otros autos"""
        for car in self.cars:
            if abs(car.rect.x - spawn_x) < 250:
                return False
        return True
    
    def _spawn_cars(self, camera_x: float, num_cars: int):
        """Spawner 1 o 2 autos con diferentes configuraciones"""
        base_x = camera_x + PANTALLA_ANCHO + random.randint(300, 500)
        
        if num_cars == 1:
            speed = self._generate_car_speed()
            new_car = Car(base_x, PISO_POS_Y - 86, self.resource_manager, speed=speed)
            self.cars.append(new_car)
        
        elif num_cars == 2:
            fast_speed = random.randint(18, 22)
            fast_car = Car(base_x, PISO_POS_Y - 86, self.resource_manager, speed=fast_speed)
            self.cars.append(fast_car)
            slow_speed = random.randint(8, 12)
            gap = random.randint(300, 500)
            slow_car = Car(base_x + gap, PISO_POS_Y - 86, self.resource_manager, speed=slow_speed)
            self.cars.append(slow_car)
    
    def _generate_car_speed(self) -> int:
        """Genera velocidad más variada para un solo auto"""
        speed_type = random.choices(['lento', 'normal', 'rapido'], weights=[30, 40, 30], k=1)[0]
        
        if speed_type == 'lento':
            return random.randint(8, 12)
        elif speed_type == 'normal':
            return random.randint(13, 17)
        else:  # rápido
            return random.randint(18, 22)
    
    def _reset_spawn_timer(self):
        """Reinicia el timer con nuevo intervalo"""
        self.spawn_timer = 0
        self.next_spawn_time = random.uniform(3.0, 6.0)
    
    def _cleanup_cars(self, camera_x: float):
        """Elimina autos que están muy atrás"""
        cleanup_threshold = camera_x - 600
        self.cars = [car for car in self.cars if car.rect.right > cleanup_threshold]
    
    def _update_cars(self, delta_time: float):
        """Actualiza todos los autos"""
        for car in self.cars:
            car.update(delta_time)
    
    def check_collisions(self, player_rect: pygame.Rect) -> bool:
        """Colisiones"""
        # Pre-calcular hitbox del jugador
        player_left = player_rect.x + 4
        player_top = player_rect.y + 4
        player_right = player_left + player_rect.width - 8
        player_bottom = player_top + player_rect.height - 8
        
        for car in self.cars:
            # Verificación rápida de distancia antes de calcular hitbox
            if abs(car.rect.x - player_rect.x) > 150:
                continue  # Skip si están muy lejos
            
            # Hitbox del auto
            car_left = car.rect.x + 2
            car_top = car.rect.y + 10
            car_right = car_left + car.rect.width - 5
            car_bottom = car_top + car.rect.height - 20
            
            # Colisión manual (más rápido que colliderect)
            if (player_right > car_left and player_left < car_right and
                player_bottom > car_top and player_top < car_bottom):
                return True
        
        return False
    
    def get_cars(self) -> List[Car]:
        """Obtiene la lista de autos"""
        return self.cars