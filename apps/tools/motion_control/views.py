from decimal import Decimal
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import inngest
from inngest_client import inngest_client
from apps.tools.motion_control.models import MotionControlGeneration
from apps.core.storage import storage_service
from apps.billing.services import WalletService, InsufficientCreditsError

@login_required
def motion_control_workspace_view(request):
    history = MotionControlGeneration.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'tools/motion_control_workspace.html', {
        'history': history,
        'tool_title_ar': 'التحكم في الحركة (Motion Control)',
        'tool_title_en': 'Motion Control',
    })

@login_required
@require_POST
def motion_control_generate_view(request):
    image_file = request.FILES.get('image')
    motion_video_file = request.FILES.get('motion_video')

    if not image_file or not motion_video_file:
        return JsonResponse({'error': 'الصورة وفيديو الحركة مطلوبان / Image and motion video are required'}, status=400)

    # Cost: 10.0 credits flat rate
    cost = Decimal('10.0000')

    try:
        deduction = WalletService.validate_and_charge(
            user_id=str(request.user.id),
            cost=cost,
            tool_name='motion_control'
        )
    except InsufficientCreditsError as e:
        return JsonResponse({'error': str(e)}, status=402)

    img_name = f"inputs/motion/{request.user.id}/img_{image_file.name}"
    storage_service.upload_file_bytes(image_file.read(), img_name, image_file.content_type or "image/png")
    image_url = storage_service.get_presigned_url(img_name)

    vid_name = f"inputs/motion/{request.user.id}/vid_{motion_video_file.name}"
    storage_service.upload_file_bytes(motion_video_file.read(), vid_name, motion_video_file.content_type or "video/mp4")
    motion_url = storage_service.get_presigned_url(vid_name)

    record = MotionControlGeneration.objects.create(
        user=request.user,
        input_image_url=image_url,
        input_motion_video_url=motion_url,
        status='processing',
        standard_credits_used=deduction['standard_deducted'],
        premium_credits_used=deduction['premium_deducted']
    )

    inngest_client.send_sync(
        inngest.Event(
            name="tools/motion_control.generate",
            data={
                "task_id": str(record.id),
                "user_id": str(request.user.id),
                "standard_credits": float(deduction['standard_deducted']),
                "premium_credits": float(deduction['premium_deducted']),
            }
        )
    )

    return JsonResponse({'task_id': str(record.id), 'status': 'processing', 'cost': float(cost)})
