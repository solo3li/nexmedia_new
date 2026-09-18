import json
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from apps.core.centrifugo import centrifugo_service

def load_catalog(filename):
    path = settings.BASE_DIR / 'data' / 'catalogs' / filename
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def dashboard_view(request):
    voices = load_catalog('tts_voices.json')
    # Assign some realistic usage stats and countries for the Vernal table
    countries = [
        {'name': 'United States', 'code': 'US', 'flag': '🇺🇸'},
        {'name': 'Egypt', 'code': 'EG', 'flag': '🇪🇬'},
        {'name': 'Saudi Arabia', 'code': 'SA', 'flag': '🇸🇦'},
        {'name': 'United Kingdom', 'code': 'GB', 'flag': '🇬🇧'},
        {'name': 'Germany', 'code': 'DE', 'flag': '🇩🇪'},
        {'name': 'France', 'code': 'FR', 'flag': '🇫🇷'},
    ]
    for idx, v in enumerate(voices):
        v['country'] = countries[idx % len(countries)]
        v['usage_count'] = f"{(idx * 1.3 + 2.5):.1f}K"
        v['date_str'] = f"{((idx % 4) + 1)} Months"

    return render(request, 'pages/dashboard.html', {
        'voices': voices,
    })

def centrifugo_token_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    token = centrifugo_service.generate_connection_token(str(request.user.id))
    return JsonResponse({'token': token, 'ws_url': settings.CENTRIFUGO_WS_URL})
