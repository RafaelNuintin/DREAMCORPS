import pygame
import math
import random

class Menu:
    def __init__(self, screen_width, screen_height):
        self.sw = screen_width
        self.sh = screen_height
        
        # Fontes do sistema estilizadas com fallbacks
        self.title_font = pygame.font.SysFont(["consolas", "lucidaconsole", "couriernew", "arial"], 46, bold=True)
        self.subtitle_font = pygame.font.SysFont(["georgia", "timesnewroman", "arial"], 17, italic=True)
        self.ui_font = pygame.font.SysFont(["consolas", "lucidaconsole", "couriernew"], 20, bold=True)
        self.small_font = pygame.font.SysFont(["consolas", "lucidaconsole", "couriernew"], 13)
        self.doc_font = pygame.font.SysFont(["consolas", "couriernew"], 15)

        # Itens do Menu
        self.options = [
            "ACESSAR DREAM LAYER",
            "REGISTROS CONFIDENCIAIS",
            "ENCERRAR PROTOCOLO"
        ]
        self.selected_index = 0

        # Estados internos do menu
        # 'MAIN', 'RECORDS', 'TRANSITION'
        self.state = 'MAIN'

        # Efeitos de animação e tempo
        self.time = 0.0
        self.glitch_timer = 0
        self.glitch_offset_x = 0
        self.glitch_offset_y = 0

        # Partículas oníricas flutuantes (estrelas/poeira de sonho)
        self.particles = []
        for _ in range(45):
            self.particles.append({
                'x': random.uniform(0, self.sw),
                'y': random.uniform(0, self.sh),
                'speed': random.uniform(0.3, 1.2),
                'radius': random.uniform(1.0, 2.8),
                'alpha': random.uniform(80, 220),
                'phase': random.uniform(0, math.pi * 2)
            })

        # Texturas pré-renderizadas
        self.moon_surface = self._generate_crescent_moon(radius=55)
        self.scanline_surface = self._generate_scanlines()

        # Controle da Transição para o Jogo
        self.transition_timer = 0.0
        self.transition_duration = 3.8 # segundos
        self.transition_done = False
        self.transition_lines = [
            "ADMINISTRANDO CÁPSULA DREAMSYNC™ [COMPOSTO LS-01]...",
            "SINCRONIZANDO ONDAS CEREBRAIS [FASE DELTA ESTÁVEL]...",
            "SUBJECT_003: CONEXÃO COM DREAM LAYER ESTABELECIDA.",
            "ENTRANDO EM // FASE I: THE BEDROOM..."
        ]

        # Efeito de Fade In inicial ao abrir o menu
        self.fade_alpha = 255.0

    def _generate_crescent_moon(self, radius):
        """Gera a Lua Crescente característica da Dreamcorps™ com gradiente quente."""
        size = radius * 2 + 20
        moon_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (size // 2, size // 2)

        # Desenha a lua com gradiente vertical (amarelo dourado -> laranja -> vermelho)
        for y in range(-radius, radius + 1):
            dy = abs(y)
            if dy <= radius:
                dx = int(math.sqrt(radius * radius - dy * dy))
                # Fator de interpolação de cor (0.0 no topo, 1.0 na base)
                t = (y + radius) / (2 * radius)
                if t < 0.5:
                    sub_t = t * 2
                    r = int(255)
                    g = int(220 * (1 - sub_t) + 120 * sub_t)
                    b = int(60 * (1 - sub_t) + 20 * sub_t)
                else:
                    sub_t = (t - 0.5) * 2
                    r = int(255 * (1 - sub_t) + 215 * sub_t)
                    g = int(120 * (1 - sub_t) + 35 * sub_t)
                    b = int(20 * (1 - sub_t) + 40 * sub_t)

                pygame.draw.line(moon_surf, (r, g, b, 250), 
                                 (center[0] - dx, center[1] + y), 
                                 (center[0] + dx, center[1] + y))

        # Cria a máscara para formar a foice da lua crescente
        cut_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cut_offset_x = int(radius * 0.45)
        cut_offset_y = -int(radius * 0.15)
        cut_radius = int(radius * 0.92)
        pygame.draw.circle(cut_surf, (0, 0, 0, 255), 
                           (center[0] + cut_offset_x, center[1] + cut_offset_y), 
                           cut_radius)

        # Subtrai o círculo usando BLEND_RGBA_SUB
        moon_surf.blit(cut_surf, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        return moon_surf

    def _generate_scanlines(self):
        """Cria textura de linhas de varredura CRT para estética analógica."""
        surf = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        for y in range(0, self.sh, 4):
            pygame.draw.line(surf, (0, 0, 0, 45), (0, y), (self.sw, y), 1)
        return surf

    def handle_event(self, event):
        """Gerencia entradas do usuário (Teclado e Mouse)."""
        if self.state == 'MAIN':
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                    self._activate_option(self.selected_index)

            elif event.type == pygame.MOUSEMOTION:
                # Hover nas opções
                mx, my = event.pos
                base_y = self.sh * 0.58
                spacing = 46
                for i in range(len(self.options)):
                    opt_rect = pygame.Rect(self.sw // 2 - 180, int(base_y + i * spacing) - 8, 360, 36)
                    if opt_rect.collidepoint(mx, my):
                        self.selected_index = i

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                base_y = self.sh * 0.58
                spacing = 46
                for i in range(len(self.options)):
                    opt_rect = pygame.Rect(self.sw // 2 - 180, int(base_y + i * spacing) - 8, 360, 36)
                    if opt_rect.collidepoint(mx, my):
                        self._activate_option(i)

        elif self.state == 'RECORDS':
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                # Qualquer tecla ou clique volta ao menu principal
                self.state = 'MAIN'

        elif self.state == 'TRANSITION':
            # Permite avançar imediatamente caso o jogador aperte espaço/enter
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                self.transition_timer = max(self.transition_timer, self.transition_duration - 0.5)

    def _activate_option(self, index):
        if index == 0:
            # ACESSAR DREAM LAYER (Inicia transição gradual)
            self.state = 'TRANSITION'
            self.transition_timer = 0.0
        elif index == 1:
            # REGISTROS CONFIDENCIAIS
            self.state = 'RECORDS'
        elif index == 2:
            # SAIR
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, dt=0.016):
        """Atualiza animações, timers e partículas."""
        self.time += dt

        # Redução do Fade In inicial
        if self.fade_alpha > 0:
            self.fade_alpha = max(0.0, self.fade_alpha - 200 * dt)

        # Atualiza partículas
        for p in self.particles:
            p['y'] -= p['speed']
            p['x'] += math.sin(self.time + p['phase']) * 0.4
            if p['y'] < -10:
                p['y'] = self.sh + 10
                p['x'] = random.uniform(0, self.sw)

        # Efeito de Glitch ocasional (Analog Horror)
        self.glitch_timer += dt
        if self.glitch_timer > 3.5:
            if random.random() < 0.25:
                self.glitch_offset_x = random.randint(-4, 4)
                self.glitch_offset_y = random.randint(-2, 2)
            else:
                self.glitch_offset_x = 0
                self.glitch_offset_y = 0
            if self.glitch_timer > 3.75:
                self.glitch_timer = 0
                self.glitch_offset_x = 0
                self.glitch_offset_y = 0

        # Lógica de Transição para o Jogo
        if self.state == 'TRANSITION':
            self.transition_timer += dt
            if self.transition_timer >= self.transition_duration:
                self.transition_done = True

    def draw(self, surface):
        """Renderiza todo o menu ou telas de estado."""
        # Fundo: Gradiente Onírico Noturno (Vaporwave/Dreamcore profundo)
        self._draw_background(surface)

        # Partículas Oníricas
        self._draw_particles(surface)

        if self.state == 'MAIN':
            self._draw_main_menu(surface)
        elif self.state == 'RECORDS':
            self._draw_records(surface)
        elif self.state == 'TRANSITION':
            self._draw_transition(surface)

        # Overlay analógico CRT scanlines
        surface.blit(self.scanline_surface, (0, 0))

        # Fade in inicial ou geral
        if self.fade_alpha > 0:
            fade_surf = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
            fade_surf.fill((10, 12, 24, int(self.fade_alpha)))
            surface.blit(fade_surf, (0, 0))

    def _draw_background(self, surface):
        """Desenha gradiente suave de azul petróleo escuro a roxo profundo."""
        top_color = (9, 11, 24)       # Deep space navy
        mid_color = (20, 20, 48)      # Corporate night purple
        bottom_color = (13, 26, 46)   # Lunar teal shadow

        # Renderização rápida de gradiente em 3 faixas
        h = self.sh
        half_h = h // 2
        for y in range(0, half_h, 2):
            t = y / half_h
            r = int(top_color[0] * (1 - t) + mid_color[0] * t)
            g = int(top_color[1] * (1 - t) + mid_color[1] * t)
            b = int(top_color[2] * (1 - t) + mid_color[2] * t)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.sw, y), 2)

        for y in range(half_h, h, 2):
            t = (y - half_h) / half_h
            r = int(mid_color[0] * (1 - t) + bottom_color[0] * t)
            g = int(mid_color[1] * (1 - t) + bottom_color[1] * t)
            b = int(mid_color[2] * (1 - t) + bottom_color[2] * t)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.sw, y), 2)

    def _draw_particles(self, surface):
        """Desenha poeira luminosa flutuante."""
        p_surf = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        for p in self.particles:
            pulse = (math.sin(self.time * 2.5 + p['phase']) + 1) * 0.5
            curr_alpha = int(p['alpha'] * (0.6 + 0.4 * pulse))
            # Partículas ligeiramente douradas e azuladas
            color = (200, 225, 255, curr_alpha) if p['phase'] > 3.0 else (255, 230, 160, curr_alpha)
            pygame.draw.circle(p_surf, color, (int(p['x']), int(p['y'])), p['radius'])
        surface.blit(p_surf, (0, 0))

    def _draw_main_menu(self, surface):
        """Renderiza a interface principal do menu."""
        # Moldura de Terminal Corporativo
        self._draw_terminal_frame(surface)

        # Centro do Logo: Lua Crescente + Título
        moon_center_x = self.sw // 2
        moon_center_y = int(self.sh * 0.22) + int(math.sin(self.time * 1.5) * 4)

        # Pulsação de brilho suave atrás da Lua
        glow_size = int(80 + math.sin(self.time * 2) * 6)
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 160, 50, 22), (glow_size, glow_size), glow_size)
        surface.blit(glow_surf, (moon_center_x - glow_size, moon_center_y - glow_size))

        # Desenha a Lua Crescente
        moon_rect = self.moon_surface.get_rect(center=(moon_center_x, moon_center_y))
        surface.blit(self.moon_surface, moon_rect)

        # Título: DREAMCORPS.™ com sombra e aberração cromática leve
        title_y = int(self.sh * 0.35)
        title_text = "DREAMCORPS.™"

        gx, gy = self.glitch_offset_x, self.glitch_offset_y

        # Sombra cromática roxa / azul
        shadow_surf = self.title_font.render(title_text, True, (60, 110, 180))
        surface.blit(shadow_surf, (self.sw // 2 - shadow_surf.get_width() // 2 + 2 + gx, title_y + 2 + gy))

        # Texto frontal
        title_surf = self.title_font.render(title_text, True, (245, 248, 255))
        surface.blit(title_surf, (self.sw // 2 - title_surf.get_width() // 2 + gx, title_y + gy))

        # Slogan oficial da Dreamcorps™
        slogan_text = "“Your dreams. Better than reality.”"
        slogan_surf = self.subtitle_font.render(slogan_text, True, (255, 205, 120))
        surface.blit(slogan_surf, (self.sw // 2 - slogan_surf.get_width() // 2, title_y + 48))

        # Divisor estético sutil
        line_w = 260
        line_y = title_y + 80
        pygame.draw.line(surface, (100, 140, 190), (self.sw // 2 - line_w // 2, line_y), (self.sw // 2 + line_w // 2, line_y), 1)

        # Opções do Menu
        base_y = self.sh * 0.58
        spacing = 46

        for i, option in enumerate(self.options):
            is_selected = (i == self.selected_index)
            y_pos = int(base_y + i * spacing)

            if is_selected:
                # Efeito de destaque pulsante no item selecionado
                pulse = (math.sin(self.time * 5.0) + 1) * 0.5
                btn_color = (255, 225, 120)
                box_bg = (30, 45, 80, 160)
                
                # Fundo do botão selecionado
                box_rect = pygame.Rect(self.sw // 2 - 170, y_pos - 6, 340, 34)
                box_surf = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
                box_surf.fill(box_bg)
                surface.blit(box_surf, box_rect.topleft)
                pygame.draw.rect(surface, (255, 180, 80, int(150 + 100 * pulse)), box_rect, 1)

                # Cursor de terminal estilo prompt ">"
                cursor_text = "> "
                label = f">  {option}  <"
            else:
                btn_color = (160, 180, 210)
                label = option

            text_surf = self.ui_font.render(label, True, btn_color)
            surface.blit(text_surf, (self.sw // 2 - text_surf.get_width() // 2, y_pos))

        # Dica de controles no rodapé
        hint_text = "[W/S ou Setas] Navegar   [Enter / E] Confirmar"
        hint_surf = self.small_font.render(hint_text, True, (110, 135, 165))
        surface.blit(hint_surf, (self.sw // 2 - hint_surf.get_width() // 2, self.sh - 38))

    def _draw_terminal_frame(self, surface):
        """Bordas e informações do sistema operacional corporativo."""
        # Header superior
        top_header = "DREAMCORPS™ NEURO-LINK TERMINAL  //  PROJETO SOMNUS"
        header_surf = self.small_font.render(top_header, True, (130, 165, 205))
        surface.blit(header_surf, (28, 18))

        # Status no canto superior direito
        status_text = "[ SYS: ONLINE ]  [ DSI: 100% ]"
        status_surf = self.small_font.render(status_text, True, (100, 220, 140))
        surface.blit(status_surf, (self.sw - status_surf.get_width() - 28, 18))

        # Linha horizontal delimitadora superior
        pygame.draw.line(surface, (40, 65, 100), (24, 38), (self.sw - 24, 38), 1)

        # Rodapé corporativo
        footer_id = "SUBJECT_003 // DURATION: 00:00:00 // DREAM LAYER v1.0"
        footer_surf = self.small_font.render(footer_id, True, (90, 120, 155))
        surface.blit(footer_surf, (28, self.sh - 22))

        # Linha horizontal delimitadora inferior
        pygame.draw.line(surface, (40, 65, 100), (24, self.sh - 48), (self.sw - 24, self.sh - 48), 1)

    def _draw_records(self, surface):
        """Tela de registros e documentação confidencial da Dreamcorps™."""
        # Moldura de Documento Confidencial
        card_rect = pygame.Rect(70, 50, self.sw - 140, self.sh - 100)
        card_surf = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
        card_surf.fill((14, 20, 38, 240))
        surface.blit(card_surf, card_rect.topleft)
        pygame.draw.rect(surface, (230, 90, 60), card_rect, 2)

        # Cabeçalho do Documento
        tag_surf = self.ui_font.render("[ CLASSIFICADO: RESTRICTED PERSONNEL ONLY ]", True, (255, 95, 80))
        surface.blit(tag_surf, (card_rect.x + 30, card_rect.y + 25))

        title_surf = self.ui_font.render("ARQUIVO SOMNUS-003: DIRETRIZES DA DREAM LAYER", True, (245, 245, 255))
        surface.blit(title_surf, (card_rect.x + 30, card_rect.y + 60))

        pygame.draw.line(surface, (60, 90, 140), (card_rect.x + 30, card_rect.y + 90), (card_rect.right - 30, card_rect.y + 90), 1)

        # Linhas do memorando corporativo
        memo_lines = [
            "• SUBSTÂNCIA ATIVA: DREAMSYNC™ (Composto lunar LS-01 sintetizado).",
            "• FINALIDADE: Estabilização de ondas neurais e conexão à Dream Layer.",
            "• AVALIAÇÃO: A integridade cognitiva é monitorada via DSI (Dream Stability Index).",
            "• PROTOCOLO DE SEGURANÇA: Evitar entidades classificadas como Type C.",
            "  O contato não encerra a vida biológica do participante, mas causa",
            "  deterioração do ambiente e colapso progressivo do espaço onírico.",
            "",
            "“Toda mente que se conecta deixa resquícios. O que você vivencia não é",
            " apenas um sonho individual, mas uma dimensão compartilhada.”",
            "",
            "REGISTRO DO PARTICIPANTE: SUBJECT_003 [EM OBSERVAÇÃO CONTÍNUA]"
        ]

        text_y = card_rect.y + 115
        for line in memo_lines:
            line_color = (255, 205, 120) if line.startswith("“") else (190, 210, 235)
            line_surf = self.doc_font.render(line, True, line_color)
            surface.blit(line_surf, (card_rect.x + 35, text_y))
            text_y += 24

        # Botão / Instrução de retorno
        back_hint = "[ Pressione qualquer tecla ou clique para voltar ]"
        back_surf = self.ui_font.render(back_hint, True, (130, 190, 255))
        surface.blit(back_surf, (self.sw // 2 - back_surf.get_width() // 2, card_rect.bottom - 42))

    def _draw_transition(self, surface):
        """Sequência gradual de indução do DREAMSYNC™ e fade para a Fase 1."""
        progress = min(1.0, self.transition_timer / self.transition_duration)

        # Fundo que escurece ou ganha tom azul-profundo de imersão
        dim_surf = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        # Opacidade do blackout vai de 0 a 255 no final
        blackout = int(min(255, (progress ** 1.5) * 255))
        dim_surf.fill((6, 7, 16, blackout))

        # Desenha a lua central desvanecendo e pulsando
        fade_moon = self.moon_surface.copy()
        moon_alpha = int(max(0, 255 * (1.0 - progress * 1.2)))
        fade_moon.set_alpha(moon_alpha)
        moon_rect = fade_moon.get_rect(center=(self.sw // 2, int(self.sh * 0.28)))
        surface.blit(fade_moon, moon_rect)

        # Caixa de terminal de indução
        term_box = pygame.Rect(self.sw // 2 - 270, int(self.sh * 0.44), 540, 160)
        box_surf = pygame.Surface((term_box.width, term_box.height), pygame.SRCALPHA)
        box_surf.fill((10, 16, 32, int(min(220, 255 * (1 - progress * 0.5)))))
        surface.blit(box_surf, term_box.topleft)
        pygame.draw.rect(surface, (80, 130, 190), term_box, 1)

        # Exibe mensagens sequenciais conforme o progresso
        lines_to_show = int(progress * (len(self.transition_lines) + 0.8))
        curr_y = term_box.y + 20
        for idx in range(min(len(self.transition_lines), lines_to_show + 1)):
            text = self.transition_lines[idx]
            color = (120, 240, 170) if idx == len(self.transition_lines) - 1 else (200, 220, 255)
            # Efeito cursor piscando na linha ativa
            if idx == lines_to_show and progress < 0.9:
                if int(self.time * 6) % 2 == 0:
                    text += " _"
            line_surf = self.small_font.render(text, True, color)
            surface.blit(line_surf, (term_box.x + 20, curr_y))
            curr_y += 30

        # Barra de Sincronização Neural
        bar_w = 400
        bar_h = 10
        bar_x = self.sw // 2 - bar_w // 2
        bar_y = term_box.bottom + 25
        pygame.draw.rect(surface, (30, 45, 70), (bar_x, bar_y, bar_w, bar_h))
        fill_w = int(bar_w * progress)
        pygame.draw.rect(surface, (255, 170, 60), (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(surface, (120, 160, 210), (bar_x, bar_y, bar_w, bar_h), 1)

        # Percentual
        pct_text = f"NEURAL SYNC: {int(progress * 100)}%"
        pct_surf = self.small_font.render(pct_text, True, (255, 210, 130))
        surface.blit(pct_surf, (self.sw // 2 - pct_surf.get_width() // 2, bar_y + 16))

        # Blackout final sobrepondo tudo
        surface.blit(dim_surf, (0, 0))
