import pygame
import random
from typing import List
from src.Constantes import *
from src.systems.car_pool import CarPool

# Constantes extraidas para evitar numeros magicos
DEFAULT_SPAWN_TIME = 2.0
MAX_VISIBLE_CARS = 4
MIN_DISTANCE_TO_PLAYER = 500
MIN_SPACING_BETWEEN_CARS = 250
SPAWN_X_OFFSET_MIN = 300
SPAWN_X_OFFSET_MAX = 500
PLAYER_HITBOX_SHRINK = (-8, -8)
CAR_HITBOX_SHRINK = (-7, -20)
CLEANUP_THRESHOLD_OFFSET = 600


# Constantes de velocidad de autos
SLOW_CAR_SPEED_MIN = 7
SLOW_CAR_SPEED_MAX = 9
NORMAL_CAR_SPEED_MIN = 10
NORMAL_CAR_SPEED_MAX = 13
FAST_CAR_SPEED_MIN = 14
FAST_CAR_SPEED_MAX = 15
VERY_FAST_CAR_SPEED_MIN = 16
VERY_FAST_CAR_SPEED_MAX = 18
SLOW_PAIRED_CAR_SPEED_MIN = 8
SLOW_PAIRED_CAR_SPEED_MAX = 12

# Pesos para generacion de tipos de auto
SLOW_CAR_WEIGHT = 30
NORMAL_CAR_WEIGHT = 40
FAST_CAR_WEIGHT = 30
SINGLE_CAR_WEIGHT = 40
DOUBLE_CAR_WEIGHT = 60

# Intervalos de spawn
SPAWN_INTERVAL_MIN = 3.0
SPAWN_INTERVAL_MAX = 6.0
CAR_GAP_MIN = 300
CAR_GAP_MAX = 500

class CarSpawner:
    """Sistema de spawn optimizado con object pooling"""

    def __init__(self, resource_manager):
        self.resource_manager = resource_manager
        
        # Usar CarPool en lugar de lista simple
        self.car_pool = CarPool(resource_manager)

        # Timers de spawn
        self.spawn_timer = 0.0
        self.next_spawn_time = DEFAULT_SPAWN_TIME

        # Configurables (extraidas como constantes)
        self.max_visible_cars = MAX_VISIBLE_CARS
        self.min_distance_to_player = MIN_DISTANCE_TO_PLAYER
        self.min_spacing_between_cars = MIN_SPACING_BETWEEN_CARS
        self.spawn_x_offset_min = SPAWN_X_OFFSET_MIN
        self.spawn_x_offset_max = SPAWN_X_OFFSET_MAX

        # Hitbox tuning
        self.player_hitbox_shrink = PLAYER_HITBOX_SHRINK
        self.car_hitbox_shrink = CAR_HITBOX_SHRINK

        # Generar primer auto
        self._spawn_initial_car()

    def _spawn_initial_car(self):
        """Crea el primer auto usando el pool"""
        x = PANTALLA_ANCHO
        y = PISO_POS_Y - 86
        speed = self._generate_car_speed()
        self.car_pool.get_car(x, y, speed)

    def _generate_car_speed(self) -> int:
        """Velocidad variada: lento / normal / rapido usando constantes"""
        type_choice = random.choices(
            ['lento', 'normal', 'rapido'], 
            weights=[SLOW_CAR_WEIGHT, NORMAL_CAR_WEIGHT, FAST_CAR_WEIGHT], 
            k=1
        )[0]
        
        if type_choice == 'lento':
            return random.randint(SLOW_CAR_SPEED_MIN, SLOW_CAR_SPEED_MAX)
        elif type_choice == 'normal':
            return random.randint(NORMAL_CAR_SPEED_MIN, NORMAL_CAR_SPEED_MAX)
        else:  # rapido
            return random.randint(FAST_CAR_SPEED_MIN, FAST_CAR_SPEED_MAX)

    def _next_spawn_interval(self) -> float:
        """Genera intervalo aleatorio entre spawns"""
        return random.uniform(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX)

    def update(self, delta_time: float, camera_x: float, player_x: float):
        """Actualizar con logica de pooling optimizada"""
        self.spawn_timer += delta_time

        if self.spawn_timer >= self.next_spawn_time:
            if self._can_spawn_car(camera_x, player_x):
                count = self._decide_spawn_count()
                self._spawn_cars(camera_x, count)
                self._reset_spawn_timer()

        # Usar metodos optimizados del pool
        self.car_pool.cleanup_cars(camera_x)
        self.car_pool.update_active_cars(delta_time)

    def _decide_spawn_count(self) -> int:
        """Decide 1 o 2 autos; ponderado con constantes"""
        return random.choices(
            [1, 2], 
            weights=[SINGLE_CAR_WEIGHT, DOUBLE_CAR_WEIGHT], 
            k=1
        )[0]

    def _can_spawn_car(self, camera_x: float, player_x: float) -> bool:
        """Comprueba condiciones usando autos activos del pool"""
        spawn_x = camera_x + PANTALLA_ANCHO + self.spawn_x_offset_min

        # Contar autos visibles del pool
        visible = self._count_visible_cars(camera_x)
        if visible >= self.max_visible_cars:
            return False

        # Evitar spawnear demasiado cerca del jugador
        if spawn_x - player_x < self.min_distance_to_player:
            return False

        # Spacing con otros autos
        return self._safe_distance_from_other_cars(spawn_x)

    def _count_visible_cars(self, camera_x: float) -> int:
        """Cuenta autos visibles usando el pool"""
        visible_count = 0
        margin = 200
        
        for car in self.car_pool.get_active_cars():
            car_screen_x = car.rect.x - camera_x
            if -margin < car_screen_x < (PANTALLA_ANCHO + margin):
                visible_count += 1
                
        return visible_count

    def _safe_distance_from_other_cars(self, spawn_x: int) -> bool:
        """Verifica distancia usando autos activos del pool"""
        for car in self.car_pool.get_active_cars():
            if abs(car.rect.x - spawn_x) < self.min_spacing_between_cars:
                return False
        return True

    def _spawn_cars(self, camera_x: float, num_cars: int):
        """Spawn usando el pool de objetos"""
        base_x = camera_x + PANTALLA_ANCHO + random.randint(
            self.spawn_x_offset_min, self.spawn_x_offset_max
        )
        y = PISO_POS_Y - 86

        if num_cars == 1:
            speed = self._generate_car_speed()
            self.car_pool.get_car(base_x, y, speed)
            return

        # num_cars == 2: uno rapido adelante y otro mas lento mas atras
        fast_speed = random.randint(VERY_FAST_CAR_SPEED_MIN, VERY_FAST_CAR_SPEED_MAX)
        slow_speed = random.randint(SLOW_PAIRED_CAR_SPEED_MIN, SLOW_PAIRED_CAR_SPEED_MAX)
        gap = random.randint(CAR_GAP_MIN, CAR_GAP_MAX)

        self.car_pool.get_car(base_x, y, fast_speed)
        self.car_pool.get_car(base_x + gap, y, slow_speed)

    def _reset_spawn_timer(self):
        """Resetea timer de spawn"""
        self.spawn_timer = 0.0
        self.next_spawn_time = self._next_spawn_interval()

    def check_collisions(self, player_rect: pygame.Rect) -> bool:
        """Verificar colisiones optimizada usando pool"""
        active_cars = self.car_pool.get_active_cars()
        if not active_cars:
            return False

        # Hitbox reducida del jugador para ser mas justo
        player_hit = player_rect.inflate(*self.player_hitbox_shrink)

        # Solo verificar autos cercanos
        for car in active_cars:
            # Filtro rapido por distancia X usando constante
            if abs(car.rect.x - player_rect.x) > COLLISION_DISTANCE_THRESHOLD:
                continue

            car_hit = car.rect.inflate(*self.car_hitbox_shrink)
            if car_hit.colliderect(player_hit):
                return True

        return False

    def get_cars(self) -> List:
        """Retorna autos activos del pool"""
        return self.car_pool.get_active_cars()
    
    def get_pool_statistics(self) -> dict:
        """Metodo de debugging para ver estado del pool"""
        return self.car_pool.get_pool_stats()