from django import template
from cinema.models import *


register = template.Library()


@register.simple_tag
def call_method_get_tickets_count(obj, method_name, date_today):
    method = getattr(obj, method_name)
    return method(date_today)
