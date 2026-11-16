import pygame
import random
import math

class CorruptionManager:
    """
    Gerenciador Central do Dream Stability Index (DSI) e Layer Corruption.
    Implementa as regras das Seções 4.3.4, 4.3.5, 4.3.6 e 4.6 do GDD:
    
    Estágios de Corrupção:
      - 0% a 20%: Stable (Ambiente normal e estável)
      - 21% a 40%: Unstable (Pequenas anomalias e ruídos sutis)
      - 41% a 70%: Distorted (Alterações visuais significativas, scanlines e fatiamento VHS)
      - 71% a 90%: Critical (Aumento de glitches e pulsação em vermelho corporativo)
      - 91% a 100%: Collapse (Colapso total da Dream Layer)
    """

    def __init__(self, initial_dsi=10000, initial_corruption=0):
        self.dsi = initial_dsi
        self.corruption = float(initial_corruption) # 0.0 a 100.0%
        
        # Estatísticas acumuladas para envio ao Django Backend
        self.anomaly_exposures = 0
        self.entity_encounters = 0
        self.collapse_count = 0

        # Efeitos de choque e impacto pós-contato
        self.shock_timer = 0.0      # Duração do flash/glitch intenso
        self.shock_duration = 0.6
        self.shake_offset = [0, 0]

        # Superfícies auxiliares para renderização de efeitos VHS / Scanlines
        self.scanline_surf = None
        self.noise_cache = []
        self._init_fx_surfaces()

    def _init_fx_surfaces(self):
        """Pré-cria superfícies de scanlines e texturas de estática analógica."""
        sw, sh = 800, 600
        self.scanline_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
        # Linhas horizontais semi-transparentes a cada 3 pixels
        for y in range(0, sh, 3):
            pygame.draw.line(self.scanline_surf, (0, 0, 0, 45), (0, y), (sw, y), 1)

    def get_state_label(self):
        """Retorna o rótulo do estado de acordo com a Seção 4.3.5 do GDD."""
        if self.corruption <= 20.0:
            return "STABLE"
        elif self.corruption <= 40.0:
            return "UNSTABLE"
        elif self.corruption <= 70.0:
            return "DISTORTED"
        elif self.corruption <= 90.0:
            return "CRITICAL"
        else:
            return "COLLAPSE"

    def add_dsi(self, amount):
        """Bonifica pontuação DSI (ex: coleta de artefatos ou descoberta de documentos)."""
        self.dsi += amount

    def drain_dsi(self, amount):
        """Penaliza pontuação DSI garantindo não ultrapassar valores negativos absurdos."""
        self.dsi = max(0, self.dsi - amount)

    def increase_corruption(self, amount):
        """Aumenta a corrupção da Dream Layer limitando entre 0% e 100%."""
        self.corruption = min(100.0, self.corruption + amount)

    def reduce_corruption(self, amount):
        """Reduz a corrupção (ex: ao restaurar estabilidade ou passar de fase)."""
        self.corruption = max(0.0, self.corruption - amount)

    def trigger_predator_contact(self):
        """
        GDD Seção 4.3.6:
        Contato com entidade Type C não mata instantaneamente. Provoca:
        - Redução do DSI (-1.250)
        - Aumento da corrupção (+18%)
        - Distorção audiovisual imediata (shock timer)
        - Incremento de encontros com anomalias
        """
        self.drain_dsi(1250)
        self.increase_corruption(18.0)
        self.entity_encounters += 1
        self.anomaly_exposures += 1
        self.shock_timer = self.shock_duration

    def update(self, dt):
        """Atualização de timers e comportamento passivo de corrupção."""
        # Se a corrupção estiver acima de 70%, o DSI sofre leve degradação contínua
        if self.corruption >= 70.0:
            self.drain_dsi(int(15 * dt))
        elif self.corruption >= 40.0:
            self.drain_dsi(int(4 * dt))

        # Atualiza timer do choque de contato
        if self.shock_timer > 0:
            self.shock_timer -= dt
            self.shake_offset[0] = random.randint(-6, 6)
            self.shake_offset[1] = random.randint(-4, 4)
        else:
            self.shake_offset[0] = 0
            self.shake_offset[1] = 0

    def check_collapse(self):
        """
        GDD Seção 4.6 (Losing - Condição 2: Colapso da Dream Layer):
        Retorna True caso a instabilidade/corrupção atinja 100%.
        Desencadeia o estado de GAME OVER e encerramento da tentativa de conexão.
        """
        return self.corruption >= 100.0

    def reset(self, initial_dsi=10000, initial_corruption=0):
        """Reinicia os parâmetros de corrupção e estabilidade para uma nova tentativa."""
        self.dsi = initial_dsi
        self.corruption = float(initial_corruption)
        self.anomaly_exposures = 0
        self.entity_encounters = 0
        self.collapse_count = 0
        self.shock_timer = 0.0
        self.shake_offset = [0, 0]

    def render_effects(self, surface):
        """
        Renderiza filtros e aberrações visuais analógicas condizentes com o nível de corrupção.
        """
        sw, sh = surface.get_size()
        state = self.get_state_label()

        # 1. Efeito de Choque / Glitch Intenso de Contato (Type C)
        if self.shock_timer > 0:
            shock_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            # Flash vermelho escuro com estática
            shock_alpha = int(120 * (self.shock_timer / self.shock_duration))
            shock_surf.fill((180, 20, 20, shock_alpha))
            surface.blit(shock_surf, (0, 0))

            # Fatias desalinhadas horizontais
            for _ in range(5):
                slice_y = random.randint(0, sh - 30)
                slice_h = random.randint(10, 30)
                offset_x = random.randint(-25, 25)
                slice_rect = pygame.Rect(0, slice_y, sw, slice_h)
                try:
                    sub = surface.subsurface(slice_rect).copy()
                    surface.blit(sub, (offset_x, slice_y))
                except Exception:
                    pass

        # 2. Renderização de Scanlines analógicas (presente a partir de UNSTABLE)
        if self.corruption > 20.0 and self.scanline_surf:
            surface.blit(self.scanline_surf, (0, 0))

        # 3. Efeitos de DISTORTED (41% a 70%)
        if self.corruption >= 41.0:
            # Glitch analógico esporádico (ruído branco sutil)
            if random.random() < 0.25:
                glitch_y = random.randint(0, sh - 10)
                pygame.draw.line(
                    surface,
                    (200, 220, 255),
                    (random.randint(0, 100), glitch_y),
                    (random.randint(sw - 150, sw), glitch_y),
                    random.randint(1, 2)
                )

        # 4. Efeitos de CRITICAL (71% a 90%)
        if self.corruption >= 71.0:
            # Tonalidade avermelhada opressiva no ambiente
            crit_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
            pulse = (math.sin(pygame.time.get_ticks() * 0.006) + 1.0) * 0.5
            crit_alpha = int(25 + 30 * pulse)
            crit_surf.fill((160, 30, 45, crit_alpha))
            surface.blit(crit_surf, (0, 0))

            # Blocos pretos de 'Void & Glitches' (conforme tiles do GDD)
            if random.random() < 0.35:
                bx = random.randint(50, sw - 120)
                by = random.randint(50, sh - 100)
                pygame.draw.rect(surface, (10, 10, 20), (bx, by, random.randint(20, 60), random.randint(6, 16)))

