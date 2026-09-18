import json
from decimal import Decimal
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import inngest
from inngest_client import inngest_client
from apps.tools.text_to_image.models import TextToImageGeneration
from apps.billing.services import WalletService, InsufficientCreditsError

@login_required
def text_to_image_workspace_view(request):
    history = TextToImageGeneration.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'tools/text_to_image_workspace.html', {
        'history': history,
        'tool_title_ar': 'توليد الصور بالذكاء الاصطناعي',
        'tool_title_en': 'Text to Image Studio',
    })

@login_required
@require_POST
def text_to_image_generate_view(request):
    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    prompt = data.get('prompt', '').strip()
    aspect_ratio = data.get('aspect_ratio', '1:1')

    if not prompt:
        return JsonResponse({'error': 'الوصف مطلوب / Prompt is required'}, status=400)

    # Cost: 2.0 credits
    cost = Decimal('2.0000')

    try:
        deduction = WalletService.validate_and_charge(
            user_id=str(request.user.id),
            cost=cost,
            tool_name='text_to_image'
        )
    except InsufficientCreditsError as e:
        return JsonResponse({'error': str(e)}, status=402)

    record = TextToImageGeneration.objects.create(
        user=request.user,
        prompt=prompt,
        aspect_ratio=aspect_ratio,
        status='processing',
        standard_credits_used=deduction['standard_deducted'],
        premium_credits_used=deduction['premium_deducted']
    )

    inngest_client.send_sync(
        inngest.Event(
            name="tools/text_to_image.generate",
            data={
                "task_id": str(record.id),
                "user_id": str(request.user.id),
                "standard_credits": float(deduction['standard_deducted']),
                "premium_credits": float(deduction['premium_deducted']),
            }
        )
    )

    return JsonResponse({'task_id': str(record.id), 'status': 'processing', 'cost': float(cost)})
