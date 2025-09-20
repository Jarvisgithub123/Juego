import pygame
import csv
import os
from datetime import datetime
from src.Constantes import *
from src.core.scene_manager import Scene
from src.entities.Player import Player
from src.UI.game_hud import GameHUD
from src.core.Camera import Camera
from src.systems.car_spawner import CarSpawner
from src.systems.Collectible_spawner import CollectibleSpawner
from src.systems.game_renderer import GameRenderer
from src.systems.ability_system import ability_system

class MissionGameScreen(Scene):
    """Pantalla de juego especifica para misiones con sistema de habilidades"""
    
    def __init__(self, screen: pygame.Surface, resource_manager, scene_manager):
        super().__init__(screen, resource_manager, scene_manager)
        
        self.scene_manager = scene_manager
        
        # Sistemas principales
        self.camera = Camera(PANTALLA_ANCHO, PANTALLA_ALTO)
        self.car_spawner = CarSpawner(resource_manager)
        self.collectible_spawner = CollectibleSpawner(resource_manager)
        self.renderer = GameRenderer(screen, resource_manager)
        self.hud = GameHUD(resource_manager)
        
        # Obtener datos de la mision
        self.mission_key = 'level_1'  # Default
        self.mission_data = {}
        selected_character = 'UIAbot'
        
        try:
            if (self.scene_manager and hasattr(self.scene_manager, 'game_manager') 
                and self.scene_manager.game_manager 
                and hasattr(self.scene_manager.game_manager, 'shared_data')):
                
                shared_data = self.scene_manager.game_manager.shared_data
                self.mission_key = shared_data.get('selected_level', 'level_1')
                self.mission_data = shared_data.get('level_data', {})
                selected_character = shared_data.get('selected_character', 'UIAbot')
                
                print(f"Iniciando mision: {self.mission_key}")
                print(f"Personaje: {selected_character}")
        except Exception as e:
            print(f"Error al obtener datos de mision: {e}")
        
        # Crear jugador
        self.player = Player(100, PISO_POS_Y - 60, GRAVEDAD, resource_manager, selected_character)
        
        # Configurar habilidades segun la mision
        self._setup_mission_abilities()
        
        # Sistema de energias por personaje (igual que game_screen)
        self.energias_individuales = {}
        self._inicializar_energias_personajes()
        
        # Sistema de tracking de distancias
        self.distancias_personajes = {}
        self._inicializar_distancias_personajes()
        self.distancia_total_partida = 0.0
        self.ultimo_personaje_activo = self.player.get_current_character()
        
        # Estado del juego
        self.pause = False
        self.game_over = False
        self.victory = False
        self.mission_completed = False
        self.new_abilities = []  # Habilidades recien desbloqueadas
        
        self.energy_remaining = self.energias_individuales[self.player.get_current_character()]
        self.shield_collision_just_happened = False
        
        # Objetivo de la mision (distancia variable segun mision)
        self.kilometers_remaining = ability_system.get_mission_distance(self.mission_key)
        self.time = 0.0
        
        print(f"Habilidades activas: {ability_system.get_unlocked_abilities()}")
        print(f"Distancia objetivo para {self.mission_key}: {self.kilometers_remaining} km")
    
    def _setup_mission_abilities(self):
        """Configura las habilidades disponibles para esta mision"""
        # No hacer nada aqui - el ability_system ya maneja que esta desbloqueado
        # Solo aplicar las mejoras de pilas y escudos al spawner si corresponde
        
        # Configurar spawner de coleccionables con habilidades mejoradas
        if hasattr(self.collectible_spawner, 'set_enhanced_battery_energy'):
            enhanced_energy = ability_system.get_enhanced_battery_energy()
            self.collectible_spawner.set_enhanced_battery_energy(enhanced_energy)
    
    def _inicializar_energias_personajes(self):
        """Inicializa las energias individuales de cada personaje"""
        for personaje in self.player.personajes:
            autonomia = self.player.stats[personaje]["autonomia"]
            self.energias_individuales[personaje] = float(autonomia)
    
    def _inicializar_distancias_personajes(self):
        """Inicializa el tracking de distancia para cada personaje"""
        for personaje in self.player.personajes:
            self.distancias_personajes[personaje] = 0.0
    
    def handle_event(self, event: pygame.event.Event):
        """Maneja los eventos de entrada del usuario"""
        if self.mission_completed:
            self._handle_completion_events(event)
        elif not self.game_over and not self.victory:
            self._handle_gameplay_events(event)
        else:
            self._handle_endgame_events(event)
    
    def _handle_completion_events(self, event: pygame.event.Event):
        """Maneja eventos cuando la mision esta completada"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Volver a la pantalla de seleccion de misiones
                from src.screens.level_select_screen import LevelSelectScreen
                self.scene_manager.change_scene(LevelSelectScreen)
            elif event.key == pygame.K_ESCAPE:
                self._return_to_menu()
    
    def _handle_gameplay_events(self, event: pygame.event.Event):
        """Maneja eventos durante el juego activo"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.pause:
                # El manejo del doble salto ahora esta en el Player._handle_jump_input
                # que se llama automaticamente en player.update()
                pass  # El salto se maneja en update() del player
            elif event.key == pygame.K_z and not self.pause:
                # Solo permitir dash si esta desbloqueado
                if ability_system.can_dash():
                    self.player.dash(self._consume_energy)
                else:
                    print("Dash no disponible - completa mas misiones para desbloquearlo")
            elif event.key == pygame.K_p:
                self.pause = not self.pause
            elif self.pause:
                if event.key == pygame.K_ESCAPE:
                    self._return_to_menu()
    
    def _handle_endgame_events(self, event: pygame.event.Event):
        """Maneja eventos en pantallas de fin de juego"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._restart_mission()
            elif event.key == pygame.K_ESCAPE:
                self._return_to_menu()
    
    def handle_character_change(self):
        """Maneja el cambio de personaje"""
        personaje_actual = self.player.get_current_character()
        self.energy_remaining = self.energias_individuales[personaje_actual]
        self.ultimo_personaje_activo = personaje_actual
    
    def update(self, delta_time: float):
        """Actualiza toda la logica del juego"""
        if self.pause or self.mission_completed:
            return
        
        if not self.game_over and not self.victory:
            self._update_game_systems(delta_time)
            self._update_entities(delta_time)
            self._check_game_conditions()
            self._update_distance_tracking(delta_time)
    
    def _update_distance_tracking(self, delta_time: float):
        """Actualiza el tracking de distancia del personaje actual"""
        personaje_actual = self.player.get_current_character()
        
        if not self.player.is_dashing:
            distancia_frame = delta_time * DECREMENTO_KM_POR_SEGUNDO
        else:
            distancia_frame = delta_time * DECREMENTO_KM_POR_SEGUNDO * 2
        
        self.distancias_personajes[personaje_actual] += distancia_frame
        self.distancia_total_partida += distancia_frame
    
    def _update_game_systems(self, delta_time: float):
        """Actualiza sistemas del juego"""
        self._update_time_and_distance(delta_time)
        self._update_camera(delta_time)
        self.renderer.update(delta_time)
    
    def _update_camera(self, delta_time: float):
        """Actualiza la camara"""
        self.camera.update(delta_time, self.player.rect)
    
    def _update_entities(self, delta_time: float):
        """Actualiza entidades del juego"""
        keys = pygame.key.get_pressed()
        
        personaje_antes = self.player.get_current_character()
        self.energias_individuales[personaje_antes] = self.energy_remaining
        
        self.player.update(delta_time, keys)
        
        personaje_despues = self.player.get_current_character()
        if personaje_antes != personaje_despues:
            self.handle_character_change()
        
        self.car_spawner.update(delta_time, self.camera.x, self.player.rect.x)
        
        # Callback para coleccionables con energia mejorada
        def collectible_callback(amount):
            enhanced_amount = ability_system.get_enhanced_battery_energy()
            self.agregar_energia(enhanced_amount)
        
        collectible_callback.__self__ = self.player
        
        self.collectible_spawner.update(
            delta_time, self.camera.x, self.player.rect.x, 
            self.player.rect, collectible_callback
        )
    
    def agregar_energia(self, cantidad):
        """Agrega energia al robot sin pasar su maximo"""
        personaje_actual = self.player.get_current_character()
        autonomia_maxima_actual = self.player.obtener_autonomia_maxima()
        self.energy_remaining = min(self.energy_remaining + cantidad, autonomia_maxima_actual)
        self.energias_individuales[personaje_actual] = self.energy_remaining
    
    def _check_game_conditions(self):
        """Verifica condiciones de fin de juego con sistema de escudo mejorado"""
        # Limpiar flag de colision protegida
        if self.shield_collision_just_happened and not self.player.should_show_collision_effect():
            self.shield_collision_just_happened = False
        
        if self.shield_collision_just_happened:
            pass
        else:
            if self.car_spawner.check_collisions(self.player.rect):
                if self.player.is_protected() or self.player.should_show_collision_effect():
                    self.player.activate_shield_collision_effect()
                    self.shield_collision_just_happened = True
                    
                    # Aplicar duracion mejorada del escudo
                    enhanced_duration = ability_system.get_enhanced_shield_duration()
                    if self.player.has_shield:
                        self.player.shield_time = enhanced_duration
                        self.player.max_shield_time = enhanced_duration
                    
                    try:
                        self.player.rect.x += 60
                    except Exception:
                        pass
                    
                    print("¡Escudo protegio de la colision!")
                    return
                else:
                    self._trigger_game_over()
                    return
        
        # Verificar condiciones de fin
        if self.energy_remaining <= 0:
            self._trigger_game_over()
        elif self.kilometers_remaining <= 0:
            self._trigger_mission_victory()
    
    def _trigger_game_over(self):
        """Activa el estado de game over"""
        self.game_over = True
        self.resource_manager.play_sound("game_over")
        self.resource_manager.stop_music()
    
    def _trigger_mission_victory(self):
        """Activa el estado de victoria de la mision"""
        self.victory = True
        self.mission_completed = True
        
        # Completar la mision y desbloquear habilidades
        self.new_abilities = ability_system.complete_mission(self.mission_key)
        
        self.resource_manager.play_sound("victoria")
        self.resource_manager.stop_music()
        
        print(f"¡Mision {self.mission_key} completada!")
        if self.new_abilities:
            print(f"Nuevas habilidades desbloqueadas: {self.new_abilities}")
    
    def _update_time_and_distance(self, delta_time: float):
        """Actualiza tiempo de energia y distancia recorrida"""
        if not self.player.is_dashing:
            self.energy_remaining -= delta_time
            self.energia_minima()
        
        if not self.player.is_dashing:
            self.time += delta_time
        if self.player.is_dashing:
            self.time += delta_time + DECREMENTO_KM_POR_SEGUNDO
        
        km_traveled = self.time * DECREMENTO_KM_POR_SEGUNDO
        mission_distance = ability_system.get_mission_distance(self.mission_key)
        self.kilometers_remaining = max(0, mission_distance - km_traveled)
    
    def _consume_energy(self, energy_amount: float) -> bool:
        """Consume energia si hay suficiente disponible"""
        if self.energy_remaining >= energy_amount:
            self.energy_remaining -= energy_amount
            self.energia_minima()
            return True
        return False
    
    def energia_minima(self):
        """Mantiene la energia en valores validos"""
        self.energy_remaining = max(0, self.energy_remaining)
        personaje_actual = self.player.get_current_character()
        self.energias_individuales[personaje_actual] = self.energy_remaining
    
    def on_enter(self):
        """Se ejecuta al entrar en la pantalla"""
        self.resource_manager.play_music("game_music", volume=0.6)
    
    def on_exit(self):
        """Se ejecuta al salir de la pantalla"""
        pygame.mixer.stop()
    
    def _restart_mission(self):
        """Reinicia la mision actual"""
        pygame.mixer.stop()
        from src.screens.game_screen_mission import MissionGameScreen
        self.scene_manager.change_scene(MissionGameScreen)
    
    def _return_to_menu(self):
        """Regresa al menu principal"""
        pygame.mixer.stop()
        from src.screens.menu_screen import MenuScreen
        self.scene_manager.change_scene(MenuScreen)
    
    def _draw_mission_completion_screen(self):
        """Dibuja la pantalla de mision completada con habilidades desbloqueadas"""
        # Overlay semi-transparente
        overlay = pygame.Surface((PANTALLA_ANCHO, PANTALLA_ALTO))
        overlay.set_alpha(180)
        overlay.fill((0, 50, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Titulo de mision completada
        font_titulo = self.resource_manager.get_font('titulo')
        if font_titulo:
            title_text = font_titulo.render("¡MISION COMPLETADA!", True, COLOR_AMARILLO)
            title_rect = title_text.get_rect(center=(PANTALLA_ANCHO // 2, 150))
            self.screen.blit(title_text, title_rect)
        
        # Mostrar habilidades desbloqueadas
        y_offset = 250
        font_habilidad = self.resource_manager.get_font('subtitulo')
        font_desc = self.resource_manager.get_font('pequeña')
        
        if self.new_abilities:
            if font_habilidad:
                unlock_text = font_habilidad.render("¡NUEVAS HABILIDADES!", True, COLOR_VERDE)
                unlock_rect = unlock_text.get_rect(center=(PANTALLA_ANCHO // 2, y_offset))
                self.screen.blit(unlock_text, unlock_rect)
                y_offset += 60
            
            for ability_name in self.new_abilities:
                ability_info = ability_system.get_ability_info(ability_name)
                
                # Nombre de la habilidad
                if font_habilidad:
                    name_text = font_habilidad.render(ability_info.get("name", ability_name), True, COLOR_AMARILLO)
                    name_rect = name_text.get_rect(center=(PANTALLA_ANCHO // 2, y_offset))
                    self.screen.blit(name_text, name_rect)
                    y_offset += 40
                
                # Descripcion
                if font_desc:
                    desc_text = font_desc.render(ability_info.get("description", ""), True, COLOR_BLANCO)
                    desc_rect = desc_text.get_rect(center=(PANTALLA_ANCHO // 2, y_offset))
                    self.screen.blit(desc_text, desc_rect)
                    y_offset += 50
        
        # Instrucciones
        if font_desc:
            instr_text = font_desc.render("Presiona ENTER para continuar", True, COLOR_BLANCO)
            instr_rect = instr_text.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO - 100))
            self.screen.blit(instr_text, instr_rect)
    
    def draw(self):
        """Dibuja todos los elementos visuales"""
        self.renderer.draw_background(self.camera.x)
        self.renderer.draw_floor()
        self.renderer.draw_player(self.player, self.camera.x)
        self.renderer.draw_cars(self.car_spawner.get_cars(), self.camera.x)
        self.renderer.draw_collectibles(self.collectible_spawner.get_collectibles(), self.camera.x)
        
        # Dibujar UI
        if not self.game_over and not self.victory and not self.mission_completed:
            autonomia_maxima_actual = self.player.obtener_autonomia_maxima()
            enhanced_shield_time = ability_system.get_enhanced_shield_duration() if self.player.has_shield else self.player.get_shield_time_remaining()
            
            self.hud.draw(self.screen, self.energy_remaining, 
                         autonomia_maxima_actual, self.kilometers_remaining,
                         self.distancias_personajes, 'mission',
                         enhanced_shield_time)
        
        # Pantalla de mision completada
        if self.mission_completed:
            self._draw_mission_completion_screen()
        elif self.game_over:
            self.renderer.draw_game_over_screen()
        elif self.victory:
            self.renderer.draw_victory_screen()
        
        # Pausa
        if self.pause and not self.game_over and not self.victory and not self.mission_completed:
            overlay = pygame.Surface((PANTALLA_ANCHO, PANTALLA_ALTO))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            font = pygame.font.SysFont(None, 60)
            text = font.render("Mision Pausada", True, (255, 255, 255))
            rect = text.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2))
            self.screen.blit(text, rect)