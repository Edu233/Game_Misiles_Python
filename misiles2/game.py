import pygame, random
import cv2
import mediapipe as mp
import numpy as np

WIDTH = 1000
HEIGHT = 850
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh

# Configuración para el seguimiento de la cabeza del usuario
cap = cv2.VideoCapture(0)
mp_face_mesh = mp.solutions.face_mesh.FaceMesh()
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DISPARA Y DESTRUYE")
clock = pygame.time.Clock()
#tipo de letra
def draw_text(surface, text, size, x, y):
    font = pygame.font.SysFont("serif", size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)
# barra de vida
def draw_shield_bar(surface, x, y, percentage):
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (percentage / 100) * BAR_LENGTH
    border = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surface, GREEN, fill)
    pygame.draw.rect(surface, WHITE, border, 2)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # carga al objeto jugador y le da las dimensiones de acuerdo a lo requerido
        self.image = pygame.transform.scale(pygame.image.load("assets/player.png").convert(), (140, 180))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed_x = 0
        self.shield = 100
        
        # Crear la nueva superficie para mostrar la imagen de la cámara
        self.camera_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
        
        # Crear un rectángulo para mostrar la imagen de la cámara en la esquina superior derecha de la pantalla
        # self.camera_rect = pygame.Rect(WIDTH - 220, 10, 200, 200)
        # self.camera_surface.fill((255, 255, 255))
        # screen.blit(self.camera_surface, (WIDTH - 200, 0))

    def update(self):
        self.speed_x = 15        
        # Capturar la imagen de la cámara y procesarla para detectar el rostro
        success, img = cap.read()
        img = cv2.flip(img, 2) # quitar efecto espejo
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = mp_face_mesh.process(img)        
        if results.multi_face_landmarks:
            # calcular la posición del centro del rostro en la imagen de la cámara
            for face_landmarks in results.multi_face_landmarks:
                for id, lm in enumerate(face_landmarks.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)                    
                    if id == 200: # ID del landmark de la punta de la nariz
                        if cx > self.rect.centerx:
                            self.speed_x = 15
                        elif cx < self.rect.centerx:
                            self.speed_x = -15
        
        self.rect.x += self.speed_x        
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        # Dibujar un rectángulo alrededor del rostro detectado en la imagen de la cámara
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                for idx, lm in enumerate(face_landmarks.landmark):
                    x, y = int(lm.x * WIDTH), int(lm.y * HEIGHT)
                    if idx == 0: # ID del landmark de la mandíbula
                        pygame.draw.rect(screen, (0, 255, 0), (x-50, y-50, 100, 100), 2)
        # Dibujar la nueva superficie en la esquina superior derecha de la pantalla
        screen.blit(self.camera_surface, (WIDTH - self.camera_surface.get_width(), 2))
        # Escalar la imagen de la cámara para que quepa en un rectángulo más pequeño en la esquina superior derecha de la pantalla
        small_img = cv2.resize(img, (200, 200))
        # Dibujar la imagen de la cámara escalada en la nueva superficie creada en el paso
        small_img = cv2.cvtColor(small_img, cv2.COLOR_RGB2BGR)
        surf = pygame.surfarray.make_surface(small_img)
        self.camera_surface.blit(surf, (0, 0))

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        laser_sound.play()

class Meteor(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.image = random.choice(meteor_images)
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.x = random.randrange(WIDTH - self.rect.width)
		self.rect.y = random.randrange(-140, -100)
		self.speedy = random.randrange(1, 10)
		self.speedx = random.randrange(-5, 5)

	def update(self):
		self.rect.y += self.speedy
		self.rect.x += self.speedx
		if self.rect.top > HEIGHT + 10 or self.rect.left < -40 or self.rect.right > WIDTH + 40:
			self.rect.x = random.randrange(WIDTH - self.rect.width)
			self.rect.y = random.randrange(-140, - 100)
			self.speedy = random.randrange(1, 10)

class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super().__init__()
		self.image = pygame.image.load("assets/laser2.png")
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.y = y
		self.rect.centerx = x
		self.speedy = -10

	def update(self):
		self.rect.y += self.speedy
		if self.rect.bottom < 0:
			self.kill()

class Explosion(pygame.sprite.Sprite):
	def __init__(self, center):
		super().__init__()
		self.image = explosion_anim[0]
		self.rect = self.image.get_rect()
		self.rect.center = center 
		self.frame = 0
		self.last_update = pygame.time.get_ticks()
		self.frame_rate = 50 # VELOCIDAD DE LA EXPLOSION

	def update(self):
		now = pygame.time.get_ticks()
		if now - self.last_update > self.frame_rate:
			self.last_update = now
			self.frame += 1
			if self.frame == len(explosion_anim):
				self.kill()
			else:
				center = self.rect.center
				self.image = explosion_anim[self.frame]
				self.rect = self.image.get_rect()
				self.rect.center = center

def show_go_screen():
	screen.blit(background, [0,0])
	draw_text(screen, "PIUM PIUM", 65, WIDTH // 2, HEIGHT // 10)
	draw_text(screen, "PRESIONA ESPACIO O ENTER PARA EMPEZAR", 27, WIDTH // 2, HEIGHT // 2)
	draw_text(screen, "Instrucciones: Mueve la cabeza a la izuierda/derecha y barra espaciadora para disparar", 20, WIDTH // 2, HEIGHT * 3/4)

    
	pygame.display.flip()
	waiting = True
	while waiting:
		clock.tick(60)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
			if event.type == pygame.KEYUP:
				waiting = False
# arreglo de imagenes para los meteoros
meteor_images = []
meteor_list = ["assets/meteorGrey_big1.png", "assets/meteorGrey_big2.png", "assets/meteorGrey_big3.png", "assets/meteorGrey_big4.png",
				"assets/meteorGrey_med1.png", "assets/meteorGrey_med2.png", "assets/meteorGrey_small1.png", "assets/meteorGrey_small2.png",
				"assets/meteorGrey_tiny1.png", "assets/meteorGrey_tiny2.png"]
# leé todos los datos del arreglo de las imagenes
for img in meteor_list:
	meteor_images.append(pygame.image.load(img).convert())

#secuencia de explocion de los meteoros
explosion_anim = []
for i in range(9):
	file = "assets/regularExplosion0{}.png".format(i)
	img = pygame.image.load(file).convert()
	img.set_colorkey(BLACK)
	img_scale = pygame.transform.scale(img, (70,70))
	explosion_anim.append(img_scale)

# Cargar imagen de fondo
background = pygame.image.load("assets/fondo1.jpeg").convert()

# Cargar sonidos
laser_sound = pygame.mixer.Sound("assets/9903.wav")
explosion_sound = pygame.mixer.Sound("assets/explosion.wav")
pygame.mixer.music.load("assets/sound1.wav")
pygame.mixer.music.set_volume(0.8)
pygame.mixer.music.play(loops=-1)

# game over del juego
game_over = True
running = True
while running:
	if game_over:

		show_go_screen()

		game_over = False
		all_sprites = pygame.sprite.Group()
		meteor_list = pygame.sprite.Group()
		bullets = pygame.sprite.Group()

		player = Player()
		all_sprites.add(player)
		for i in range(8):
			meteor = Meteor()
			all_sprites.add(meteor)
			meteor_list.add(meteor)

		score = 0     

	clock.tick(60)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				player.shoot()

	all_sprites.update()

	#colisiones - meteoro - laser
	hits = pygame.sprite.groupcollide(meteor_list, bullets, True, True)
	for hit in hits:
		score += 15
		#explosion_sound.play()
		explosion = Explosion(hit.rect.center)
		all_sprites.add(explosion)
		meteor = Meteor()
		all_sprites.add(meteor)
		meteor_list.add(meteor)

	# Checar colisiones - jugador - meteoro
	hits = pygame.sprite.spritecollide(player, meteor_list, True)
	for hit in hits:
		player.shield -= 25
		meteor = Meteor()
		all_sprites.add(meteor)
		meteor_list.add(meteor)
		if player.shield <= 0:
			game_over = True

	screen.blit(background, [0, 0])

	all_sprites.draw(screen)

	#Marcador
	draw_text(screen, "Puntaje: " + str(score), 25, WIDTH // 5, 10)
	# Escudo.
	draw_shield_bar(screen, 5, 5, player.shield)

	pygame.display.flip()
pygame.quit()
