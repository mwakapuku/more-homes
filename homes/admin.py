from django.contrib import admin

from homes.models import Property, PropertyImage, FacilityProperty, Facility, PropertyFeedBack, PropertyCost

admin.site.site_header = "More Homes"
admin.site.site_title = "More Homes"
admin.site.index_title = "More Homes"

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = [
        'uploader', 'name', 'type', 'address', 'price', 'category', 'is_booked', 'region', 'district', 'longitude',
        'latitude', 'created_at'
    ]
    list_filter = ['is_booked', 'category', 'created_at', 'updated_at']
    list_max_show_all = True
    search_fields = ['name']
    list_per_page = 30


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ['property', 'image', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    list_per_page = 30


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    list_per_page = 30


@admin.register(PropertyFeedBack)
class PropertyFeedBackAdmin(admin.ModelAdmin):
    list_display = ['property', 'message', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    list_per_page = 30


@admin.register(FacilityProperty)
class FacilityPropertyAdmin(admin.ModelAdmin):
    list_display = ['property', 'name', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    list_per_page = 30

@admin.register(PropertyCost)
class FacilityPropertyAdmin(admin.ModelAdmin):
    list_display = ['property', 'name', 'amount', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    list_per_page = 30
