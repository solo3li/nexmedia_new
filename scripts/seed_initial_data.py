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

    print("🎉 Database seeding completed successfully!")

if __name__ == '__main__':
    seed_all()
