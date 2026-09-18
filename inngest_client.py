import inngest
import inngest.django
import logging

logger = logging.getLogger(__name__)

inngest_client = inngest.Inngest(
    app_id="nexmedia",
    is_production=False,
)

inngest_functions = []

def register_inngest_function(fn):
    inngest_functions.append(fn)
    return fn

def get_all_inngest_functions():
    # Explicitly import all 9 tool worker functions
    import apps.tools.tts.inngest_functions
    import apps.tools.stt.inngest_functions
    import apps.tools.text_to_video.inngest_functions
    import apps.tools.image_to_video.inngest_functions
    import apps.tools.reference_to_video.inngest_functions
    import apps.tools.lipsync.inngest_functions
    import apps.tools.motion_control.inngest_functions
    import apps.tools.text_to_image.inngest_functions
    import apps.tools.avatar_video.inngest_functions
    return inngest_functions
