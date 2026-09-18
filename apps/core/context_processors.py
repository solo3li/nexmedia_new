from django.conf import settings
from apps.core.centrifugo import centrifugo_service

def nexmedia_global_context(request):
    """
    Global template context processor:
    - User wallets (standard_credits, premium_credits)
    - Bilingual text direction (rtl/ltr) and language code
    - Realtime Centrifugo WebSocket connection parameters
    """
    context = {
        'LANGUAGE_CODE': getattr(request, 'LANGUAGE_CODE', 'ar'),
        'DIR': getattr(request, 'DIR', 'rtl'),
        'CENTRIFUGO_WS_URL': settings.CENTRIFUGO_WS_URL,
        'DEBUG': settings.DEBUG,
    }

    if request.user.is_authenticated:
        context['standard_credits'] = request.user.standard_credits
        context['premium_credits'] = request.user.premium_credits
        context['centrifugo_token'] = centrifugo_service.generate_connection_token(str(request.user.id))
        context['user_channel'] = f"personal:#{request.user.id}"
    else:
        context['standard_credits'] = 0
        context['premium_credits'] = 0
        context['centrifugo_token'] = ''
        context['user_channel'] = ''

    return context
