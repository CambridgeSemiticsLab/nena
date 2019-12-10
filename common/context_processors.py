from django.conf import settings

def last_updated_date(request):
    return {'LAST_UPDATED_DATE': settings.LAST_UPDATED_DATE}

def google_analytics_reference(request):
    return {'GOOGLE_ANALYTICS_REFERENCE': settings.GOOGLE_ANALYTICS_REFERENCE}
