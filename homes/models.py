from django.db import models

from payment.models import AuditModel


class Facility(AuditModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'facility'
        verbose_name_plural = 'Facilities'
        verbose_name = 'Facility'
        ordering = ['name']


# Create your models here.
class Property(AuditModel):
    CATEGORY_CHOICES = (
        ("Rent", "Rent"),
        ("Sale", "Sale"),
        ("Short Stay", "Short Stay"),
    )
    TYPE_CHOICES = (
        ("House", "House"),
        ("Apartment", "Apartment"),
        ("Room", "Room"),
        ("Land", "Land"),
        ("Office", "Office"),
        ("Construction", "Construction"),
    )
    uploader = models.ForeignKey('users.User', on_delete=models.CASCADE)
    name = models.CharField('Propert Name', max_length=255)
    type = models.CharField('Property Type', max_length=100, choices=TYPE_CHOICES)
    address = models.TextField('Property Address')
    price = models.DecimalField('Property Price', max_digits=10, decimal_places=2)
    category = models.CharField('Property Category', max_length=255, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    maintenance = models.DecimalField(max_digits=10, decimal_places=2)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'property'
        ordering = ['-created_at']
        verbose_name_plural = "Properties"
        verbose_name = "Property"
        unique_together = ('name', 'type', 'uploader')


class PropertyImage(AuditModel):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='property_images')
    image = models.ImageField('Property Image', upload_to='property/images/')

    def __str__(self):
        return self.property.name

    class Meta:
        db_table = 'property_image'
        verbose_name_plural = "Property Images"
        verbose_name = "Property Images"
        ordering = ['-created_at']


class FacilityProperty(AuditModel):
    name = models.CharField('Facility Name', max_length=100)
    property = models.ForeignKey(Property, related_name='facilities', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.property.name})"

    class Meta:
        db_table = 'property_facility'
        verbose_name_plural = "Property Facilities"
        verbose_name = "Property Facilities"
        ordering = ['-created_at']


class PropertyFeedBack(AuditModel):
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name="property_feedback")
    message = models.TextField()

    def __str__(self):
        return f"{self.property.name}"
