from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def whatsapp_url(context, payment):
    """
    Template tag para generar la URL de WhatsApp para un pago.
    Uso: {% whatsapp_url payment %}
    """
    phone_number = settings.WHATSAPP_PHONE
    request = context.get('request')
    return payment.get_whatsapp_url(phone_number, request=request)
