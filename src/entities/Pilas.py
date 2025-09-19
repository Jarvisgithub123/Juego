import pygame
from typing import List, Optional
from src.Constantes import *
from src.entities.Collectible import Collectible

class pilas(Collectible):
    """Clase de pilas que hereda de Collectible"""
    
    def __init__(self, resource_manager, *groups, width: int = DEFAULT_PILAS_WIDTH, height: int = DEFAULT_PILAS_HEIGHT):
        super().__init__(resource_manager, "pila", *groups, width, height)
        
        # Configuracion especifica de las pilas
        self.energy_amount = ENERGIA_PILA
        self.effect_duration = 0.0  # Las pilas dan energia instantanea
    
    def _apply_effect(self, robot):
        """Aplica el efecto especifico de la pila - aumenta energia"""
        energia_anterior = robot.energia if hasattr(robot, 'energia') else 0
        
        # Aumentar la energia del robot sin exceder su maximo
        if hasattr(robot, 'energia_maxima'):
            nueva_energia = min(robot.energia + self.energy_amount, robot.energia_maxima)
            robot.energia = nueva_energia
            print(f"Energia del robot: {energia_anterior} -> {nueva_energia}")
        
        print(f"¡Pila recolectada! +{self.energy_amount} segundos de energia")
    
    def _play_collection_sound(self):
        """Reproduce el sonido de recoleccion de pila"""
        # Aqui puedes agregar un sonido especifico para las pilas
        # self.resource_manager.play_sound("collect_battery")
        pass
    
    def get_effect_info(self) -> str:
        """Retorna informacion sobre el efecto de la pila"""
        return f"Restaura {self.energy_amount} puntos de energia"