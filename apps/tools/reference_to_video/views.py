from decimal import Decimal
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import inngest
from inngest_client import inngest_client
from apps.tools.reference_to_video.models import ReferenceToVideoGeneration
from apps.core.storage import storage_service
from apps.billing.services import WalletService, InsufficientCreditsError

@login_required
def reference_to_video_workspace_view(request):
    history = ReferenceToVideoGeneration.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'tools/reference_to_video_workspace.html', {
        'history': history,
        'tool_title_ar': 'فيديو بحركة مرجعية (Seedance)',
        'tool_title_en': 'Reference to Video (Seedance)',
    })

@login_required
@require_POST
def reference_to_video_generate_view(request):
    ref_file = request.FILES.get('reference')
    prompt = request.POST.get('prompt', '').strip()

    if not ref_file:
        return JsonResponse({'error': 'الملف المرجعي مطلوب / Reference file is required'}, status=400)

    from apps.tools.reference_to_video.models import ReferenceToVideoSetting, ReferenceToVideoModelPricing

    setting = ReferenceToVideoSetting.objects.first()
    if setting:
        if not setting.is_active:
            return JsonResponse({'error': 'الأداة معطلة حالياً من قبل الإدارة / Tool is currently disabled'}, status=503)
        if setting.is_maintenance_mode:
            return JsonResponse({'error': 'الأداة في وضع الصيانة حالياً / Tool is under maintenance'}, status=503)

    pricing = ReferenceToVideoModelPricing.objects.filter(is_active=True).first()
    cost = pricing.fixed_cost if pricing else Decimal('6.0000')
    allow_premium = (pricing.allowed_wallet in ('premium', 'both')) if pricing else True

    try:
        deduction = WalletService.validate_and_charge(
            user_id=str(request.user.id),
            cost=cost,
            tool_name='reference_to_video',
            allow_premium=allow_premium
        )
    except InsufficientCreditsError as e:
        return JsonResponse({'error': str(e)}, status=402)

    object_name = f"inputs/r2v/{request.user.id}/{ref_file.name}"
    storage_service.upload_file_bytes(ref_file.read(), object_name, ref_file.content_type or "video/mp4")
    ref_url = storage_service.get_presigned_url(object_name)

    record = ReferenceToVideoGeneration.objects.create(
        user=request.user,
        reference_media_url=ref_url,
        prompt=prompt,
        model_name='seedance',
        status='processing',
        standard_credits_used=deduction['standard_deducted'],
        premium_credits_used=deduction['premium_deducted']
    )

    inngest_client.send_sync(
        inngest.Event(
            name="tools/reference_to_video.generate",
            data={
                "task_id": str(record.id),
                "user_id": str(request.user.id),
                "model_name": "seedance",
                "standard_credits": float(deduction['standard_deducted']),
                "premium_credits": float(deduction['premium_deducted']),
            }
        )
    )

    return JsonResponse({'task_id': str(record.id), 'status': 'processing', 'cost': float(cost)})
