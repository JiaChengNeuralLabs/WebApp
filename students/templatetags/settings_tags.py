from django import template
from django.conf import settings

register = template.Library()


@register.filter
def whatsapp_url(payment):
    """
    Template filter para generar la URL de WhatsApp para un pago.
    Uso: {{ payment|whatsapp_url }}
    """
    phone_number = settings.WHATSAPP_PHONE
    return payment.get_whatsapp_url(phone_number)
