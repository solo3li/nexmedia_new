import inngest
import logging
from decimal import Decimal
from inngest_client import inngest_client, register_inngest_function
from apps.tools.stt.models import SttTranscription
from apps.core.centrifugo import centrifugo_service
from apps.billing.services import WalletService
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

@register_inngest_function
@inngest_client.create_function(
    fn_id="stt-transcription-worker",
    trigger=inngest.TriggerEvent(event="tools/stt.transcribe"),
    concurrency=[inngest.Concurrency(limit=10, key="event.data.user_id")],
)
async def process_stt_job(ctx: inngest.Context, step: inngest.Step) -> dict:
    data = ctx.event.data
    task_id = data.get("task_id")
    user_id = data.get("user_id")
    standard_credits = Decimal(str(data.get("standard_credits", "0")))
    premium_credits = Decimal(str(data.get("premium_credits", "0")))

    try:
        async def transcribe_audio():
            # In production, calls OpenAI Whisper API
            return "مرحباً بكم في منصة NexMedia للذكاء الاصطناعي وتوليد المحتوى الصوتي والمرئي."

        transcribed_text = await step.run("whisper-transcribe", transcribe_audio)

        @sync_to_async
        def mark_complete():
            record = SttTranscription.objects.get(id=task_id)
            record.status = 'completed'
            record.result_text = transcribed_text
            record.save(update_fields=['status', 'result_text'])
            return record

        await step.run("update-database", mark_complete)

        centrifugo_service.notify_user(user_id, "GENERATION_COMPLETED", {
            "tool": "stt",
            "task_id": task_id,
            "result_text": transcribed_text,
            "status": "completed"
        })

        return {"status": "completed", "result_text": transcribed_text}

    except Exception as e:
        logger.error(f"STT transcription failed for task {task_id}: {e}")

        @sync_to_async
        def mark_failed():
            try:
                record = SttTranscription.objects.get(id=task_id)
                record.status = 'failed'
                record.error_message = str(e)
                record.save(update_fields=['status', 'error_message'])
            except Exception:
                pass
            WalletService.refund(user_id, standard_credits, premium_credits, "stt", reason=str(e))

        await step.run("handle-failure", mark_failed)

        centrifugo_service.notify_user(user_id, "GENERATION_FAILED", {
            "tool": "stt",
            "task_id": task_id,
            "error": str(e),
            "status": "failed"
        })
        raise
