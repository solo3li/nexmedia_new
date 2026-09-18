import json
from decimal import Decimal
from pathlib import Path
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.conf import settings
import inngest
from inngest_client import inngest_client
from apps.tools.tts.models import TtsGeneration
from apps.billing.services import WalletService, InsufficientCreditsError

def load_voices_catalog():
    catalog_path = settings.BASE_DIR / 'data' / 'catalogs' / 'tts_voices.json'
    if catalog_path.exists():
        with open(catalog_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

@login_required
def tts_workspace_view(request):
    voices = load_voices_catalog()
    history = TtsGeneration.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'tools/tts_workspace.html', {
        'voices': voices,
        'history': history,
        'tool_title_ar': 'تحويل النص إلى كلام',
        'tool_title_en': 'Text to Speech',
    })

@login_required
def tts_estimate_view(request):
    text = request.GET.get('text', '')
    # 0.001 credit per character (minimum 0.1 credit)
    char_count = len(text)
    cost = max(Decimal(str(char_count)) * Decimal('0.001'), Decimal('0.1000'))
    return JsonResponse({'cost': float(cost), 'characters': char_count})

@login_required
@require_POST
def tts_generate_view(request):
    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    text = data.get('text', '').strip()
    voice_name = data.get('voice_name', 'صبرينة')
    quality = data.get('quality', 'Standard')

    if not text:
        return JsonResponse({'error': 'النص مطلوب / Text is required'}, status=400)

    # Cost calculation: 0.001 per char, min 0.1
    cost = max(Decimal(str(len(text))) * Decimal('0.001'), Decimal('0.1000'))

    try:
        deduction = WalletService.validate_and_charge(
            user_id=str(request.user.id),
            cost=cost,
            tool_name='tts'
        )
    except InsufficientCreditsError as e:
        return JsonResponse({'error': str(e)}, status=402)

    record = TtsGeneration.objects.create(
        user=request.user,
        text=text,
        voice_name=voice_name,
        quality=quality,
        status='processing',
        standard_credits_used=deduction['standard_deducted'],
        premium_credits_used=deduction['premium_deducted']
    )

    # Dispatch event to Inngest
    try:
        inngest_client.send_sync(
            inngest.Event(
                name="tools/tts.generate",
                data={
                    "task_id": str(record.id),
                    "user_id": str(request.user.id),
                    "text": text,
                    "voice_name": voice_name,
                    "standard_credits": float(deduction['standard_deducted']),
                    "premium_credits": float(deduction['premium_deducted']),
                }
            )
        )
    except Exception as e:
        # If inngest fails to receive event, refund immediately
        WalletService.refund(
            user_id=str(request.user.id),
            standard_amount=deduction['standard_deducted'],
            premium_amount=deduction['premium_deducted'],
            tool_name='tts',
            reason=f"Failed to enqueue inngest job: {e}"
        )
        record.status = 'failed'
        record.error_message = str(e)
        record.save(update_fields=['status', 'error_message'])
        return JsonResponse({'error': f'تعذر إرسال المهمة: {e}'}, status=500)

    return JsonResponse({
        'task_id': str(record.id),
        'status': 'processing',
        'cost': float(cost),
        'standard_deducted': float(deduction['standard_deducted']),
        'premium_deducted': float(deduction['premium_deducted'])
    })
