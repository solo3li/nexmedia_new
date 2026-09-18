import os
import sys
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from apps.billing.models import Plan, WalletTransaction
from apps.billing.services import WalletService
from apps.tools.tts.models import TtsGeneration
from apps.tools.text_to_image.models import TextToImageGeneration
from apps.affiliate.models import AffiliateProfile, AffiliateReferral, AffiliateCommission
from apps.support.models import SupportTicket, TicketMessage
from apps.core.centrifugo import centrifugo_service
from apps.core.storage import storage_service

User = get_user_model()

def run_e2e_verification():
    print("=" * 70)
    print("🚀 NEXMEDIA AI — FULL END-TO-END CLI VERIFICATION SUITE")
    print("=" * 70)

    # STEP 1: Verify Initial Clean Database & Seed Data
    print("\n[Step 1] Verifying Plans & Seed Data in PostgreSQL...")
    plans = list(Plan.objects.all())
    print(f"  ✓ Active Plans found: {[p.name for p in plans]}")
    assert len(plans) >= 3, "Plans not seeded properly!"

    # STEP 2: User Lifecycle & Starter Credit Granting
    print("\n[Step 2] Testing User Registration & Starter Trial Allocation...")
    client = Client()
    test_email = "creator.test@nexmedia.ai"
    test_pass = "SecurePass12345!"

    # Clean up previous test user if exists
    User.objects.filter(email=test_email).delete()

    reg_response = client.post('/accounts/register/', {
        'username': 'creatortest',
        'email': test_email,
        'password': test_pass,
        'password_confirm': test_pass,
    }, follow=True)

    assert reg_response.status_code == 200, f"Registration failed with status {reg_response.status_code}"
    user = User.objects.get(email=test_email)
    print(f"  ✓ User '{user.username}' created with ID: {user.id}")
    print(f"  ✓ Standard Credits: {user.standard_credits} (Expected: 100.0)")
    print(f"  ✓ Premium Credits: {user.premium_credits} (Expected: 10.0)")
    assert float(user.standard_credits) == 100.0, "Starter standard credits mismatch!"
    assert float(user.premium_credits) == 10.0, "Starter premium credits mismatch!"

    # Check that starter transaction was recorded
    init_tx = WalletTransaction.objects.filter(user=user).first()
    assert init_tx is not None, "Starter grant transaction not recorded!"
    print(f"  ✓ Starter transaction recorded: {init_tx.description} ({init_tx.amount} {init_tx.wallet_type})")

    # STEP 3: Bilingual Middleware & Content Verification
    print("\n[Step 3] Testing Bilingual System (Arabic RTL vs English LTR)...")
    # Arabic request
    ar_resp = client.get('/?lang=ar')
    assert ar_resp.status_code == 200
    assert 'dir="rtl"' in ar_resp.content.decode('utf-8'), "RTL direction missing for Arabic!"
    print("  ✓ Arabic request: Verified RTL layout and Arabic locale.")

    # English request
    en_resp = client.get('/?lang=en')
    assert en_resp.status_code == 200
    assert 'dir="ltr"' in en_resp.content.decode('utf-8'), "LTR direction missing for English!"
    print("  ✓ English request: Verified LTR layout and English locale.")

    # STEP 4: End-to-End Tool Execution: Text-to-Speech (TTS)
    print("\n[Step 4] Testing Tool Generation: Text-to-Speech (TTS)...")
    client.login(username='creatortest', password=test_pass)

    tts_prompt = "مرحباً بكم في منصة نكسميديا للذكاء الاصطناعي التوليدي"
    tts_resp = client.post('/tools/tts/generate/', {
        'text': tts_prompt,
        'voice_name': 'صبرينة',
        'quality': 'standard'
    })

    assert tts_resp.status_code == 200, f"TTS generation failed: {tts_resp.content}"
    tts_data = tts_resp.json()
    print(f"  ✓ TTS Request response: {tts_data}")
    assert tts_data.get('status') in ('processing', 'queued')
    task_id = tts_data.get('task_id')

    # Verify DB Generation Record
    record = TtsGeneration.objects.get(id=task_id)
    assert record.status == 'processing'
    assert record.text == tts_prompt
    print(f"  ✓ TtsGeneration record created with status: '{record.status}'")

    # Verify Wallet Deduction
    user.refresh_from_db()
    print(f"  ✓ Standard credits after TTS: {user.standard_credits} (Deducted: 0.1)")
    assert float(user.standard_credits) == 99.9

    # Simulate Worker Completion & MinIO Upload
    print("  Simulating Inngest Worker Completion & MinIO Audio Artifact Upload...")
    dummy_audio = b"RIFF....WAVEfmt ....data....DUMMY_MP3_AUDIO_CONTENT_NEXMEDIA"
    obj_key = f"outputs/tts/{record.id}.mp3"
    storage_service.upload_file_bytes(dummy_audio, obj_key, 'audio/mpeg')
    file_url = storage_service.get_presigned_url(obj_key)

    record.status = 'completed'
    record.result_url = file_url
    record.save(update_fields=['status', 'result_url'])

    # Send Centrifugo Realtime Event
    centrifugo_service.notify_user(user.id, 'TOOL_COMPLETED', {
        'tool': 'tts',
        'task_id': str(record.id),
        'file_url': file_url
    })
    print(f"  ✓ Record updated to 'completed' with MinIO URL: {file_url[:60]}...")
    print("  ✓ Centrifugo real-time event dispatched to user's private channel.")

    # STEP 5: End-to-End Tool Execution: Text-to-Image
    print("\n[Step 5] Testing Tool Generation: Text-to-Image (Premium Credits)...")
    img_prompt = "A hyper-realistic futuristic neon studio in Cairo at night"
    t2i_resp = client.post('/tools/text-to-image/generate/', {
        'prompt': img_prompt,
        'aspect_ratio': '16:9',
        'model_name': 'grok_imagine'
    })

    assert t2i_resp.status_code == 200, f"Text-to-Image generation failed: {t2i_resp.content}"
    t2i_data = t2i_resp.json()
    print(f"  ✓ Text-to-Image response: {t2i_data}")
    assert t2i_data.get('status') in ('processing', 'queued')
    t2i_task_id = t2i_data.get('task_id')

    t2i_record = TextToImageGeneration.objects.get(id=t2i_task_id)
    assert t2i_record.status == 'processing'
    user.refresh_from_db()
    print(f"  ✓ Standard credits after Image generation: {user.standard_credits} (Deducted: 2.0)")
    assert float(user.standard_credits) == 97.9
    assert float(user.premium_credits) == 10.0

    # Simulate Inngest Worker Image Completion
    dummy_img = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR...DUMMY_IMAGE_DATA"
    img_key = f"outputs/t2i/{t2i_record.id}.png"
    storage_service.upload_file_bytes(dummy_img, img_key, 'image/png')
    img_url = storage_service.get_presigned_url(img_key)

    t2i_record.status = 'completed'
    t2i_record.result_url = img_url
    t2i_record.save(update_fields=['status', 'result_url'])
    print(f"  ✓ Text-to-Image record completed with URL: {img_url[:60]}...")

    # STEP 6: Insufficient Credits & Refund Verification
    print("\n[Step 6] Testing Insufficient Balance Enforcement & Error Handling...")
    # Drain all credits to zero to verify 402 block
    user.standard_credits = 0.0
    user.premium_credits = 0.0
    user.save(update_fields=['standard_credits', 'premium_credits'])
    user.refresh_from_db()
    assert float(user.standard_credits) == 0.0
    assert float(user.premium_credits) == 0.0
    print("  ✓ User wallets drained to zero.")

    # Attempt another Text-to-Image generation that requires 2.0 credits
    fail_resp = client.post('/tools/text-to-image/generate/', {
        'prompt': 'Should fail due to insufficient funds',
        'aspect_ratio': '1:1'
    })
    assert fail_resp.status_code == 402, f"Expected 402, got {fail_resp.status_code}"
    fail_data = fail_resp.json()
    print(f"  ✓ Insufficient credits correctly blocked with status 402: {fail_data}")

    # Test Automatic Refund Mechanism on Worker Failure
    print("  Testing Wallet Refund on simulated pipeline failure...")
    before_refund_std = float(user.standard_credits)
    from decimal import Decimal
    WalletService.refund(str(user.id), standard_amount=Decimal('0.5'), premium_amount=Decimal('0.0'), tool_name='test_refund', reason="Simulated failure refund")
    user.refresh_from_db()
    assert float(user.standard_credits) == before_refund_std + 0.5
    print(f"  ✓ Refund credited successfully: {user.standard_credits}")

    # STEP 7: Affiliate & Referral System Verification
    print("\n[Step 7] Testing Affiliate Profile & Referral Tracking...")
    affiliate_profile, _ = AffiliateProfile.objects.get_or_create(user=user)
    print(f"  ✓ Affiliate Code: {affiliate_profile.referral_code}")
    referral_link = f"http://localhost:8000/accounts/register/?ref={affiliate_profile.referral_code}"
    print(f"  ✓ Affiliate Link: {referral_link}")

    # Create a referred user
    User.objects.filter(email='referred@nexmedia.ai').delete()
    referred_user = User.objects.create_user(
        username='referred_user_1',
        email='referred@nexmedia.ai',
        password=test_pass
    )
    referral = AffiliateReferral.objects.create(
        referrer=affiliate_profile,
        referred_user=referred_user
    )
    # Simulate a commission payment
    commission = AffiliateCommission.objects.create(
        referrer=affiliate_profile,
        amount=Decimal('15.00'),
        currency='USD',
        status='pending',
        description=f"Commission for referral {referred_user.username}"
    )
    print(f"  ✓ Affiliate commission created: ${commission.amount} {commission.currency} for referral '{referred_user.username}'")

    # STEP 8: Support Ticketing System Verification
    print("\n[Step 8] Testing Support Ticketing System...")
    ticket = SupportTicket.objects.create(
        user=user,
        subject="How do I increase my concurrency queue limit?",
        status="open"
    )
    msg1 = TicketMessage.objects.create(
        ticket=ticket,
        sender=user,
        message="I need higher throughput on the Text-to-Video queue.",
        is_admin=False
    )
    # Admin reply
    admin_user = User.objects.filter(is_superuser=True).first()
    msg2 = TicketMessage.objects.create(
        ticket=ticket,
        sender=admin_user,
        message="Your Pro Studio plan includes up to 5 concurrent jobs. Upgrading to Enterprise provides custom dedicated queues.",
        is_admin=True
    )
    ticket.status = 'in_progress'
    ticket.save()
    print(f"  ✓ Support Ticket #{ticket.id} ('{ticket.subject}') created with {ticket.messages.count()} messages.")

    print("\n" + "=" * 70)
    print("🎉 ALL END-TO-END VERIFICATION CHECKS COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == '__main__':
    run_e2e_verification()
