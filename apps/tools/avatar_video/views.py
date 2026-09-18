from decimal import Decimal
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import inngest
from inngest_client import inngest_client
from apps.tools.avatar_video.models import AvatarVideoGeneration
from apps.core.storage import storage_service
from apps.billing.services import WalletService, InsufficientCreditsError

@login_required
def avatar_video_workspace_view(request):
    history = AvatarVideoGeneration.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'tools/avatar_video_workspace.html', {
        'history': history,
        'tool_title_ar': 'الأفاتار الرقمي المتحدث (Digital Avatar)',
        'tool_title_en': 'Digital Avatar Video',
    })

@login_required
@require_POST
def avatar_video_generate_view(request):
    avatar_image = request.FILES.get('avatar_image')
    prompt = request.POST.get('prompt', '').strip()

    if not avatar_image:
        return JsonResponse({'error': 'صورة الأفاتار مطلوبة / Avatar portrait is required'}, status=400)

    # Cost: 8.0 credits
    cost = Decimal('8.0000')

    try:
        deduction = WalletService.validate_and_charge(
            user_id=str(request.user.id),
            cost=cost,
            tool_name='avatar_video'
        )
    except InsufficientCreditsError as e:
        return JsonResponse({'error': str(e)}, status=402)

    img_name = f"inputs/avatar/{request.user.id}/{avatar_image.name}"
    storage_service.upload_file_bytes(avatar_image.read(), img_name, avatar_image.content_type or "image/png")
    image_url = storage_service.get_presigned_url(img_name)

    record = AvatarVideoGeneration.objects.create(
        user=request.user,
        avatar_image_url=image_url,
        prompt=prompt,
        status='processing',
        standard_credits_used=deduction['standard_deducted'],
        premium_credits_used=deduction['premium_deducted']
    )

    inngest_client.send_sync(
        inngest.Event(
            name="tools/avatar_video.generate",
            data={
                "task_id": str(record.id),
                "user_id": str(request.user.id),
                "standard_credits": float(deduction['standard_deducted']),
                "premium_credits": float(deduction['premium_deducted']),
            }
        )
    )

    return JsonResponse({'task_id': str(record.id), 'status': 'processing', 'cost': float(cost)})
