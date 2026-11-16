import pygame
import math
import random

class Entity(pygame.sprite.Sprite):
    """
    Classe base para todas as anomalias da Dream Layer.
    Segue a classificação oficial da Dreamcorps.™ estabelecida no GDD (Seção 1.3).
    """
    def __init__(self, x, y, entity_type, name, width=32, height=48):
        super().__init__()
        self.entity_type = entity_type  # 'TYPE_A', 'TYPE_B', 'TYPE_C', 'TYPE_NULL'
        self.name = name
        self.width = width
        self.height = height

        self.x = float(x)
        self.y = float(y)
        self.rect = pygame.Rect(int(self.x), int(self.y), width, height)
        self.hitbox = pygame.Rect(int(self.x + 4), int(self.y + height - 16), width - 8, 14)

        self.time = random.uniform(0.0, 10.0)
        self.active = True
        self.alpha = 255.0
        self.font = pygame.font.SysFont(["consolas", "couriernew"], 11, bold=True)

    def update(self, dt, player_rect, colliders=None):
        self.time += dt
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.hitbox.x = int(self.x + 4)
        self.hitbox.y = int(self.y + self.height - 16)

    def draw(self, surface, debug=False):
        if not self.active or self.alpha <= 0:
            return
        if debug:
            pygame.draw.rect(surface, (255, 0, 255), self.rect, 1)
            pygame.draw.rect(surface, (255, 255, 0), self.hitbox, 1)


# ==============================================================================
# TYPE A: WATCHER (Observador)
# ==============================================================================
class Watcher(Entity):
    """
    Entidade Type A: Observador.
    Permanece imóvel em pontos estratégicos, observando o protagonista com olhos brilhantes.
    Quando o jogador se aproxima demais (raio de evasão), ele desvanece (fade-out)
    ou se teletransporta, gerando sensação de vigilância onírica.
    """
    def __init__(self, x, y, name="WATCHER_01", detection_radius=110):
        super().__init__(x, y, 'TYPE_A', name, width=32, height=50)
        self.detection_radius = detection_radius
        self.fading = False
        self.fade_speed = 320.0
        self.respawn_timer = 0.0
        self.initial_pos = (x, y)

    def update(self, dt, player_rect, colliders=None):
        super().update(dt, player_rect, colliders)

        # Distância Euclidiana em relação ao jogador
        p_center = player_rect.center
        e_center = self.rect.center
        dist = math.hypot(p_center[0] - e_center[0], p_center[1] - e_center[1])

        if dist < self.detection_radius and not self.fading:
            self.fading = True

        if self.fading:
            self.alpha = max(0.0, self.alpha - self.fade_speed * dt)
            if self.alpha <= 0:
                self.respawn_timer += dt
                # Ocasionalmente reaparece em um leve desvio onírico após 6 a 10 segundos
                if self.respawn_timer > 8.0:
                    self.fading = False
                    self.alpha = 255.0
                    self.respawn_timer = 0.0
                    jitter_x = random.choice([-20, 0, 20])
                    jitter_y = random.choice([-15, 0, 15])
                    self.x = self.initial_pos[0] + jitter_x
                    self.y = self.initial_pos[1] + jitter_y

    def draw(self, surface, debug=False):
        if self.alpha <= 0:
            return
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        cur_alpha = int(self.alpha)

        # Silhueta cinza-azulada com sobrecasaco e quepe (conforme Seção 1.3 do GDD)
        # Cabeça / Gorro
        pygame.draw.ellipse(surf, (72, 84, 102, cur_alpha), (6, 4, 20, 18))
        pygame.draw.rect(surf, (55, 66, 82, cur_alpha), (4, 14, 24, 6))

        # Olhos azuis brilhantes (observadores característicos)
        eye_pulse = (math.sin(self.time * 5.0) + 1.0) * 0.5
        eye_b = int(210 + 45 * eye_pulse)
        pygame.draw.rect(surf, (40, 170, eye_b, cur_alpha), (10, 11, 4, 4))
        pygame.draw.rect(surf, (40, 170, eye_b, cur_alpha), (18, 11, 4, 4))

        # Corpo / Uniforme de observação
        pygame.draw.rect(surf, (85, 98, 118, cur_alpha), (5, 20, 22, 22), border_radius=3)
        pygame.draw.rect(surf, (60, 72, 90, cur_alpha), (14, 20, 4, 22))

        # Pernas
        pygame.draw.rect(surf, (48, 56, 70, cur_alpha), (7, 42, 7, 8))
        pygame.draw.rect(surf, (48, 56, 70, cur_alpha), (18, 42, 7, 8))

        surface.blit(surf, (self.rect.x, self.rect.y))
        super().draw(surface, debug)


# ==============================================================================
# TYPE B: MIMIC (Mímico)
# ==============================================================================
class Mimic(Entity):
    """
    Entidade Type B: Mimic.
    Capaz de assumir a forma de objetos aparentemente inofensivos (como um urso de pelúcia,
    um computador antigo ou uma TV). Ao interagir ou se aproximar, distorce a percepção
    revelando anomalias estáticas e pupilas que acompanham o jogador.
    """
    def __init__(self, x, y, disguise="BEAR", name="MIMIC_ANOMALY"):
        super().__init__(x, y, 'TYPE_B', name, width=32, height=36)
        self.disguise = disguise  # 'BEAR', 'TV', 'CHAIR'
        self.revealed = False
        self.revealed_timer = 0.0

    def update(self, dt, player_rect, colliders=None):
        super().update(dt, player_rect, colliders)
        p_center = player_rect.center
        e_center = self.rect.center
        dist = math.hypot(p_center[0] - e_center[0], p_center[1] - e_center[1])

        if dist < 65:
            self.revealed = True
            self.revealed_timer += dt
        else:
            if self.revealed_timer > 0:
                self.revealed_timer = max(0.0, self.revealed_timer - dt)
            if self.revealed_timer <= 0:
                self.revealed = False

    def draw(self, surface, debug=False):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        if self.disguise == "BEAR":
            # Urso de pelúcia aparentemente fofo da infância / Fase II
            body_color = (138, 92, 60) if not self.revealed else (90, 70, 85)
            # Orelhas
            pygame.draw.circle(surf, body_color, (8, 9), 5)
            pygame.draw.circle(surf, body_color, (24, 9), 5)
            # Cabeça
            pygame.draw.circle(surf, body_color, (16, 15), 11)
            # Corpo
            pygame.draw.ellipse(surf, body_color, (7, 18, 18, 16))
            # Patas
            pygame.draw.ellipse(surf, (110, 70, 45), (4, 22, 6, 8))
            pygame.draw.ellipse(surf, (110, 70, 45), (22, 22, 6, 8))

            if not self.revealed:
                # Olhos normais de botão preto
                pygame.draw.circle(surf, (20, 20, 25), (13, 14), 2)
                pygame.draw.circle(surf, (20, 20, 25), (19, 14), 2)
                # Focinho
                pygame.draw.circle(surf, (210, 180, 140), (16, 18), 3)
                pygame.draw.circle(surf, (40, 20, 10), (16, 17), 1)
            else:
                # Efeito Mimic: Múltiplos olhos oníricos piscando/glitch
                for ex, ey in [(11, 13), (17, 12), (21, 15), (14, 19)]:
                    pygame.draw.circle(surf, (255, 40, 40), (ex, ey), 2)
                    pygame.draw.circle(surf, (255, 255, 255), (ex, ey), 1)
                # Linha de estática analógica
                if int(self.time * 20) % 2 == 0:
                    pygame.draw.line(surf, (200, 220, 255, 180), (2, 16), (30, 16), 1)
        else:
            # Disfarce genérico de objeto onírico
            pygame.draw.rect(surf, (90, 100, 115), (4, 4, 24, 28), border_radius=4)
            pygame.draw.rect(surf, (30, 35, 45), (8, 8, 16, 14))

        surface.blit(surf, (self.rect.x, self.rect.y))
        super().draw(surface, debug)


# ==============================================================================
# TYPE C: PREDATOR (Predador / O Professor)
# ==============================================================================
class Predator(Entity):
    """
    Entidade Type C: Predador.
    Entidade hostil patrulhadora que detecta o jogador e inicia perseguição direta.
    Possui comportamento de:
    - PATROL: Anda suavemente entre waypoints pré-definidos.
    - CHASE: Ao avistar o jogador, seus olhos mudam e sua velocidade aumenta.
    - COOLDOWN: Após alcançar o jogador ou perdê-lo de vista.
    """
    def __init__(self, x, y, waypoints=None, name="PREDATOR_PROFESSOR", speed=1.8, chase_speed=3.0):
        super().__init__(x, y, 'TYPE_C', name, width=36, height=54)
        self.state = 'PATROL'  # 'PATROL', 'CHASE', 'COOLDOWN'
        self.waypoints = waypoints if waypoints else [(x, y), (x + 120, y)]
        self.current_wp_idx = 0
        self.speed = speed
        self.chase_speed = chase_speed
        self.detection_range = 160.0
        self.lose_sight_range = 250.0
        self.cooldown_timer = 0.0

        # Rastro de distorção (glitch trail)
        self.trail = []
        self.max_trail = 4

    def update(self, dt, player_rect, colliders=None):
        super().update(dt, player_rect, colliders)

        # Posição do jogador
        p_center = player_rect.center
        e_center = self.rect.center
        dist_to_player = math.hypot(p_center[0] - e_center[0], p_center[1] - e_center[1])

        # Atualiza trilha de pós-imagem
        if int(self.time * 15) % 2 == 0:
            self.trail.append((self.rect.x, self.rect.y, self.alpha))
            if len(self.trail) > self.max_trail:
                self.trail.pop(0)

        # Lógica de Estados
        if self.state == 'COOLDOWN':
            self.cooldown_timer -= dt
            if self.cooldown_timer <= 0:
                self.state = 'PATROL'

        elif self.state == 'PATROL':
            # Checa se detectou o jogador
            if dist_to_player < self.detection_range:
                self.state = 'CHASE'
            else:
                # Movimenta em direção ao waypoint atual
                target = self.waypoints[self.current_wp_idx]
                dx = target[0] - self.x
                dy = target[1] - self.y
                dist_wp = math.hypot(dx, dy)

                if dist_wp < 6.0:
                    self.current_wp_idx = (self.current_wp_idx + 1) % len(self.waypoints)
                else:
                    move_dist = min(self.speed * 60.0 * dt, dist_wp)
                    self.x += (dx / dist_wp) * move_dist
                    self.y += (dy / dist_wp) * move_dist

        elif self.state == 'CHASE':
            # Persegue ativamente o jogador
            if dist_to_player > self.lose_sight_range:
                self.state = 'COOLDOWN'
                self.cooldown_timer = 2.0
            else:
                dx = p_center[0] - e_center[0]
                dy = p_center[1] - e_center[1]
                if dist_to_player > 0:
                    move_dist = self.chase_speed * 60.0 * dt
                    # Teste preliminar de colisão simples com o cenário se colliders estiver disponível
                    step_x = (dx / dist_to_player) * move_dist
                    step_y = (dy / dist_to_player) * move_dist
                    
                    self.x += step_x
                    self.y += step_y

    def trigger_contact(self):
        """Chamado quando alcança o protagonista com sucesso."""
        self.state = 'COOLDOWN'
        self.cooldown_timer = 3.5

    def draw(self, surface, debug=False):
        # Desenha rastro corrompido
        for tx, ty, t_alpha in self.trail:
            t_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            t_surf.fill((160, 20, 20, 35))
            surface.blit(t_surf, (tx, ty))

        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Aparência do GDD: "Type C: Predator (Professor)"
        # Sobretudo vinho / castanho-avermelhado e expressão perturbadora
        coat_color = (118, 42, 42) if self.state != 'CHASE' else (160, 28, 28)
        head_color = (195, 185, 180)

        # Cabelo grisalho
        pygame.draw.ellipse(surf, (85, 85, 95), (4, 3, 28, 20))
        # Rosto pálido
        pygame.draw.circle(surf, head_color, (18, 17), 11)

        # Expressão facial: Sorriso distorcido permanente do GDD
        pygame.draw.arc(surf, (30, 20, 20), (12, 16, 12, 8), 3.14, 0, 2)

        # Olhos
        if self.state == 'CHASE':
            # Estado Corrompido / Chase: múltiplos olhos vermelhos arregalados
            glitch_offset = random.randint(-1, 1)
            pygame.draw.circle(surf, (255, 30, 30), (13 + glitch_offset, 14), 3)
            pygame.draw.circle(surf, (255, 30, 30), (22 + glitch_offset, 14), 3)
            pygame.draw.circle(surf, (255, 255, 255), (13 + glitch_offset, 14), 1)
            pygame.draw.circle(surf, (255, 255, 255), (22 + glitch_offset, 14), 1)
            # Glitch visual na silhueta
            if random.random() < 0.25:
                pygame.draw.rect(surf, (220, 220, 220, 190), (0, random.randint(8, 40), self.width, 3))
        else:
            # Olhos escuros observadores
            pygame.draw.circle(surf, (40, 25, 25), (14, 14), 2)
            pygame.draw.circle(surf, (40, 25, 25), (22, 14), 2)

        # Sobretudo / Corpo
        pygame.draw.rect(surf, coat_color, (6, 24, 24, 22), border_radius=3)
        pygame.draw.rect(surf, (60, 20, 20), (16, 24, 4, 22))

        # Pernas
        pygame.draw.rect(surf, (40, 35, 45), (8, 46, 7, 8))
        pygame.draw.rect(surf, (40, 35, 45), (21, 46, 7, 8))

        # Alerta visual corporativo discreto se estiver perseguindo
        if self.state == 'CHASE':
            alert = self.font.render("! PERSEGUIÇÃO !", True, (255, 70, 70))
            surface.blit(alert, (self.rect.x + self.width//2 - alert.get_width()//2, self.rect.y - 14))

        surface.blit(surf, (self.rect.x, self.rect.y))
        super().draw(surface, debug)


# ==============================================================================
# TYPE Ø: THE OTHER (O Outro / Subject_004)
# ==============================================================================
class TheOther(Entity):
    """
    Entidade Secreta Type Ø: THE OTHER.
    GDD Seção 1.3: "DO NOT ATTEMPT CONTACT."
    Apresenta-se como uma duplicata espectral do próprio protagonista (mesmo pijama azul),
    mas com o rosto sombreado ou distorcido por estática e olhos vazios.
    Surge principalmente na Fase IV (THE NULL) e Fase V.
    """
    def __init__(self, x, y, name="THE_OTHER_SUBJECT_04"):
        super().__init__(x, y, 'TYPE_NULL', name, width=32, height=48)
        self.stalking = True
        self.mimic_dist = 110.0
        self.teleport_timer = 0.0

    def update(self, dt, player_rect, colliders=None):
        super().update(dt, player_rect, colliders)
        p_center = player_rect.center
        e_center = self.rect.center
        dist = math.hypot(p_center[0] - e_center[0], p_center[1] - e_center[1])

        # Segue a distância mantendo a separação onírica
        if dist > self.mimic_dist:
            dx = p_center[0] - e_center[0]
            dy = p_center[1] - e_center[1]
            speed = 2.2 * 60.0 * dt
            self.x += (dx / dist) * speed
            self.y += (dy / dist) * speed

        # Teletransporte aleatório caso chegue perto demais ou timer expire
        self.teleport_timer += dt
        if dist < 45 or self.teleport_timer > 12.0:
            self.teleport_timer = 0.0
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(120, 200)
            self.x = p_center[0] + math.cos(angle) * radius
            self.y = p_center[1] + math.sin(angle) * radius
            self.alpha = 255.0

    def draw(self, surface, debug=False):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # Pijama azul frio do protagonista, mas desaturado
        pj_color = (60, 95, 140)
        skin_color = (180, 190, 210)

        # Gorro azul
        pygame.draw.ellipse(surf, (40, 75, 120), (5, 4, 22, 16))
        # Rosto (quase sem feições)
        pygame.draw.circle(surf, skin_color, (16, 17), 9)

        # Olhos vazios / glitch de estática
        flicker = random.random() < 0.3
        if flicker:
            pygame.draw.circle(surf, (255, 255, 255), (13, 16), 2)
            pygame.draw.circle(surf, (255, 255, 255), (19, 16), 2)
        else:
            pygame.draw.circle(surf, (15, 20, 35), (13, 16), 2)
            pygame.draw.circle(surf, (15, 20, 35), (19, 16), 2)

        # Pijama
        pygame.draw.rect(surf, pj_color, (6, 22, 20, 18), border_radius=3)
        # Pernas
        pygame.draw.rect(surf, (30, 55, 90), (8, 40, 6, 8))
        pygame.draw.rect(surf, (30, 55, 90), (18, 40, 6, 8))

        # Efeito de duplicação translúcida
        surface.blit(surf, (self.rect.x, self.rect.y))
        super().draw(surface, debug)

