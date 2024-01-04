from django import template

register = template.Library()

CURRENCIES_SYMBOLS = {
    'rub': '₽',
    'usd': '$',
}


@register.filter()
def currency(value, code='rub'):
    """
    value: значение, к которому нужно применить фильтр
    """
    postfix = CURRENCIES_SYMBOLS[code]

    return f'{value} {postfix}'
