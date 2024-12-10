from django.shortcuts import render

from django.http import JsonResponse
from .utils import get_message

def contract_message(request):
    try:
        message = get_message()
        return JsonResponse({"message": message})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
