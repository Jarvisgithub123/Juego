import pygame, random

class PlaneSpawner:
    def __init__(self, resource_manager):
        # variables principales del sistema
        self.resource_manager = resource_manager
        self.planes = []
        self.timer = 0
        self.spawn_interval = random.randint(10000, 20000)
        
        # cargar spritesheet y extraer frames de animacion
        self.plane_spritesheet = self.resource_manager.get_spritesheet("avion")
        if self.plane_spritesheet:
            self.plane_frames = []
            for row in range(self.plane_spritesheet.rows):
                self.plane_frames.extend(self.plane_spritesheet.get_row(row))
        else:
            self.plane_frames = []

    def update(self, delta_time, camera_x):
        # Control de spawn
        self.timer += delta_time * 1000
        if self.timer >= self.spawn_interval:
            self.spawn_plane(camera_x)
            self.timer = 0
            self.spawn_interval = random.randint(20000, 30000)

        # aodos los aviones existentes
        for plane in self.planes:
            # mover avion hacia la izquierda
            plane["x"] -= 150 * delta_time
            
            # actualiza la  animación de la bandera
            plane["animation_timer"] += delta_time
            if plane["animation_timer"] >= plane["animation_speed"]:
                plane["current_frame"] = (plane["current_frame"] + 1) % len(self.plane_frames)
                plane["animation_timer"] = 0

        # Limpiar aviones que salieron de pantalla
        self.planes = [p for p in self.planes if p["x"] + 200 > -200]

    def spawn_plane(self, camera_x):
        if self.plane_frames:
            # escalar  los frames 
            scaled_frames = []
            for frame in self.plane_frames:
                scaled_frame = pygame.transform.scale(frame, (280, 187))
                scaled_frames.append(scaled_frame)
            
            # crear nuevo avion con todas sus propiedades
            new_plane = {
                "frames": scaled_frames,
                "current_frame": 0,
                "animation_timer": 0,
                "animation_speed": random.uniform(0.15, 0.25), 
                "x": camera_x + 1200,
                "y": random.randint(20, 80)
            }
            self.planes.append(new_plane)
            print(f"¡Avión animado creado! Frames: {len(scaled_frames)}")

    def get_planes(self):
        # Preparar aviones para el renderer con el frame actual
        animated_planes = []
        for plane in self.planes:
            if plane["frames"]:
                current_frame = plane["frames"][plane["current_frame"]]
                animated_planes.append({
                    "img": current_frame,
                    "x": plane["x"],
                    "y": plane["y"]
                })
        return animated_planes
    
    def get_debug_info(self):
        # Información de debugging del sistema
        return {
            "planes_activos": len(self.planes),
            "timer_actual": self.timer,
            "proximo_spawn": self.spawn_interval - self.timer,
            "frames_disponibles": len(self.plane_frames)
        }