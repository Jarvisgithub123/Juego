import pygame
import sys
import os
import math
import random
from Constantes import *


def juego():
    sonido_salto = pygame.mixer.Sound("Assets\Music\Jump.mp3")
    sonido_derrota = pygame.mixer.Sound("Assets\Music\Game-over.mp3")
    sonido_ganar = pygame.mixer.Sound("Assets\Music\Win.mp3")
    pygame.init()


    class Auto(pygame.sprite.Sprite):
        """Clase que representa los autos enemigos"""
        def __init__(self, x, y, velocidad=7, ancho=100, alto=40):
            super().__init__()
            
            # Intentar cargar imagen del auto o crear rectangulo como respaldo
            try:
                imagen = pygame.image.load("Assets/Imagenes/auto.png").convert_alpha()
                self.image = pygame.transform.scale(imagen, (ancho, alto))
            except:
                # Crear superficie roja como respaldo
                self.image = pygame.Surface((ancho, alto))
                self.image.fill(COLOR_ROJO)
            
            self.rect = pygame.Rect(x, y, ancho, alto)
            self.velocidad = velocidad
            self.ancho = ancho
            self.alto = alto
            
        def actualizar(self):
            """Actualiza la posicion del auto moviendolo hacia la izquierda"""
            self.rect.x -= self.velocidad
            
            # Si sale de la pantalla, reiniciar posicion
            if self.rect.right < 0:
                self.rect.left = PANTALLA_ANCHO
                
        def dibujar(self, pantalla):
            """Dibuja el auto en la pantalla"""
            if hasattr(self, 'image'):
                pantalla.blit(self.image, self.rect)
            else:
                pygame.draw.rect(pantalla, COLOR_ROJO, self.rect)

    class Collisions:
        """Clase para manejar las colisiones entre sprites"""
        def __init__(self):
            pass
            
        def verificar_colision_personaje_autos(self, personaje, autos):
            """Verifica colision entre el personaje y una lista de autos"""
            for auto in autos:
                if personaje.rect.colliderect(auto.rect):
                    return True
            return False
        
        def verificar_colision_sprites(self, sprite1, sprite2):
            """Verifica colision entre dos sprites cualesquiera"""
            return sprite1.rect.colliderect(sprite2.rect)
        
        def verificar_colision_grupo(self, sprite, grupo_sprites):
            """Verifica colision entre un sprite y un grupo de sprites"""
            for sprite_grupo in grupo_sprites:
                if sprite.rect.colliderect(sprite_grupo.rect):
                    return sprite_grupo
            return None

    class UI:
        """Clase para manejar la interfaz de usuario (HUD)"""
        def __init__(self):
            # Configurar fuentes
            self.font_instrucciones = pygame.font.SysFont(None, 36)
            self.font_hud = pygame.font.SysFont(None, 32)
            
            # Crear textos estaticos
            self.txt_instrucciones = self.font_instrucciones.render(
                "Usa la barra espaciadora para saltar", True, COLOR_BLANCO)
            self.instrucciones_rect = self.txt_instrucciones.get_rect()
            self.instrucciones_rect.topleft = (10, 10)
            
            # Configurar fondo de instrucciones
            padding = 10
            self.fondo_instrucciones = pygame.Rect(
                self.instrucciones_rect.left - padding,
                self.instrucciones_rect.top - padding,
                self.instrucciones_rect.width + 2 * padding,
                self.instrucciones_rect.height + 2 * padding
            )
        
        def dibujar_instrucciones(self, pantalla):
            """Dibuja las instrucciones en pantalla"""
            pygame.draw.rect(pantalla, COLOR_INSTRUCCION_FONDO, self.fondo_instrucciones)
            pantalla.blit(self.txt_instrucciones, self.instrucciones_rect)
        
        def dibujar_barra_energia(self, pantalla, energia_actual, energia_maxima):
            """Dibuja la barra de energia en la parte superior derecha"""
            # Calcular porcentaje
            porcentaje = (energia_actual / energia_maxima) * 100
            
            # Configuracion de la barra
            barra_ancho = 200
            barra_alto = 20
            barra_x = PANTALLA_ANCHO - barra_ancho - 20
            barra_y = 20
            
            # Dibujar fondo de la barra
            pygame.draw.rect(pantalla, COLOR_BARRA_FONDO, (barra_x, barra_y, barra_ancho, barra_alto))
            
            # Calcular ancho segun energia restante
            ancho_energia = int((energia_actual / energia_maxima) * barra_ancho)
            
            # Determinar color segun nivel de energia
            if porcentaje > 60:
                color_energia = COLOR_BARRA_ENERGIA
            elif porcentaje > 30: 
                color_energia = COLOR_AMARILLO
            else:
                color_energia = COLOR_ROJO
            
            # Dibujar barra de energia
            if ancho_energia > 0:
                pygame.draw.rect(pantalla, color_energia, (barra_x, barra_y, ancho_energia, barra_alto))
            
            # Dibujar borde
            pygame.draw.rect(pantalla, COLOR_BLANCO, (barra_x, barra_y, barra_ancho, barra_alto), 2)
            
            # Dibujar texto con porcentaje
            texto_energia = self.font_hud.render(f"Energia: {porcentaje:.0f}%", True, COLOR_BLANCO)
            pantalla.blit(texto_energia, (barra_x, barra_y - 25))
        
        def dibujar_contador_kilometros(self, pantalla, km_restantes):
            """Dibuja el contador de kilometros en la parte superior izquierda"""
            contador_x = 20
            contador_y = 60
            
            # Crear texto
            texto_km = self.font_hud.render(f"Kilometros restantes: {km_restantes:.2f} km", True, COLOR_AMARILLO)
            
            # Crear fondo para el texto
            texto_rect = texto_km.get_rect()
            texto_rect.topleft = (contador_x, contador_y)
            
            fondo_contador = pygame.Rect(texto_rect.left - 5, texto_rect.top - 5, 
                                        texto_rect.width + 10, texto_rect.height + 10)
            pygame.draw.rect(pantalla, COLOR_INSTRUCCION_FONDO, fondo_contador)
            
            # Dibujar el texto
            pantalla.blit(texto_km, (contador_x, contador_y))

    
    class GameOver:
        """Clase para manejar el estado de fin de juego"""
        def __init__(self):
            # Configurar fuentes
            self.font_game_over = pygame.font.SysFont(None, 100)
            self.font_victoria = pygame.font.SysFont(None, 80)
            self.font_normal = pygame.font.SysFont(None, 32)
            self.font_reintentar = pygame.font.SysFont(None, 38)
        
            # Crear textos
            self.txt_game_over = self.font_game_over.render("JUEGO TERMINADO", True, COLOR_ROJO)
            self.txt_reintentar = self.font_reintentar.render("Presione [ENTER] o [ESPACIO] para volver a jugar", True, COLOR_VERDE)
            self.txt_victoria = self.font_victoria.render("¡El paquete fue entregado con exito!", True, COLOR_TEXTO_VICTORIA)
            self.txt_salir = self.font_normal.render("Presiona [ESCAPE]  para volver al menu", True, COLOR_BLANCO)
            
            # Posicionar textos
            self.game_over_rect = self.txt_game_over.get_rect(center=(PANTALLA_ANCHO // 2, (PANTALLA_ALTO // 2) - 200))
            self.reintentar_rect = self.txt_reintentar.get_rect(center=(PANTALLA_ANCHO // 2, (PANTALLA_ALTO // 2) - 150))
            self.victoria_rect = self.txt_victoria.get_rect(center=(PANTALLA_ANCHO // 2, (PANTALLA_ALTO // 2) - 200))
            self.salir_rect = self.txt_salir.get_rect(center=(PANTALLA_ANCHO // 2, (PANTALLA_ALTO // 2) - 120))
        
        def dibujar_game_over(self, pantalla):
            """Dibuja la pantalla de game over"""
            pantalla.blit(self.txt_game_over, self.game_over_rect)
            pantalla.blit(self.txt_reintentar, self.reintentar_rect)
            pantalla.blit(self.txt_salir, self.salir_rect)
        
        def dibujar_victoria(self, pantalla):
            """Dibuja la pantalla de victoria"""
            pantalla.blit(self.txt_victoria, self.victoria_rect)
            pantalla.blit(self.txt_salir, self.salir_rect)

    class Game:
        """Clase principal del juego que maneja toda la logica y renderizado"""
        def __init__(self):
            # Configurar pantalla
            self.pantalla = pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
            pygame.display.set_caption("OFIRCA 2025 - Ronda 1 Inicio")
            self.clock = pygame.time.Clock()
            
            # Cargar imagen de fondo
            self.cargar_fondo()
            
            # Inicializar componentes del juego
            self.personaje = Personaje(100, PISO_POS_Y - 64, scale=0.2)
            self.autos = [Auto(PANTALLA_ANCHO, PISO_POS_Y - 40)]  # Lista de autos
            self.collisions = Collisions()
            self.ui = UI()
            self.game_over_screen = GameOver()
            
            # Variables de estado
            self.ejecutando = True
            self.game_over = False
            self.victoria = False
            
            # Variables de tiempo y distancia
            self.tiempo_inicio = pygame.time.get_ticks()
            self.energia_restante = DURACION_ENERGIA
            self.kilometros_restantes = KILOMETROS_OBJETIVO
            
            # Variables para animacion del fondo
            self.fondo_x1 = 0
            self.fondo_x2 = PANTALLA_ANCHO
            self.velocidad_fondo = 2
        
        def cargar_fondo(self):
            """Carga la imagen de fondo del juego"""
            if os.path.exists(RUTA_ARCHIVO_FONDO):
                self.img_fondo = pygame.image.load(RUTA_ARCHIVO_FONDO)
                self.img_fondo = pygame.transform.scale(self.img_fondo, (PANTALLA_ANCHO, PANTALLA_ALTO))
            else:
                self.img_fondo = None

        def manejar_eventos(self):
            """Maneja todos los eventos del juego"""
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    self.ejecutando = False
                
                keys = pygame.key.get_pressed()
                if (keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER] or keys[pygame.K_SPACE]) and self.game_over or self.victoria:
                    sonido_derrota.stop()
                    sonido_ganar.stop()
                    return "reiniciar"  # Reiniciar el juego
                    
                elif (keys[pygame.K_ESCAPE]) and self.game_over or self.victoria:
                    sonido_derrota.stop()
                    sonido_ganar.stop()
                    return "menu"  # Volver al menú
                


        
        def manejar_input(self):
            """Maneja el input del jugador"""
            if not self.game_over and not self.victoria:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    self.personaje.saltar()

        
        def actualizar_tiempo_y_distancia(self):
            """Actualiza el tiempo transcurrido y calcula kilometros restantes"""
            tiempo_actual = pygame.time.get_ticks()
            tiempo_transcurrido = (tiempo_actual - self.tiempo_inicio) / 1000
            
            # Calcular energia restante
            self.energia_restante = max(0, DURACION_ENERGIA - tiempo_transcurrido)
            
            # Calcular kilometros restantes
            km_recorridos = tiempo_transcurrido * DECREMENTO_KM_POR_SEGUNDO
            self.kilometros_restantes = max(0, KILOMETROS_OBJETIVO - km_recorridos)
            
            return tiempo_transcurrido
        
        def verificar_condiciones_fin_juego(self):
            """Verifica si el juego debe terminar (victoria o derrota)"""
            if not self.game_over and not self.victoria:
                # Verificar colision con autos
                if self.collisions.verificar_colision_personaje_autos(self.personaje, self.autos):
                    self.game_over = True
                    sonido_derrota.play()
                    return
                
                # Verificar si se agoto la energia
                if self.energia_restante <= 0:
                    self.game_over = True
                    return
                
                # Verificar victoria (completar recorrido)
                if self.kilometros_restantes <= 0:
                    self.victoria = True
                    sonido_ganar.play()
                    return
        
        def actualizar_objetos(self):
            """Actualiza todos los objetos del juego"""
            if not self.game_over and not self.victoria:
                # Actualizar personaje
                self.personaje.actualizar()
                
                # Actualizar autos
                for auto in self.autos:
                    auto.actualizar()
                
                # Animar fondo
                self.fondo_x1 -= self.velocidad_fondo
                self.fondo_x2 -= self.velocidad_fondo
                
                # Reiniciar posiciones del fondo
                if self.fondo_x1 <= -PANTALLA_ANCHO:
                    self.fondo_x1 = PANTALLA_ANCHO
                if self.fondo_x2 <= -PANTALLA_ANCHO:
                    self.fondo_x2 = PANTALLA_ANCHO
        
        def dibujar_fondo_animado(self):
            """Dibuja el fondo animado"""
            if self.img_fondo:
                self.pantalla.blit(self.img_fondo, (self.fondo_x1, -(PANTALLA_ALTO - PISO_POS_Y)))
                self.pantalla.blit(self.img_fondo, (self.fondo_x2, -(PANTALLA_ALTO - PISO_POS_Y)))
            else:
                self.pantalla.fill(COLOR_BLANCO)
        
        def dibujar_piso(self):
            """Dibuja el piso del juego"""
            piso_altura = PANTALLA_ALTO - PISO_POS_Y
            piso_rect = pygame.Rect(0, PISO_POS_Y, PANTALLA_ANCHO, piso_altura)
            pygame.draw.rect(self.pantalla, COLOR_VERDE, piso_rect)
            pygame.draw.line(self.pantalla, COLOR_NEGRO, (0, PISO_POS_Y), (PANTALLA_ANCHO, PISO_POS_Y), 3)
        
        def dibujar_objetos(self):
            """Dibuja todos los objetos del juego"""
            # Dibujar personaje
            self.pantalla.blit(self.personaje.image, self.personaje.rect)
            
            # Dibujar autos
            for auto in self.autos:
                auto.dibujar(self.pantalla)
        
        def dibujar_ui(self):
            """Dibuja la interfaz de usuario"""
            if not self.game_over and not self.victoria:
                self.ui.dibujar_instrucciones(self.pantalla)
                self.ui.dibujar_barra_energia(self.pantalla, self.energia_restante, DURACION_ENERGIA)
                self.ui.dibujar_contador_kilometros(self.pantalla, self.kilometros_restantes)
        
        def dibujar_pantallas_fin(self):
            """Dibuja las pantallas de fin de juego"""
            if self.game_over:
                self.game_over_screen.dibujar_game_over(self.pantalla)
            elif self.victoria:
                self.game_over_screen.dibujar_victoria(self.pantalla)
        
        def dibujar(self):
            """Dibuja todos los elementos del juego en orden correcto"""
            # Dibujar fondo
            self.dibujar_fondo_animado()
            
            # Dibujar piso
            self.dibujar_piso()
            
            # Dibujar objetos del juego
            self.dibujar_objetos()
            
            # Dibujar interfaz de usuario
            self.dibujar_ui()
            
            # Dibujar pantallas de fin de juego si es necesario
            self.dibujar_pantallas_fin()
        
        def actualizar(self):
            """Actualiza toda la logica del juego"""
            # Actualizar tiempo y distancia
            self.actualizar_tiempo_y_distancia()
            
            # Verificar condiciones de fin de juego
            self.verificar_condiciones_fin_juego()
            
            # Actualizar objetos
            self.actualizar_objetos()
        
        def run(self):
            """Bucle principal del juego"""
            while self.ejecutando:
                # Mantener framerate
                self.clock.tick(FPS)
                resultado = self.manejar_eventos()  
                if resultado in ["reiniciar", "menu"]:
                    return resultado
                    
                # Manejar input del jugador
                self.manejar_input()
                
                # Actualizar logica del juego
                self.actualizar()
                
                # Dibujar todo
                self.dibujar()
                
                # Actualizar pantalla
                pygame.display.flip()
  
      
    while True:
        game = Game()
        resultado = game.run()

        if resultado == "reiniciar":
            continue
        elif resultado == "menu":
            break
    return

    # Punto de entrada del programa
if __name__ == "__main__":
    juego()