from django.shortcuts import render

from django.http import JsonResponse
from .utils import get_message

from django.views.decorators.csrf import csrf_exempt
import json

def contract_message(request):
    try:
        message = get_message()
        return JsonResponse({"message": message})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt  # Disabilita il CSRF solo per test; in produzione usa autenticazione adeguata!
def receive_esp32_data(request):
    if request.method == "POST":
        try:
            # Decodifica il JSON inviato dalla ESP32
            data = json.loads(request.body)

            # Estrai il codice ricevuto
            code = data.get("code", "")

            # Controlla se il codice è valido
            if len(code) != 6:
                return JsonResponse({"error": "Codice non valido"}, status=400)

            # Logica di elaborazione del codice (ad esempio verifica nel database)
            # Qui puoi aggiungere la logica per confrontare il codice con il database
            is_valid = (code == "123456")  # Esempio: codice di prova

            if is_valid:
                return JsonResponse({"status": "success", "message": "Accesso consentito"})
            else:
                return JsonResponse({"status": "error", "message": "Codice errato"}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Formato JSON non valido"}, status=400)

    return JsonResponse({"error": "Metodo non consentito"}, status=405)