import pygame

class Level1:
    def __init__(self, screen_width, screen_height):
        # Carrega a imagem do cenário completo gerada pela IA
        self.background = pygame.image.load("assets/phase1.png").convert()
        # Redimensiona para encaixar na janela do jogo, se necessário
        self.background = pygame.transform.scale(self.background, (screen_width, screen_height))
        
        # Lista para armazenar as áreas de colisão (móveis, paredes e limites)
        self.colliders = []
        self._setup_colliders(screen_width, screen_height)

    def _setup_colliders(self, sw, sh):
        """
        Define as caixas de colisão usando proporções relativas à largura (sw) e altura (sh) da tela.
        Ajuste as coordenadas conforme o posicionamento dos móveis no seu ecrã.
        """
        # Exemplo: Limites das paredes externas da casa
        self.colliders.append(pygame.Rect(0, 0, sw, int(sh * 0.14)))          # Parede Superior
        self.colliders.append(pygame.Rect(0, 0, int(sw * 0.05), sh))          # Parede Esquerda
        self.colliders.append(pygame.Rect(int(sw * 0.93), 0, int(sw * 0.05), sh)) # Parede Direita
        self.colliders.append(pygame.Rect(0, int(sh * 0.77), sw, int(sh * 0.08))) # Parede Inferior

        # Paredes internas (Divisórias das salas)
        self.colliders.append(pygame.Rect(int(sw * 0.36), int(sh * 0.08), int(sw * 0.03), int(sh * 0.26)))
        self.colliders.append(pygame.Rect(int(sw * 0.36), int(sh * 0.39), int(sw * 0.03), int(sh * 0.15)))
        self.colliders.append(pygame.Rect(int(sw * 0.36), int(sh * 0.59), int(sw * 0.03), int(sh * 0.30))) # Parede Vertical Esquerda
        self.colliders.append(pygame.Rect(int(sw * 0.61), int(sh * 0.08), int(sw * 0.03), int(sh * 0.26)))
        self.colliders.append(pygame.Rect(int(sw * 0.61), int(sh * 0.39), int(sw * 0.03), int(sh * 0.15)))
        self.colliders.append(pygame.Rect(int(sw * 0.61), int(sh * 0.59), int(sw * 0.03), int(sh * 0.30))) # Parede Vertical Direita
        self.colliders.append(pygame.Rect(int(sw * 0.36), int(sh * 0.25), int(sw * 0.11), int(sh * 0.08)))
        self.colliders.append(pygame.Rect(int(sw * 0.52), int(sh * 0.25), int(sw * 0.11), int(sh * 0.08))) # Parede Horizontal Meio
        self.colliders.append(pygame.Rect(0, int(sh * 0.39), int(sw * 0.38), int(sh * 0.08))) # Parede Horizontal Esquerda
        self.colliders.append(pygame.Rect(int(sw * 0.61), int(sh * 0.39), int(sw * 0.38), int(sh * 0.08))) # Parede Horizontal Esquerda

        # Colisões dos móveis do Quarto do Protagonista (Canto Superior Direito)
     #   self.colliders.append(pygame.Rect(int(sw * 0.85), int(sh * 0.14), int(sw * 0.10), int(sh * 0.22))) # Cama
     #   self.colliders.append(pygame.Rect(int(sw * 0.70), int(sh * 0.18), int(sw * 0.10), int(sh * 0.12))) # Secretária e Computador
     #   self.colliders.append(pygame.Rect(int(sw * 0.64), int(sh * 0.10), int(sw * 0.05), int(sh * 0.15))) # Estante de Livros

    def draw(self, surface, debug=False):
        """Desenha o cenário e opcionalmente os retângulos de colisão para testes."""
        surface.blit(self.background, (0, 0))
        
        # Ative debug=True se quiser visualizar as caixas vermelhas de colisão na tela
        if debug:
            for rect in self.colliders:
                pygame.draw.rect(surface, (255, 0, 0), rect, 2)