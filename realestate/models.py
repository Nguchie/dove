from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

# ----------------------
# Abstract Base Property
# ----------------------
class PropertyBase(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_on_application = models.BooleanField(default=False)

    images = GenericRelation('PropertyImage')   # Allow reverse access to images
    amenities = GenericRelation('Amenity')      # Allow reverse access to amenities
    description = models.TextField(blank=True)  # Now on all property types

    class Meta:
        abstract = True

    def display_price(self):
        return "On Application" if self.price_on_application else f"Ksh {self.price:,.2f}"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Default URL that child classes can override"""
        return "#"  # Fallback URL
# -------------------
# BUY CATEGORY
# -------------------

class BuyDevelopment(PropertyBase):
    STATUS_CHOICES = [
        ('under_construction', 'Under Construction'),
        ('ready_to_move', 'Ready to Move In'),
        ('sold_out', 'Sold Out'),
        ('pre_launch', 'Pre-Launch'),
    ]

    beds = models.IntegerField()
    floorplans = models.FileField(upload_to='floorplans/', null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='under_construction')

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('buy_development_detail', args=[str(self.id)])

class CommercialBuy(PropertyBase):
    size = models.CharField(max_length=100)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('commercial_buy_detail', args=[str(self.id)])

class ResidentialBuy(PropertyBase):
    PROPERTY_TYPES = [
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('duplex', 'Duplex'),
        ('townhouse', 'Townhouse'),
    ]

    FURNISHING_CHOICES = [
        ('unfurnished', 'Unfurnished'),
        ('semi-furnished', 'Semi-Furnished'),
        ('furnished', 'Furnished'),
    ]

    type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    furnishing = models.CharField(max_length=50, choices=FURNISHING_CHOICES)
    beds = models.IntegerField()
    baths = models.IntegerField()
    size = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.get_type_display()}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('residential_buy_detail', args=[str(self.id)])


class BuyLand(PropertyBase):
    size = models.CharField(max_length=100)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('buy_land_detail', args=[str(self.id)])

# -------------------
# RENT CATEGORY
# -------------------

class ResidentialRent(PropertyBase):
    PROPERTY_TYPES = [
        ('unfurnished', 'Unfurnished'),
        ('furnished', 'Furnished'),
    ]
    type = models.CharField(max_length=50, choices=PROPERTY_TYPES)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('residential_rent_detail', args=[str(self.id)])


class CommercialRent(PropertyBase):
    size = models.CharField(max_length=100)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('commercial_rent_detail', args=[str(self.id)])
# -------------------
# IMAGES FOR LISTINGS
# -------------------

class PropertyImage(models.Model):
    image = models.ImageField(upload_to='property_images/')
    caption = models.CharField(max_length=255, blank=True)

    # Generic relation fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.caption or f"Image {self.id}"


# -------------------
# AMENITIES (Generic for all Property Models)
# -------------------

class Amenity(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='amenities/')

    # Generic relation fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.name
