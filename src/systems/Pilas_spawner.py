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
        self.next_spawn_time = 5.0  # Generar una pila cada 5 segundos
        print("PilaSpawner inicializado")
    
    def update(self, dt: float, camera_x: float, player_x: float, player_rect: pygame.Rect,energy_callback=None):
        """Actualiza el spawner y genera nuevas pilas cada 5 segundos
        
        Args:
            dt: Delta time
            camera_x: Posicion X de la camara
            player_x: Posicion X del jugador
            energy_callback: Funcion callback para manejar la energia
        """
        self.spawn_timer += dt
        
        # Actualizar pilas
        for pila in self.pilas:
            pila.update()
        
        # Generar pilas cada 5 segundos
        if self.spawn_timer >= self.next_spawn_time:
            
            # Difentes alturas para las pilas
            spawn_x = camera_x + PANTALLA_ANCHO + 100 # Siempre fuera de pantalla a la derecha
            spawn_y = random.randint(PISO_POS_Y - 400, PISO_POS_Y - 100)  # Se genera en diferentes alturas aleatoriamente
            
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
        
        self.check_collisions(player_rect, energy_callback)
    
    
    def check_collisions(self, player_rect: pygame.Rect, energy_callback) -> pilas:
        """Verifica colisiones entre el jugador y las pilas
        
        Args:
            player_rect: Rectangulo del jugador
            
        Returns:
            La pila recolectada o None
        """
        for pila in self.pilas:
            if not pila.collected and player_rect.colliderect(pila.rect):
                
                if energy_callback:
                    energy_callback(ENERGIA_PILA)
                
                pila.collect(None)
                
                print(f"¡Pila recolectada en posicion ({pila.rect.x}, {pila.rect.y})!")
                break
                
    
    
    def get_pilas(self) -> List[pilas]:
        """Devuelve la lista de pilas activas"""
        return [pila for pila in self.pilas if not pila.collected]
