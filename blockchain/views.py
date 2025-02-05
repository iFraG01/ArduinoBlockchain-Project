from django.shortcuts import render
from django.http import JsonResponse
from .utils import get_access_logs, log_access_on_blockchain
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

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
        messages.success(request, f"L'utente {user.first_name} {user.last_name} è stato eliminato con successo!")
    except User.DoesNotExist:
        messages.error(request, "L'utente non esiste!")

    return redirect('user_management')

# Vista per aggiungere un utente
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

    elif request.method == 'GET':  # ✅ Permetti test con GET
        code = request.GET.get('code')  # Prende il codice dall'URL

    else:
        return JsonResponse({'success': False, 'message': 'Metodo non supportato'}, status=405)

    if not code:
        return JsonResponse({'success': False, 'message': 'Codice non fornito'}, status=400)
    
    # Ricava l'utente dal database
    user = User.objects.filter(unlock_code=code).first()  # Prende il primo utente con quel codice
    is_valid = User.objects.filter(unlock_code=code).exists()

    if user:
        username = user.first_name + " " + user.last_name # Recupera il nome utente
    else:
        username = None

    log_access_on_blockchain(code,username)

    return JsonResponse({
        'success': True,
        'is_valid': is_valid,
        'username': username  
    })

def get_access_logs_view(request):
    """API endpoint per recuperare i log di accesso dalla blockchain."""
    logs = get_access_logs()

    # Se c'è un errore, restituisce un JSON con il messaggio di errore
    if "error" in logs:
        return JsonResponse({"error": logs["error"]}, status=500)

    return JsonResponse(logs, safe=False)
