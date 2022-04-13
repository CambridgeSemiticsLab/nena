from dialects.models import DialectGroup

def subdomain_dialect_group_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        try:
            subdomain = request.META['HTTP_HOST'].split('.')[0]

            if request.GET.get('act_like_subdomain'):
                subdomain = request.GET.get('act_like_subdomain')

            staging_suffix = '-staging'
            if subdomain.endswith(staging_suffix):
                subdomain = subdomain[0:-1 * len(staging_suffix)]

            dialect_group = DialectGroup.objects.filter(subdomain=subdomain).first()

            if dialect_group or 'dialect_group_id' not in request.session:
                if not dialect_group:
                    dialect_group = DialectGroup.objects.first()

                request.session['dialect_group_id'] = dialect_group.id
                request.session['dialect_group_site_title'] = dialect_group.site_title

        except KeyError:
            pass

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware
