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

    from apps.tools.text_to_image.models import TextToImageSetting, TextToImageModelPricing

    # Dynamic Tool Settings Validation
    setting = TextToImageSetting.objects.first()
    if setting:
        if not setting.is_active:
            return JsonResponse({'error': 'الأداة معطلة حالياً من قبل الإدارة / Tool is currently disabled'}, status=503)
        if setting.is_maintenance_mode:
            return JsonResponse({'error': 'الأداة في وضع الصيانة حالياً / Tool is under maintenance'}, status=503)
        if len(prompt) > setting.max_prompt_length:
            return JsonResponse({'error': f'تجاوز الوصف الحد الأقصى ({setting.max_prompt_length} حرف) / Prompt exceeds max length'}, status=400)

    # Dynamic Pricing
    pricing = TextToImageModelPricing.objects.filter(is_active=True).first()
    cost = pricing.cost_per_image if pricing else Decimal('2.0000')
    allow_premium = (pricing.allowed_wallet in ('premium', 'both')) if pricing else True

    try:
        deduction = WalletService.validate_and_charge(
            user_id=str(request.user.id),
            cost=cost,
            tool_name='text_to_image',
            allow_premium=allow_premium
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
