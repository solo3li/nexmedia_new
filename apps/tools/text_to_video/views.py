import json
from decimal import Decimal
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import inngest
from inngest_client import inngest_client
from apps.tools.text_to_video.models import TextToVideoGeneration
from apps.billing.services import WalletService, InsufficientCreditsError

RESOLUTION_RATES = {
    '480p': Decimal('2.4'),
    '720p': Decimal('4.5'),
    '1080p': Decimal('7.5'),
}

@login_required
def text_to_video_workspace_view(request):
    history = TextToVideoGeneration.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'tools/text_to_video_workspace.html', {
        'history': history,
        'tool_title_ar': 'تحويل النص إلى فيديو',
        'tool_title_en': 'Text to Video',
    })

@login_required
def text_to_video_estimate_view(request):
    res = request.GET.get('resolution', '720p')
    duration = int(request.GET.get('duration', 5))
    rate = RESOLUTION_RATES.get(res, Decimal('4.5'))
    cost = rate * Decimal(str(duration))
    return JsonResponse({'cost': float(cost), 'resolution': res, 'duration': duration})

@login_required
@require_POST
def text_to_video_generate_view(request):
    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    prompt = data.get('prompt', '').strip()
    resolution = data.get('resolution', '720p')
    duration = int(data.get('duration', 5))
    model_name = data.get('model_name', 'veo-3.1-fast')
    aspect_ratio = data.get('aspect_ratio', '16:9')

    if not prompt:
        return JsonResponse({'error': 'الوصف مطلوب / Prompt is required'}, status=400)

    rate = RESOLUTION_RATES.get(resolution, Decimal('4.5'))
    cost = rate * Decimal(str(duration))

    try:
        deduction = WalletService.validate_and_charge(
            user_id=str(request.user.id),
            cost=cost,
            tool_name='text_to_video'
        )
    except InsufficientCreditsError as e:
        return JsonResponse({'error': str(e)}, status=402)

    record = TextToVideoGeneration.objects.create(
        user=request.user,
        prompt=prompt,
        model_name=model_name,
        resolution=resolution,
        duration_seconds=duration,
        aspect_ratio=aspect_ratio,
        status='processing',
        standard_credits_used=deduction['standard_deducted'],
        premium_credits_used=deduction['premium_deducted']
    )

    inngest_client.send_sync(
        inngest.Event(
            name="tools/text_to_video.generate",
            data={
                "task_id": str(record.id),
                "user_id": str(request.user.id),
                "model_name": model_name,
                "standard_credits": float(deduction['standard_deducted']),
                "premium_credits": float(deduction['premium_deducted']),
            }
        )
    )

    return JsonResponse({'task_id': str(record.id), 'status': 'processing', 'cost': float(cost)})
