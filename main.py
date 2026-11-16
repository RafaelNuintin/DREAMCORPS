import pygame
import sys
from models.menu import Menu
from models.stage_manager import StageManager
from models.player import Player

def main():
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("DREAMCORPS.™")
    clock = pygame.time.Clock()

    # Inicialização dos Módulos Principais
    menu = Menu(SCREEN_WIDTH, SCREEN_HEIGHT)
    stage_manager = StageManager(SCREEN_WIDTH, SCREEN_HEIGHT)
    player = Player(x=620, y=180, spritesheet_path="assets/player_spritesheet.png")

    # Estados do Jogo: 'MENU' e 'PLAYING'
    game_state = 'MENU'

    # Pontuação e Métricas do GDD
    dsi_score = 10000
    corruption_level = 0
    play_time = 0.0

    # Controle de despertar e UI
    wake_up_fade = 255.0
    hud_font = pygame.font.SysFont(["consolas", "couriernew"], 13, bold=True)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time em segundos

        # -----------------------------
        # EVENTOS
        # -----------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state == 'MENU':
                menu.handle_event(event)
            elif game_state == 'PLAYING':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Retorna ao Menu mantendo a identidade
                        game_state = 'MENU'
                        menu.state = 'MAIN'
                        menu.fade_alpha = 180.0
                        menu.transition_done = False
                        menu.transition_timer = 0.0

                    elif event.key in (pygame.K_e, pygame.K_SPACE):
                        # Interação do Jogador com Artefatos do Cenário
                        success, artifact = stage_manager.interact(player)
                        if success:
                            dsi_score += 500  # Bonificação de DSI por recuperação de artefato

        # -----------------------------
        # ATUALIZAÇÃO (UPDATE)
        # -----------------------------
        if game_state == 'MENU':
            menu.update(dt)
            if menu.transition_done:
                game_state = 'PLAYING'
                wake_up_fade = 255.0
                # Posiciona o jogador no spawn da Fase 1
                spawn_x, spawn_y = stage_manager.get_current_stage().player_spawn
                player.hitbox.x = spawn_x
                player.hitbox.y = spawn_y
                player.rect.x = spawn_x - 4
                player.rect.y = spawn_y - 28

        elif game_state == 'PLAYING':
            play_time += dt
            curr_stage = stage_manager.get_current_stage()

            # Atualiza jogador usando os colisores da fase ativa
            player.update(curr_stage.colliders)

            # Atualiza o gerenciador de fases e transições
            stage_manager.update(dt, player)

            # Reduz o fade inicial de acordar
            if wake_up_fade > 0:
                wake_up_fade = max(0.0, wake_up_fade - (255.0 / 1.8) * dt)

        # -----------------------------
        # RENDERIZAÇÃO (DRAW)
        # -----------------------------
        if game_state == 'MENU':
            menu.draw(screen)
        elif game_state == 'PLAYING':
            # 1. Renderiza a fase ativa, artefatos e saídas
            stage_manager.draw(screen, player, debug=False)

            # 2. Renderiza o protagonista
            player.draw(screen, debug=False)

            # 3. HUD Minimalista da Dreamcorps™ (Conforme Seção 5.4 do GDD)
            # Indicadores corporativos: DSI e Corruption
            hud_bg = pygame.Surface((310, 26), pygame.SRCALPHA)
            hud_bg.fill((8, 12, 24, 180))
            screen.blit(hud_bg, (16, 14))
            pygame.draw.rect(screen, (70, 105, 150), (16, 14, 310, 26), 1)

            curr_phase_num = stage_manager.current_index + 1
            dsi_text = f"DSI: {dsi_score}  |  CORR: {corruption_level}%  |  FASE {curr_phase_num}/5"
            dsi_surf = hud_font.render(dsi_text, True, (130, 220, 180))
            screen.blit(dsi_surf, (24, 20))

            # Dica discreta de controles no canto superior direito
            hint_bg = pygame.Surface((190, 26), pygame.SRCALPHA)
            hint_bg.fill((8, 12, 24, 180))
            screen.blit(hint_bg, (SCREEN_WIDTH - 206, 14))
            pygame.draw.rect(screen, (70, 105, 150), (SCREEN_WIDTH - 206, 14, 190, 26), 1)

            hint_text = "[E] Interagir | [ESC] Menu"
            hint_surf = hud_font.render(hint_text, True, (180, 200, 225))
            screen.blit(hint_surf, (SCREEN_WIDTH - 198, 20))

            # 4. Efeito de Despertar Suave (Wake Up Fade-in)
            if wake_up_fade > 0:
                wake_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                wake_surf.fill((4, 6, 14, int(wake_up_fade)))
                screen.blit(wake_surf, (0, 0))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
