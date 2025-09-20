import pygame
from src.Constantes import *
from src.core.scene_manager import Scene
from src.entities.Player import Player
from src.UI.game_hud import GameHUD
from src.core.Camera import Camera
from src.systems.car_spawner import CarSpawner
from src.systems.Collectible_spawner import CollectibleSpawner
from src.systems.game_renderer import GameRenderer
from src.systems.avion_spawn import PlaneSpawner
import csv
import os
from datetime import datetime

class GameScreen(Scene):
    """Pantalla principal del juego donde UAIBOT corre, esquiva autos y usa escudos"""
    
    def __init__(self, screen: pygame.Surface, resource_manager, scene_manager):
        super().__init__(screen, resource_manager, scene_manager)
        
        self.scene_manager = scene_manager
        
        # Sistemas principales
        self.camera = Camera(PANTALLA_ANCHO, PANTALLA_ALTO)
        self.car_spawner = CarSpawner(resource_manager)
        #Reemplazar pila_spawner con collectible_spawner
        self.collectible_spawner = CollectibleSpawner(resource_manager)
        self.renderer = GameRenderer(screen, resource_manager)
        self.plane_spawner = PlaneSpawner(resource_manager)
        self.hud = GameHUD(resource_manager)
        
        selected_character = 'UIAbot'  # pj por defecto
        # Obtener personaje seleccionado desde shared_data de forma robusta
        try:
            gm = getattr(self.scene_manager, 'game_manager', None)
            if gm is not None:
                shared = getattr(gm, 'shared_data', None) or {}
                selected_character = shared.get('selected_character', 'UIAbot')
                print(f"Personaje seleccionado : {selected_character}")
            else:
                print("Warning: No se pudo acceder a game_manager")
        except Exception as e:
            print(f"Error al acceder a shared_data: {e}")
            print("Usando personaje por defecto")
        
        self.game_mode = 'normal'  # Por defecto
        try:
            gm = getattr(self.scene_manager, 'game_manager', None)
            if gm is not None:
                shared = getattr(gm, 'shared_data', None) or {}
                self.game_mode = shared.get('game_mode', 'normal')
                print(f"Modo de juego: {self.game_mode}")
        except Exception as e:
            print(f"Error al obtener modo de juego: {e}")
            print("Usando modo normal por defecto")
        
        self.time = 0.0
        # Crear el player con el personaje correcto
        self.player = Player(100, PISO_POS_Y - 60, GRAVEDAD, resource_manager, selected_character)

        self.energias_individuales = {}
        self._inicializar_energias_personajes()
        
        # Sistema de tracking de distancias por personaje
        self.distancias_personajes = {}
        self._inicializar_distancias_personajes()
        self.distancia_total_partida = 0.0
        self.ultimo_personaje_activo = self.player.get_current_character()
        
        # Estado del juego
        self.pause = False
        self.game_over = False
        self.victory = False
        self.energy_remaining = self.energias_individuales[self.player.get_current_character()]
        
        #Variable para evitar game over mientras el escudo esta activo
        self.shield_collision_just_happened = False
    
        if self.game_mode == 'infinite':
            self.kilometers_remaining = float('inf')
            print("Modo infinito")
        else:
            self.kilometers_remaining = KILOMETROS_OBJETIVO
            print(f"Modo normal {KILOMETROS_OBJETIVO} km")
    
    def _inicializar_distancias_personajes(self):
        """Inicializa el tracking de distancia para cada personaje"""
        for personaje in self.player.personajes:
            self.distancias_personajes[personaje] = 0.0
        print("Distancias de personajes inicializadas:", self.distancias_personajes)
    
    def _inicializar_energias_personajes(self):
        """Inicializa las energias individuales de cada personaje con su autonomia maxima"""
        for personaje in self.player.personajes:
            autonomia = self.player.stats[personaje]["autonomia"]
            self.energias_individuales[personaje] = float(autonomia)
            print(f"Energia inicial {personaje}: {autonomia}")
    
    def handle_event(self, event: pygame.event.Event):
        """Maneja los eventos de entrada del usuario"""
        if not self.game_over and not self.victory:
            self._handle_gameplay_events(event)
        else:
            self._handle_endgame_events(event)
    
    def _handle_gameplay_events(self, event: pygame.event.Event):
        """Maneja eventos durante el juego activo"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not self.pause:
                self.player.jump()
            elif event.key == pygame.K_z and not self.pause:
                self.player.dash(self._consume_energy)
            elif event.key == pygame.K_p: 
                self.pause = not self.pause 
            elif self.pause: 
                if event.key == pygame.K_ESCAPE:
                    self._return_to_menu()
    
    def _handle_endgame_events(self, event: pygame.event.Event):
        """Maneja eventos en pantallas de fin de juego"""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_r]:
                self._restart_game()
            elif event.key == pygame.K_ESCAPE:
                self._return_to_menu()
    
    def handle_character_change(self):
        personaje_actual = self.player.get_current_character()
        self.energy_remaining = self.energias_individuales[personaje_actual] 
        self.player.obtener_autonomia_maxima()
        
        print(f"Cambio a {personaje_actual}")
        print(f"Energia {personaje_actual}: {self.energy_remaining}")
        
        # Actualizar el ultimo personaje activo para el tracking
        self.ultimo_personaje_activo = personaje_actual
    
    def update(self, delta_time: float):
        """Para que no se reinicie al entrar en pausa"""
        if self.pause:
            return
        """Actualiza toda la logica del juego"""
        if not self.game_over and not self.victory:
            self._update_game_systems(delta_time)
            self._update_entities(delta_time)
            self._check_game_conditions()
            self.plane_spawner.update(delta_time, self.camera.x)

            
            # Actualizar tracking de distancias
            self._update_distance_tracking(delta_time)
       
    def _update_distance_tracking(self, delta_time: float):
        """Actualiza el tracking de distancia del personaje actual"""
        personaje_actual = self.player.get_current_character()
        
        # Calcular distancia recorrida en este frame
        if not self.player.is_dashing:
            distancia_frame = delta_time * DECREMENTO_KM_POR_SEGUNDO
        else:
            # Durante el dash se avanza mas rapido
            distancia_frame = delta_time * DECREMENTO_KM_POR_SEGUNDO * 2
        
        # Agregar distancia al personaje actual
        self.distancias_personajes[personaje_actual] += distancia_frame
        self.distancia_total_partida += distancia_frame
            
    def _update_game_systems(self, delta_time: float):
        """Actualiza sistemas del juego"""
        self._update_time_and_distance(delta_time)
        self._update_camera(delta_time)
        self.renderer.update(delta_time)
    
    def _update_camera(self, delta_time: float):
        """Actualiza la camara usando el sistema de Camera (suavizado centralizado)."""
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
        
        #Usar CollectibleSpawner en lugar de PilaSpawner
        # Crear un wrapper para manejar tanto escudos como pilas
        def collectible_callback(amount):
            """Callback que maneja tanto energia como escudos"""
            self.agregar_energia(amount)
        
        # Pasar el player como contexto para que el spawner pueda manejar escudos
        collectible_callback.__self__ = self.player
        
        self.collectible_spawner.update(
            delta_time, 
            self.camera.x, 
            self.player.rect.x, 
            self.player.rect, 
            collectible_callback
        )
    
    def agregar_energia(self, cantidad):
        """Agrega energia a los robots sin pasar su maximo"""
        personaje_actual = self.player.get_current_character()
        
        autonomia_maxima_actual = self.player.obtener_autonomia_maxima()
       
        self.energy_remaining = min(self.energy_remaining + cantidad, autonomia_maxima_actual)
        self.energias_individuales[personaje_actual] = self.energy_remaining 
    
    def _check_game_conditions(self):
        """Verifica condiciones de fin de juego - ACTUALIZADO con sistema de escudo"""
        # Limpiar flag de colision protegida cuando ya termino el efecto visual
        if self.shield_collision_just_happened and not self.player.should_show_collision_effect():
            self.shield_collision_just_happened = False

        # Si acabamos de absorber una colision y aun estamos en la ventana de efecto,
        # evitamos chequear nuevas colisiones para no repetir el problema.
        if self.shield_collision_just_happened:
            # Aun en periodo post-absorcion: no comprobar colisiones
            pass
        else:
            # Verificar colisiones
            if self.car_spawner.check_collisions(self.player.rect):
                # Considerar absorbida si el jugador tiene escudo activo O si
                # aun esta el efecto visual de absorcion (por timing)
                if self.player.is_protected() or self.player.should_show_collision_effect():
                    # El escudo absorbe la colision: activar efecto y marcar flag
                    self.player.activate_shield_collision_effect()
                    self.shield_collision_just_happened = True

                    # Empujar ligeramente al jugador hacia delante para evitar solapamiento continuo
                    try:
                        PUSH_OUT = 60
                        self.player.rect.x += PUSH_OUT
                    except Exception:
                        pass

                    print("¡Escudo protegio de la colision!")
                    # No procesar game over
                    return
                else:
                    # Sin escudo, game over normal
                    self._trigger_game_over()
                    return

        # Verificar condiciones de fin
        if self.energy_remaining <= 0:
            self._trigger_game_over()
            return
        
        elif self.game_mode == 'normal' and self.kilometers_remaining <= 0:
            self._trigger_victory()
            return
    
    def _trigger_game_over(self):
        """Activa el estado de game over"""
        self.game_over = True
        self.resource_manager.play_sound("game_over")
        self.resource_manager.stop_music()
    
    def _trigger_victory(self):
        """Activa el estado de victoria"""
        self.victory = True
        self.resource_manager.play_sound("victoria")
        self.resource_manager.stop_music()
    
    def _update_time_and_distance(self, delta_time: float):
        """Actualiza tiempo de energia y distancia recorrida"""
        # Solo consumir energia si no esta haciendo dash
        if not self.player.is_dashing:
            self.energy_remaining -= delta_time
            self.energia_minima()
            
        if not self.player.is_dashing:
            self.time += delta_time 
        if self.player.is_dashing:
            self.time += delta_time + DECREMENTO_KM_POR_SEGUNDO
        # Calcular distancia basada en tiempo transcurrido
        if self.game_mode == 'normal':
            km_traveled = self.time * DECREMENTO_KM_POR_SEGUNDO
            self.kilometers_remaining = max(0, KILOMETROS_OBJETIVO - km_traveled)
        else: 
            self.kilometers_remaining = self.time * DECREMENTO_KM_POR_SEGUNDO
    
    def _consume_energy(self, energy_amount: float) -> bool:
        """Consume energia si hay suficiente disponible"""
        if self.energy_remaining >= energy_amount:
            self.energy_remaining -= energy_amount
            self.energia_minima()
            return True
        return False
    
    def energia_minima(self):
        self.energy_remaining = max(0, self.energy_remaining)
        personaje_actual = self.player.get_current_character()
        self.energias_individuales[personaje_actual] = self.energy_remaining
    
    def on_enter(self):
        self.resource_manager.play_music("game_music", volume=0.6)
    
    def on_exit(self):
        pygame.mixer.stop()  
        print("Sonidos detenidos al salir del juego")
    
    def _save_game_statistics(self):
        """Guarda las estadisticas de la partida en un archivo CSV"""
        try:
            filename = "estadisticas_juego.csv"
            file_exists = os.path.exists(filename)
            
            # Obtener numero de partida
            partida_num = self._get_next_game_number(filename)
            
            with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Escribir datos de la partida actual
                if not file_exists:
                    # Escribir encabezado si el archivo no existia
                    writer.writerow(["Partida", "Modo","Km"])
                
                modo_texto = "Infinito" if self.game_mode == 'infinite' else "Normal"
                
                if self.game_mode == 'infinite':
                    km_final = f"{self.kilometers_remaining:.2f} km recorridos"
                else:
                    km_restantes = KILOMETROS_OBJETIVO - self.kilometers_remaining
                    km_final = f"{km_restantes:.2f}/{KILOMETROS_OBJETIVO} km"
                    
                row = [f"Partida {partida_num}:", modo_texto, km_final]
                writer.writerow(row)
                for personaje, distancia in self.distancias_personajes.items():
                    row = [f"{personaje}:", f"{distancia:.2f} km".replace(".",",")]
                    writer.writerow(row)

                
            print(f"Estadisticas guardadas - Partida {partida_num}")
            print("Distancias por personaje:")
            for personaje, distancia in self.distancias_personajes.items():
                print(f"  {personaje}: {distancia:.2f} km")
                
        except Exception as e:
            print(f"Error guardando estadisticas: {e}")
    
    def _get_next_game_number(self, filename):
        """Obtiene el proximo numero de partida"""
        if not os.path.exists(filename):
            return 1
            
        try:
            last_game_num = 0
            with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Saltamos la primera linea del encabezado
                for row in reader:
                    if row and row[0].startswith("Partida"):
                        try:
                            num = int(''.join(filter(str.isdigit, row[0])))
                            last_game_num = max(last_game_num, num)
                        except ValueError:
                            continue
                return last_game_num + 1
        except Exception as e:
            print(f"Error leyendo archivo de estadisticas: {e}")
            return 1
    
    def _restart_game(self):
        """Reinicia el juego desde el principio"""
        # Guardar estadisticas antes de reiniciar
        self._save_game_statistics()
        
        # reproducir sonido de respawn antes
        self.resource_manager.play_sound("reiniciar")      
        # pausa para que se escuche el sonido
        pygame.time.wait(500)  # 500ms de espera
        
        pygame.mixer.stop()
        from src.screens.game_screen import GameScreen
        self.scene_manager.change_scene(GameScreen)
    def _return_to_menu(self):
        """Regresa al menu principal"""
        # Guardar estadisticas antes de volver al menu
        if self.game_over or self.victory:
            self._save_game_statistics()
            
        pygame.mixer.stop()
        from src.screens.menu_screen import MenuScreen
        self.scene_manager.change_scene(MenuScreen)
    
    def draw(self):
        """Dibuja todos los elementos visuales"""
        self.renderer.draw_background(self.camera.x)
        self.renderer.draw_floor()
        self.renderer.draw_player(self.player, self.camera.x)
        self.renderer.draw_cars(self.car_spawner.get_cars(), self.camera.x)
        self.renderer.draw_planes(self.plane_spawner.get_planes(), self.camera.x)
        
        #Usar el metodo unificado para dibujar todos los coleccionables
        self.renderer.draw_collectibles(self.collectible_spawner.get_collectibles(), self.camera.x)
        
        # Dibujar UI
        if not self.game_over and not self.victory:
            autonomia_maxima_actual = self.player.obtener_autonomia_maxima()
            #Pasar informacion del escudo al HUD
            self.hud.draw(self.screen, self.energy_remaining, 
                         autonomia_maxima_actual, self.kilometers_remaining,
                         self.distancias_personajes, self.game_mode,
                         self.player.get_shield_time_remaining())  # Tiempo de escudo restante
        
        # Dibujar pantallas de fin de juego
        if self.game_over:
            self.renderer.draw_game_over_screen()
        elif self.victory:
            self.renderer.draw_victory_screen()
        if self.pause and not self.game_over and not self.victory:
            overlay = pygame.Surface((PANTALLA_ANCHO, PANTALLA_ALTO))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            font = pygame.font.SysFont(None, 60)
            text = font.render("Juego Pausado", True, (255, 255, 255))
            rect = text.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2))
            self.screen.blit(text, rect)

            font_small = pygame.font.SysFont(None, 36)
            text2 = font_small.render("Presiona R para continuar o ESC para volver al menu", True, (200, 200, 200))
            rect2 = text2.get_rect(center=(PANTALLA_ANCHO // 2, PANTALLA_ALTO // 2 + 60))
            self.screen.blit(text2, rect2)