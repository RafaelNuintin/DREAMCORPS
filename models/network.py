import json
import threading
import requests

API_URL = "http://127.0.0.1:8000/api/sessions/"

def send_session_data_async(data, callback=None):
    """
    Envia os dados da sessão para o Django em segundo plano (thread separada),
    evitando qualquer travamento no loop do Pygame.
    """
    def _worker():
        try:
            response = requests.post(
                API_URL,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=4.0
            )
            if response.status_code == 201:
                res_json = response.json()
                if callback:
                    callback(True, res_json)
            else:
                if callback:
                    callback(False, f"Status code: {response.status_code}")
        except Exception as e:
            if callback:
                callback(False, str(e))

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    return thread
