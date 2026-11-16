import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .models import ParticipantSession

@csrf_exempt
def submit_session(request):
    """Recebe dados da partida enviados pelo cliente Pygame via POST JSON."""
    if request.method != 'POST':
        return HttpResponseBadRequest("Apenas requisições POST são aceitas.")

    try:
        data = json.loads(request.body.decode('utf-8'))
        
        session = ParticipantSession(
            player_name=data.get('player_name', 'SUBJECT_003').strip() or 'SUBJECT_003',
            dsi=int(data.get('dsi', 10000)),
            phase_reached=data.get('phase_reached', 'Phase I: The Bedroom'),
            artifacts_collected=int(data.get('artifacts_collected', 0)),
            corruption_level=int(data.get('corruption_level', 0)),
            entity_encounters=int(data.get('entity_encounters', 0)),
            play_time_seconds=int(data.get('play_time_seconds', 0))
        )
        session.save()

        # Determina a posição no ranking
        rank_position = ParticipantSession.objects.filter(dsi__gt=session.dsi).count() + 1

        return JsonResponse({
            'status': 'success',
            'message': 'Relatório de avaliação registrado com sucesso.',
            'id': session.id,
            'rank': rank_position,
            'participant_status': session.participant_status,
            'dsi': session.dsi
        }, status=201)

    except (ValueError, KeyError, json.JSONDecodeError) as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def ranking_api(request):
    """Retorna os dados dos melhores participantes em formato JSON."""
    sessions = ParticipantSession.objects.all()[:25]
    data = [
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
            'date': s.created_at.strftime('%Y-%m-%d %H:%M')
        }
        for idx, s in enumerate(sessions)
    ]
    return JsonResponse({'ranking': data})

def ranking_dashboard(request):
    """Renderiza a interface do DREAMCORPS.™ PARTICIPANT EVALUATION SYSTEM."""
    sessions = ParticipantSession.objects.all()[:30]
    total_sessions = ParticipantSession.objects.count()
    integrated_count = ParticipantSession.objects.filter(participant_status='INTEGRATED').count()
    avg_dsi = 0
    if total_sessions > 0:
        avg_dsi = int(sum(s.dsi for s in sessions) / len(sessions))

    context = {
        'sessions': sessions,
        'total_sessions': total_sessions,
        'integrated_count': integrated_count,
        'avg_dsi': avg_dsi,
    }
    return render(request, 'ranking/dashboard.html', context)
