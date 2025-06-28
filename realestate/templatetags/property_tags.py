# property_tags.py
from django import template
from ..utils import generate_enquiry_description

register = template.Library()

@register.simple_tag(takes_context=True)
def enquiry_description(context, property=None):
    """
    Template tag to generate enquiry description text
    Usage: {% enquiry_description property %}
    """
    request = context['request']
    return generate_enquiry_description(request, property)