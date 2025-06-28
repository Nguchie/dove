from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import (
    BuyDevelopment, CommercialBuy, BuyLand,
    ResidentialRent, CommercialRent, ResidentialBuy
)
from django.views.generic.detail import DetailView
from .forms import ContactForm
from django.shortcuts import render, redirect
from django.contrib import messages

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
import json
from .utils import generate_enquiry_description
from django.core.mail import EmailMessage


@csrf_exempt
def contact_form_submit(request):
    if request.method == "POST":
        try:
            # Get data from both JSON and form submissions
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            phone = data.get('phone', '').strip()
            inquiry_type = data.get('inquiryType', '').strip()
            description = data.get('description', '').strip()

            if not all([name, email, description]):
                raise ValueError("Missing required fields")

            subject = f"New Inquiry from {name} - {inquiry_type or 'General'}"
            message = f"""
Name: {name}
Email: {email}
Phone: {phone or 'Not provided'}
Inquiry Type: {inquiry_type or 'Not specified'}

Message:
{description}
            """

            recipient_list = ['info@doverealestateltd.com']  # Ensure this is correct
            from_email = settings.DEFAULT_FROM_EMAIL  # Use your configured email

            # Simple send_mail version first for testing
            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=False,
            )

            # Log successful sending
            print(f"Email sent to {recipient_list}")

            return JsonResponse({
                'status': 'success',
                'message': 'Your inquiry has been sent successfully'
            })

        except Exception as e:
            # Detailed error logging
            import traceback
            error_msg = f"Error sending email: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)

            return JsonResponse({
                'status': 'error',
                'message': 'Failed to send your inquiry. Please try again later.'
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)

def get_unique_values(field):
    models = [BuyDevelopment, CommercialBuy, BuyLand, ResidentialRent, CommercialRent]
    values = set()
    for model in models:
        if field in [f.name for f in model._meta.get_fields()]:
            values.update(model.objects.values_list(field, flat=True))
    return sorted(filter(None, values))


def homepage(request):
    properties = []
    search_performed = False

    # Dynamic filter values
    dynamic_locations = get_unique_values('location')
    dynamic_beds = sorted(set(get_unique_values('beds')))
    dynamic_sizes = sorted(set(get_unique_values('property_size')))

    if request.method == 'GET' and 'search' in request.GET:
        search_performed = True
        status = request.GET.get('status', '')
        property_type = request.GET.get('type', '')
        state = request.GET.get('state', '')
        min_price = request.GET.get('min_price', '')
        max_price = request.GET.get('max_price', '')
        bedrooms = request.GET.get('bedrooms', '')
        property_size = request.GET.get('property_size', '')

        query = Q()
        query &= Q(price_on_application=False) | Q(price__isnull=False)

        if status == 'buy':
            buy_models = [BuyDevelopment, CommercialBuy, BuyLand]
            properties = []
            for model in buy_models:
                properties.extend(model.objects.filter(query).prefetch_related('images'))
        elif status == 'rent':
            rent_models = [ResidentialRent, CommercialRent]
            properties = []
            for model in rent_models:
                properties.extend(model.objects.filter(query).prefetch_related('images'))

        if property_type:
            def match_type(p):
                return (
                    (property_type == 'development' and isinstance(p, BuyDevelopment)) or
                    (property_type == 'commercial' and isinstance(p, (CommercialBuy, CommercialRent))) or
                    (property_type == 'land' and isinstance(p, BuyLand)) or
                    (property_type == 'residential' and isinstance(p, ResidentialRent))
                )
            properties = [p for p in properties if match_type(p)]

        if state:
            properties = [p for p in properties if state.lower() in (p.location or '').lower()]

        try:
            if min_price:
                properties = [p for p in properties if p.price and p.price >= float(min_price)]
            if max_price:
                properties = [p for p in properties if p.price and p.price <= float(max_price)]
        except ValueError:
            pass

        if bedrooms and bedrooms.isdigit():
            bedrooms = int(bedrooms)
            properties = [p for p in properties if getattr(p, 'beds', 0) >= bedrooms]

        if property_size and property_size.isdigit():
            size = int(property_size)
            properties = [p for p in properties if getattr(p, 'property_size', 0) >= size]

    context = {
        'properties': properties,
        'search_performed': search_performed,
        'dynamic_locations': dynamic_locations,
        'dynamic_beds': dynamic_beds,
        'dynamic_sizes': dynamic_sizes
    }
    return render(request, 'index.html', context)


def buy_developments_view(request):
    developments = BuyDevelopment.objects.all().prefetch_related('images')
    return render(request, 'buy_developments.html', {'developments': developments})


def commercial_buy_view(request):
    commercial = CommercialBuy.objects.all().prefetch_related('images')
    return render(request, 'commercial_buy.html', {'commercial': commercial})


def buy_land_view(request):
    lands = BuyLand.objects.all().prefetch_related('images')
    return render(request, 'buy_land.html', {'lands': lands})


def buy_portfolio_view(request):
    developments = BuyDevelopment.objects.all().prefetch_related('images')[:3]
    commercial = CommercialBuy.objects.all().prefetch_related('images')[:3]
    lands = BuyLand.objects.all().prefetch_related('images')[:3]

    context = {
        'developments': developments,
        'commercial': commercial,
        'lands': lands,
    }
    return render(request, 'buy_portfolio.html', context)

def residential_buy_list(request):
    properties = ResidentialBuy.objects.all()
    return render(request, 'residential_buy_list.html', {
        'properties': properties
    })


class ResidentialBuyDetailView(DetailView):
    model = ResidentialBuy
    template_name = 'residential_buy_detail.html'
    context_object_name = 'property'

    def get_queryset(self):
        """Optimized query to fetch property with all related data"""
        return super().get_queryset().prefetch_related('images', 'amenities')

def rent_commercial_list(request):
    properties = CommercialRent.objects.all()
    return render(request, 'rent_commercial_list.html', {'properties': properties})


def rent_residential_list(request):
    properties = ResidentialRent.objects.all().prefetch_related('images', 'amenities')

    context = {
        'properties': properties,
    }
    return render(request, 'rent_residential_list.html', context)


def residential_rent_detail(request, pk):
    """
    Function-based view for displaying residential rent property details
    """
    # Get the property with prefetched images and amenities
    property = get_object_or_404(
        ResidentialRent.objects.prefetch_related('images', 'amenities'),
        pk=pk
    )

    context = {
        'property': property,
    }

    return render(request, 'residential_rent_detail.html', context)

def about_view(request):
    return render(request, 'about.html')


def sell_view(request):
    return render(request, 'sell.html')

def terian_view(request):
    return render(request, 'terian.html')


def contact_view(request):
    initial_data = {}
    property_id = request.GET.get('property_id')

    if property_id:
        # Try to get the property from any of our models
        from .models import (
            BuyDevelopment, CommercialBuy, BuyLand,
            ResidentialRent, CommercialRent, ResidentialBuy
        )

        models = [BuyDevelopment, CommercialBuy, BuyLand, ResidentialRent, CommercialRent, ResidentialBuy]
        property_obj = None

        for model in models:
            try:
                property_obj = model.objects.get(pk=property_id)
                break
            except model.DoesNotExist:
                continue

    description = generate_enquiry_description(request, property_obj)
    if description:
        initial_data['description'] = description

    form = ContactForm(initial=initial_data)

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Compose email content
            subject = 'New Property Enquiry'
            message = (
                f"Name: {form.cleaned_data['name']}\n"
                f"Email: {form.cleaned_data['email']}\n"
                f"Phone: {form.cleaned_data.get('phone')}\n\n"
                f"Message:\n{form.cleaned_data['description']}"
            )
            from_email = form.cleaned_data['email']
            recipient_list = ['yourcompany@example.com']  # 👈 Replace with your address

            # Send the email
            send_mail(subject, message, from_email, recipient_list)

            messages.success(request, "Thank you! Your enquiry has been sent.")
            return redirect('contact')

    return render(request, 'contact.html', {'form': form})




# views.py

def search_view(request):
    properties = []
    search_performed = False

    # Dynamic filter values
    dynamic_locations = get_unique_values('location')
    dynamic_beds = sorted(set(get_unique_values('beds')))
    dynamic_sizes = sorted(set(get_unique_values('property_size')))

    if request.method == 'GET' and 'search' in request.GET:
        search_performed = True
        status = request.GET.get('status', '')
        property_type = request.GET.get('type', '')
        state = request.GET.get('state', '')
        min_price = request.GET.get('min_price', '')
        max_price = request.GET.get('max_price', '')
        bedrooms = request.GET.get('bedrooms', '')
        property_size = request.GET.get('property_size', '')

        query = Q()
        query &= Q(price_on_application=False) | Q(price__isnull=False)

        if status == 'buy':
            buy_models = [BuyDevelopment, CommercialBuy, BuyLand, ResidentialBuy]
            properties = []
            for model in buy_models:
                properties.extend(model.objects.filter(query).prefetch_related('images'))
        elif status == 'rent':
            rent_models = [ResidentialRent, CommercialRent]
            properties = []
            for model in rent_models:
                properties.extend(model.objects.filter(query).prefetch_related('images'))

        if property_type:
            def match_type(p):
                return (
                    (property_type == 'development' and isinstance(p, BuyDevelopment)) or
                    (property_type == 'commercial' and isinstance(p, (CommercialBuy, CommercialRent))) or
                    (property_type == 'land' and isinstance(p, BuyLand)) or
                    (property_type == 'residential' and isinstance(p, (ResidentialRent, ResidentialBuy)))
                )
            properties = [p for p in properties if match_type(p)]

        if state:
            properties = [p for p in properties if state.lower() in (p.location or '').lower()]

        try:
            if min_price:
                properties = [p for p in properties if p.price and p.price >= float(min_price)]
            if max_price:
                properties = [p for p in properties if p.price and p.price <= float(max_price)]
        except ValueError:
            pass

        if bedrooms and bedrooms.isdigit():
            bedrooms = int(bedrooms)
            properties = [p for p in properties if getattr(p, 'beds', 0) >= bedrooms]

        if property_size and property_size.isdigit():
            size = int(property_size)
            properties = [p for p in properties if getattr(p, 'property_size', 0) >= size]

    context = {
        'properties': properties,
        'search_performed': search_performed,
        'dynamic_locations': dynamic_locations,
        'dynamic_beds': dynamic_beds,
        'dynamic_sizes': dynamic_sizes
    }
    return render(request, 'search.html', context)


# For BuyDevelopment
class BuyDevelopmentDetailView(DetailView):
    model = BuyDevelopment
    template_name = 'buy_development_detail.html'
    context_object_name = 'property'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('images', 'amenities')

# For CommercialBuy
class CommercialBuyDetailView(DetailView):
    model = CommercialBuy
    template_name = 'commercial_buy_detail.html'
    context_object_name = 'property'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('images', 'amenities')

# For BuyLand
class BuyLandDetailView(DetailView):
    model = BuyLand
    template_name = 'buy_land_detail.html'
    context_object_name = 'property'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('images', 'amenities')

# For CommercialRent
class CommercialRentDetailView(DetailView):
    model = CommercialRent
    template_name = 'commercial_rent_detail.html'
    context_object_name = 'property'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('images', 'amenities')