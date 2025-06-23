import pygame
import random
import sys
import os
import math

# Inicialización
pygame.init()
pygame.mixer.init() # Initialize the mixer for sounds

ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Super Mario Pygame")
reloj = pygame.time.Clock()

# Cargar imágenes (solo fondo y personajes)
try:
    fondo_img = pygame.image.load('fondo.png').convert()
    fondo_img = pygame.transform.scale(fondo_img, (ANCHO, ALTO))
    
    mario_img = pygame.image.load('mariop.png').convert_alpha()
    mario_img_pequeno = pygame.transform.scale(mario_img, (50, 50))
    mario_img_grande = pygame.image.load('mariog.png').convert_alpha()
    mario_img_grande = pygame.transform.scale(mario_img, (70, 70))  # Nueva imagen grande
    
    goomba_img = pygame.image.load('goomba.png').convert_alpha()
    goomba_img = pygame.transform.scale(goomba_img, (40, 40))
    
    hongo_img = pygame.image.load('hongo.png').convert_alpha()
    hongo_img = pygame.transform.scale(hongo_img, (30, 30))
    
    moneda_img = pygame.image.load('moneda.png').convert_alpha()
    moneda_img = pygame.transform.scale(moneda_img, (30, 30))
    
    tortuga_img = pygame.image.load('tortuga.png').convert_alpha()  # Nueva imagen para tortuga
    tortuga_img = pygame.transform.scale(tortuga_img, (50, 50))
    
    print("¡Imágenes principales cargadas correctamente!")
except pygame.error as e:
    print(f"Error al cargar imágenes: {e}")
    print("Usando gráficos vectoriales alternativos...")
    fondo_img = mario_img_pequeno = mario_img_grande = goomba_img = hongo_img = moneda_img = tortuga_img = None

# Cargar sonidos
try:
    coin_sound = pygame.mixer.Sound('coin.wav') # Path to your coin sound file
    game_over_sound = pygame.mixer.Sound('lose.wav') # Path to your game over sound file
    print("¡Sonidos cargados correctamente!")
except pygame.error as e:
    print(f"Error al cargar sonidos: {e}")
    coin_sound = None
    game_over_sound = None

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (100, 100, 255)
AMARILLO = (255, 255, 0)
MARRON = (139, 69, 19)
GRIS = (150, 150, 150)
MARRON_PLATAFORMA = (139, 69, 19)
VERDE_HIERBA = (34, 139, 34)
victoria = False  
game_over_played = False # Flag to ensure game over sound plays only once

# Jugador (Mario)
class Jugador:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ancho = 40
        self.alto = 60
        self.vel_x = 0
        self.vel_y = 0
        self.saltando = False
        self.vidas = 3
        self.direccion = 1
        self.invencible = False
        self.tiempo_invencible = 0
        self.grande = False
        self.cayendo_activo = False  # Nuevo atributo para controlar la caída
        
    def mover(self, teclas):
        self.vel_x = 0
        if teclas[pygame.K_LEFT]: 
            self.vel_x = -5
            self.direccion = -1
        if teclas[pygame.K_RIGHT]: 
            self.vel_x = 5
            self.direccion = 1
        self.x += self.vel_x
        
        # Permitir caer a través de plataformas presionando abajo (S)
        if teclas[pygame.K_s] and not self.saltando:
            self.cayendo_activo = True
            self.saltando = True
            self.y += 2  # Pequeño empujón hacia abajo
        
        if teclas[pygame.K_SPACE] and not self.saltando:
            self.vel_y = -15
            self.saltando = True
            self.cayendo_activo = False
            
    def gravedad(self, plataformas):
        self.vel_y += 0.8
        self.y += self.vel_y
        
        # Colisión con plataformas
        en_plataforma = False
        for plataforma in plataformas:
            # Solo colisionar si no estamos en modo caída activo
            if (not self.cayendo_activo and 
                self.y + self.alto >= plataforma.y and 
                self.y + self.alto <= plataforma.y + 20 and
                self.x + self.ancho > plataforma.x and 
                self.x < plataforma.x + plataforma.width):
                
                self.y = plataforma.y - self.alto
                self.vel_y = 0
                self.saltando = False
                self.cayendo_activo = False  
                en_plataforma = True
        
        # Colisión con el suelo principal
        if not en_plataforma and self.y + self.alto > ALTO - 50:
            self.y = ALTO - 50 - self.alto
            self.vel_y = 0
            self.saltando = False
            self.cayendo_activo = False
        
        # Colisión con el suelo principal (redundante, but keeping for now based on original code)
        if not en_plataforma and self.y + self.alto > ALTO - 50:
            self.y = ALTO - 50 - self.alto
            self.vel_y = 0
            self.saltando = False
            
    def dibujar(self):
        if mario_img_pequeno and mario_img_grande:
            # Voltear imagen según direccion
            img = pygame.transform.flip(mario_img_grande if self.grande else mario_img_pequeno, 
                                      self.direccion == -1, False)
            pantalla.blit(img, (self.x, self.y))
        else:
            # Dibujo vectorial alternativo (ahora con tamaño variable)
            size_factor = 1.3 if self.grande else 1.0
            pygame.draw.rect(pantalla, ROJO, (self.x, self.y + 20*size_factor, 
                                            self.ancho*size_factor, (self.alto - 20)*size_factor))
            pygame.draw.rect(pantalla, (0, 0, 255), (self.x, self.y + 30*size_factor, 
                                                   self.ancho*size_factor, (self.alto - 30)*size_factor))
            pygame.draw.circle(pantalla, (255, 200, 150), 
                             (self.x + 20*size_factor, self.y + 15*size_factor), 
                             15*size_factor)
            ojo_x = self.x + 25*size_factor if self.direccion > 0 else self.x + 15*size_factor
            pygame.draw.circle(pantalla, BLANCO, (ojo_x, self.y + 15*size_factor), 5*size_factor)
            pygame.draw.circle(pantalla, NEGRO, (ojo_x, self.y + 15*size_factor), 2*size_factor)
            
    def hacer_invencible(self, tiempo):
        self.invencible = True
        self.tiempo_invencible = tiempo
        
    def hacer_grande(self):
        self.grande = True
        self.ancho = int(self.ancho * 1.3)
        self.alto = int(self.alto * 1.3)


class Goomba:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ancho = 40
        self.alto = 40
        self.velocidad = 1
        self.vivo = True
        self.direccion = -1  # Empieza moviéndose a la izquierda
        self.en_plataforma = False

    def mover(self, plataformas):
        # Movimiento horizontal
        self.x += self.direccion * self.velocidad
        
        # Detección de bordes mejorada
        self.en_plataforma = False
        for plataforma in plataformas:
            # Verifica si está sobre la plataforma
            if (self.y + self.alto >= plataforma.y - 5 and  # Margen superior
                self.y + self.alto <= plataforma.y + 20 and  # Margen inferior
                self.x + self.ancho > plataforma.x and 
                self.x < plataforma.x + plataforma.width):
                
                self.en_plataforma = True
                
                # Cambia dirección si golpea el borde
                if (self.direccion < 0 and self.x <= plataforma.x + 5) or \
                   (self.direccion > 0 and self.x + self.ancho >= plataforma.x + plataforma.width - 5):
                    self.direccion *= -1
                    break  # Evita cambios múltiples
        
        # Gravedad solo si no está en plataforma
        if not self.en_plataforma:
            self.y += 5
            # Buscar plataforma debajo
            for plataforma in plataformas:
                if (self.y + self.alto <= plataforma.y and
                    self.x + self.ancho > plataforma.x and
                    self.x < plataforma.x + plataforma.width):
                    self.y = plataforma.y - self.alto
                    self.en_plataforma = True
                    break

    def dibujar(self):
        if self.vivo:
            if goomba_img:
                pantalla.blit(goomba_img, (self.x, self.y))
            else:
                # Dibujo vectorial alternativo
                pygame.draw.ellipse(pantalla, MARRON, (self.x, self.y, self.ancho, self.alto))
                pygame.draw.circle(pantalla, BLANCO, (self.x + 10, self.y + 15), 5)
                pygame.draw.circle(pantalla, BLANCO, (self.x + 30, self.y + 15), 5)
                pygame.draw.circle(pantalla, NEGRO, (self.x + 10, self.y + 15), 2)
                pygame.draw.circle(pantalla, NEGRO, (self.x + 30, self.y + 15), 2)

class Tortuga:
    def __init__(self, x, y, direccion):
        self.x = x
        self.y = y
        self.ancho = 50
        self.alto = 50
        self.velocidad = 2
        self.vivo = True
        self.direccion = direccion  # 1 para derecha, -1 para izquierda
        self.en_plataforma = False
        # Eliminamos los atributos relacionados con el caparazón
        # self.en_caparazon = False
        # self.tiempo_caparazon = 0
        # self.velocidad_caparazon = 5
    
    def mover(self, plataformas):
        # Eliminamos la lógica del estado de caparazón
        self.x += self.direccion * self.velocidad
        
        # Detección de bordes
        self.en_plataforma = False
        for plataforma in plataformas:
            if (self.y + self.alto >= plataforma.y - 5 and
                self.y + self.alto <= plataforma.y + 20 and
                self.x + self.ancho > plataforma.x and 
                self.x < plataforma.x + plataforma.width):
                
                self.en_plataforma = True
                
                if (self.direccion < 0 and self.x <= plataforma.x + 5) or \
                   (self.direccion > 0 and self.x + self.ancho >= plataforma.x + plataforma.width - 5):
                    self.direccion *= -1
                    break
        
        # Gravedad solo si no está en plataforma
        if not self.en_plataforma:
            self.y += 5
            for plataforma in plataformas:
                if (self.y + self.alto <= plataforma.y and
                    self.x + self.ancho > plataforma.x and
                    self.x < plataforma.x + plataforma.width):
                    self.y = plataforma.y - self.alto
                    self.en_plataforma = True
                    break
    
    def golpear(self):
        # Ahora simplemente mata a la tortuga y da puntos
        self.vivo = False
        return 200  # Puntos por matar tortuga
    
    def dibujar(self):
        if self.vivo:
            if tortuga_img:
                img = pygame.transform.flip(tortuga_img, self.direccion == -1, False)
                pantalla.blit(img, (self.x, self.y))
            else:
                # Dibujo vectorial alternativo (solo estado normal, sin caparazón)
                pygame.draw.ellipse(pantalla, VERDE, (self.x, self.y, self.ancho, self.alto))
                pygame.draw.ellipse(pantalla, (0, 100, 0), (self.x + 5, self.y + 15, self.ancho - 10, self.alto - 20))
                # Cabeza
                cabeza_x = self.x + (self.ancho - 15) if self.direccion > 0 else self.x
                pygame.draw.ellipse(pantalla, VERDE, (cabeza_x, self.y + 15, 15, 20))
                pygame.draw.circle(pantalla, NEGRO, (cabeza_x + 10 if self.direccion > 0 else cabeza_x + 5, self.y + 25), 2)

class Estrella:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ancho = 30
        self.alto = 30
        self.recogida = False
        
    def dibujar(self):
        if not self.recogida:
            if moneda_img:
                pantalla.blit(moneda_img, (self.x, self.y))
            else:
                # Dibujar estrella con polígonos
                puntos = []
                for i in range(5):
                    angulo = math.pi * 2 * i / 5 - math.pi/2
                    puntos.append((self.x + self.ancho/2 + math.cos(angulo) * self.ancho/2, 
                                 self.y + self.alto/2 + math.sin(angulo) * self.alto/2))
                    angulo = math.pi * 2 * (i + 0.5) / 5 - math.pi/2
                    puntos.append((self.x + self.ancho/2 + math.cos(angulo) * self.ancho/4, 
                                 self.y + self.alto/2 + math.sin(angulo) * self.alto/4))
                pygame.draw.polygon(pantalla, AMARILLO, puntos)

class Hongo:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.ancho = 30
        self.alto = 30
        self.recogido = False
        self.direccion = 1  # Se mueve a la derecha
        
    def mover(self, plataformas):
        self.x += self.direccion * 2
        
        # Cambiar dirección en bordes
        for plataforma in plataformas:
            if (self.y + self.alto >= plataforma.y and 
                self.y + self.alto <= plataforma.y + 5 and
                self.x + self.ancho > plataforma.x and 
                self.x < plataforma.x + plataforma.width):
                
                if (self.direccion < 0 and self.x <= plataforma.x) or \
                   (self.direccion > 0 and self.x + self.ancho >= plataforma.x + plataforma.width):
                    self.direccion *= -1
                    break
    
    def dibujar(self):
        if not self.recogido:
            if hongo_img:
                pantalla.blit(hongo_img, (self.x, self.y))
            else:
                # Dibujo vectorial alternativo
                pygame.draw.rect(pantalla, ROJO, (self.x, self.y + 10, self.ancho, self.alto - 10))
                pygame.draw.ellipse(pantalla, BLANCO, (self.x - 5, self.y, self.ancho + 10, 20))
                pygame.draw.circle(pantalla, BLANCO, (self.x + 5, self.y + 10), 5)
                pygame.draw.circle(pantalla, BLANCO, (self.x + 25, self.y + 10), 5)

def dibujar_plataforma(plataforma):
    # Dibujar la parte principal de la plataforma (madera)
    pygame.draw.rect(pantalla, MARRON_PLATAFORMA, plataforma)
    
    # Dibujar hierba en la parte superior
    pygame.draw.rect(pantalla, VERDE_HIERBA, 
                    (plataforma.x, plataforma.y - 5, plataforma.width, 10))
    
    # Dibujar detalles de madera (rayas)
    for i in range(plataforma.x + 5, plataforma.x + plataforma.width, 15):
        pygame.draw.line(pantalla, (101, 67, 33), 
                        (i, plataforma.y + 5), 
                        (i, plataforma.y + plataforma.height - 5), 2)


def crear_mundo():
    # Plataformas
    plataformas = [
        pygame.Rect(0, ALTO-50, ANCHO, 50),  # Suelo principal
        pygame.Rect(100, 450, 200, 20),
        pygame.Rect(400, 450, 200, 20),
        pygame.Rect(150, 350, 200, 20),
        pygame.Rect(450, 350, 200, 20),
        pygame.Rect(200, 250, 150, 20),
        pygame.Rect(450, 250, 150, 20),
        pygame.Rect(350, 180, 100, 15)
    ]
    
    # Monedas (estrellas) - Exactamente 10 monedas
    monedas = []
    plataformas_validas = [p for p in plataformas if p.y < ALTO - 100]
    for _ in range(10):  # Solo crea 10 monedas iniciales
        plat = random.choice(plataformas_validas)
        monedas.append(Estrella(
            random.randint(plat.x + 10, plat.x + plat.width - 30),
            plat.y - 30
        ))
    
    
    # Goombas
    goombas = [
        Goomba(150, 450-40),
        Goomba(450, 450-40),
        Goomba(200, 350-40),
        Goomba(500, 350-40),
        Goomba(250, 250-40)
    ]
    
    # Hongos (aparecen aleatoriamente)
    hongos = [Hongo(300, 450-30)]
    
    # Tortugas (se generarán aleatoriamente durante el juego)
    tortugas = []
    
    return plataformas, monedas, goombas, hongos, tortugas

# Inicialización del juego
plataformas, monedas, goombas, hongos, tortugas = crear_mundo()
jugador = Jugador(100, ALTO - 110)
puntaje = 0
fuente = pygame.font.SysFont(None, 36)

# Variables para control de aparición de tortugas
ultimo_tiempo_tortuga = 0
intervalo_tortugas = 5000  # 5 segundos en milisegundos
max_tortugas = 4  # Máximo de tortugas en pantalla

ejecutando = True
while ejecutando:
    reloj.tick(60)
    
    # Dibujar fondo
    if fondo_img:
        pantalla.blit(fondo_img, (0, 0))
    else:
        pantalla.fill(AZUL)  # Fondo azul si no hay imagen
    
    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_r:  # Reiniciar
                plataformas, monedas, goombas, hongos, tortugas = crear_mundo()
                jugador = Jugador(100, ALTO - 110)
                puntaje = 0
                victoria = False  # Resetear estado de victoria
                game_over_played = False # Reset this flag for sound
    
    # Movimiento
    teclas = pygame.key.get_pressed()
    jugador.mover(teclas)
    jugador.gravedad(plataformas)
    
    # Actualizar invencibilidad
    if jugador.invencible:
        jugador.tiempo_invencible -= 1
        if jugador.tiempo_invencible <= 0:
            jugador.invencible = False
    
    # Generar nuevas tortugas aleatoriamente
    tiempo_actual = pygame.time.get_ticks()
    if (tiempo_actual - ultimo_tiempo_tortuga > intervalo_tortugas and 
        len(tortugas) < max_tortugas):
        
        # Decidir de qué lado aparece (0: izquierda, 1: derecha)
        lado = random.randint(0, 1)
        if lado == 0:
            # Aparece por la izquierda, moviéndose a la derecha
            tortugas.append(Tortuga(-50, ALTO - 100, 1))
        else:
            # Aparece por la derecha, moviéndose a la izquierda
            tortugas.append(Tortuga(ANCHO + 50, ALTO - 100, -1))
        
        ultimo_tiempo_tortuga = tiempo_actual
        # Hacer el intervalo un poco aleatorio (entre 3 y 7 segundos)
        intervalo_tortugas = random.randint(3000, 7000)
    
    # Dibujar plataformas
    for plataforma in plataformas:
        dibujar_plataforma(plataforma)
    
    # Recolectar estrellas
    for moneda in monedas[:]:
        moneda.dibujar()
        if (jugador.x < moneda.x + moneda.ancho and
            jugador.x + jugador.ancho > moneda.x and
            jugador.y < moneda.y + moneda.alto and
            jugador.y + jugador.alto > moneda.y and not moneda.recogida):
            
            moneda.recogida = True
            puntaje += 10
            monedas.remove(moneda)
            if coin_sound: # Play sound if loaded
                coin_sound.play()
            
            # (Eliminado el código que generaba nuevas monedas para mantener las 10 iniciales)
            
    # Verificar condición de victoria
    if len(monedas) == 0 and not victoria:
        victoria = True
        # Congelar al jugador
        jugador.vel_x = 0
        jugador.vel_y = 0    
    
    # Mover y dibujar Hongos
    for hongo in hongos[:]:
        hongo.mover(plataformas)
        hongo.dibujar()
        
        # Recolectar hongos
        if (jugador.x < hongo.x + hongo.ancho and
            jugador.x + jugador.ancho > hongo.x and
            jugador.y < hongo.y + hongo.alto and
            jugador.y + jugador.alto > hongo.y and not hongo.recogido):
            
            hongo.recogido = True
            hongos.remove(hongo)
            jugador.vidas += 1
            jugador.hacer_grande()  # Mario se hace grande al coger el hongo
    
    # Mover y dibujar Tortugas
    
        # Mover y dibujar Tortugas
    for tortuga in tortugas[:]:
        if tortuga.vivo:
            tortuga.mover(plataformas)
            
            if not jugador.invencible or pygame.time.get_ticks() % 200 < 100:
                tortuga.dibujar()
            
            # Colisión con jugador
            if (jugador.x < tortuga.x + tortuga.ancho and
                jugador.x + jugador.ancho > tortuga.x and
                jugador.y < tortuga.y + tortuga.alto and
                jugador.y + jugador.alto > tortuga.y):
                
                # Si cae sobre la tortuga (la mata)
                if (jugador.y + jugador.alto < tortuga.y + 20 and
                    jugador.vel_y > 0):
                    
                    puntaje += tortuga.golpear()  # Esto ahora mata a la tortuga
                    jugador.vel_y = -10
                
                # Colisión lateral
                elif not jugador.invencible:
                    if jugador.grande:
                        jugador.grande = False
                        jugador.ancho = 40
                        jugador.alto = 60
                        jugador.y += 20
                        jugador.hacer_invencible(60)
                    else:
                        if jugador.vidas == 1:
                            jugador.vidas = 0
                        else:
                            jugador.vidas -= 1
                        jugador.hacer_invencible(60)
                    
                    # Empujar al jugador
                    jugador.x -= 50 if jugador.x < tortuga.x else -50
        
        # Eliminar tortugas muertas
        tortugas = [t for t in tortugas if t.vivo]
        
    # Mover y dibujar Goombas
    for goomba in goombas[:]:
        if goomba.vivo:
            goomba.mover(plataformas)
            
            if not jugador.invencible or pygame.time.get_ticks() % 200 < 100:
                goomba.dibujar()
        
            if (jugador.x < goomba.x + goomba.ancho and
                jugador.x + jugador.ancho > goomba.x and
                jugador.y < goomba.y + goomba.alto and
                jugador.y + jugador.alto > goomba.y):
                
                # Si cae sobre el Goomba (lo mata)
                if (jugador.y + jugador.alto < goomba.y + 20 and
                    jugador.vel_y > 0):
                    
                    goomba.vivo = False
                    puntaje += 100
                    jugador.vel_y = -10
                
                # Colisión lateral
                elif not jugador.invencible:
                    if jugador.grande:
                        # Volver a estado pequeño
                        jugador.grande = False
                        jugador.ancho = 40
                        jugador.alto = 60
                        jugador.y += 20  # Ajustar posición al encogerse
                        jugador.hacer_invencible(60)  # 1 segundo de invencibilidad
                    else:
                        if jugador.vidas == 1:
                            # Última vida - juego termina
                            jugador.vidas = 0
                        else:
                            # Restar una vida
                            jugador.vidas -= 1
                        jugador.hacer_invencible(60)  # 1 segundo de invencibilidad
                    
                    # Empujar al jugador
                    jugador.x -= 50 if jugador.x < goomba.x else -50
    
    # Eliminar Goombas muertos
    goombas = [g for g in goombas if g.vivo]
    
    # Dibujar jugador (con efecto de invencibilidad)
    if not jugador.invencible or pygame.time.get_ticks() % 200 < 100:
        jugador.dibujar()
    
    # Mostrar puntaje y vidas
    texto = fuente.render(f"Vidas: {jugador.vidas}  Puntaje: {puntaje}", True, BLANCO)
    pantalla.blit(texto, (10, 10))
    
    # Game Over
    if victoria:
        texto_victoria = fuente.render("¡GANASTE! - Presiona R para reiniciar", True, VERDE)
        pantalla.blit(texto_victoria, (ANCHO//2 - 150, ALTO//2 - 18))
    elif jugador.vidas <= 0:  # El Game Over original
        texto_gameover = fuente.render("GAME OVER - Presiona R para reiniciar", True, ROJO)
        pantalla.blit(texto_gameover, (ANCHO//2 - 180, ALTO//2 - 18))
        if not game_over_played and game_over_sound: # Play sound only once
            game_over_sound.play()
            game_over_played = True

    pygame.display.flip()

pygame.quit()
sys.exit()