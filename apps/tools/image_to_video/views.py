from decimal import Decimal
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import inngest
from inngest_client import inngest_client
from apps.tools.image_to_video.models import ImageToVideoGeneration
from apps.core.storage import storage_service
from apps.billing.services import WalletService, InsufficientCreditsError

@login_required
def image_to_video_workspace_view(request):
    history = ImageToVideoGeneration.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'tools/image_to_video_workspace.html', {
        'history': history,
        'tool_title_ar': 'تحويل الصورة إلى فيديو',
        'tool_title_en': 'Image to Video',
    })

@login_required
@require_POST
def image_to_video_generate_view(request):
    image_file = request.FILES.get('image')
    prompt = request.POST.get('prompt', '').strip()
    resolution = request.POST.get('resolution', '720p')
    duration = int(request.POST.get('duration', 5))

    if not image_file:
        return JsonResponse({'error': 'الصورة مطلوبة / Image file is required'}, status=400)

    # Cost calculation: 5.0 base credits
    cost = Decimal('5.0000')

    try:
        deduction = WalletService.validate_and_charge(
            user_id=str(request.user.id),
            cost=cost,
            tool_name='image_to_video'
        )
    except InsufficientCreditsError as e:
        return JsonResponse({'error': str(e)}, status=402)

    object_name = f"inputs/i2v/{request.user.id}/{image_file.name}"
    storage_service.upload_file_bytes(image_file.read(), object_name, image_file.content_type or "image/png")
    image_url = storage_service.get_presigned_url(object_name)

    record = ImageToVideoGeneration.objects.create(
        user=request.user,
        input_image_url=image_url,
        prompt=prompt,
        resolution=resolution,
        duration_seconds=duration,
        status='processing',
        standard_credits_used=deduction['standard_deducted'],
        premium_credits_used=deduction['premium_deducted']
    )

    inngest_client.send_sync(
        inngest.Event(
            name="tools/image_to_video.generate",
            data={
                "task_id": str(record.id),
                "user_id": str(request.user.id),
                "standard_credits": float(deduction['standard_deducted']),
                "premium_credits": float(deduction['premium_deducted']),
            }
        )
    )

    return JsonResponse({'task_id': str(record.id), 'status': 'processing', 'cost': float(cost)})
