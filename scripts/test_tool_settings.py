import os
import sys
from pathlib import Path
from decimal import Decimal

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from apps.tools.tts.models import TtsSetting, TtsModelPricing
from apps.tools.stt.models import SttSetting, SttModelPricing
from apps.tools.text_to_video.models import TextToVideoSetting, TextToVideoModelPricing
from apps.tools.image_to_video.models import ImageToVideoSetting, ImageToVideoModelPricing
from apps.tools.reference_to_video.models import ReferenceToVideoSetting, ReferenceToVideoModelPricing
from apps.tools.lipsync.models import LipSyncSetting, LipSyncModelPricing
from apps.tools.motion_control.models import MotionControlSetting, MotionControlModelPricing
from apps.tools.text_to_image.models import TextToImageSetting, TextToImageModelPricing
from apps.tools.avatar_video.models import AvatarVideoSetting, AvatarVideoModelPricing

User = get_user_model()

def test_tool_settings_end_to_end():
    print("=" * 70)
    print("🛠️ TESTING DYNAMIC TOOL SETTINGS & PRICING (END-TO-END)")
    print("=" * 70)

    # 1. Verify existence of settings and pricings for all 9 tools
    print("\n[Step 1] Verifying all 9 tool settings & pricings in Database...")
    tool_settings = [
        ("TTS", TtsSetting.objects.first(), TtsModelPricing.objects.first()),
        ("STT", SttSetting.objects.first(), SttModelPricing.objects.first()),
        ("Text-to-Video", TextToVideoSetting.objects.first(), TextToVideoModelPricing.objects.first()),
        ("Image-to-Video", ImageToVideoSetting.objects.first(), ImageToVideoModelPricing.objects.first()),
        ("Reference-to-Video", ReferenceToVideoSetting.objects.first(), ReferenceToVideoModelPricing.objects.first()),
        ("LipSync", LipSyncSetting.objects.first(), LipSyncModelPricing.objects.first()),
        ("Motion-Control", MotionControlSetting.objects.first(), MotionControlModelPricing.objects.first()),
        ("Text-to-Image", TextToImageSetting.objects.first(), TextToImageModelPricing.objects.first()),
        ("Avatar-Video", AvatarVideoSetting.objects.first(), AvatarVideoModelPricing.objects.first()),
    ]

    for name, setting, pricing in tool_settings:
        assert setting is not None, f"Setting for {name} is missing!"
        assert pricing is not None, f"Pricing for {name} is missing!"
        print(f"  ✓ {name}: Setting (Active={setting.is_active}) | Pricing ({pricing.model_name}: {getattr(pricing, 'fixed_cost', getattr(pricing, 'cost_per_image', getattr(pricing, 'fixed_cost_720p', 'N/A')))})")

    # 2. Test Admin Panel Access for all 9 Tool Apps
    print("\n[Step 2] Testing Django Admin Panel URLs for Tool Settings & Pricings...")
    client = Client()
    admin_user = User.objects.filter(is_superuser=True).first()
    client.force_login(admin_user)

    admin_urls = [
        "/admin/tts/ttssetting/",
        "/admin/tts/ttsmodelpricing/",
        "/admin/stt/sttsetting/",
        "/admin/stt/sttmodelpricing/",
        "/admin/text_to_video/texttovideosetting/",
        "/admin/text_to_video/texttovideomodelpricing/",
        "/admin/image_to_video/imagetovideosetting/",
        "/admin/image_to_video/imagetovideomodelpricing/",
        "/admin/reference_to_video/referencetovideosetting/",
        "/admin/reference_to_video/referencetovideomodelpricing/",
        "/admin/lipsync/lipsyncsetting/",
        "/admin/lipsync/lipsyncmodelpricing/",
        "/admin/motion_control/motioncontrolsetting/",
        "/admin/motion_control/motioncontrolmodelpricing/",
        "/admin/text_to_image/texttoimagesetting/",
        "/admin/text_to_image/texttoimagemodelpricing/",
        "/admin/avatar_video/avatarvideosetting/",
        "/admin/avatar_video/avatarvideomodelpricing/",
    ]

    for url in admin_urls:
        resp = client.get(url)
        assert resp.status_code == 200, f"Admin URL {url} returned {resp.status_code}"
        print(f"  ✓ Admin accessible (200 OK): {url}")

    # 3. Test Dynamic Inactive Toggle Enforcement
    print("\n[Step 3] Testing Dynamic Tool Disabling (is_active = False)...")
    test_user, _ = User.objects.get_or_create(username="setting_tester", defaults={'email': "tester@example.com", 'standard_credits': 100.0})
    test_user.standard_credits = Decimal('100.0000')
    test_user.save()
    client.force_login(test_user)

    # Disable TTS
    tts_set = TtsSetting.objects.first()
    tts_set.is_active = False
    tts_set.save()

    disabled_resp = client.post('/tools/tts/generate/', {'text': 'Should fail because tool is disabled', 'voice_name': 'صبرينة'})
    assert disabled_resp.status_code == 503, f"Expected 503 for disabled tool, got {disabled_resp.status_code}"
    print(f"  ✓ Disabled tool successfully blocked with 503: {disabled_resp.json()}")

    # 4. Test Dynamic Maintenance Mode Enforcement
    print("\n[Step 4] Testing Dynamic Maintenance Mode (is_maintenance_mode = True)...")
    tts_set.is_active = True
    tts_set.is_maintenance_mode = True
    tts_set.save()

    maint_resp = client.post('/tools/tts/generate/', {'text': 'Should fail because of maintenance', 'voice_name': 'صبرينة'})
    assert maint_resp.status_code == 503, f"Expected 503 for maintenance mode, got {maint_resp.status_code}"
    print(f"  ✓ Maintenance mode successfully blocked with 503: {maint_resp.json()}")

    # Restore TTS settings
    tts_set.is_maintenance_mode = False
    tts_set.save()

    # 5. Test Dynamic Pricing Adjustment
    print("\n[Step 5] Testing Dynamic Pricing Alteration via Database...")
    t2i_pricing = TextToImageModelPricing.objects.first()
    original_price = t2i_pricing.cost_per_image

    # Change cost from 2.0 to 3.5 credits
    t2i_pricing.cost_per_image = Decimal('3.5000')
    t2i_pricing.save()

    init_bal = float(test_user.standard_credits)
    t2i_resp = client.post('/tools/text-to-image/generate/', {'prompt': 'Testing dynamic 3.5 credits price'})
    assert t2i_resp.status_code == 200, f"Failed: {t2i_resp.content}"
    assert t2i_resp.json().get('cost') == 3.5, f"Expected 3.5 cost in response, got {t2i_resp.json().get('cost')}"

    test_user.refresh_from_db()
    assert float(test_user.standard_credits) == init_bal - 3.5, "Standard credits deduction mismatch after price change!"
    print(f"  ✓ Dynamic price change verified: debited exactly 3.5 credits (Remaining: {test_user.standard_credits})")

    # Restore original price
    t2i_pricing.cost_per_image = original_price
    t2i_pricing.save()

    print("\n" + "=" * 70)
    print("🎉 DYNAMIC TOOL SETTINGS & PRICING VERIFICATION PASSED 100%!")
    print("=" * 70)

if __name__ == '__main__':
    test_tool_settings_end_to_end()
