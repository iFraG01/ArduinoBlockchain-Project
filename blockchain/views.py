from django.shortcuts import render

from django.http import JsonResponse
from .utils import get_message

from django.views.decorators.csrf import csrf_exempt
import json


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import User
from django.contrib import messages

from django.contrib.auth import authenticate, login, logout




# 1️⃣ Vista per mostrare tutti gli utenti
@login_required  # Solo gli amministratori possono accedere
def user_management(request):
    users = User.objects.all()
    return render(request, 'user_management.html', {'users': users})

# 2️⃣ Vista per eliminare un utente
@login_required
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        messages.success(request, f"L'utente {user.first_name} {user.last_name} è stato eliminato con successo!")
    except User.DoesNotExist:
        messages.error(request, "L'utente non esiste!")

    return redirect('user_management')

# 3️⃣ Vista per aggiungere un utente
@login_required
def add_user(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        unlock_code = request.POST.get('unlock_code')

        # Verifica che il codice sia univoco
        if User.objects.filter(unlock_code=unlock_code).exists():
            messages.error(request, "Questo codice è già in uso!")
        else:
            User.objects.create(first_name=first_name, last_name=last_name, unlock_code=unlock_code)
            messages.success(request, f"Utente {first_name} {last_name} aggiunto con successo!")

    return redirect('user_management')


# 1️⃣ Vista per gestire il login
def custom_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("user_management")  # Dopo il login, reindirizza alla gestione utenti
        else:
            messages.error(request, "Username o password errati!")

    return render(request, "login.html")

# 2️⃣ Vista per il logout
def custom_logout(request):
    logout(request)
    return redirect("login")  # Torna alla pagina di login dopo il logout


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