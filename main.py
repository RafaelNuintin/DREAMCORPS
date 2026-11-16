import pygame
import sys
import math
from models.menu import Menu
from models.stage_manager import StageManager
from models.player import Player
from models.corruption import CorruptionManager
from models.network import send_session_data_async

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
    corruption_manager = CorruptionManager(initial_dsi=10000, initial_corruption=0)

    # Estados do Jogo: 'MENU', 'PLAYING', 'GAME_OVER'
    game_state = 'MENU'

    play_time = 0.0
    session_sent = False
    game_over_fade = 0.0
    game_over_timer = 0.0

    # Controle de despertar e UI
    wake_up_fade = 255.0
    hud_font = pygame.font.SysFont(["consolas", "couriernew"], 13, bold=True)
    alert_font = pygame.font.SysFont(["consolas", "couriernew"], 14, bold=True)
    game_over_title_font = pygame.font.SysFont(["consolas", "couriernew", "arial"], 32, bold=True)
    game_over_sub_font = pygame.font.SysFont(["consolas", "couriernew"], 15, bold=True)
    game_over_detail_font = pygame.font.SysFont(["consolas", "couriernew"], 13)

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
                            corruption_manager.add_dsi(500)
                            corruption_manager.reduce_corruption(4.0)

            elif game_state == 'GAME_OVER':
                if event.type == pygame.KEYDOWN:
                    # Pressionar [R] ou [ESPAÇO] reinicia o loop de gameplay
                    if event.key in (pygame.K_r, pygame.K_SPACE, pygame.K_RETURN):
                        # Restart total da sessão
                        stage_manager.reset()
                        corruption_manager.reset(initial_dsi=10000, initial_corruption=0)
                        play_time = 0.0
                        session_sent = False
                        game_over_fade = 0.0
                        game_over_timer = 0.0
                        wake_up_fade = 255.0

                        # Reposiciona jogador no spawn da Fase 1
                        spawn_x, spawn_y = stage_manager.get_current_stage().player_spawn
                        player.hitbox.x = spawn_x
                        player.hitbox.y = spawn_y
                        player.rect.x = spawn_x - 4
                        player.rect.y = spawn_y - 28

                        game_state = 'PLAYING'

                    elif event.key == pygame.K_ESCAPE:
                        # Retorna ao Menu Inicial
                        stage_manager.reset()
                        corruption_manager.reset(initial_dsi=10000, initial_corruption=0)
                        play_time = 0.0
                        session_sent = False
                        game_over_fade = 0.0
                        game_over_timer = 0.0

                        game_state = 'MENU'
                        menu.state = 'MAIN'
                        menu.fade_alpha = 255.0
                        menu.transition_done = False
                        menu.transition_timer = 0.0

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

            # 1. Atualiza gerenciador de corrupção
            corruption_manager.update(dt)

            # 2. Atualiza jogador usando os colisores da fase ativa
            player.update(curr_stage.colliders)

            # 3. Atualiza o gerenciador de fases e transições (e suas entidades)
            stage_manager.update(dt, player)

            # 4. Checagem de Colisão com Entidades Type C (GDD Seção 4.3.6)
            for ent in curr_stage.entities:
                if ent.active and ent.entity_type == 'TYPE_C':
                    if player.hitbox.colliderect(ent.hitbox):
                        # Aciona penalidade de contato com Predador
                        corruption_manager.trigger_predator_contact()
                        if hasattr(ent, 'trigger_contact'):
                            ent.trigger_contact()

                        # Retorna o jogador ao spawn da fase atual conforme GDD
                        spawn_x, spawn_y = curr_stage.player_spawn
                        player.hitbox.x = spawn_x
                        player.hitbox.y = spawn_y
                        player.rect.x = spawn_x - 4
                        player.rect.y = spawn_y - 28

                        stage_manager.notification_text = "! CONTATO COM ANOMALIA TYPE C: RETORNO AO SPAWN !"
                        stage_manager.notification_timer = 3.0

            # 5. Checagem de GAME OVER por Instabilidade / Corrupção a 100% (GDD Seção 4.6)
            if corruption_manager.check_collapse():
                game_state = 'GAME_OVER'
                game_over_fade = 0.0
                game_over_timer = 0.0

                # Registro imediato da pontuação da sessão no banco de dados Django
                if not session_sent:
                    session_sent = True
                    participant_data = {
                        "player_name": "SUBJECT_003",
                        "dsi": int(corruption_manager.dsi),
                        "phase_reached": curr_stage.name,
                        "artifacts_collected": int(stage_manager.artifacts_collected_count),
                        "corruption_level": 100,
                        "entity_encounters": int(corruption_manager.entity_encounters),
                        "play_time_seconds": int(play_time)
                    }
                    send_session_data_async(participant_data)

            # 6. Envio dos Resultados ao Django ao Concluir o Jogo
            if stage_manager.game_completed and not session_sent:
                session_sent = True
                participant_data = {
                    "player_name": "SUBJECT_003",
                    "dsi": int(corruption_manager.dsi),
                    "phase_reached": "Phase V: Reality (Completed)",
                    "artifacts_collected": int(stage_manager.artifacts_collected_count),
                    "corruption_level": int(corruption_manager.corruption),
                    "entity_encounters": int(corruption_manager.entity_encounters),
                    "play_time_seconds": int(play_time)
                }
                send_session_data_async(participant_data)

            # Reduz o fade inicial de acordar
            if wake_up_fade > 0:
                wake_up_fade = max(0.0, wake_up_fade - (255.0 / 1.8) * dt)

        elif game_state == 'GAME_OVER':
            game_over_timer += dt
            game_over_fade = min(245.0, game_over_fade + 280.0 * dt)

        # -----------------------------
        # RENDERIZAÇÃO (DRAW)
        # -----------------------------
        if game_state == 'MENU':
            menu.draw(screen)

        elif game_state == 'PLAYING':
            # Cria superfície temporária caso haja tremor (shake) do choque
            shake_x, shake_y = corruption_manager.shake_offset
            game_surf = screen if (shake_x == 0 and shake_y == 0) else pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

            # 1. Renderiza a fase ativa, artefatos, entidades e saídas
            stage_manager.draw(game_surf, player, debug=False)

            # 2. Renderiza o protagonista
            player.draw(game_surf, debug=False)

            # 3. Efeitos visuais de Corrupção (Scanlines, Glitches e Choques)
            corruption_manager.render_effects(game_surf)

            if game_surf != screen:
                screen.fill((0, 0, 0))
                screen.blit(game_surf, (shake_x, shake_y))

            # 4. HUD Minimalista da Dreamcorps™ (Conforme Seção 5.4 do GDD)
            # Indicadores corporativos: DSI e Corruption sincronizados
            hud_bg = pygame.Surface((340, 26), pygame.SRCALPHA)
            hud_bg.fill((8, 12, 24, 190))
            screen.blit(hud_bg, (16, 14))
            
            # Borda com cor dinâmica de acordo com o estado de corrupção
            corr_state = corruption_manager.get_state_label()
            border_colors = {
                "STABLE": (70, 105, 150),
                "UNSTABLE": (180, 160, 60),
                "DISTORTED": (210, 110, 50),
                "CRITICAL": (230, 40, 40),
                "COLLAPSE": (255, 20, 20)
            }
            pygame.draw.rect(screen, border_colors.get(corr_state, (70, 105, 150)), (16, 14, 340, 26), 1)

            curr_phase_num = stage_manager.current_index + 1
            dsi_text = f"DSI: {corruption_manager.dsi} | CORR: {int(corruption_manager.corruption)}% [{corr_state}]"
            dsi_surf = hud_font.render(dsi_text, True, (130, 220, 180) if corr_state == "STABLE" else (255, 200, 120))
            screen.blit(dsi_surf, (24, 20))

            # Dica discreta de controles no canto superior direito
            hint_bg = pygame.Surface((190, 26), pygame.SRCALPHA)
            hint_bg.fill((8, 12, 24, 180))
            screen.blit(hint_bg, (SCREEN_WIDTH - 206, 14))
            pygame.draw.rect(screen, (70, 105, 150), (SCREEN_WIDTH - 206, 14, 190, 26), 1)

            hint_text = "[E] Interagir | [ESC] Menu"
            hint_surf = hud_font.render(hint_text, True, (180, 200, 225))
            screen.blit(hint_surf, (SCREEN_WIDTH - 198, 20))

            # 5. Efeito de Despertar Suave (Wake Up Fade-in)
            if wake_up_fade > 0:
                wake_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                wake_surf.fill((4, 6, 14, int(wake_up_fade)))
                screen.blit(wake_surf, (0, 0))

        elif game_state == 'GAME_OVER':
            # 1. Mantém o último frame de jogo por trás com os efeitos de corrupção
            curr_stage = stage_manager.get_current_stage()
            stage_manager.draw(screen, player, debug=False)
            player.draw(screen, debug=False)
            corruption_manager.render_effects(screen)

            # 2. Camada escura de Colapso Analógico
            go_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            go_overlay.fill((8, 10, 20, int(game_over_fade)))
            screen.blit(go_overlay, (0, 0))

            if game_over_fade > 100:
                # Caixa Corporativa Dreamcorps de Avaliação Pós-Colapso
                box_w, box_h = 580, 340
                box_x = SCREEN_WIDTH // 2 - box_w // 2
                box_y = SCREEN_HEIGHT // 2 - box_h // 2

                box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
                box_surf.fill((10, 14, 28, 235))
                screen.blit(box_surf, (box_x, box_y))
                pygame.draw.rect(screen, (220, 50, 50), (box_x, box_y, box_w, box_h), 2, border_radius=4)
                pygame.draw.rect(screen, (120, 20, 30), (box_x + 4, box_y + 4, box_w - 8, box_h - 8), 1, border_radius=2)

                # Título
                title = game_over_title_font.render("COLAPSO DA DREAM LAYER", True, (255, 60, 60))
                screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, box_y + 24))

                # Mensagem Corporativa
                sub_txt = "CONEXÃO SINÁPTICA INTERROMPIDA — STATUS: REQUIRES REVIEW"
                sub_surf = game_over_sub_font.render(sub_txt, True, (255, 180, 120))
                screen.blit(sub_surf, (SCREEN_WIDTH // 2 - sub_surf.get_width() // 2, box_y + 70))

                # Linha divisória
                pygame.draw.line(screen, (80, 40, 50), (box_x + 30, box_y + 102), (box_x + box_w - 30, box_y + 102), 1)

                # Detalhes corporativos da sessão
                report_lines = [
                    f"PARTICIPANTE: SUBJECT_003",
                    f"ÍNDICE DSI FINAL: {corruption_manager.dsi} pts",
                    f"INSTABILIDADE ATINGIDA: 100% [COLLAPSE]",
                    f"REGIÃO DO COLAPSO: {curr_stage.name}",
                    f"ARTEFATOS RECUPERADOS: {stage_manager.artifacts_collected_count}/5",
                    f"ENCONTROS COM ANOMALIAS: {corruption_manager.entity_encounters}",
                    f"TEMPO DE PERMANÊNCIA: {int(play_time)}s",
                    f"[STATUS DO BACKEND: SESSÃO TRANSMITIDA AO BANCO DE DADOS]"
                ]

                start_y = box_y + 118
                for idx, line in enumerate(report_lines):
                    color = (130, 230, 160) if "BACKEND" in line else (210, 225, 240)
                    line_surf = game_over_detail_font.render(line, True, color)
                    screen.blit(line_surf, (box_x + 45, start_y + idx * 22))

                # Prompt para Restart ou Retornar ao Menu
                pulse = (math.sin(game_over_timer * 4.0) + 1.0) * 0.5
                prompt_alpha = int(160 + 95 * pulse)
                prompt_surf = game_over_sub_font.render("[R] REINICIAR TESTE   |   [ESC] MENU PRINCIPAL", True, (255, 255, 255))
                prompt_surf.set_alpha(prompt_alpha)
                screen.blit(prompt_surf, (SCREEN_WIDTH // 2 - prompt_surf.get_width() // 2, box_y + box_h - 38))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
