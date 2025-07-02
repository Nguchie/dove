from urllib.parse import unquote
from django.core.exceptions import ObjectDoesNotExist
from .models import (
    BuyDevelopment, CommercialBuy, BuyLand,
    ResidentialRent, CommercialRent, ResidentialBuy
)


def get_property_by_id(property_id):
    """Helper function to get a property by ID from any model"""
    models = [BuyDevelopment, CommercialBuy, BuyLand,
              ResidentialRent, CommercialRent, ResidentialBuy]

    for model in models:
        try:
            return model.objects.get(pk=property_id)
        except (model.DoesNotExist, ValueError):
            continue
    return None


def generate_enquiry_description(request, property=None):
    """
    Generates a standardized enquiry description
    """
    if property is None:
        property_id = request.GET.get('property_id')
        if property_id:
            property = get_property_by_id(property_id)

    if property:
        description = f"I'm interested in {property.name} at {property.location}."
        if property.description:
            description += f" {property.description[:100]}..."
        return description

    # Fallback to URL parameter if provided
    description = request.GET.get('description', '')
    if description:
        return unquote(description)

    return "I'm interested in learning more about your properties."