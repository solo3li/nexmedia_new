from decimal import Decimal
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import inngest
from inngest_client import inngest_client
from apps.tools.lipsync.models import LipSyncGeneration
from apps.core.storage import storage_service
from apps.billing.services import WalletService, InsufficientCreditsError

@login_required
def lipsync_workspace_view(request):
    history = LipSyncGeneration.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'tools/lipsync_workspace.html', {
        'history': history,
        'tool_title_ar': 'مزامنة حركة الشفاه (Lip-Sync)',
        'tool_title_en': 'Advanced Lip Sync',
    })

@login_required
@require_POST
def lipsync_generate_view(request):
    video_file = request.FILES.get('video')
    audio_file = request.FILES.get('audio')

    if not video_file or not audio_file:
        return JsonResponse({'error': 'الفيديو وملف الصوت مطلوبان / Both video and audio files are required'}, status=400)

    from apps.tools.lipsync.models import LipSyncSetting, LipSyncModelPricing

    setting = LipSyncSetting.objects.first()
    if setting:
        if not setting.is_active:
            return JsonResponse({'error': 'الأداة معطلة حالياً من قبل الإدارة / Tool is currently disabled'}, status=503)
        if setting.is_maintenance_mode:
            return JsonResponse({'error': 'الأداة في وضع الصيانة حالياً / Tool is under maintenance'}, status=503)

    pricing = LipSyncModelPricing.objects.filter(is_active=True).first()
    cost = pricing.cost_per_generation if pricing else Decimal('4.0000')
    allow_premium = (pricing.allowed_wallet in ('premium', 'both')) if pricing else True

    try:
        deduction = WalletService.validate_and_charge(
            user_id=str(request.user.id),
            cost=cost,
            tool_name='lipsync',
            allow_premium=allow_premium
        )
    except InsufficientCreditsError as e:
        return JsonResponse({'error': str(e)}, status=402)

    v_name = f"inputs/lipsync/{request.user.id}/video_{video_file.name}"
    storage_service.upload_file_bytes(video_file.read(), v_name, video_file.content_type or "video/mp4")
    video_url = storage_service.get_presigned_url(v_name)

    a_name = f"inputs/lipsync/{request.user.id}/audio_{audio_file.name}"
    storage_service.upload_file_bytes(audio_file.read(), a_name, audio_file.content_type or "audio/mpeg")
    audio_url = storage_service.get_presigned_url(a_name)

    record = LipSyncGeneration.objects.create(
        user=request.user,
        input_video_url=video_url,
        input_audio_url=audio_url,
        status='processing',
        standard_credits_used=deduction['standard_deducted'],
        premium_credits_used=deduction['premium_deducted']
    )

    inngest_client.send_sync(
        inngest.Event(
            name="tools/lipsync.generate",
            data={
                "task_id": str(record.id),
                "user_id": str(request.user.id),
                "standard_credits": float(deduction['standard_deducted']),
                "premium_credits": float(deduction['premium_deducted']),
            }
        )
    )

    return JsonResponse({'task_id': str(record.id), 'status': 'processing', 'cost': float(cost)})
