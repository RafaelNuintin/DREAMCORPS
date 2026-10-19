import pygame
import sys
from models.level1 import Level1
from models.player import Player

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("DREAMCORPS.™")
clock = pygame.time.Clock()

# Inicializa o nível e o jogador no quarto do canto superior direito
level1 = Level1(SCREEN_WIDTH, SCREEN_HEIGHT)
player = Player(x=620, y=180, spritesheet_path="assets/player_spritesheet.png")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Atualiza a lógica do jogador passando a lista de colisões do cenário
    player.update(level1.colliders)

    # Renderiza o fundo e o jogador (defina debug=True para visualizar as caixas verdes/vermelhas)
    level1.draw(screen, debug=False)
    player.draw(screen, debug=False)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()