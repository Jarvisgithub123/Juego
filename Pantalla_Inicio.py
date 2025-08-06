import pygame
import sys
import random
import math
import Constantes
# Inicializar Pygame
pygame.init()



PANTALLA = pygame.display.set_mode((Constantes.ANCHO_PANTALLA, Constantes.ALTO_PANTALLA))
pygame.display.set_caption("Neo-Ciudad Vista - Edición Eco")
pygame.mixer.music.load("Recursos\Music\wwd.mp3juice.blog - Aventura - Los Infieles (192 KBps).mp3")
pygame.mixer.music.play(-1)  # Reproducir en bucle
sonido_boton=pygame.mixer.Sound("Recursos\Music\mixkit-arcade-game-jump-coin-216.mp3")

SONIDO_ACTIVADO = True
SALIR = False
# Fuentes
FUENTE_TITULO = pygame.font.Font(None, 90)
FUENTE_SUBTITULO = pygame.font.Font(None, 40)
FUENTE_BOTON = pygame.font.Font(None, 55)
FUENTE_PEQUENA = pygame.font.Font(None, 32)

# --- Clase Ventana  ---
class Ventana:
    def __init__(self, rel_x, rel_y, ancho, alto, es_eco=False):
        self.rect_rel = pygame.Rect(rel_x, rel_y, ancho, alto)
        self.es_eco = es_eco 
        self.esta_encendida = random.random() < (0.2 if es_eco else 0.3)
        self.alfa_actual = 255 if self.esta_encendida else 0
        self.velocidad_desvanecimiento = random.uniform(1.0, 2.5) 
        self.direccion_desvanecimiento = 0
        self.tiempo_cambio_siguiente_estado = pygame.time.get_ticks() + random.randint(2000, 8000) 

    def actualizar(self):
        tiempo_actual = pygame.time.get_ticks()
        if self.direccion_desvanecimiento != 0:
            self.alfa_actual += self.direccion_desvanecimiento * self.velocidad_desvanecimiento
            self.alfa_actual = max(0, min(255, self.alfa_actual))
            if (self.direccion_desvanecimiento == 1 and self.alfa_actual >= 255) or \
               (self.direccion_desvanecimiento == -1 and self.alfa_actual <= 0):
                self.direccion_desvanecimiento = 0
                self.esta_encendida = (self.alfa_actual > 0)
                self.tiempo_cambio_siguiente_estado = tiempo_actual + random.randint(2000, 8000)
        if self.direccion_desvanecimiento == 0 and tiempo_actual >= self.tiempo_cambio_siguiente_estado:
            probabilidad_cambio = 0.03 if self.es_eco else 0.05
            if random.random() < probabilidad_cambio:
                if self.esta_encendida:
                    self.direccion_desvanecimiento = -1
                else:
                    self.direccion_desvanecimiento = 1
                self.tiempo_cambio_siguiente_estado = tiempo_actual + random.randint(2000, 8000)

    def dibujar(self, superficie, abs_x, abs_y, multiplicador_alfa=1.0):
        rect_abs = self.rect_rel.copy()
        rect_abs.x += abs_x
        rect_abs.y += abs_y
        if self.alfa_actual > 0:
            if self.es_eco:
                color_ventana = Constantes.COLOR_VENTANA_ECO + (int(self.alfa_actual * multiplicador_alfa),)
            else:
                color_ventana = Constantes.COLOR_VENTANA_CLARA + (int(self.alfa_actual * multiplicador_alfa),)
            s = pygame.Surface((rect_abs.width, rect_abs.height), pygame.SRCALPHA)
            s.fill(color_ventana)
            superficie.blit(s, (rect_abs.x, rect_abs.y))
        else:
            color_apagado = Constantes.COLOR_VENTANA_APAGADA + (int(255 * multiplicador_alfa),)
            pygame.draw.rect(superficie, color_apagado, rect_abs)

# --- Clase Edificio ---
class Edificio:
    def __init__(self, x, y, ancho, alto, profundidad, tipo_edificio="normal"):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = alto
        self.profundidad = profundidad
        self.tipo_edificio = tipo_edificio 
        self.ventanas = []
        
        if tipo_edificio == "eco":
            self.tiene_brillo_azotea = random.random() < 0.4 
            self.tiene_paneles_solares = random.random() < 0.8
        elif tipo_edificio == "solar":
            self.tiene_brillo_azotea = True
            self.tiene_paneles_solares = True
        else:
            self.tiene_brillo_azotea = random.random() < 0.15
            self.tiene_paneles_solares = False
            
        if self.tiene_brillo_azotea:
            self.alfa_brillo = random.randint(120, 220)
            self.velocidad_desvanecimiento_brillo = random.uniform(0.5, 1.2)
            self.direccion_desvanecimiento_brillo = random.choice([-1, 1])
            if tipo_edificio in ["eco", "solar"]:
                self.color_brillo = random.choice([Constantes.BRILLO_VERDE, Constantes.BRILLO_ECO_CLARO])
            else:
                self.color_brillo = random.choice(Constantes.COLORES_BRILLO_FUTURISTA)
                
        self._generar_ventanas()

    def _generar_ventanas(self):
        espaciado_ventana_x = 12
        espaciado_ventana_y = 25
        ancho_ventana = 6
        alto_ventana = 12
        
        es_edificio_eco = self.tipo_edificio in ["eco", "solar"]
        
        for wx in range(8, self.ancho - 8, espaciado_ventana_x):
            for wy in range(15, self.alto - 25, espaciado_ventana_y):
                es_ventana_eco = es_edificio_eco or random.random() < 0.3
                self.ventanas.append(Ventana(wx, wy, ancho_ventana, alto_ventana, es_ventana_eco))

    def actualizar(self):
        for ventana in self.ventanas:
            ventana.actualizar()
            
        if self.tiene_brillo_azotea:
            self.alfa_brillo += self.direccion_desvanecimiento_brillo * self.velocidad_desvanecimiento_brillo
            if self.alfa_brillo <= 120 or self.alfa_brillo >= 220:
                self.direccion_desvanecimiento_brillo *= -1
                self.alfa_brillo = max(120, min(220, self.alfa_brillo))

    def dibujar(self, superficie, factor_escala=1.0, factor_alfa=1.0):
        ancho_escalado = int(self.ancho * factor_escala)
        alto_escalado = int(self.alto * factor_escala)
        profundidad_escalada = int(self.profundidad * factor_escala)
        
        # Calcular vértices isométricos
        p1_base = (self.x, self.y)
        p2_base = (self.x + ancho_escalado, self.y)
        p3_base = (self.x + ancho_escalado + profundidad_escalada * 0.5, self.y + profundidad_escalada * 0.5)
        p4_base = (self.x + profundidad_escalada * 0.5, self.y + profundidad_escalada * 0.5)
        
        p1_superior = (p1_base[0], p1_base[1] - alto_escalado)
        p2_superior = (p2_base[0], p2_base[1] - alto_escalado)
        p3_superior = (p3_base[0], p3_base[1] - alto_escalado)
        p4_superior = (p4_base[0], p4_base[1] - alto_escalado)
        
        puntos_cara_lateral = [p2_base, p3_base, p3_superior, p2_superior]
        puntos_cara_frontal = [p1_base, p2_base, p2_superior, p1_superior]
        puntos_cara_superior = [p1_superior, p2_superior, p3_superior, p4_superior]
        
        if self.tipo_edificio == "eco":
            color_lateral = Constantes.COLOR_EDIFICIO_ECO + (int(255 * factor_alfa),)
            color_frontal = (Constantes.COLOR_EDIFICIO_ECO[0] + 20, Constantes.COLOR_EDIFICIO_ECO[1] + 20, Constantes.COLOR_EDIFICIO_ECO[2] + 20) + (int(255 * factor_alfa),)
            color_superior = (Constantes.COLOR_EDIFICIO_ECO[0] + 40, Constantes.COLOR_EDIFICIO_ECO[1] + 40, Constantes.COLOR_EDIFICIO_ECO[2] + 40) + (int(255 * factor_alfa),)
        else:
            color_lateral = Constantes.COLOR_EDIFICIO_OSCURO + (int(255 * factor_alfa),)
            color_frontal = Constantes.COLOR_EDIFICIO_MEDIO + (int(255 * factor_alfa),)
            color_superior = Constantes.COLOR_EDIFICIO_CLARO + (int(255 * factor_alfa),)
            
        # Dibujar caras
        pygame.draw.polygon(superficie, color_lateral, puntos_cara_lateral)
        pygame.draw.polygon(superficie, color_frontal, puntos_cara_frontal)
        pygame.draw.polygon(superficie, color_superior, puntos_cara_superior)
        
        if self.tiene_paneles_solares:
            color_panel = (100, 150, 200) + (int(200 * factor_alfa),)
            ancho_panel = int(ancho_escalado * 0.8)
            alto_panel = int(profundidad_escalada * 0.8)
            rect_panel = pygame.Rect(
                p1_superior[0] + (ancho_escalado - ancho_panel) // 2,
                p1_superior[1] + (profundidad_escalada - alto_panel) // 4,
                ancho_panel,
                alto_panel
            )
            pygame.draw.rect(superficie, color_panel, rect_panel)
            
        # Dibujar contornos 
        color_contorno = random.choice(Constantes.COLORES_BRILLO_FUTURISTA) + (int(150 * factor_alfa),)
        ancho_contorno = max(1, int(2 * factor_escala))
        
        pygame.draw.line(superficie, color_contorno, p1_superior, p2_superior, ancho_contorno)
        pygame.draw.line(superficie, color_contorno, p2_superior, p3_superior, ancho_contorno)
        pygame.draw.line(superficie, color_contorno, p1_superior, p4_superior, ancho_contorno)
        pygame.draw.line(superficie, color_contorno, p1_superior, p1_base, ancho_contorno)
        pygame.draw.line(superficie, color_contorno, p2_superior, p2_base, ancho_contorno)
        pygame.draw.line(superficie, color_contorno, p3_superior, p3_base, ancho_contorno)
        pygame.draw.line(superficie, color_contorno, p1_base, p2_base, ancho_contorno)
        pygame.draw.line(superficie, color_contorno, p2_base, p3_base, ancho_contorno)
        
        # Dibujar ventanas
        for ventana in self.ventanas:
            ventana.dibujar(superficie, p1_superior[0], p1_superior[1], multiplicador_alfa=factor_alfa)
            
        if self.tiene_brillo_azotea:
            color_brillo = self.color_brillo + (int(self.alfa_brillo * factor_alfa),)
            tamano_brillo = int(8 * factor_escala)
            s = pygame.Surface((tamano_brillo * 2, tamano_brillo * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, color_brillo, (tamano_brillo, tamano_brillo), tamano_brillo)
            superficie.blit(s, (int(p1_superior[0] + ancho_escalado / 2 - tamano_brillo), int(p1_superior[1] - tamano_brillo)))

# --- Generación de Ciudad  ( EDIFICIOS) ---
FILAS_CUADRICULA_EDIFICIOS = 30 
COLUMNAS_CUADRICULA_EDIFICIOS = 40 
ESPACIADO_EDIFICIO_X = 38 
ESPACIADO_EDIFICIO_Y = 32 
edificios = []

def generar_edificios_ciudad_isometricos():
    global edificios
    edificios = []
    
    origen_mundo_x = -Constantes.ANCHO_PANTALLA // 2  
    origen_mundo_y = Constantes.ALTO_PANTALLA - 80
    
    for fila in range(FILAS_CUADRICULA_EDIFICIOS):
        for col in range(COLUMNAS_CUADRICULA_EDIFICIOS):
            base_x = col * ESPACIADO_EDIFICIO_X + origen_mundo_x
            base_y = fila * ESPACIADO_EDIFICIO_Y + origen_mundo_y
            
            # Variar más las dimensiones del edificio
            ancho = random.randint(22, 65)
            alto = random.randint(70, 320)
            profundidad = random.randint(12, 40)
            
            tipo_edificio_aleatorio = random.random()
            if tipo_edificio_aleatorio < 0.3:
                tipo_edificio = "eco"
            elif tipo_edificio_aleatorio < 0.4:
                tipo_edificio = "solar"
            else:
                tipo_edificio = "normal"
                
            # Escala y alfa según la distancia
            factor_escala = 1.0 - (fila / FILAS_CUADRICULA_EDIFICIOS) * 0.75
            factor_alfa = 1.0 - (fila / FILAS_CUADRICULA_EDIFICIOS) * 0.8
            
            # Ajustar posición
            x_ajustado = base_x + (1 - factor_escala) * (ancho / 2)
            y_ajustado = base_y + (1 - factor_escala) * (alto / 2)
            
            edificios.append({
                'obj': Edificio(x_ajustado, y_ajustado, ancho, alto, profundidad, tipo_edificio),
                'escala': factor_escala,
                'alfa': factor_alfa,
                'orden_dibujo_y': y_ajustado + alto * factor_escala
            })
    edificios.sort(key=lambda b: b['orden_dibujo_y'])

generar_edificios_ciudad_isometricos()

# --- Clase Botón ---
class Boton:
    def __init__(self, texto, x, y, ancho, alto, accion=None):
        self.texto = texto
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.accion = accion
        self.color = Constantes.COLOR_PRIMARIO
        self.color_hover = Constantes.COLOR_SECUNDARIO
        self.color_texto = Constantes.COLOR_TEXTO_EN_BOTON
        self.hover_viejo= False

    def dibujar(self, superficie):
        pos_raton = pygame.mouse.get_pos()
        color_actual = self.color


        esta_en_hover = self.rect.collidepoint(pos_raton)
        if esta_en_hover and not self.hover_viejo:
            sonido_boton.play()
            
        self.hover_viejo = esta_en_hover

        if esta_en_hover:
            color_actual = self.color_hover
            
        pygame.draw.rect(superficie, color_actual, self.rect, border_radius=8) 
        
        superficie_texto = FUENTE_BOTON.render(self.texto, True, self.color_texto)
        rect_texto = superficie_texto.get_rect(center=self.rect.center)
        superficie.blit(superficie_texto, rect_texto)

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(evento.pos) and self.accion:
                self.accion()

# --- Función de Dibujo de Fondo Dinámico (Simplificada con árboles) ---
def dibujar_fondo_dinamico(superficie):
    superficie.fill(Constantes.COLOR_FONDO_BASE)
    
    pygame.draw.circle(superficie, Constantes.COLOR_LUNA, (Constantes.ANCHO_PANTALLA - 100, 80), 30)
    
    for datos_edificio in edificios:
        edificio = datos_edificio['obj']
        escala = datos_edificio['escala']
        alfa = datos_edificio['alfa']
        edificio.actualizar()
        edificio.dibujar(superficie, factor_escala=escala, factor_alfa=alfa)
        
   
        
    superficie_bruma = pygame.Surface(superficie.get_size(), pygame.SRCALPHA)
    superficie_bruma.fill(Constantes.COLOR_BRUMA)
    superficie.blit(superficie_bruma, (0,0))
    
    # Plano del suelo
    pygame.draw.rect(superficie, Constantes.COLOR_SUELO, (0, Constantes.ALTO_PANTALLA - 50, Constantes.ANCHO_PANTALLA, 50))



# --- Funciones del Menú ---
def Juego():
    musica = pygame.mixer.music.stop()  # Llamar a la función de inicio del juego desde el módulo Juego


def ver_opciones():
    print("Viendo Opciones Ambientales")
    ejecutar_menu_opciones() 

def salir_juego():
    print("Saliendo de Eco-Ciudad")
    pygame.quit()
    sys.exit()

            

# --- Nueva función para el menú de opciones ---
def ejecutar_menu_opciones():

    def alternar_sonido():
        global SONIDO_ACTIVADO
        if SONIDO_ACTIVADO:
            pygame.mixer.music.pause() 
            SONIDO_ACTIVADO = False
        else: 
            pygame.mixer.music.unpause()
            SONIDO_ACTIVADO = True
    
    ancho_boton_opcion = 400
    alto_boton_opcion = 70
    espaciado_opcion = 20
    
    centro_x = Constantes.ANCHO_PANTALLA // 2
    inicio_y_opciones = Constantes.ALTO_PANTALLA // 2 - 100 
    
    
    # Botón de Sonido
    boton_sonido = Boton(
        f"Sonido: {'Activado' if SONIDO_ACTIVADO else 'Desactivado'}",
        centro_x - ancho_boton_opcion // 2,
        inicio_y_opciones,
        ancho_boton_opcion,
        alto_boton_opcion,
        alternar_sonido
    )

    boton_volver = Boton(
        "Volver al Menú",
        centro_x - ancho_boton_opcion // 2,
        inicio_y_opciones + 1 * (alto_boton_opcion + espaciado_opcion),
        ancho_boton_opcion,
        alto_boton_opcion,
        lambda: None
    )
    
    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                salir_juego()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    ejecutando = False 
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_volver.rect.collidepoint(evento.pos):
                    ejecutando = False
            
            boton_sonido.manejar_evento(evento)

       

        dibujar_fondo_dinamico(PANTALLA)
        
        superficie_titulo_opciones = FUENTE_TITULO.render("Opciones", True, Constantes.COLOR_TEXTO_EN_FONDO)
        rect_titulo_opciones = superficie_titulo_opciones.get_rect(center=(Constantes.ANCHO_PANTALLA // 2, 120))
        PANTALLA.blit(superficie_titulo_opciones, rect_titulo_opciones)

        # Actualizar el texto de los botones cada frame
        boton_sonido.texto = f"Sonido: {'Activado' if SONIDO_ACTIVADO else 'Desactivado'}"
       
        
        boton_sonido.dibujar(PANTALLA)
        boton_volver.dibujar(PANTALLA)

        texto_volver_ayuda = FUENTE_PEQUENA.render("Presiona ESC para volver", True, Constantes.COLOR_TEXTO_SUTIL_EN_FONDO)
        rect_volver_ayuda = texto_volver_ayuda.get_rect(center=(Constantes.ANCHO_PANTALLA // 2, Constantes.ALTO_PANTALLA // 2 - 150))
        PANTALLA.blit(texto_volver_ayuda, rect_volver_ayuda)

        pygame.display.flip()

def main_menu():
    ancho_boton = 250
    alto_boton = 75
    espaciado = 30
    altura_total_botones = 3 * alto_boton + 2 * espaciado
    inicio_y = (Constantes.ALTO_PANTALLA - altura_total_botones) // 2 + 60
    
    inicio_x = Constantes.ANCHO_PANTALLA - ancho_boton - 480
    
    botones = [
        Boton("Jugar", inicio_x, inicio_y, ancho_boton, alto_boton, Juego),
        Boton("Ajustes", inicio_x, inicio_y + alto_boton + espaciado, ancho_boton, alto_boton, ver_opciones),
        Boton("Salir", inicio_x, inicio_y + 2 * (alto_boton + espaciado), ancho_boton, alto_boton, salir_juego)
    ]
    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                salir_juego()
            for boton in botones:
                boton.manejar_evento(evento)
        dibujar_fondo_dinamico(PANTALLA)
        superficie_titulo = FUENTE_TITULO.render("Centro Eco-Ciudad", True, Constantes.COLOR_TEXTO_EN_FONDO)
        rect_titulo = superficie_titulo.get_rect(center=(Constantes.ANCHO_PANTALLA // 2, 120))
        PANTALLA.blit(superficie_titulo, rect_titulo)
        superficie_subtitulo = FUENTE_SUBTITULO.render("Construyendo un Futuro Sostenible", True, Constantes.COLOR_TEXTO_SUTIL_EN_FONDO)
        rect_subtitulo = superficie_subtitulo.get_rect(center=(Constantes.ANCHO_PANTALLA // 2, 180))
        PANTALLA.blit(superficie_subtitulo, rect_subtitulo)
        for boton in botones:
            boton.dibujar(PANTALLA)
        pygame.display.flip()

if __name__ == "__main__":
    PANTALLA = pygame.display.set_mode((Constantes.ANCHO_PANTALLA, Constantes.ALTO_PANTALLA))
    pygame.display.set_caption(f"Neo-Ciudad Vista - {Constantes.ANCHO_PANTALLA}x{Constantes.ALTO_PANTALLA}")
    
    generar_edificios_ciudad_isometricos()

    for i in range(20):
        x = random.randint(50, Constantes.ANCHO_PANTALLA - 50)
        y = Constantes.ALTO_PANTALLA - 50
    

    main_menu()
