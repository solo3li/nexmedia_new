from decimal import Decimal
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import inngest
from inngest_client import inngest_client
from apps.tools.stt.models import SttTranscription
from apps.core.storage import storage_service
from apps.billing.services import WalletService, InsufficientCreditsError

@login_required
def stt_workspace_view(request):
    history = SttTranscription.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'tools/stt_workspace.html', {
        'history': history,
        'tool_title_ar': 'تحويل الصوت إلى نص (تفريغ صوتي)',
        'tool_title_en': 'Voice to Text (Transcription)',
    })

@login_required
@require_POST
def stt_transcribe_view(request):
    audio_file = request.FILES.get('audio')
    if not audio_file:
        return JsonResponse({'error': 'ملف الصوت مطلوب / Audio file required'}, status=400)

    # Base cost: 1.0 credit per audio transcription
    cost = Decimal('1.0000')

    try:
        deduction = WalletService.validate_and_charge(
            user_id=str(request.user.id),
            cost=cost,
            tool_name='stt'
        )
    except InsufficientCreditsError as e:
        return JsonResponse({'error': str(e)}, status=402)

    object_name = f"stt/{request.user.id}/{audio_file.name}"
    storage_service.upload_file_bytes(audio_file.read(), object_name, audio_file.content_type or "audio/mpeg")
    audio_url = storage_service.get_presigned_url(object_name)

    record = SttTranscription.objects.create(
        user=request.user,
        audio_url=audio_url,
        language=request.POST.get('language', 'auto'),
        translate=request.POST.get('translate') == 'true',
        status='processing',
        standard_credits_used=deduction['standard_deducted'],
        premium_credits_used=deduction['premium_deducted']
    )

    inngest_client.send_sync(
        inngest.Event(
            name="tools/stt.transcribe",
            data={
                "task_id": str(record.id),
                "user_id": str(request.user.id),
                "audio_url": audio_url,
                "standard_credits": float(deduction['standard_deducted']),
                "premium_credits": float(deduction['premium_deducted']),
            }
        )
    )

    return JsonResponse({'task_id': str(record.id), 'status': 'processing'})
