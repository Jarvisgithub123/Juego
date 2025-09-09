import pygame
import random
from typing import List
from src.Constantes import *
from src.entities.Pilas import pilas

class pilaSpawner:
    
    def __init__(self, resource_manager):
        self.resource_manager = resource_manager
        self.spawn_timer = 0.0
        self.pilas: List[pilas] = []
        self.next_spawn_time = 5.0  # Empezar con 5 segundos como solicita el usuario
        print("PilaSpawner inicializado")
    
    def update(self, dt: float, camera_x: float, player_x: float, energy_callback=None):
        """Actualiza el spawner y genera nuevas pilas cada 5 segundos
        
        Args:
            dt: Delta time
            camera_x: Posición X de la cámara
            player_x: Posición X del jugador
            energy_callback: Función callback para manejar la energía
        """
        self.spawn_timer += dt
        
        # Actualizar pilas existentes
        for pila in self.pilas:
            pila.update()
        
        # Generar nueva pila cuando sea tiempo
        if self.spawn_timer >= self.next_spawn_time:
            # Calcular posición inicial para la nueva pila
            spawn_x = camera_x + PANTALLA_ANCHO + 100  # Usar camera_x en lugar de player_x
            spawn_y = random.randint(PISO_POS_Y - 300, PISO_POS_Y - 100)  # Altura aleatoria
            
            new_pila = pilas(self.resource_manager)
            new_pila.rect.x = spawn_x
            new_pila.rect.y = spawn_y
            
            self.pilas.append(new_pila)
            print(f"Nueva pila spawneada en ({spawn_x}, {spawn_y})")
            
            self.spawn_timer = 0
            self.next_spawn_time = 5.0  # Exactamente cada 5 segundos
            
        pilas_activas = []
        for pila in self.pilas:
            # Verificar si la pila sigue en pantalla y no ha sido recolectada
            if not pila.collected and pila.rect.right > camera_x - 200:
                pilas_activas.append(pila)
            else:
                print(f"Pila eliminada: collected={pila.collected}, pos={pila.rect.x}")
        
        self.pilas = pilas_activas
    
    def check_collisions(self, player_rect: pygame.Rect) -> pilas:
        """Verifica colisiones entre el jugador y las pilas
        
        Args:
            player_rect: Rectángulo del jugador
            
        Returns:
            La pila recolectada o None
        """
        for pila in self.pilas:
            if not pila.collected and player_rect.colliderect(pila.rect):
                print(f"¡Pila recolectada en posición ({pila.rect.x}, {pila.rect.y})!")
                return pila
        return None
    
    def get_pilas(self) -> List[pilas]:
        """Devuelve la lista de pilas activas"""
        return [pila for pila in self.pilas if not pila.collected]
