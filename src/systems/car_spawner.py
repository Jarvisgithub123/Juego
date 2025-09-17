import pygame
import random
from typing import List
from src.Constantes import *
from src.entities.Car import Car

class CarSpawner:
    """Sistema de spawn de autos más claro y configurable."""

    def __init__(self, resource_manager):
        self.resource_manager = resource_manager
        self.cars: List[Car] = []

        # Timers de spawn
        self.spawn_timer = 0.0
        self.next_spawn_time = 2.0

        # Configurables (fáciles de ajustar)
        self.max_visible_cars = 4
        self.min_distance_to_player = 500
        self.min_spacing_between_cars = 250
        self.spawn_x_offset_min = 300
        self.spawn_x_offset_max = 500

        # Hitbox tuning (usar inflate)
        self.player_hitbox_shrink = (-8, -8)  # (x, y) reducción del rect del jugador
        self.car_hitbox_shrink = (-7, -20)    # reduce ancho/alto para colisión más justa

        # Generar primer auto
        self._spawn_initial_car()

    # ------------------------------
    # Métodos internos de spawn
    # ------------------------------
    def _spawn_initial_car(self):
        x = PANTALLA_ANCHO
        y = PISO_POS_Y - 86
        self.cars.append(self._create_car(x, y, self._generate_car_speed()))

    def _create_car(self, x: float, y: float, speed: int) -> Car:
        """Factory para crear un objeto Car con recursos ya cargados."""
        return Car(x, y, self.resource_manager, speed=speed)

    def _generate_car_speed(self) -> int:
        """Velocidad variada: lento / normal / rápido."""
        type_choice = random.choices(['lento', 'normal', 'rapido'], weights=[30, 40, 30], k=1)[0]
        if type_choice == 'lento':
            return random.randint(7, 9) # 6 7
        if type_choice == 'normal':
            return random.randint(10, 13)
        return random.randint(14, 16)

    def _next_spawn_interval(self):
        return random.uniform(3.0, 6.0)

    def update(self, delta_time: float, camera_x: float, player_x: float):
        """Actualizar timer, spawnear si corresponde, actualizar y limpiar autos."""
        self.spawn_timer += delta_time

        if self.spawn_timer >= self.next_spawn_time:
            if self._can_spawn_car(camera_x, player_x):
                count = self._decide_spawn_count()
                self._spawn_cars(camera_x, count)
                self._reset_spawn_timer()

        self._cleanup_cars(camera_x)
        self._update_cars(delta_time)

    def _decide_spawn_count(self) -> int:
        """Decide 1 o 2 autos; ponderado."""
        return random.choices([1, 2], weights=[40, 60], k=1)[0]

    def _can_spawn_car(self, camera_x: float, player_x: float) -> bool:
        """Comprueba condiciones para spawnear: visibilidad, distancia al jugador y spacing."""
        spawn_x = camera_x + PANTALLA_ANCHO + self.spawn_x_offset_min

        # contar autos en pantalla (con margen)
        visible = sum(
            1 for car in self.cars
            if -200 < (car.rect.x - camera_x) < (PANTALLA_ANCHO + 200)
        )
        if visible >= self.max_visible_cars:
            return False

        # evitar spawnear demasiado cerca del jugador
        if spawn_x - player_x < self.min_distance_to_player:
            return False

        # spacing con otros autos
        return self._safe_distance_from_other_cars(spawn_x)

    def _safe_distance_from_other_cars(self, spawn_x: int) -> bool:
        """Asegura distancia mínima frente a otros autos ya spawneados."""
        for car in self.cars:
            if abs(car.rect.x - spawn_x) < self.min_spacing_between_cars:
                return False
        return True

    def _spawn_cars(self, camera_x: float, num_cars: int):
        """Spawn principal: configura 1 o 2 autos con separaciones y velocidades variadas."""
        base_x = camera_x + PANTALLA_ANCHO + random.randint(self.spawn_x_offset_min, self.spawn_x_offset_max)
        y = PISO_POS_Y - 86

        if num_cars == 1:
            self.cars.append(self._create_car(base_x, y, self._generate_car_speed()))
            return

        # num_cars == 2: uno rápido adelante y otro más lento más atrás
        fast_speed = random.randint(18, 22)
        slow_speed = random.randint(8, 12)
        gap = random.randint(300, 500)

        self.cars.append(self._create_car(base_x, y, speed=fast_speed))
        self.cars.append(self._create_car(base_x + gap, y, speed=slow_speed))

    def _reset_spawn_timer(self):
        self.spawn_timer = 0.0
        self.next_spawn_time = self._next_spawn_interval()


    # Actualizar y limpiar autos
    def _update_cars(self, delta_time: float):
        for car in self.cars:
            car.update(delta_time)

    def _cleanup_cars(self, camera_x: float):
        cleanup_threshold = camera_x - 600
        self.cars = [car for car in self.cars if car.rect.right > cleanup_threshold]

    def check_collisions(self, player_rect: pygame.Rect) -> bool:
        if not self.cars:
            return False

        # hitbox reducida del jugador para ser más justo
        player_hit = player_rect.inflate(*self.player_hitbox_shrink)

        # recorrido solo de autos cercanos (mejor que iterar todos)
        for car in self.cars:
            # filtro rápido por distancia X
            if abs(car.rect.x - player_rect.x) > 150:
                continue

            car_hit = car.rect.inflate(*self.car_hitbox_shrink)
            if car_hit.colliderect(player_hit):
                return True

        return False

    def get_cars(self) -> List[Car]:
        return self.cars