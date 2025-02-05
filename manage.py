#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import webbrowser
import threading
import time

def open_browser():
    time.sleep(3)  # Aspetta un secondo per dare tempo al server di avviarsi
    webbrowser.open("https://192.168.178.40:8000/blockchain/login/")  # Apri il browser sulla pagina di login

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    
    # Avvia il browser in un thread separato per non bloccare l'esecuzione del server
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()

