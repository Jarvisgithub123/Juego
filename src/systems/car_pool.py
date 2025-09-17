import pygame
from typing import List, Optional
from src.entities.Car import Car

class CarPool:
    """Pool de objetos Car para evitar creacion/destruccion constante"""
    def __init__(self, resource_manager, initial_size: int = 8):
        self.resource_manager = resource_manager
        self.available_cars: List[Car] = []
        self.active_cars: List[Car] = []
        self.max_pool_size = 15  # Límite maximo del pool
        
        # Pre-crear algunos autos
        for _ in range(initial_size):
            car = Car(0, 0, resource_manager)
            car.active = False
            self.available_cars.append(car)
    
    def get_car(self, x: float, y: float, speed: int) -> Car:
        """Obtiene un auto del pool o crea uno nuevo si es necesario"""
        if self.available_cars:
            car = self.available_cars.pop()
            car.reset_for_reuse(x, y, speed)
            car.active = True
            self.active_cars.append(car)
            return car
        else:
            # Solo crear nuevo si no excedemos el límite del pool
            if len(self.active_cars) < self.max_pool_size:
                car = Car(x, y, self.resource_manager, speed)
                car.active = True
                self.active_cars.append(car)
                return car
            else:
                # En caso extremo, reutilizar el auto mas viejo
                oldest_car = self.active_cars[0]
                oldest_car.reset_for_reuse(x, y, speed)
                return oldest_car
    
    def return_car(self, car: Car):
        """Devuelve un auto al pool para reutilizacion"""
        if car in self.active_cars:
            self.active_cars.remove(car)
            car.active = False
            # Solo mantener un número razonable en el pool disponible
            if len(self.available_cars) < 6:
                self.available_cars.append(car)
    
    def update_active_cars(self, delta_time: float):
        """Actualiza solo los autos activos"""
        for car in self.active_cars:
            car.update(delta_time)
    
    def cleanup_cars(self, camera_x: float):
        """Limpia autos que salieron de pantalla y los devuelve al pool"""
        cleanup_threshold = camera_x - 600
        cars_to_return = []
        
        for car in self.active_cars[:]:  # Copia shallow para iterar seguro
            if car.rect.right <= cleanup_threshold:
                cars_to_return.append(car)
        
        for car in cars_to_return:
            self.return_car(car)
    
    def get_active_cars(self) -> List[Car]:
        """Retorna lista de autos activos"""
        return self.active_cars
    
    def get_pool_stats(self) -> dict:
        """Retorna estadísticas del pool para debugging"""
        return {
            "active": len(self.active_cars),
            "available": len(self.available_cars),
            "total_pool_size": len(self.active_cars) + len(self.available_cars)
        }