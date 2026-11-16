import pygame
from models.stages import Stage1Bedroom, Stage2School, Stage3Office, Stage4Null, Stage5Reality

class StageManager:
    """Orquestrador das 5 fases da Dream Layer e suas transições suaves."""
    def __init__(self, screen_width=800, screen_height=600):
        self.sw = screen_width
        self.sh = screen_height

        # As 5 fases estruturadas
        self.stages = [
            Stage1Bedroom(sw=screen_width, sh=screen_height),
            Stage2School(sw=screen_width, sh=screen_height),
            Stage3Office(sw=screen_width, sh=screen_height),
            Stage4Null(sw=screen_width, sh=screen_height),
            Stage5Reality(sw=screen_width, sh=screen_height)
        ]
        self.current_index = 0
        self.current_stage = self.stages[self.current_index]

        # Controle de Transição entre Fases
        self.transitioning = False
        self.transition_timer = 0.0
        self.transition_fade = 0.0 # 0 a 255
        self.transition_state = 'NONE' # 'FADE_OUT', 'FADE_IN'
        self.target_stage_index = 0

        # Notificações in-game de coleta de artefato
        self.notification_text = ""
        self.notification_timer = 0.0

        # Banner de introdução da fase
        self.banner_timer = 3.5

        # Estado de conclusão total
        self.game_completed = False

        # Total de artefatos coletados na campanha
        self.artifacts_collected_count = 0

        # Fontes de UI
        self.notif_font = pygame.font.SysFont(["consolas", "couriernew"], 15, bold=True)
        self.banner_font = pygame.font.SysFont(["consolas", "couriernew", "arial"], 22, bold=True)
        self.sub_banner_font = pygame.font.SysFont(["georgia", "timesnewroman"], 14, italic=True)

    def get_current_stage(self):
        return self.current_stage

    def trigger_stage_change(self, target_index):
        """Inicia a transição suave para uma nova fase."""
        if self.transitioning or target_index >= len(self.stages):
            return
        self.transitioning = True
        self.transition_state = 'FADE_OUT'
        self.transition_timer = 0.0
        self.target_stage_index = target_index

    def interact(self, player):
        """Tenta interagir com artefatos próximos ao jogador."""
        for art in self.current_stage.artifacts:
            if not art.collected and art.is_near_player(player.rect):
                art.collected = True
                self.artifacts_collected_count += 1
                
                # Feedback de notificação corporativa
                self.notification_text = f"ARTEFATO COLETADO: {art.name}"
                self.notification_timer = 3.2

                # Se estiver na Fase V e coletou a âncora final: conclui a jornada
                if self.current_stage.stage_id == 5:
                    self.game_completed = True

                return True, art
        return False, None

    def update(self, dt, player):
        """Atualiza a lógica da fase ativa e transições."""
        self.current_stage.update(dt)

        # Redução do timer de notificação
        if self.notification_timer > 0:
            self.notification_timer = max(0.0, self.notification_timer - dt)

        # Redução do timer do banner
        if self.banner_timer > 0:
            self.banner_timer = max(0.0, self.banner_timer - dt)

        # Verifica se o jogador cruzou a saída aberta da fase atual
        if not self.transitioning and self.current_stage.check_exit(player.hitbox):
            self.trigger_stage_change(self.current_index + 1)

        # Gerenciamento do Fade de transição suave
        if self.transitioning:
            self.transition_timer += dt
            if self.transition_state == 'FADE_OUT':
                self.transition_fade = min(255.0, self.transition_fade + 500.0 * dt)
                if self.transition_fade >= 255.0:
                    # Troca a fase
                    self.current_index = self.target_stage_index
                    self.current_stage = self.stages[self.current_index]
                    
                    # Reposiciona o jogador no ponto de spawn da nova fase
                    spawn_x, spawn_y = self.current_stage.player_spawn
                    player.hitbox.x = spawn_x
                    player.hitbox.y = spawn_y
                    player.rect.x = spawn_x - 4
                    player.rect.y = spawn_y - 28

                    self.transition_state = 'FADE_IN'
                    self.banner_timer = 3.5

            elif self.transition_state == 'FADE_IN':
                self.transition_fade = max(0.0, self.transition_fade - 350.0 * dt)
                if self.transition_fade <= 0.0:
                    self.transitioning = False
                    self.transition_state = 'NONE'

    def draw(self, surface, player, debug=False):
        """Renderiza a fase, artefatos, avisos corporativos e fade."""
        self.current_stage.draw(surface, player.rect, debug=debug)

        # Banner de Apresentação da Fase (PHASE I, II, III, IV, V)
        if self.banner_timer > 0:
            self._draw_phase_banner(surface)

        # Notificação de Coleta de Artefato no topo da tela
        if self.notification_timer > 0:
            self._draw_notification(surface)

        # Camada de Fade de Transição entre fases
        if self.transition_fade > 0:
            fade_surf = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
            fade_surf.fill((6, 7, 16, int(self.transition_fade)))
            surface.blit(fade_surf, (0, 0))

    def _draw_phase_banner(self, surface):
        if self.banner_timer > 2.5:
            alpha = int(255 * (3.5 - self.banner_timer))
        elif self.banner_timer < 1.0:
            alpha = int(255 * self.banner_timer)
        else:
            alpha = 255
        alpha = max(0, min(255, alpha))

        banner_surf = pygame.Surface((self.sw, 75), pygame.SRCALPHA)
        banner_surf.fill((6, 8, 18, int(alpha * 0.85)))
        
        t_surf = self.banner_font.render(self.current_stage.name, True, (245, 248, 255))
        t_surf.set_alpha(alpha)
        banner_surf.blit(t_surf, (self.sw // 2 - t_surf.get_width() // 2, 14))

        st_surf = self.sub_banner_font.render(f"— {self.current_stage.subtitle} —", True, (255, 210, 130))
        st_surf.set_alpha(alpha)
        banner_surf.blit(st_surf, (self.sw // 2 - st_surf.get_width() // 2, 44))

        surface.blit(banner_surf, (0, self.sh // 2 - 120))

    def _draw_notification(self, surface):
        pulse = min(1.0, self.notification_timer / 0.5)
        alpha = int(240 * pulse) if self.notification_timer < 0.5 else 240
        
        box_w = 460
        box_h = 36
        box_x = self.sw // 2 - box_w // 2
        box_y = 52

        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box_surf.fill((16, 28, 48, alpha))
        surface.blit(box_surf, (box_x, box_y))
        pygame.draw.rect(surface, (255, 195, 60), (box_x, box_y, box_w, box_h), 1, border_radius=3)

        txt_surf = self.notif_font.render(self.notification_text, True, (255, 235, 160))
        surface.blit(txt_surf, (self.sw // 2 - txt_surf.get_width() // 2, box_y + 9))
