import pygame
from typing import Optional, Type

class Scene:
    """Clase base para todas las escenas del juego"""
    
    def __init__(self, screen: pygame.Surface, resource_manager, scene_manager):
        self.screen = screen
        self.resource_manager = resource_manager
        self.scene_manager = scene_manager  
    
    def on_enter(self):
        """Se llama cuando se entra a la escena"""
        pass
    
    def on_exit(self):
        """Se llama cuando se sale de la escena"""
        pass
    
    def handle_event(self, event: pygame.event.Event):
        """Maneja los eventos de la escena"""
        pass
    
    def update(self, dt: float):
        """Actualiza la logica de la escena"""
        pass
    
    def draw(self):
        """Dibuja la escena"""
        pass

class SceneManager:
    """Gestor de escenas del juego"""
    
    def __init__(self, screen: pygame.Surface, resource_manager):
        self.screen = screen
        self.resource_manager = resource_manager
        self.current_scene: Optional[Scene] = None
        self.next_scene: Optional[Type[Scene]] = None
        self.next_scene_args = None
    
    def change_scene(self, scene_class: Type[Scene], *args, **kwargs):
        """Cambia a una nueva escena"""
        self.next_scene = scene_class
        self.next_scene_args = (args, kwargs)
    
    def _perform_scene_change(self):
        """Realiza el cambio de escena pendiente"""
        if self.next_scene:
            # Salir de la escena actual
            if self.current_scene:
                self.current_scene.on_exit()
            
            # Crear la nueva escena
            args, kwargs = self.next_scene_args if self.next_scene_args else ((), {})
            self.current_scene = self.next_scene(self.screen, self.resource_manager, self, *args, **kwargs)
            self.current_scene.scene_manager = self
            
            # Pasar referencia al game_manager si existe
            if hasattr(self, 'game_manager'):
                self.current_scene.game_manager = self.game_manager
                
            self.current_scene.on_enter()
            
            # Limpiar el cambio pendiente
            self.next_scene = None
            self.next_scene_args = None
    
    def handle_event(self, event: pygame.event.Event):
        """Maneja los eventos de la escena actual"""
        if self.current_scene:
            self.current_scene.handle_event(event)
    
    def update(self, dt: float):
        """Actualiza la escena actual"""
        # Realizar cambio de escena si es necesario
        if self.next_scene:
            self._perform_scene_change()
        
        # Actualizar la escena actual
        if self.current_scene:
            self.current_scene.update(dt)
    
    def draw(self):
        """Dibuja la escena actual"""
        if self.current_scene:
            self.current_scene.draw()
