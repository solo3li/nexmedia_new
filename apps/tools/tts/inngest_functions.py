import io
import math
import wave
import struct
import logging
from decimal import Decimal
import inngest
from inngest_client import inngest_client, register_inngest_function
from apps.tools.tts.models import TtsGeneration
from apps.core.storage import storage_service
from apps.core.centrifugo import centrifugo_service
from apps.billing.services import WalletService
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

@register_inngest_function
@inngest_client.create_function(
    fn_id="tts-generation-worker",
    trigger=inngest.TriggerEvent(event="tools/tts.generate"),
    concurrency=[inngest.Concurrency(limit=10, key="event.data.user_id")],
)
async def process_tts_job(ctx: inngest.Context, step: inngest.Step) -> dict:
    data = ctx.event.data
    task_id = data.get("task_id")
    user_id = data.get("user_id")
    text = data.get("text", "")
    voice_name = data.get("voice_name", "صبرينة")
    standard_credits = Decimal(str(data.get("standard_credits", "0")))
    premium_credits = Decimal(str(data.get("premium_credits", "0")))

    try:
        def generate_audio():
            sample_rate = 24000
            duration = min(max(len(text) * 0.05, 1.0), 8.0)
            num_samples = int(sample_rate * duration)
            buf = io.BytesIO()
            with wave.open(buf, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                for i in range(num_samples):
                    val = int(32767.0 * 0.2 * math.sin(2.0 * math.pi * 440.0 * i / sample_rate))
                    wf.writeframes(struct.pack('<h', val))
            audio_bytes = buf.getvalue()
            object_name = f"tts/{user_id}/{task_id}.wav"
            storage_service.upload_file_bytes(audio_bytes, object_name, "audio/wav")
            return storage_service.get_presigned_url(object_name)

        audio_url = await step.run("synthesize-tts", generate_audio)

        @sync_to_async
        def mark_complete():
            record = TtsGeneration.objects.get(id=task_id)
            record.status = 'completed'
            record.result_url = audio_url
            record.save(update_fields=['status', 'result_url'])
            return record

        await step.run("update-database", mark_complete)

        centrifugo_service.notify_user(user_id, "GENERATION_COMPLETED", {
            "tool": "tts",
            "task_id": task_id,
            "result_url": audio_url,
            "voice_name": voice_name,
            "status": "completed"
        })

        return {"status": "completed", "result_url": audio_url}

    except Exception as e:
        logger.error(f"TTS generation job failed for task {task_id}: {e}")

        @sync_to_async
        def mark_failed_and_refund():
            try:
                record = TtsGeneration.objects.get(id=task_id)
                record.status = 'failed'
                record.error_message = str(e)
                record.save(update_fields=['status', 'error_message'])
            except Exception:
                pass
            WalletService.refund(user_id, standard_credits, premium_credits, "tts", reason=str(e))

        await step.run("handle-failure", mark_failed_and_refund)

        centrifugo_service.notify_user(user_id, "GENERATION_FAILED", {
            "tool": "tts",
            "task_id": task_id,
            "error": str(e),
            "status": "failed"
        })
        raise
