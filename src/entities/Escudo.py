import pygame
from typing import List, Optional
from src.Constantes import *
from src.entities.Collectible import Collectible

class Escudo(Collectible):
    """Clase de escudo que hereda de Collectible - proporciona protección temporal"""
    
    def __init__(self, resource_manager, *groups, width: int = DEFAULT_PILAS_WIDTH, height: int = DEFAULT_PILAS_HEIGHT):
        super().__init__(resource_manager, "escudo", *groups, width, height)
        
        # Configuración específica del escudo
        self.protection_duration = ESCUDO_DURACION  # Duración de la protección en segundos
        self.effect_duration = self.protection_duration
    
    def _apply_effect(self, robot):
        """Aplica el efecto específico del escudo - otorga protección temporal"""
        if hasattr(robot, 'shield_time'):
            robot.shield_time = self.protection_duration
            robot.has_shield = True
            print(f"¡Escudo activado! Protección por {self.protection_duration} segundos")
        else:
            print("Robot no compatible con sistema de escudo")
    
    def _play_collection_sound(self):
        """Reproduce el sonido de recolección de escudo"""
        # Reproducir sonido específico para escudos
        if hasattr(self.resource_manager, 'play_sound'):
            self.resource_manager.play_sound("collect_shield")
    
    def get_effect_info(self) -> str:
        """Retorna información sobre el efecto del escudo"""
        return f"Protección durante {self.protection_duration} segundos contra colisiones"
    
    def create_shield_visual_effect(self, screen, player_rect, camera_x):
        """Crea efecto visual del escudo alrededor del jugador"""
        # Posición en pantalla
        screen_x = player_rect.x - camera_x + player_rect.width // 2
        screen_y = player_rect.y + player_rect.height // 2
        
        # Crear un efecto de anillo pulsante
        current_time = pygame.time.get_ticks()
        pulse = abs(pygame.math.Vector2(0, 1).rotate(current_time * 0.3).y)
        
        # Radius que pulsa
        base_radius = 50
        radius = int(base_radius + pulse * 15)
        
        # Color del escudo con transparencia
        shield_color = (0, 150, 255, 100)  # Azul con transparencia
        
        # Crear surface temporal para el efecto con transparencia
        shield_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(shield_surface, shield_color, (radius, radius), radius, 3)
        
        # Dibujar en la pantalla
        shield_rect = shield_surface.get_rect(center=(screen_x, screen_y))
        screen.blit(shield_surface, shield_rect)
        
        # Añadir partículas brillantes alrededor del escudo
        for i in range(8):
            angle = (current_time * 0.05 + i * 45) % 360
            particle_x = screen_x + pygame.math.Vector2(radius - 10, 0).rotate(angle).x
            particle_y = screen_y + pygame.math.Vector2(0, radius - 10).rotate(angle).y
            
            # Dibujar pequeñas partículas brillantes
            particle_size = 3
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(particle_x), int(particle_y)), particle_size)
    
    @staticmethod
    def create_collision_visual_effect(screen, player_rect, camera_x):
        """Crea efecto visual cuando el escudo absorbe una colisión"""
        # Posición en pantalla
        screen_x = player_rect.x - camera_x + player_rect.width // 2
        screen_y = player_rect.y + player_rect.height // 2
        
        # Efecto de explosión/impacto
        current_time = pygame.time.get_ticks()
        
        # Múltiples anillos expansivos
        for ring in range(3):
            radius = 30 + ring * 20 + (current_time % 500) // 10
            alpha = max(0, 255 - (current_time % 500) // 2)
            
            if alpha > 0:
                # Color de impacto (amarillo/naranja)
                impact_color = (255, 200 - ring * 30, 0, alpha)
                
                # Crear surface para el anillo
                ring_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(ring_surface, impact_color, (radius, radius), radius, 4)
                
                # Dibujar en pantalla
                ring_rect = ring_surface.get_rect(center=(screen_x, screen_y))
                screen.blit(ring_surface, ring_rect)