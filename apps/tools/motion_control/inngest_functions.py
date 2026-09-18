import inngest
import logging
from decimal import Decimal
from inngest_client import inngest_client, register_inngest_function
from apps.tools.motion_control.models import MotionControlGeneration
from apps.core.storage import storage_service
from apps.core.centrifugo import centrifugo_service
from apps.billing.services import WalletService
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

@register_inngest_function
@inngest_client.create_function(
    fn_id="motion-control-worker",
    trigger=inngest.TriggerEvent(event="tools/motion_control.generate"),
    concurrency=[inngest.Concurrency(limit=5, key="event.data.user_id")],
)
async def process_motion_control_job(ctx: inngest.Context, step: inngest.Step) -> dict:
    data = ctx.event.data
    task_id = data.get("task_id")
    user_id = data.get("user_id")
    standard_credits = Decimal(str(data.get("standard_credits", "0")))
    premium_credits = Decimal(str(data.get("premium_credits", "0")))

    try:
        def render_motion_video():
            dummy_mp4 = b"\x00\x00\x00\x20ftypisom\x00\x00\x02\x00isomiso2avc1mp41"
            object_name = f"videos/motion/{user_id}/{task_id}.mp4"
            storage_service.upload_file_bytes(dummy_mp4, object_name, "video/mp4")
            return storage_service.get_presigned_url(object_name)

        video_url = await step.run("render-motion-pipeline", render_motion_video)

        @sync_to_async
        def mark_complete():
            record = MotionControlGeneration.objects.get(id=task_id)
            record.status = 'completed'
            record.result_url = video_url
            record.save(update_fields=['status', 'result_url'])
            return record

        await step.run("update-database", mark_complete)

        centrifugo_service.notify_user(user_id, "GENERATION_COMPLETED", {
            "tool": "motion_control",
            "task_id": task_id,
            "result_url": video_url,
            "status": "completed"
        })

        return {"status": "completed", "result_url": video_url}

    except Exception as e:
        logger.error(f"Motion control failed for task {task_id}: {e}")

        @sync_to_async
        def mark_failed():
            try:
                record = MotionControlGeneration.objects.get(id=task_id)
                record.status = 'failed'
                record.error_message = str(e)
                record.save(update_fields=['status', 'error_message'])
            except Exception:
                pass
            WalletService.refund(user_id, standard_credits, premium_credits, "motion_control", reason=str(e))

        await step.run("handle-failure", mark_failed)

        centrifugo_service.notify_user(user_id, "GENERATION_FAILED", {
            "tool": "motion_control",
            "task_id": task_id,
            "error": str(e),
            "status": "failed"
        })
        raise
