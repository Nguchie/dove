from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.contenttypes.models import ContentType
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import (
    BuyDevelopment, CommercialBuy, ResidentialBuy, BuyLand,
    ResidentialRent, CommercialRent,
    PropertyImage, Amenity
)
from .forms import BulkImageUploadForm


# -------------------
# Inlines for Images and Amenities
# -------------------

class PropertyImageInline(GenericTabularInline):
    model = PropertyImage
    extra = 1


class AmenityInline(GenericTabularInline):
    model = Amenity
    extra = 1


# -------------------
# Bulk Upload Mixin
# -------------------

class BulkImageUploadAdminMixin:
    change_form_template = "admin/property_with_upload.html"

    def get_urls(self):
        urls = super().get_urls()
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        custom_urls = [
            path(
                '<int:property_id>/upload-images/',
                self.admin_site.admin_view(self.upload_images),
                name=f'{app_label}_{model_name}_upload_images',
            ),
        ]
        return custom_urls + urls

    def upload_images(self, request, property_id):
        property_instance = self.get_object(request, property_id)

        if request.method == 'POST':
            form = BulkImageUploadForm(request.POST, request.FILES)
            if form.is_valid():
                for img in form.cleaned_data['images']:
                    PropertyImage.objects.create(
                        image=img,
                        content_object=property_instance
                    )
                messages.success(request, f"Successfully uploaded {len(form.cleaned_data['images'])} images.")
                return redirect(f'../../{property_id}/change/')
        else:
            form = BulkImageUploadForm()

        return render(request, 'admin/bulk_upload.html', {
            'form': form,
            'property': property_instance,
            'opts': self.model._meta,
        })
# -------------------
# Base Admin for Properties
# -------------------


class PropertyBaseAdmin(BulkImageUploadAdminMixin, admin.ModelAdmin):
    inlines = [PropertyImageInline, AmenityInline]
    list_display = ['name', 'location', 'display_price']
    search_fields = ['name', 'location']
    list_filter = ['price_on_application']
    readonly_fields = ['display_price']
    fieldsets = (
        (None, {
            'fields': ('name', 'location', 'price', 'price_on_application')
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )

@admin.register(BuyDevelopment)
class BuyDevelopmentAdmin(PropertyBaseAdmin):
    list_display = ['name', 'location', 'display_price', 'status', 'beds']
    list_filter = ['status']
    fieldsets = PropertyBaseAdmin.fieldsets + (
        ('Development Details', {
            'fields': ('status', 'beds', 'floorplans')
        }),
    )

@admin.register(CommercialBuy)
class CommercialBuyAdmin(PropertyBaseAdmin):
    fieldsets = PropertyBaseAdmin.fieldsets + (
        ('Commercial Info', {
            'fields': ('size',)  # Removed duplicate 'description'
        }),
    )

@admin.register(ResidentialBuy)
class ResidentialBuyAdmin(PropertyBaseAdmin):
    list_filter = ['type', 'furnishing']
    fieldsets = PropertyBaseAdmin.fieldsets + (
        ('Residential Info', {
            'fields': ('type', 'furnishing', 'beds', 'baths', 'size')
        }),
    )

@admin.register(BuyLand)
class BuyLandAdmin(PropertyBaseAdmin):
    fieldsets = PropertyBaseAdmin.fieldsets + (
        ('Land Info', {
            'fields': ('size',)  # Removed duplicate 'description'
        }),
    )

@admin.register(ResidentialRent)
class ResidentialRentAdmin(PropertyBaseAdmin):
    list_display = PropertyBaseAdmin.list_display + ['type', 'beds']  # Use list instead of tuple
    list_filter = ['type', 'beds']
    fieldsets = PropertyBaseAdmin.fieldsets + (
        ('Rent Info', {
            'fields': ('type', 'beds')
        }),
    )

@admin.register(CommercialRent)
class CommercialRentAdmin(PropertyBaseAdmin):
    fieldsets = PropertyBaseAdmin.fieldsets + (
        ('Commercial Info', {
            'fields': ('size',)  # Removed duplicate 'description'
        }),
    )

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'caption', 'content_type', 'object_id']
    search_fields = ['caption']


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'content_type', 'object_id']
    search_fields = ['name']
