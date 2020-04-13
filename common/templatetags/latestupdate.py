from django import template

register = template.Library()


@register.simple_tag
def date_updated():
    ''' return the date this container image was built, written into file by Dockerfile '''
    try:
        with open('/usr/src/build-date.txt', 'r') as f:
            return f.read()
    except Exception:
        pass
    return ''
