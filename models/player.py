import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, spritesheet_path):
        super().__init__()
        # Dimensões originais de corte no Spritesheet
        self.crop_width = 90
        self.crop_height = 125
        
        # Dimensões finais desejadas na tela (mantém a proporção próxima de 32x32)
        self.target_width = 48
        self.target_height = 66

        self.spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
        
        # Mapeamento dos frames (coluna, linha) extraídos e redimensionados
        self.animations = {
            'down':  [self._get_sprite(0, 0), self._get_sprite(0, 2), self._get_sprite(2, 0)],
            'up':    [self._get_sprite(3, 0), self._get_sprite(4, 0), self._get_sprite(5, 0)],
            'right': [self._get_sprite(0, 1), self._get_sprite(1, 1), self._get_sprite(2, 1)],
            'left':  [pygame.transform.flip(s, True, False) for s in [self._get_sprite(0, 1), self._get_sprite(1, 1), self._get_sprite(2, 1)]]
        }
        
        self.direction = 'down'
        self.frame_index = 0.0
        self.animation_speed = 0.15
        self.is_moving = False

        self.image = self.animations[self.direction][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # Hitbox ajustada para a base dos pés do personagem redimensionado (24x12 px)
        # Posicionada no rodapé da imagem de 32x44 px (offset de +4px na largura e +28px na altura)
        self.hitbox = pygame.Rect(x + 4, y + 28, 24, 12)
        self.speed = 2.5

    def _get_sprite(self, col, row):
        """Recorta da imagem original (90x125) e redimensiona para a escala final (32x44)."""
        rect = pygame.Rect(col * self.crop_width, row * self.crop_height, self.crop_width, self.crop_height)
        subsurface = self.spritesheet.subsurface(rect)
        
        # Redimensiona mantendo nitidez de pixel art
        return pygame.transform.scale(subsurface, (self.target_width, self.target_height))

    def handle_input(self):
        """Lê os comandos de teclado e calcula o vetor de velocidade."""
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
            self.direction = 'left'
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
            self.direction = 'right'

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
            self.direction = 'up'
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
            self.direction = 'down'

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.is_moving = (dx != 0 or dy != 0)
        return dx * self.speed, dy * self.speed

    def animate(self):
        """Atualiza o ciclo de animação do personagem."""
        if self.is_moving:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.animations[self.direction]):
                self.frame_index = 0.0
        else:
            self.frame_index = 0.0

        self.image = self.animations[self.direction][int(self.frame_index)]

    def move_and_collide(self, dx, dy, colliders):
        """Aplica o movimento e resolve as colisões com as caixas do cenário."""
        # Colisão no Eixo X
        self.hitbox.x += dx
        for collider in colliders:
            if self.hitbox.colliderect(collider):
                if dx > 0:
                    self.hitbox.right = collider.left
                elif dx < 0:
                    self.hitbox.left = collider.right

        # Colisão no Eixo Y
        self.hitbox.y += dy
        for collider in colliders:
            if self.hitbox.colliderect(collider):
                if dy > 0:
                    self.hitbox.bottom = collider.top
                elif dy < 0:
                    self.hitbox.top = collider.bottom

        # Sincroniza o rect visual do sprite com a posição da hitbox
        self.rect.x = self.hitbox.x - 4
        self.rect.y = self.hitbox.y - 28

    def update(self, colliders):
        """Método de atualização executado a cada frame."""
        dx, dy = self.handle_input()
        self.move_and_collide(dx, dy, colliders)
        self.animate()

    def draw(self, surface, debug=False):
        """Desenha o sprite e opcionalmente a hitbox de colisão."""
        surface.blit(self.image, self.rect)
        if debug:
            pygame.draw.rect(surface, (0, 255, 0), self.hitbox, 1)