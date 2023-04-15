from django import template

register = template.Library()

@register.filter
def split_first(value, arg):
    return value.split(arg)[0]

@register.filter
def split_last(value, arg):
    return value.split(arg)[-1]