from django import template

register = template.Library()

@register.filter
def tem_pdf(url):
    if not url:
        return False
    return url.lower().endswith('.pdf')

@register.filter
def get_item(dictionary, key):
    if not dictionary:
        return None
    return dictionary.get(key)
