import re
from django.shortcuts import render
from django.http import JsonResponse
from .utils import get_access_logs, get_user_operations, log_access_on_blockchain, log_user_operation
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

# Funzione per validare nome e cognome
def validate_name(name):
    return bool(re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ' ]{2,50}$", name))

# Vista per mostrare tutti gli utenti
@login_required  # Solo gli amministratori possono accedere
def user_management(request):
    users = User.objects.all()
    return render(request, 'user_management.html', {'users': users})

# Vista per eliminare un utente
@login_required
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        messages.success(request, f"✅ L'utente {user.first_name} {user.last_name} è stato eliminato con successo!")

        # Registra l'operazione sulla blockchain
        log_user_operation("Eliminazione", f"{user.first_name} {user.last_name}")

    except User.DoesNotExist:
        messages.error(request, "⚠️ L'utente non esiste!")

    return redirect('user_management')

# Vista per aggiungere un utente
@login_required
def add_user(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        unlock_code = request.POST.get('unlock_code')

        if not validate_name(first_name) or not validate_name(last_name):
            messages.error(request, "⚠️ Nome e Cognome devono contenere solo lettere e spazi!")
            return redirect('user_management')

        if User.objects.filter(unlock_code=unlock_code).exists():
            messages.error(request, "⚠️ Questo codice è già in uso!")
        else:
            User.objects.create(first_name=first_name, last_name=last_name, unlock_code=unlock_code)
            messages.success(request, f"✅ Utente {first_name} {last_name} aggiunto con successo!")

            # Registra l'operazione sulla blockchain
            log_user_operation("Aggiunta", first_name + " " + last_name)

    return redirect('user_management')

# Vista per modificare un utente
@login_required
def edit_user(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        unlock_code = request.POST.get('unlock_code')

        try:
            user = User.objects.get(id=user_id)

            if not validate_name(first_name) or not validate_name(last_name):
                messages.error(request, "Nome e Cognome devono contenere solo lettere e spazi!")
                return redirect('user_management')

            if User.objects.filter(unlock_code=unlock_code).exclude(id=user_id).exists():
                messages.error(request, "Questo codice è già in uso!")
            else:
                user.first_name = first_name
                user.last_name = last_name
                user.unlock_code = unlock_code
                user.save()
                messages.success(request, f"Utente {first_name} {last_name} modificato con successo!")

                # Registra l'operazione sulla blockchain
                log_user_operation("Modifica", f"{first_name} {last_name}")

        except User.DoesNotExist:
            messages.error(request, "L'utente non esiste!")

    return redirect('user_management')

# Vista per gestire il login
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

# Vista per il logout
def custom_logout(request):
    logout(request)
    return redirect("login")  # Torna alla pagina di login dopo il logout

'''@csrf_exempt  # Disabilita il CSRF solo per test; in produzione usa autenticazione adeguata!
def receive_esp32_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code')

            if not code:
                return JsonResponse({'success': False, 'message': 'Codice non fornito'}, status=400)

            # Controllo se esiste un utente con questo codice
            is_valid = User.objects.filter(unlock_code=code).exists()

            # Registra l'esito sulla blockchain, ricorda di levare il commento alla funzione
            #log_access_on_blockchain(code, is_valid)
            return JsonResponse({'success': True, 'is_valid': is_valid})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Formato JSON non valido'}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Metodo non supportato'}, status=405)'''

@csrf_exempt
def receive_esp32_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Formato JSON non valido'}, status=400)
        
    if not code:
        return JsonResponse({'success': False, 'message': 'Codice non fornito'}, status=400)
    
    # Ricava l'utente dal database
    user = User.objects.filter(unlock_code=code).first()  # Prende il primo utente con quel codice
    result = "RIUSCITO" if user is not None else "FALLITO"
    is_valid = User.objects.filter(unlock_code=code).exists()
    username = user.first_name + " " + user.last_name if user else "Sconosciuto"

    log_access_on_blockchain(username,code,result)

    return JsonResponse({
        'success': True,
        'is_valid': is_valid,
        'username': username,
        'result': result  
    }) 
 
@login_required
def get_access_logs_view(request):
    logs = get_access_logs()

    # Se c'è un errore, restituisce un JSON con il messaggio di errore
    if "error" in logs:
        return JsonResponse({"error": logs["error"]}, status=500)

    return JsonResponse(logs, safe=False)

# API per recuperare il log delle operazioni dalla blockchain
@login_required
def get_user_operations_view(request):
    operations = get_user_operations()

    if "error" in operations:
        return JsonResponse({"error": operations["error"]}, status=500)
    
    return JsonResponse(operations, safe=False)
