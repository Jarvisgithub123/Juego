import pygame, random

class PlaneSpawner:
    def __init__(self, resource_manager):
        self.resource_manager = resource_manager
        self.planes = []
        self.timer = 0
        self.spawn_interval = random.randint(10000, 15000)  
        
        test_img = self.resource_manager.get_image("avion")
        if test_img:
            print("✓ Imagen de avión cargada correctamente")
        else:
            print("✗ ERROR: No se pudo cargar la imagen del avión")

    def update(self, delta_time, camera_x):
        self.timer += delta_time * 1000  
        
        if self.timer >= self.spawn_interval:
            self.spawn_plane(camera_x)
            self.timer = 0
            self.spawn_interval = random.randint(20000, 50000)  
            print(f"Próximo avión en {self.spawn_interval/1000:.1f} segundos")

        for plane in self.planes:
            plane["x"] -= 150 * delta_time  
            
        before_count = len(self.planes)
        self.planes = [p for p in self.planes if p["x"] + p["img"].get_width() > -200]
        
        if len(self.planes) < before_count:
            print(f"Aviones eliminados. Restantes: {len(self.planes)}")

    def spawn_plane(self, camera_x):
        img = self.resource_manager.get_image("avion")
        if img:
            new_plane = {
                "img": img,
                "x": camera_x + 1200,   
                "y": random.randint(10, 40)            }
            self.planes.append(new_plane)
            print(f"¡Avión creado! Posición: ({new_plane['x']}, {new_plane['y']})")
        else:
            print("ERROR: No se pudo crear el avión - imagen no disponible")

    def get_planes(self):
        return self.planes
    
    # Método de debug adicional
    def get_debug_info(self):
        return {
            "planes_activos": len(self.planes),
            "timer_actual": self.timer,
            "proximo_spawn": self.spawn_interval - self.timer,
            "posiciones": [(p["x"], p["y"]) for p in self.planes]
        }