from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)
@register.filter(name='index')
def index(lista, i):
    try:
        return lista[i]
    except:
        return 'hsl(0, 0%, 50%)'
