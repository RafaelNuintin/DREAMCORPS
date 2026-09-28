import pygame

pygame.init()

tamanhoTela = [600, 400]

tela = pygame.display.set_mode(tamanhoTela)

pygame.display.set_caption("DREAMCORPS")

relogio = pygame.time.Clock()

corFundo = (25,25,112)

cenaAtual = 'menu'


while True:

    for e in pygame.event.get():

        if e.type == pygame.QUIT:

            pygame.quit()
            exit()

    tela.fill(corFundo)

    relogio.tick(60)

    pygame.display.flip()