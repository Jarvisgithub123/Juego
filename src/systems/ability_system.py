import json
import os
from typing import Dict, List, Any
from src.Constantes import *

class AbilitySystem:
    """Sistema centralizado de habilidades desbloqueables"""
    
    def __init__(self):
        # Configuracion de habilidades por mision
        self.ability_rewards = {
            "level_1": ["dash"],  # Mision 1: desbloquear dash
            "level_2": ["enhanced_batteries"],  # Mision 2: pilas mejoradas
            "level_3": ["double_jump"],  # Mision 3: doble salto
            "level_4": ["enhanced_shield"],  # Mision 4: escudo mejorado
            # Facil agregar mas misiones aqui
        }
        
        # Configuracion de distancias por mision (en km)
        self.mission_distances = {
            "level_1": 0.8,   # Mision 1: 0.8 km (mas facil para empezar)
            "level_2": 1.2,   # Mision 2: 1.2 km 
            "level_3": 1.5,   # Mision 3: 1.5 km
            "level_4": 2.0,   # Mision 4: 2.0 km (mas dificil)
            # Facil agregar mas misiones aqui
        }
        
        # Configuracion de efectos de cada habilidad
        self.ability_effects = {
            "dash": {
                "name": "Dash Desbloqueado",
                "description": "Presiona Z para hacer dash y avanzar rapidamente",
                "enabled": False
            },
            "enhanced_batteries": {
                "name": "Pilas Mejoradas",
                "description": "Las pilas ahora recarga +5 segundos adicionales de energia",
                "energy_bonus": 5,
                "enabled": False
            },
            "double_jump": {
                "name": "Salto Doble",
                "description": "Presiona ESPACIO dos veces para hacer doble salto",
                "enabled": False
            },
            "enhanced_shield": {
                "name": "Escudo Reforzado", 
                "description": "Los escudos duran 4 segundos adicionales",
                "duration_bonus": 4.0,
                "enabled": False
            }
        }
        
        # Estado actual de habilidades desbloqueadas
        self.unlocked_abilities = set()
        self.completed_missions = set()
        
        # Archivo para persistir progreso
        self.save_file = "mission_progress.json"
        
        # Cargar progreso guardado
        self.load_progress()
    
    def complete_mission(self, mission_key: str) -> List[str]:
        """
        Marca una mision como completada y desbloquea sus habilidades
        Retorna lista de habilidades desbloqueadas
        """
        if mission_key in self.completed_missions:
            return []  # Ya completada
        
        # Marcar mision como completada
        self.completed_missions.add(mission_key)
        
        # Desbloquear habilidades de esta mision
        new_abilities = []
        if mission_key in self.ability_rewards:
            for ability in self.ability_rewards[mission_key]:
                if ability not in self.unlocked_abilities:
                    self.unlocked_abilities.add(ability)
                    self.ability_effects[ability]["enabled"] = True
                    new_abilities.append(ability)
                    print(f"¡Habilidad desbloqueada: {self.ability_effects[ability]['name']}!")
        
        # Guardar progreso
        self.save_progress()
        
        return new_abilities
    
    def is_ability_unlocked(self, ability_name: str) -> bool:
        """Verifica si una habilidad esta desbloqueada"""
        return ability_name in self.unlocked_abilities
    
    def get_ability_info(self, ability_name: str) -> Dict[str, Any]:
        """Obtiene informacion completa de una habilidad"""
        return self.ability_effects.get(ability_name, {})
    
    def get_unlocked_abilities(self) -> List[str]:
        """Retorna lista de habilidades desbloqueadas"""
        return list(self.unlocked_abilities)
    
    def get_completed_missions(self) -> List[str]:
        """Retorna lista de misiones completadas"""
        return list(self.completed_missions)
    
    def unlock_all_abilities(self):
        """Desbloquea todas las habilidades (para modo normal/infinito)"""
        for ability in self.ability_effects:
            self.unlocked_abilities.add(ability)
            self.ability_effects[ability]["enabled"] = True
        print("Todas las habilidades desbloqueadas para modo libre")
    
    def reset_progress(self):
        """Resetea todo el progreso (util para testing)"""
        self.unlocked_abilities.clear()
        self.completed_missions.clear()
        for ability in self.ability_effects:
            self.ability_effects[ability]["enabled"] = False
        self.save_progress()
        print("Progreso de misiones reseteado")
    
    def save_progress(self):
        """Guarda el progreso en archivo JSON"""
        try:
            progress_data = {
                "unlocked_abilities": list(self.unlocked_abilities),
                "completed_missions": list(self.completed_missions)
            }
            with open(self.save_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
        except Exception as e:
            print(f"Error guardando progreso: {e}")
    
    def load_progress(self):
        """Carga el progreso desde archivo JSON"""
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    progress_data = json.load(f)
                
                self.unlocked_abilities = set(progress_data.get("unlocked_abilities", []))
                self.completed_missions = set(progress_data.get("completed_missions", []))
                
                # Actualizar estado de habilidades
                for ability in self.unlocked_abilities:
                    if ability in self.ability_effects:
                        self.ability_effects[ability]["enabled"] = True
                
                print(f"Progreso cargado: {len(self.unlocked_abilities)} habilidades, {len(self.completed_missions)} misiones")
        except Exception as e:
            print(f"Error cargando progreso: {e}")
    
    def get_enhanced_battery_energy(self) -> float:
        """Retorna la energia que dan las pilas (con bonificacion si esta desbloqueada)"""
        base_energy = ENERGIA_PILA
        if self.is_ability_unlocked("enhanced_batteries"):
            bonus = self.ability_effects["enhanced_batteries"].get("energy_bonus", 0)
            return base_energy + bonus
        return base_energy
    
    def get_enhanced_shield_duration(self) -> float:
        """Retorna la duracion del escudo (con bonificacion si esta desbloqueada)"""
        base_duration = ESCUDO_DURACION
        if self.is_ability_unlocked("enhanced_shield"):
            bonus = self.ability_effects["enhanced_shield"].get("duration_bonus", 0)
            return base_duration + bonus
        return base_duration
    
    def can_double_jump(self) -> bool:
        """Verifica si el doble salto esta disponible"""
        return self.is_ability_unlocked("double_jump")
    
    def can_dash(self) -> bool:
        """Verifica si el dash esta disponible"""
        return self.is_ability_unlocked("dash")
    
    def get_mission_reward_preview(self, mission_key: str) -> List[Dict[str, str]]:
        """Obtiene preview de recompensas para una mision"""
        rewards = []
        if mission_key in self.ability_rewards:
            for ability in self.ability_rewards[mission_key]:
                if ability in self.ability_effects:
                    ability_info = self.ability_effects[ability]
                    rewards.append({
                        "name": ability_info["name"],
                        "description": ability_info["description"]
                    })
        return rewards
    
    def get_mission_distance(self, mission_key: str) -> float:
        """Obtiene la distancia objetivo para una mision especifica"""
        return self.mission_distances.get(mission_key, KILOMETROS_OBJETIVO)

# Instancia global del sistema de habilidades
ability_system = AbilitySystem()