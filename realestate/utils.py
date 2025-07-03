from urllib.parse import unquote
from django.core.exceptions import ObjectDoesNotExist
from .models import (
    BuyDevelopment, CommercialBuy, BuyLand,
    ResidentialRent, CommercialRent, ResidentialBuy
)


def get_property_by_id(property_id, property_type=None):
    """
    Improved property lookup that maintains type integrity
    Args:
        property_id: ID of the property to lookup
        property_type: Optional type hint ('commercial', 'residential', 'land',
                     'rent_residential', 'rent_commercial', 'development')
    """
    if not property_id:
        return None

    # If property_type is specified, only check that specific model
    if property_type:
        model_map = {
            'commercial': CommercialBuy,
            'residential': ResidentialBuy,
            'land': BuyLand,
            'rent_residential': ResidentialRent,
            'rent_commercial': CommercialRent,
            'development': BuyDevelopment
        }
        models = [model_map.get(property_type)]
    else:
        # Fallback to checking all models if no type specified
        models = [
            ResidentialBuy, ResidentialRent,
            CommercialBuy, CommercialRent,
            BuyLand, BuyDevelopment
        ]

    for model in models:
        if model is None:  # Skip if property_type was invalid
            continue

        try:
            prop = model.objects.get(pk=property_id)
            # Verify concrete type matches exactly
            if prop.__class__.__name__ == model.__name__:
                return prop
        except (model.DoesNotExist, ValueError):
            continue

    return None


def generate_enquiry_description(request, property=None):
    """
    Generates enquiry description using only mandatory fields (name + location)
    """
    if property is None:
        property_id = request.GET.get('property_id')
        if property_id:
            property = get_property_by_id(property_id)

    if property:
        # Using only the mandatory fields that all properties have
        return f"I'm interested in the {property.name} at {property.location}"

    # Fallback for direct URL parameters
    if 'property' in request.GET and 'location' in request.GET:
        name = unquote(request.GET.get('property'))
        location = unquote(request.GET.get('location'))
        return f"I'm interested in the {name} at {location}"

    # Default message
    return "I'm interested in learning more about your properties."