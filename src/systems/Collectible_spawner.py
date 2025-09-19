import pygame
import random
from typing import List
from src.Constantes import *
from src.entities.Pilas import pilas
from src.entities.Escudo import Escudo

class CollectibleSpawner:
    """Spawner unificado para objetos coleccionables (pilas y escudos)"""
    
    def __init__(self, resource_manager):
        self.resource_manager = resource_manager
        self.spawn_timer = 0.0
        self.collectibles: List = []
        self.next_spawn_time = 5.0  # Generar un objeto cada 5 segundos
        print("CollectibleSpawner inicializado")
    
    def update(self, dt: float, camera_x: float, player_x: float, player_rect: pygame.Rect, energy_callback=None):
        """Actualiza el spawner y genera nuevos objetos coleccionables cada 5 segundos
        
        Args:
            dt: Delta time
            camera_x: Posicion X de la camara
            player_x: Posicion X del jugador
            player_rect: Rectangulo del jugador para verificar colisiones
            energy_callback: Funcion callback para manejar la energia
        """
        self.spawn_timer += dt
        
        # Actualizar objetos coleccionables
        for collectible in self.collectibles:
            collectible.update()
        
        # Generar objetos cada 5 segundos
        if self.spawn_timer >= self.next_spawn_time:
            self._spawn_random_collectible(camera_x)
            self.spawn_timer = 0
            self.next_spawn_time = 5.0  # Exactamente cada 5 segundos
            
        # Limpiar objetos que salieron de pantalla o fueron recolectados
        self._cleanup_collectibles(camera_x)
        
        # Verificar colisiones
        self.check_collisions(player_rect, energy_callback)
    
    def _spawn_random_collectible(self, camera_x: float):
        """Genera aleatoriamente una pila o un escudo"""
        spawn_x = camera_x + PANTALLA_ANCHO + 100  # Siempre fuera de pantalla a la derecha
        spawn_y = random.randint(PISO_POS_Y - 400, PISO_POS_Y - 100)  # Diferentes alturas
        
        # Decidir qué tipo de objeto generar
        if random.random() < ESCUDO_SPAWN_CHANCE:
            # Generar escudo
            new_collectible = Escudo(self.resource_manager)
            collectible_type = "escudo"
        else:
            # Generar pila
            new_collectible = pilas(self.resource_manager)
            collectible_type = "pila"
        
        new_collectible.rect.x = spawn_x
        new_collectible.rect.y = spawn_y
        
        self.collectibles.append(new_collectible)
        print(f"Nuevo {collectible_type} spawneado en ({spawn_x}, {spawn_y})")
    
    def _cleanup_collectibles(self, camera_x: float):
        """Limpia objetos que salieron de pantalla o fueron recolectados"""
        active_collectibles = []
        for collectible in self.collectibles:
            # Verificar si el objeto sigue en pantalla y no ha sido recolectado
            if not collectible.collected and collectible.rect.right > camera_x - 200:
                active_collectibles.append(collectible)
            else:
                collectible_type = "escudo" if isinstance(collectible, Escudo) else "pila"
                print(f"{collectible_type} eliminado: collected={collectible.collected}, pos={collectible.rect.x}")
        
        self.collectibles = active_collectibles
    
    def check_collisions(self, player_rect: pygame.Rect, energy_callback):
        """Verifica colisiones entre el jugador y los objetos coleccionables
        
        Args:
            player_rect: Rectangulo del jugador
            energy_callback: Callback para efectos en el jugador
        """
        for collectible in self.collectibles:
            if not collectible.collected and player_rect.colliderect(collectible.rect):
                # Aplicar efecto específico según el tipo de objeto
                if isinstance(collectible, Escudo):
                    # Para escudos, necesitamos acceder al player directamente
                    # El energy_callback debería ser una referencia al método que maneja escudos
                    if hasattr(energy_callback, '__self__'):  # Si es un método bound
                        player = energy_callback.__self__
                        if hasattr(player, 'has_shield'):
                            player.has_shield = True
                            player.shield_time = ESCUDO_DURACION
                            print(f"¡Escudo recolectado! Protección por {ESCUDO_DURACION} segundos")
                elif isinstance(collectible, pilas):
                    # Para pilas, usar el callback de energía normal
                    if energy_callback:
                        energy_callback(ENERGIA_PILA)
                
                # Marcar como recolectado
                collectible.collect(None)
                
                collectible_type = "escudo" if isinstance(collectible, Escudo) else "pila"
                print(f"¡{collectible_type} recolectado en posicion ({collectible.rect.x}, {collectible.rect.y})!")
                break
    
    def get_collectibles(self) -> List:
        """Devuelve la lista de objetos coleccionables activos"""
        return [collectible for collectible in self.collectibles if not collectible.collected]
    
    def get_pilas(self) -> List[pilas]:
        """Devuelve solo las pilas activas (compatibilidad con código existente)"""
        return [collectible for collectible in self.collectibles 
                if isinstance(collectible, pilas) and not collectible.collected]
    
    def get_escudos(self) -> List[Escudo]:
        """Devuelve solo los escudos activos"""
        return [collectible for collectible in self.collectibles 
                if isinstance(collectible, Escudo) and not collectible.collected]