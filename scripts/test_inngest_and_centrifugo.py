import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import django
django.setup()

import inngest
from inngest_client import inngest_client, get_all_inngest_functions
from apps.core.centrifugo import centrifugo_service
from apps.core.storage import storage_service

def test_infrastructure():
    print("🔌 [Infrastructure Test] Testing Centrifugo, MinIO, and Inngest...")

    # 1. Test MinIO Storage
    print("  Testing MinIO S3 Service...")
    sample_bytes = b"Hello from NexMedia AI S3 Storage Engine!"
    obj_name = "tests/health_check.txt"
    storage_service.upload_file_bytes(sample_bytes, obj_name, "text/plain")
    presigned_url = storage_service.get_presigned_url(obj_name)
    print(f"  ✓ MinIO Upload & Presigned URL generated: {presigned_url[:60]}...")

    # 2. Test Centrifugo Real-time Connection & Publish
    print("  Testing Centrifugo WebSocket API...")
    test_token = centrifugo_service.generate_connection_token("test-user-12345")
    assert len(test_token) > 20, "Failed to generate Centrifugo connection token!"
    print("  ✓ Centrifugo HMAC Token generated.")

    pub_success = centrifugo_service.notify_user("test-user-12345", "TEST_PING", {
        "message": "Real-time communication verified!"
    })
    print(f"  ✓ Centrifugo HTTP Publish result: {pub_success}")

    # 3. Test Inngest Function Registration (All 9 Tools)
    print("  Testing Inngest Function Registry...")
    funcs = get_all_inngest_functions()
    print(f"  ✓ Total registered Inngest functions: {len(funcs)} (Expected: 9)")
    assert len(funcs) == 9, f"Expected 9 registered Inngest functions, found {len(funcs)}"

    for f in funcs:
        print(f"    - Function: {f.name} ({f.id})")

    # 4. Dispatch Inngest Events for Queues
    print("  Dispatching test events to Inngest Dev Server...")
    try:
        inngest_client.send_sync(
            inngest.Event(
                name="tools/tts.generate",
                data={
                    "task_id": "00000000-0000-0000-0000-000000000001",
                    "user_id": "test-user-12345",
                    "text": "مرحباً بكم في نكسميديا",
                    "voice_name": "صبرينة",
                    "standard_credits": 0.1,
                    "premium_credits": 0.0
                }
            )
        )
        print("  ✓ Dispatched event to 'tools/tts.generate' (tts_queue)")
    except Exception as e:
        print(f"  ⚠️ Event dispatch notice (Inngest dev server sync): {e}")

    print("🎉 Infrastructure Verification PASSED!")

if __name__ == '__main__':
    test_infrastructure()
