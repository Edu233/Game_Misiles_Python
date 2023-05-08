import pygame
import cv2
import mediapipe as mp
# ancho y largo de la ventana
WIDTH = 1000
HEIGHT = 800
BLACK = (0, 0, 0)
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shooter")
clock = pygame.time.Clock()
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("assets/player.png").convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed_x = 10

    def update(self, head_x):
        self.speed_x = 40
        if head_x < self.rect.centerx + 10:
            self.speed_x = -10
        elif head_x > self.rect.centerx - 10:
            self.speed_x = 10
        self.rect.x += self.speed_x
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

# Configurar la cámara y el detector de pose
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
cap = cv2.VideoCapture(0)
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Crear el jugador
all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

# Game Loop
running = True
while running:
    # Keep loop running at the right speed
    clock.tick(60)

    # Process input (events)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False        

    # Leer la imagen de la cámara
    ret, frame = cap.read()

    # Procesar la imagen para detectar el movimiento de la cabeza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)

    results = pose.process(rgb)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        head_x = int(landmarks[mp_pose.PoseLandmark.NOSE].x * WIDTH)
        player.update(head_x)
        
    # Limpiar la pantalla
    screen.fill(BLACK)


    # Dibujar la imagen de la cámara en la esquina superior izquierda
    frame = cv2.resize(frame, (120, 120))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = pygame.surfarray.make_surface(frame.swapaxes(0,1))
    screen.blit(frame, (0, 0))

    # Update
    all_sprites.update(head_x)

    #Draw / Render
    all_sprites.draw(screen)

    # *after* drawing everything, flip the display.
    pygame.display.flip()

# Liberar la cámara y cerrar la ventana
cap.release()
pygame.quit()
