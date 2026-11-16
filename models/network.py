import json
import threading
import urllib.request
import urllib.error

API_URL = "http://127.0.0.1:8000/api/sessions/"
RANKING_URL = "http://127.0.0.1:8000/api/ranking/"

def fetch_ranking_direct():
    """
    Recupera as sessões e pontuações diretamente do banco de dados SQLite do Django.
    Isso garante que o ranking funcione imediatamente no Pygame sem exigir
    que o servidor web HTTP (runserver) esteja rodando.
    """
    try:
        import os
        import sys
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
        if base_dir not in sys.path:
            sys.path.insert(0, base_dir)
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dreamcorps_backend.settings')
        import django
        django.setup()
        from ranking.models import ParticipantSession

        sessions = list(ParticipantSession.objects.all()[:15])
        return [
            {
                'rank': idx + 1,
                'player_name': s.player_name,
                'dsi': s.dsi,
                'phase_reached': s.phase_reached,
                'artifacts_collected': s.artifacts_collected,
                'corruption_level': s.corruption_level,
                'entity_encounters': s.entity_encounters,
                'play_time_seconds': s.play_time_seconds,
                'participant_status': s.participant_status,
                'date': s.created_at.strftime('%d/%m %H:%M')
            }
            for idx, s in enumerate(sessions)
        ]
    except Exception as e:
        return []

def send_session_data_async(data, callback=None):
    """
    Envia os dados da sessão tanto via requisição HTTP (caso o servidor esteja online)
    quanto grava diretamente no banco SQLite via Django ORM caso o servidor não responda.
    """
    def _worker():
        # 1. Tenta envio via API HTTP
        http_success = False
        try:
            payload = json.dumps(data).encode("utf-8")
            req = urllib.request.Request(
                API_URL,
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=2.0) as response:
                if response.getcode() in (200, 201):
                    http_success = True
                    body = response.read().decode("utf-8")
                    if callback:
                        callback(True, json.loads(body) if body else {})
        except Exception:
            http_success = False

        # 2. Se a API HTTP falhar ou não estiver rodando o servidor, salva diretamente via Django
        if not http_success:
            try:
                import os
                import sys
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
                if base_dir not in sys.path:
                    sys.path.insert(0, base_dir)
                os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dreamcorps_backend.settings')
                import django
                django.setup()
                from ranking.models import ParticipantSession

                session = ParticipantSession.objects.create(
                    player_name=data.get('player_name', 'SUBJECT_003'),
                    dsi=int(data.get('dsi', 10000)),
                    phase_reached=data.get('phase_reached', 'Phase I: The Bedroom'),
                    artifacts_collected=int(data.get('artifacts_collected', 0)),
                    corruption_level=int(data.get('corruption_level', 0)),
                    entity_encounters=int(data.get('entity_encounters', 0)),
                    play_time_seconds=int(data.get('play_time_seconds', 0))
                )
                if callback:
                    callback(True, {'id': session.id, 'rank': 1, 'status': session.participant_status})
            except Exception as e:
                if callback:
                    callback(False, str(e))

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    return thread
