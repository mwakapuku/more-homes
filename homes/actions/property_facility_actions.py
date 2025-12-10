from homes.models import FacilityProperty, PropertyCost


def create_project_cost(project_costs, property_instance):
    if project_costs:
        for project_cost in project_costs:
            name = project_cost.get("name")
            amount = project_cost.get("amount")
            PropertyCost.objects.create(
                property=property_instance,
                name=name,
                amount=amount,
                created_by=property_instance.created_by,
                updated_by=property_instance.created_by,
            )


def create_property_facilities(facilities, property_instance):
    """
     Create new property facilities.

     Args:
         property_instance: The Property instance whose images are being updated.
         facilities: A list of dictionaries containing 'filename'.
     """
    if facilities:
        print("Facilities on saving")
        print(facilities)
        for facility in facilities:
            name = facility.get("name")
            FacilityProperty.objects.create(
                property=property_instance,
                name=name,
                created_by=property_instance.created_by,
                updated_by=property_instance.created_by,
            )
    else:
        print("No facilities on try")


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
            name = facility.get("name")
            FacilityProperty.objects.create(
                property=property_instance,
                name=name,
                created_by=property_instance.created_by,
                updated_by=property_instance.created_by,
            )
