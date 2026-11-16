import pygame
import math

class Artifact:
    """Objeto interativo/artefato que o protagonista pode coletar ou examinar."""
    def __init__(self, x, y, item_id, name, description, color=(255, 215, 60), prompt="[E] Coletar"):
        self.x = x
        self.y = y
        self.item_id = item_id
        self.name = name
        self.description = description
        self.color = color
        self.prompt = prompt
        
        self.collected = False
        self.interaction_radius = 45
        self.time = 0.0

        # Superfície do ícone do artefato
        self.icon_size = 24
        self.surface = self._generate_icon()

    def _generate_icon(self):
        """Desenha um ícone temático em pixel art dependendo do tipo do artefato."""
        surf = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
        s = self.icon_size
        
        if self.item_id == "dreamsync_capsule":
            # Cápsula de medicamento DREAMSYNC™ (vermelho e branco)
            pygame.draw.rect(surf, (230, 45, 60), (s//4, s//4, s//2, s//4))
            pygame.draw.rect(surf, (240, 240, 250), (s//4, s//2, s//2, s//4))
            pygame.draw.rect(surf, (30, 30, 40), (s//4, s//4, s//2, s//2), 1)

        elif self.item_id == "red_id_card":
            # Cartão de acesso vermelho
            pygame.draw.rect(surf, (220, 50, 50), (3, 5, s - 6, s - 10), border_radius=2)
            pygame.draw.rect(surf, (255, 255, 255), (6, 8, 5, 5))
            pygame.draw.line(surf, (240, 240, 240), (14, 9), (s - 7, 9), 1)
            pygame.draw.line(surf, (240, 240, 240), (14, 12), (s - 7, 12), 1)
            pygame.draw.rect(surf, (30, 20, 20), (3, 5, s - 6, s - 10), 1, border_radius=2)

        elif self.item_id == "employee_key":
            # Chave de acesso dourada/corporativa
            pygame.draw.circle(surf, (255, 205, 50), (8, 12), 5, 2)
            pygame.draw.line(surf, (255, 205, 50), (12, 12), (20, 12), 2)
            pygame.draw.line(surf, (255, 205, 50), (17, 12), (17, 16), 2)
            pygame.draw.line(surf, (255, 205, 50), (20, 12), (20, 15), 2)

        elif self.item_id == "subject_03_file":
            # Dossiê confidencial
            pygame.draw.rect(surf, (200, 180, 130), (4, 4, 16, 17))
            pygame.draw.rect(surf, (220, 60, 50), (7, 7, 10, 4)) # Tag CONFIDENTIAL
            pygame.draw.line(surf, (80, 60, 40), (7, 13), (16, 13), 1)
            pygame.draw.line(surf, (80, 60, 40), (7, 16), (14, 16), 1)
            pygame.draw.rect(surf, (70, 50, 30), (4, 4, 16, 17), 1)

        elif self.item_id == "reality_anchor":
            # Segunda cápsula / Âncora da Realidade
            pygame.draw.circle(surf, (100, 220, 255), (s//2, s//2), 8, 2)
            pygame.draw.circle(surf, (255, 255, 255), (s//2, s//2), 3)

        else:
            # Padrão: orbe de luz reluzente
            pygame.draw.circle(surf, self.color, (s//2, s//2), 6)
            pygame.draw.circle(surf, (255, 255, 255), (s//2, s//2), 2)

        return surf

    def update(self, dt):
        self.time += dt

    def is_near_player(self, player_rect):
        """Verifica se o jogador está a uma distância de interação."""
        center_x = self.x + self.icon_size // 2
        center_y = self.y + self.icon_size // 2
        p_center = player_rect.center
        dist = math.hypot(center_x - p_center[0], center_y - p_center[1])
        return dist <= self.interaction_radius

    def draw(self, surface, player_rect, font):
        if self.collected:
            return

        # Animação de pulsação e levitação suave
        float_y = self.y + math.sin(self.time * 3.0) * 3
        pulse = (math.sin(self.time * 4.0) + 1) * 0.5

        # Glow ao redor do artefato
        glow_radius = int(14 + pulse * 4)
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color[:3], int(40 + 40 * pulse)), (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surf, (self.x + self.icon_size//2 - glow_radius, int(float_y) + self.icon_size//2 - glow_radius))

        # Desenha o ícone
        surface.blit(self.surface, (self.x, int(float_y)))

        # Se o jogador estiver perto, exibe o balão de dica de interação [E]
        if self.is_near_player(player_rect):
            prompt_text = f"{self.prompt}: {self.name}"
            text_surf = font.render(prompt_text, True, (255, 240, 180))
            
            box_w = text_surf.get_width() + 16
            box_h = text_surf.get_height() + 8
            box_x = int(self.x + self.icon_size // 2 - box_w // 2)
            box_y = int(float_y - box_h - 8)

            box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            box_surf.fill((10, 14, 28, 220))
            surface.blit(box_surf, (box_x, box_y))
            pygame.draw.rect(surface, (255, 190, 60), (box_x, box_y, box_w, box_h), 1, border_radius=3)
            surface.blit(text_surf, (box_x + 8, box_y + 4))
