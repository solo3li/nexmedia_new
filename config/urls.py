from django.contrib import admin
from django.urls import path, include
from inngest_client import inngest_client, get_all_inngest_functions
import inngest.django
from apps.core import views as core_views

inngest_url_pattern = inngest.django.serve(
    inngest_client,
    get_all_inngest_functions(),
    serve_path="/api/inngest",
    enable_unauthed_sync=True
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Inngest Background Webhook
    inngest_url_pattern,

    # Dashboard & Realtime
    path('', core_views.dashboard_view, name='dashboard'),
    path('api/centrifugo-token/', core_views.centrifugo_token_view, name='centrifugo_token'),

    # Modular Business Apps
    path('accounts/', include('apps.accounts.urls')),
    path('billing/', include('apps.billing.urls')),
    path('content/', include('apps.content.urls')),
    path('affiliate/', include('apps.affiliate.urls')),
    path('support/', include('apps.support.urls')),

    # 9 Modular AI Tool Apps
    path('tools/tts/', include('apps.tools.tts.urls')),
    path('tools/stt/', include('apps.tools.stt.urls')),
    path('tools/text-to-video/', include('apps.tools.text_to_video.urls')),
    path('tools/image-to-video/', include('apps.tools.image_to_video.urls')),
    path('tools/reference-to-video/', include('apps.tools.reference_to_video.urls')),
    path('tools/lipsync/', include('apps.tools.lipsync.urls')),
    path('tools/motion-control/', include('apps.tools.motion_control.urls')),
    path('tools/text-to-image/', include('apps.tools.text_to_image.urls')),
    path('tools/avatar-video/', include('apps.tools.avatar_video.urls')),
]
