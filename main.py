import pygame
import sys
from tilemap import Tilemap
from levels import LEVEL_1_BACKGROUND, LEVEL_1_OBJECTS

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("DREAMCORPS")
clock = pygame.time.Clock()

# Carrega o tileset e inicializa o sistema
tilemap = Tilemap("assets/tileset.png")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((10, 10, 15)) # Cor de fundo da tela

    # Desenha as camadas (Chão primeiro, Objetos depois)
    tilemap.draw(screen, LEVEL_1_BACKGROUND)
    tilemap.draw(screen, LEVEL_1_OBJECTS)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()