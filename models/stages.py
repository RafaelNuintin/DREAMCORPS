import pygame
import math
import random
from models.artifacts import Artifact

class Stage:
    """Classe base para cada uma das 5 fases da Dream Layer."""
    def __init__(self, stage_id, name, subtitle, screen_width=800, screen_height=600):
        self.stage_id = stage_id
        self.name = name
        self.subtitle = subtitle
        self.sw = screen_width
        self.sh = screen_height
        
        self.colliders = []
        self.artifacts = []
        self.exit_rect = None
        self.exit_open = False
        self.player_spawn = (100, 100)
        self.time = 0.0

        # Superfície pré-renderizada do cenário
        self.background = pygame.Surface((self.sw, self.sh))
        self.font = pygame.font.SysFont(["consolas", "couriernew"], 13, bold=True)
        self.banner_font = pygame.font.SysFont(["consolas", "couriernew"], 18, bold=True)

    def update(self, dt):
        self.time += dt
        for art in self.artifacts:
            art.update(dt)

        # A saída se abre assim que todos os artefatos da fase são coletados
        if not self.exit_open:
            if all(art.collected for art in self.artifacts):
                self.exit_open = True

    def check_exit(self, player_hitbox):
        """Retorna True se o jogador pisou na área de saída e ela está aberta."""
        if self.exit_open and self.exit_rect and player_hitbox.colliderect(self.exit_rect):
            return True
        return False

    def draw(self, surface, player_rect, debug=False):
        surface.blit(self.background, (0, 0))

        # Desenha a saída/portal
        if self.exit_rect:
            self._draw_exit(surface)

        # Desenha artefatos
        for art in self.artifacts:
            art.draw(surface, player_rect, self.font)

        # Debug colisores
        if debug:
            for c in self.colliders:
                pygame.draw.rect(surface, (255, 0, 0), c, 2)
            if self.exit_rect:
                pygame.draw.rect(surface, (0, 255, 255), self.exit_rect, 2)

    def _draw_exit(self, surface):
        """Renderiza visualmente o portal ou porta de saída."""
        pulse = (math.sin(self.time * 4.0) + 1) * 0.5
        rx, ry, rw, rh = self.exit_rect
        
        if self.exit_open:
            # Portal aberto brilhante
            glow_color = (100, 220, 255) if self.stage_id < 4 else (255, 120, 80)
            exit_surf = pygame.Surface((rw, rh), pygame.SRCALPHA)
            exit_surf.fill((*glow_color, int(140 + 80 * pulse)))
            surface.blit(exit_surf, (rx, ry))
            pygame.draw.rect(surface, (255, 255, 255), self.exit_rect, 2)

            hint = self.font.render("SAÍDA [ENTRAR]", True, (255, 255, 255))
            surface.blit(hint, (rx + rw//2 - hint.get_width()//2, ry - 18))
        else:
            # Porta trancada / bloqueada
            pygame.draw.rect(surface, (80, 40, 40), self.exit_rect)
            pygame.draw.rect(surface, (180, 60, 60), self.exit_rect, 2)
            hint = self.font.render("[BLOQUEADO]", True, (255, 100, 100))
            surface.blit(hint, (rx + rw//2 - hint.get_width()//2, ry - 18))


# ==============================================================================
# FASE I: THE BEDROOM (Memória Pessoal)
# ==============================================================================
class Stage1Bedroom(Stage):
    def __init__(self, sw=800, sh=600):
        super().__init__(1, "PHASE I: THE BEDROOM", "Memória Pessoal", sw, sh)
        
        # Carrega imagem base da fase 1
        try:
            raw_bg = pygame.image.load("assets/phase1.png").convert()
            self.background = pygame.transform.scale(raw_bg, (sw, sh))
        except Exception:
            self.background.fill((16, 20, 36))

        # Posição inicial no quarto
        self.player_spawn = (620, 180)

        # Artefato: Cápsula de DREAMSYNC™ na escrivaninha
        self.artifacts.append(
            Artifact(550, 200, "dreamsync_capsule", "CÁPSULA DREAMSYNC™", 
                     "Medicamento experimental indutor de sonho lúcido.")
        )

        # Saída: Corredor inferior esquerdo
        self.exit_rect = pygame.Rect(int(sw * 0.12), int(sh * 0.72), 70, 45)

        # Colisores principais (Paredes e móveis)
        self.colliders.append(pygame.Rect(0, 0, sw, int(sh * 0.14)))
        self.colliders.append(pygame.Rect(0, 0, int(sw * 0.05), sh))
        self.colliders.append(pygame.Rect(int(sw * 0.93), 0, int(sw * 0.05), sh))
        self.colliders.append(pygame.Rect(0, int(sh * 0.77), sw, int(sh * 0.08)))
        # Divisórias internas
        self.colliders.append(pygame.Rect(int(sw * 0.36), int(sh * 0.08), int(sw * 0.03), int(sh * 0.26)))
        self.colliders.append(pygame.Rect(int(sw * 0.61), int(sh * 0.08), int(sw * 0.03), int(sh * 0.26)))
        self.colliders.append(pygame.Rect(int(sw * 0.36), int(sh * 0.39), int(sw * 0.03), int(sh * 0.35)))
        self.colliders.append(pygame.Rect(int(sw * 0.61), int(sh * 0.39), int(sw * 0.03), int(sh * 0.35)))


# ==============================================================================
# FASE II: THE SCHOOL (Weirdcore & Memória Coletiva)
# ==============================================================================
class Stage2School(Stage):
    def __init__(self, sw=800, sh=600):
        super().__init__(2, "PHASE II: THE SCHOOL", "Infância e Memória Coletiva", sw, sh)
        self.player_spawn = (80, 300)
        self._build_scenery()

        # Artefato: Red ID Card no laboratório escolar
        self.artifacts.append(
            Artifact(680, 160, "red_id_card", "RED ID CARD", 
                     "Cartão de acesso corporativo esquecido em uma sala de aula.", color=(255, 80, 80))
        )

        # Saída: Porta vermelha / Elevador de serviço no canto inferior direito
        self.exit_rect = pygame.Rect(700, 480, 60, 50)

    def _build_scenery(self):
        # Chão: Azulejos quadriculados Weirdcore (rosa suave e creme)
        tile = 40
        c1 = (245, 215, 225)
        c2 = (235, 195, 210)
        for y in range(0, self.sh, tile):
            for x in range(0, self.sw, tile):
                color = c1 if ((x // tile) + (y // tile)) % 2 == 0 else c2
                pygame.draw.rect(self.background, color, (x, y, tile, tile))

        # Paredes do topo e laterais (corredor e salas)
        wall_color = (210, 225, 235)
        baseboard = (70, 120, 110)
        pygame.draw.rect(self.background, wall_color, (0, 0, self.sw, 120))
        pygame.draw.rect(self.background, baseboard, (0, 115, self.sw, 8))

        # Quadro Negro / Lousa com mensagem inquietante
        pygame.draw.rect(self.background, (35, 60, 45), (180, 25, 280, 75))
        pygame.draw.rect(self.background, (110, 75, 45), (180, 25, 280, 75), 4)
        chalk_font = pygame.font.SysFont(["consolas", "couriernew"], 16, bold=True)
        txt = chalk_font.render("SUBJECT_003: RETURNED", True, (240, 240, 240))
        self.background.blit(txt, (200, 50))

        # Desenhos infantis colados na parede (conforme GDD pág. 16)
        drawing_colors = [(255, 140, 140), (140, 200, 255), (255, 240, 140)]
        for idx, dx in enumerate([500, 560, 620]):
            pygame.draw.rect(self.background, (255, 255, 250), (dx, 35, 45, 55))
            pygame.draw.circle(self.background, drawing_colors[idx], (dx + 22, 55), 12)
            pygame.draw.line(self.background, (80, 80, 80), (dx + 22, 67), (dx + 22, 80), 2)

        # Armários escolares (Lockers amarelos nostálgicos)
        for lx in range(480, 750, 45):
            pygame.draw.rect(self.background, (240, 185, 65), (lx, 140, 40, 80))
            pygame.draw.rect(self.background, (180, 130, 40), (lx, 140, 40, 80), 2)
            pygame.draw.rect(self.background, (80, 80, 80), (lx + 8, 175, 6, 12))

        # Fileiras de Carteiras Escolares
        for row in range(3):
            for col in range(4):
                dx = 160 + col * 110
                dy = 220 + row * 100
                # Mesa de madeira
                pygame.draw.rect(self.background, (190, 135, 80), (dx, dy, 50, 32), border_radius=3)
                pygame.draw.rect(self.background, (130, 90, 50), (dx, dy, 50, 32), 1, border_radius=3)
                # Cadeira azul
                pygame.draw.rect(self.background, (70, 110, 170), (dx + 12, dy + 36, 26, 18), border_radius=2)
                # Colisor na mesa
                self.colliders.append(pygame.Rect(dx, dy, 50, 45))

        # Colisões perimetrais
        self.colliders.append(pygame.Rect(0, 0, self.sw, 120))
        self.colliders.append(pygame.Rect(0, 0, 25, self.sh))
        self.colliders.append(pygame.Rect(self.sw - 25, 0, 25, self.sh))
        self.colliders.append(pygame.Rect(0, self.sh - 30, self.sw, 30))
        # Colisão nos lockers
        self.colliders.append(pygame.Rect(480, 140, 270, 80))


# ==============================================================================
# FASE III: THE OFFICE (Analog Horror Corporativo & Frutiger Aero)
# ==============================================================================
class Stage3Office(Stage):
    def __init__(self, sw=800, sh=600):
        super().__init__(3, "PHASE III: THE OFFICE", "Controle Corporativo", sw, sh)
        self.player_spawn = (100, 480)
        self._build_scenery()

        # Artefato: Employee Access Key no terminal de servidores
        self.artifacts.append(
            Artifact(400, 160, "employee_key", "EMPLOYEE ACCESS KEY", 
                     "Chave de segurança com o logotipo da Dreamcorps™.", color=(255, 215, 60))
        )

        # Saída: Porta restrita de alta segurança
        self.exit_rect = pygame.Rect(720, 260, 50, 65)

    def _build_scenery(self):
        # Chão: Azulejo Frutiger Aero / Carpete Corporativo Azul Petróleo
        for y in range(0, self.sh, 32):
            for x in range(0, self.sw, 32):
                col = (20, 32, 54) if ((x // 32) + (y // 32)) % 2 == 0 else (24, 38, 64)
                pygame.draw.rect(self.background, col, (x, y, 32, 32))

        # Parede superior corporativa
        pygame.draw.rect(self.background, (180, 195, 210), (0, 0, self.sw, 110))
        # Faixa corporativa Dreamcorps (azul e laranja)
        pygame.draw.rect(self.background, (35, 65, 120), (0, 104, self.sw, 6))
        pygame.draw.rect(self.background, (255, 110, 40), (0, 110, self.sw, 3))

        # Logo da Lua Crescente Corporativa na parede
        logo_font = pygame.font.SysFont(["consolas", "couriernew"], 22, bold=True)
        txt = logo_font.render("DREAMCORPS.™ // RESEARCH LAB", True, (25, 45, 80))
        self.background.blit(txt, (40, 35))
        slogan_font = pygame.font.SysFont(["georgia", "timesnewroman"], 12, italic=True)
        slogan = slogan_font.render("“Your dreams. Better than reality.”", True, (190, 70, 30))
        self.background.blit(slogan, (42, 65))

        # Servidores pretos no topo com luzes de monitoramento
        for sx in range(320, 560, 50):
            pygame.draw.rect(self.background, (20, 22, 28), (sx, 125, 42, 70), border_radius=2)
            pygame.draw.rect(self.background, (60, 65, 75), (sx, 125, 42, 70), 1, border_radius=2)
            # LEDs
            pygame.draw.circle(self.background, (80, 255, 120), (sx + 10, 140), 3)
            pygame.draw.circle(self.background, (255, 80, 80), (sx + 20, 140), 3)
            pygame.draw.circle(self.background, (80, 180, 255), (sx + 30, 140), 3)
            self.colliders.append(pygame.Rect(sx, 125, 42, 70))

        # Cubículos com computadores CRT e divisórias de vidro acrílico
        for cx in [120, 340, 560]:
            for cy in [260, 400]:
                # Divisória azul translúcida
                pygame.draw.rect(self.background, (45, 80, 130), (cx, cy, 140, 70), border_radius=3)
                pygame.draw.rect(self.background, (70, 130, 200), (cx, cy, 140, 70), 2, border_radius=3)
                # Mesa interna
                pygame.draw.rect(self.background, (160, 175, 190), (cx + 10, cy + 15, 120, 45))
                # Monitor CRT (tela verde corporativa)
                pygame.draw.rect(self.background, (40, 45, 55), (cx + 25, cy + 20, 35, 25))
                pygame.draw.rect(self.background, (50, 220, 120), (cx + 28, cy + 23, 29, 19))
                # Teclado
                pygame.draw.rect(self.background, (210, 215, 220), (cx + 70, cy + 28, 40, 15))

                self.colliders.append(pygame.Rect(cx, cy, 140, 70))

        # Câmeras de segurança nos cantos
        pygame.draw.rect(self.background, (30, 35, 45), (740, 120, 25, 16))
        pygame.draw.circle(self.background, (255, 50, 50), (745, 128), 3)

        # Colisões perimetrais
        self.colliders.append(pygame.Rect(0, 0, self.sw, 115))
        self.colliders.append(pygame.Rect(0, 0, 25, self.sh))
        self.colliders.append(pygame.Rect(self.sw - 25, 0, 25, self.sh))
        self.colliders.append(pygame.Rect(0, self.sh - 30, self.sw, 30))


# ==============================================================================
# FASE IV: THE NULL (Identidade e Corrupção / Surrealismo)
# ==============================================================================
class Stage4Null(Stage):
    def __init__(self, sw=800, sh=600):
        super().__init__(4, "PHASE IV: THE NULL", "Identidade e Corrupção", sw, sh)
        self.player_spawn = (120, 300)
        self._build_scenery()

        # Artefato: Dossiê confidencial SUBJECT_03
        self.artifacts.append(
            Artifact(400, 280, "subject_03_file", "DOSSIÊ SUBJECT_03", 
                     "Arquivo restrito contendo o verdadeiro propósito do experimento.", color=(255, 100, 120))
        )

        # Saída: O Espelho / Portal Dimensional para a Realidade
        self.exit_rect = pygame.Rect(690, 270, 50, 70)

    def _build_scenery(self):
        # Fundo do Vazio Negro Estrelado
        self.background.fill((5, 6, 14))

        # Estrelas e ruído estático de fundo
        for _ in range(80):
            sx = random.randint(0, self.sw)
            sy = random.randint(0, self.sh)
            rad = random.choice([1, 2])
            col = random.choice([(140, 160, 220), (220, 120, 255), (100, 240, 255)])
            pygame.draw.circle(self.background, col, (sx, sy), rad)

        # Lua gigante distorcida ao fundo (conforme arte da página 19)
        moon_center = (400, 180)
        pygame.draw.circle(self.background, (255, 235, 140), moon_center, 90)
        pygame.draw.circle(self.background, (5, 6, 14), (435, 160), 85)

        # Ilhas Flutuantes (Fragmentos de fases anteriores)
        # Plataforma 1 (Spawn do Jogador)
        self._draw_floating_island(80, 240, 160, 140, floor_type='wood')
        # Plataforma Central (Artefato)
        self._draw_floating_island(310, 210, 200, 170, floor_type='office')
        # Plataforma da Saída (Espelho)
        self._draw_floating_island(630, 220, 140, 150, floor_type='school')

        # Pontes e fragmentos de ligação
        self._draw_floating_island(240, 280, 70, 60, floor_type='wood')
        self._draw_floating_island(510, 270, 120, 60, floor_type='office')

        # Portas e janelas desconexas flutuando no vazio (Weirdcore/Dreamcore)
        self._draw_floating_door(200, 130)
        self._draw_floating_door(580, 120)

        # Paredes invisíveis que impedem o jogador de cair no abismo negro
        self._setup_null_colliders()

    def _draw_floating_island(self, x, y, w, h, floor_type='wood'):
        # Sombra da plataforma
        pygame.draw.rect(self.background, (15, 18, 32), (x - 4, y + h, w + 8, 14), border_radius=4)
        
        # Superfície da ilha
        if floor_type == 'wood':
            pygame.draw.rect(self.background, (150, 100, 60), (x, y, w, h))
            for ly in range(y, y + h, 18):
                pygame.draw.line(self.background, (110, 70, 40), (x, ly), (x + w, ly), 1)
        elif floor_type == 'office':
            pygame.draw.rect(self.background, (28, 48, 80), (x, y, w, h))
            pygame.draw.rect(self.background, (60, 110, 180), (x, y, w, h), 2)
        elif floor_type == 'school':
            pygame.draw.rect(self.background, (230, 180, 200), (x, y, w, h))
            pygame.draw.rect(self.background, (180, 120, 150), (x, y, w, h), 2)

    def _draw_floating_door(self, x, y):
        # Porta solta flutuando no espaço
        pygame.draw.rect(self.background, (120, 75, 45), (x, y, 36, 60))
        pygame.draw.rect(self.background, (200, 140, 80), (x, y, 36, 60), 2)
        pygame.draw.circle(self.background, (255, 215, 60), (x + 28, y + 32), 3)

    def _setup_null_colliders(self):
        # Os caminhos navegáveis são as ilhas e pontes:
        # Colisões para impedir saída das plataformas para o vazio
        # Topo e base da ilha 1
        self.colliders.append(pygame.Rect(0, 0, self.sw, 200))
        self.colliders.append(pygame.Rect(0, 420, self.sw, 180))
        self.colliders.append(pygame.Rect(0, 0, 70, self.sh))
        self.colliders.append(pygame.Rect(self.sw - 30, 0, 30, self.sh))
        # Abismos entre plataformas
        self.colliders.append(pygame.Rect(230, 200, 80, 70))
        self.colliders.append(pygame.Rect(230, 350, 80, 70))
        self.colliders.append(pygame.Rect(510, 200, 120, 60))
        self.colliders.append(pygame.Rect(510, 340, 120, 80))


# ==============================================================================
# FASE V: REALITY (Realidade e Ambiguidade)
# ==============================================================================
class Stage5Reality(Stage):
    def __init__(self, sw=800, sh=600):
        super().__init__(5, "PHASE V: REALITY", "Normalidade Artificial", sw, sh)
        self.player_spawn = (620, 180)
        self._build_scenery()

        # Interação Final: A Segunda Cápsula / Âncora de Realidade
        self.artifacts.append(
            Artifact(550, 200, "reality_anchor", "SEGUNDA CÁPSULA DREAMSYNC™", 
                     "Uma nova cápsula idêntica aguarda sobre a escrivaninha.", color=(100, 240, 255), prompt="[E] Acordar / Integrar")
        )

        # Não há saída tradicional; coletar a cápsula encerra a sessão com sucesso!
        self.exit_rect = None

        # Mesmos colisores do quarto
        self.colliders.append(pygame.Rect(0, 0, sw, int(sh * 0.14)))
        self.colliders.append(pygame.Rect(0, 0, int(sw * 0.05), sh))
        self.colliders.append(pygame.Rect(int(sw * 0.93), 0, int(sw * 0.05), sh))
        self.colliders.append(pygame.Rect(0, int(sh * 0.77), sw, int(sh * 0.08)))
        self.colliders.append(pygame.Rect(int(sw * 0.36), int(sh * 0.08), int(sw * 0.03), int(sh * 0.26)))
        self.colliders.append(pygame.Rect(int(sw * 0.61), int(sh * 0.08), int(sw * 0.03), int(sh * 0.26)))

    def _build_scenery(self):
        # Carrega o quarto original, mas dessatura as cores para dar sensação de ambiguidade
        try:
            raw_bg = pygame.image.load("assets/phase1.png").convert()
            scaled = pygame.transform.scale(raw_bg, (self.sw, self.sh))
            # Aplica camada cinzenta/fria
            tint = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
            tint.fill((20, 30, 50, 90)) # Tom dessaturado frio
            scaled.blit(tint, (0, 0))
            self.background = scaled
        except Exception:
            self.background.fill((20, 24, 34))

        # TV ligada na sala com a propaganda perturbadora da Dreamcorps™
        # Conforme GDD pág. 21: "Your reality. Better than dreams."
        tv_rect = pygame.Rect(480, 245, 90, 60)
        pygame.draw.rect(self.background, (30, 30, 40), tv_rect)
        pygame.draw.rect(self.background, (180, 240, 255), (tv_rect.x + 6, tv_rect.y + 6, tv_rect.w - 12, tv_rect.h - 12))
        tv_font = pygame.font.SysFont(["consolas", "couriernew"], 8, bold=True)
        t1 = tv_font.render("DREAMSYNC", True, (20, 20, 30))
        t2 = tv_font.render("YOUR REALITY.", True, (190, 40, 40))
        self.background.blit(t1, (tv_rect.x + 12, tv_rect.y + 14))
        self.background.blit(t2, (tv_rect.x + 8, tv_rect.y + 28))
