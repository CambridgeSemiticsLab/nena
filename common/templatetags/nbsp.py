# copied from https://djangosnippets.org/snippets/2842/

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter()
def nbsp(value):
    return mark_safe("&nbsp;".join(value.split(' ')))
