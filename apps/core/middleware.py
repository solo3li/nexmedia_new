from django.utils.deprecation import MiddlewareMixin
from django.utils import translation

class BilingualDirectionMiddleware(MiddlewareMixin):
    """
    Middleware that manages bilingual language and text direction (RTL/LTR)
    via cookies or query parameter 'lang=ar' / 'lang=en'.
    """
    def process_request(self, request):
        lang = request.GET.get('lang')
        if lang in ('ar', 'en'):
            request.session['nexmedia_lang'] = lang
        else:
            lang = request.session.get('nexmedia_lang') or request.COOKIES.get('nexmedia_lang')
            if not lang:
                accept_lang = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
                lang = 'en' if accept_lang.startswith('en') else 'ar'

        if lang not in ('ar', 'en'):
            lang = 'ar'

        request.LANGUAGE_CODE = lang
        request.DIR = 'rtl' if lang == 'ar' else 'ltr'
        translation.activate(lang)

    def process_response(self, request, response):
        lang = getattr(request, 'LANGUAGE_CODE', 'ar')
        response.set_cookie('nexmedia_lang', lang, max_age=60 * 60 * 24 * 365)
        return response
