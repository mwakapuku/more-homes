from homes.models import FacilityProperty


def create_property_facilities(facilities, property_instance):
    """
     Create new property facilities.

     Args:
         property_instance: The Property instance whose images are being updated.
         facilities: A list of dictionaries containing 'filename' and Base64-encoded 'data'.
     """
    if facilities:
        for facility in facilities:
            FacilityProperty.objects.create(property=property_instance, **facility)


def update_property_facilities(facilities, property_instance):
    """
     Replace existing property facilities with a new list of facilities.

     Args:
         property_instance: The Property instance whose facility are being updated.
         facilities: A list of facility names.
     """
    if facilities:
        property_instance.facilities.all().delete()
        for facility in facilities:
            FacilityProperty.objects.create(property=property_instance, **facility)
