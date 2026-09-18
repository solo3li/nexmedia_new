import inngest
import logging
from decimal import Decimal
from inngest_client import inngest_client, register_inngest_function
from apps.tools.text_to_image.models import TextToImageGeneration
from apps.core.storage import storage_service
from apps.core.centrifugo import centrifugo_service
from apps.billing.services import WalletService
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

@register_inngest_function
@inngest_client.create_function(
    fn_id="text-to-image-worker",
    trigger=inngest.TriggerEvent(event="tools/text_to_image.generate"),
    concurrency=[inngest.Concurrency(limit=10, key="event.data.user_id")],
)
async def process_text_to_image_job(ctx: inngest.Context, step: inngest.Step) -> dict:
    data = ctx.event.data
    task_id = data.get("task_id")
    user_id = data.get("user_id")
    standard_credits = Decimal(str(data.get("standard_credits", "0")))
    premium_credits = Decimal(str(data.get("premium_credits", "0")))

    try:
        def render_image():
            # Generate dummy 1x1 png bytes
            dummy_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\r\xefU\xbf\x00\x00\x00\x00IEND\xaeB`\x82"
            object_name = f"images/t2i/{user_id}/{task_id}.png"
            storage_service.upload_file_bytes(dummy_png, object_name, "image/png")
            return storage_service.get_presigned_url(object_name)

        image_url = await step.run("render-image-pipeline", render_image)

        @sync_to_async
        def mark_complete():
            record = TextToImageGeneration.objects.get(id=task_id)
            record.status = 'completed'
            record.result_url = image_url
            record.save(update_fields=['status', 'result_url'])
            return record

        await step.run("update-database", mark_complete)

        centrifugo_service.notify_user(user_id, "GENERATION_COMPLETED", {
            "tool": "text_to_image",
            "task_id": task_id,
            "result_url": image_url,
            "status": "completed"
        })

        return {"status": "completed", "result_url": image_url}

    except Exception as e:
        logger.error(f"Text-to-Image failed for task {task_id}: {e}")

        @sync_to_async
        def mark_failed():
            try:
                record = TextToImageGeneration.objects.get(id=task_id)
                record.status = 'failed'
                record.error_message = str(e)
                record.save(update_fields=['status', 'error_message'])
            except Exception:
                pass
            WalletService.refund(user_id, standard_credits, premium_credits, "text_to_image", reason=str(e))

        await step.run("handle-failure", mark_failed)

        centrifugo_service.notify_user(user_id, "GENERATION_FAILED", {
            "tool": "text_to_image",
            "task_id": task_id,
            "error": str(e),
            "status": "failed"
        })
        raise
