from homes.models import Property


def get_property_to_display(uploader):
    return (
        Property.objects.all().
        filter(is_booked=False).
        exclude(uploader=uploader).
        prefetch_related('uploader', 'property_images', 'facilities')
    )


def get_property_detail(property_uuid) -> Property:
    return Property.objects.get(uuid=property_uuid)


def get_property_by_uploader(uploader):
    return Property.objects.filter(uploader=uploader)
