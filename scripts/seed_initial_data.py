import os
import sys
from decimal import Decimal
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import django
django.setup()

from django.contrib.auth import get_user_model
from apps.billing.models import Plan, ManualPaymentMethod
from apps.content.models import BlogPost, CustomPage
from apps.billing.services import WalletService

User = get_user_model()

def seed_all():
    print("🌱 Starting NexMedia Database Seeding...")

    # 1. Superuser / Admin
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@nexmedia.local',
            'is_staff': True,
            'is_superuser': True,
            'standard_credits': Decimal('9999.0000'),
            'premium_credits': Decimal('9999.0000'),
        }
    )
    if created:
        admin_user.set_password('admin123456')
        admin_user.save()
        print("  ✓ Superuser created: admin / admin123456")
    else:
        print("  ✓ Superuser already exists: admin")

    # 2. Subscription Plans
    trial_plan, _ = Plan.objects.get_or_create(
        name="Free Trial",
        defaults={
            'name_ar': "التجربة المجانية",
            'description': "Starter credits to explore all 9 AI tools for free.",
            'description_ar': "رصيد تجريبي مجاني لاستكشاف جميع أدوات الذكاء الاصطناعي.",
            'price_usd': Decimal('0.00'),
            'price_egp': Decimal('0.00'),
            'duration_days': 14,
            'standard_credits_grant': Decimal('100.0000'),
            'premium_credits_grant': Decimal('10.0000'),
            'is_free_trial': True,
            'is_default_registration_plan': True,
            'is_active': True
        }
    )
    print("  ✓ Plan seeded: Free Trial")

    creator_plan, _ = Plan.objects.get_or_create(
        name="Creator",
        defaults={
            'name_ar': "صانع المحتوى",
            'description': "Perfect for individual content creators and voice artists.",
            'description_ar': "مثالي لصناع المحتوى المستقلين وفناني الصوت.",
            'price_usd': Decimal('19.00'),
            'price_egp': Decimal('550.00'),
            'duration_days': 30,
            'standard_credits_grant': Decimal('500.0000'),
            'premium_credits_grant': Decimal('50.0000'),
            'is_active': True
        }
    )
    print("  ✓ Plan seeded: Creator ($19)")

    pro_plan, _ = Plan.objects.get_or_create(
        name="Pro Studio",
        defaults={
            'name_ar': "استوديو احترافي",
            'description': "High concurrency, full studio video diffusion & avatar generation.",
            'description_ar': "أعلى سرعة مع وصول كامل لتوليد الفيديو والأفاتار الرقمي.",
            'price_usd': Decimal('49.00'),
            'price_egp': Decimal('1400.00'),
            'duration_days': 30,
            'standard_credits_grant': Decimal('1500.0000'),
            'premium_credits_grant': Decimal('200.0000'),
            'is_active': True
        }
    )
    print("  ✓ Plan seeded: Pro Studio ($49)")

    # 3. Manual Payment Methods
    methods = [
        ("Vodafone Cash / فودافون كاش", "01012345678", "قم بالتحويل لرقم المحفظة ثم ارفع صورة الإيصال."),
        ("InstaPay / إنستاباي", "nexmedia@instapay", "قم بالتحويل لحساب إنستاباي ثم ارفع لقطة الشاشة."),
        ("Bank Wire / تحويل بنكي", "CIB - IBAN: EG12000000000000001234567", "التحويل البنكي المباشر مع كتابة اسم المستخدم في خانة الملاحظات.")
    ]
    for name, details, instructions in methods:
        ManualPaymentMethod.objects.get_or_create(
            name=name,
            defaults={'account_details': details, 'instructions': instructions, 'is_active': True}
        )
    print("  ✓ Manual payment methods seeded")

    # 4. Bilingual Blog Articles
    BlogPost.objects.get_or_create(
        slug="google-veo-3-1-next-evolution",
        defaults={
            'category': 'models',
            'title_en': 'Google Veo 3.1: The Next Evolution in AI Video Generation',
            'title_ar': 'جوجل Veo 3.1: التطور الثوري القادم في توليد الفيديو بالذكاء الاصطناعي',
            'content_en': '<p>Google Veo 3.1 introduces a groundbreaking latent diffusion architecture. It simulates real fluid physics, motion blur, and cinematic camera controls.</p>',
            'content_ar': '<p>يقدم نموذج Google Veo 3.1 معمارية جديدة كلياً لمحاكاة فيزياء الحركة الواقعية والتحكم السينمائي بالكاميرا في توليد الفيديو.</p>',
            'is_published': True
        }
    )

    BlogPost.objects.get_or_create(
        slug="ultimate-guide-ai-lip-syncing",
        defaults={
            'category': 'tutorials',
            'title_en': 'The Ultimate Guide to AI Lip-Syncing for Avatars',
            'title_ar': 'الدليل الشامل لمزامنة الشفاه بالذكاء الاصطناعي للأفاتار',
            'content_en': '<p>Learn how to produce perfectly synced digital avatar videos with Vidu Studio on NexMedia AI platform.</p>',
            'content_ar': '<p>تعرف على كيفية إنشاء مقاطع أفاتار رقمية متحدثة بمزامنة شفاه متقنة باستخدام استوديو Vidu في نكسميديا.</p>',
            'is_published': True
        }
    )
    print("  ✓ Bilingual Blog Articles seeded")

    # 5. CMS Custom Pages
    CustomPage.objects.get_or_create(
        slug="about-us",
        defaults={
            'title_en': 'About NexMedia AI',
            'title_ar': 'عن منصة نكسميديا',
            'content_en': '<p>NexMedia is the premier bilingual creative AI platform delivering next-generation text-to-speech, video diffusion, and digital avatars.</p>',
            'content_ar': '<p>نكسميديا هي منصة الذكاء الاصطناعي التوليدي الرائدة المتخصصة في تحويل النص لكلام، توليد الفيديو، والأفاتار الرقمي.</p>',
            'is_published': True
        }
    )
    print("  ✓ CMS Custom Pages seeded")

    # 6. Seed All 9 Tool Settings & Model Pricings
    from apps.tools.tts.models import TtsSetting, TtsModelPricing
    from apps.tools.stt.models import SttSetting, SttModelPricing
    from apps.tools.text_to_video.models import TextToVideoSetting, TextToVideoModelPricing
    from apps.tools.image_to_video.models import ImageToVideoSetting, ImageToVideoModelPricing
    from apps.tools.reference_to_video.models import ReferenceToVideoSetting, ReferenceToVideoModelPricing
    from apps.tools.lipsync.models import LipSyncSetting, LipSyncModelPricing
    from apps.tools.motion_control.models import MotionControlSetting, MotionControlModelPricing
    from apps.tools.text_to_image.models import TextToImageSetting, TextToImageModelPricing
    from apps.tools.avatar_video.models import AvatarVideoSetting, AvatarVideoModelPricing

    # TTS
    TtsSetting.objects.get_or_create(id="00000000-0000-0000-0000-000000000001", defaults={'is_active': True, 'max_text_length': 5000, 'max_concurrent_operations': 10})
    TtsModelPricing.objects.get_or_create(quality_level='standard', defaults={'model_name': 'gemini-2.5-flash-preview-tts', 'provider_name': 'Gemini', 'fixed_cost': Decimal('0.1000'), 'is_active': True})
    TtsModelPricing.objects.get_or_create(quality_level='high', defaults={'model_name': 'gemini-2.5-flash-preview-tts', 'provider_name': 'Gemini', 'fixed_cost': Decimal('0.2500'), 'is_active': True})

    # STT
    SttSetting.objects.get_or_create(id="00000000-0000-0000-0000-000000000002", defaults={'is_active': True, 'max_audio_size_mb': 25, 'max_duration_seconds': 300})
    SttModelPricing.objects.get_or_create(model_name='whisper-large-v3', defaults={'provider_name': 'Whisper', 'fixed_cost': Decimal('0.5000'), 'cost_per_minute': Decimal('0.2000'), 'is_active': True})

    # Text to Video
    TextToVideoSetting.objects.get_or_create(id="00000000-0000-0000-0000-000000000003", defaults={'is_active': True, 'default_resolution': '720p', 'max_duration_seconds': 30})
    TextToVideoModelPricing.objects.get_or_create(model_name='veo 3.1 Fast', defaults={'provider_name': 'CrunAI', 'fixed_cost_720p': Decimal('30.0000'), 'fixed_cost_1080p': Decimal('37.5000'), 'fixed_cost_4k': Decimal('90.0000'), 'is_active': True})
    TextToVideoModelPricing.objects.get_or_create(model_name='grok-imagine', defaults={'provider_name': 'CrunAI', 'billing_type': 'per_second', 'cost_per_second_720p': Decimal('4.5000'), 'cost_per_second_1080p': Decimal('8.0000'), 'is_active': True})

    # Image to Video
    ImageToVideoSetting.objects.get_or_create(id="00000000-0000-0000-0000-000000000004", defaults={'is_active': True, 'max_duration_seconds': 30, 'max_image_size_mb': 25})
    ImageToVideoModelPricing.objects.get_or_create(model_name='veo 3.1 Fast', defaults={'provider_name': 'CrunAI', 'fixed_cost_720p': Decimal('30.0000'), 'fixed_cost_1080p': Decimal('37.5000'), 'is_active': True})

    # Reference to Video
    ReferenceToVideoSetting.objects.get_or_create(id="00000000-0000-0000-0000-000000000005", defaults={'is_active': True, 'max_duration_seconds': 30})
    ReferenceToVideoModelPricing.objects.get_or_create(model_name='bytedance/seedance2-0-mini-r2v', defaults={'provider_name': 'CrunAI', 'fixed_cost': Decimal('15.0000'), 'cost_per_second_720p': Decimal('0.0286'), 'is_active': True})

    # LipSync
    LipSyncSetting.objects.get_or_create(id="00000000-0000-0000-0000-000000000006", defaults={'is_active': True, 'max_video_size_mb': 100, 'max_duration_seconds': 120})
    LipSyncModelPricing.objects.get_or_create(model_name='vidu-lipsync-std', defaults={'provider_name': 'CrunAI', 'cost_per_generation': Decimal('10.0000'), 'cost_per_second': Decimal('0.5000'), 'is_active': True})

    # Motion Control
    MotionControlSetting.objects.get_or_create(id="00000000-0000-0000-0000-000000000007", defaults={'is_active': True, 'max_video_size_mb': 100, 'max_duration_seconds': 30})
    MotionControlModelPricing.objects.get_or_create(model_name='kling-motion-control', defaults={'provider_name': 'KlingAI', 'cost_per_generation': Decimal('20.0000'), 'cost_per_second': Decimal('2.0000'), 'is_active': True})

    # Text to Image
    TextToImageSetting.objects.get_or_create(id="00000000-0000-0000-0000-000000000008", defaults={'is_active': True, 'max_prompt_length': 2000})
    TextToImageModelPricing.objects.get_or_create(model_name='grok-imagine', defaults={'provider_name': 'CrunAI', 'cost_per_image': Decimal('2.0000'), 'is_active': True})

    # Avatar Video
    AvatarVideoSetting.objects.get_or_create(id="00000000-0000-0000-0000-000000000009", defaults={'is_active': True, 'max_text_length': 2000, 'max_duration_seconds': 60})
    AvatarVideoModelPricing.objects.get_or_create(model_name='kling-avatar', defaults={'provider_name': 'KlingAI', 'cost_per_generation': Decimal('15.0000'), 'cost_per_second': Decimal('1.0000'), 'is_active': True})

    print("  ✓ All 9 Tool Settings & Model Pricings seeded")

    print("🎉 Database seeding completed successfully!")

if __name__ == '__main__':
    seed_all()
