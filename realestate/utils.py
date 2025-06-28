# utils.py
from urllib.parse import unquote


def generate_enquiry_description(request, property=None):
    """
    Generates a standardized enquiry description based on the property or request parameters
    """
    if property:
        # If we have the property object
        return f"I'm interested in {property.name} at {property.location}. {property.description[:100]}..."

    # Fallback to URL parameters if property object isn't available
    description = request.GET.get('description', '')
    if description:
        return unquote(description)

    return "I'm interested in learning more about your properties."