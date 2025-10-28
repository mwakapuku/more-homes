import base64

from django.core.files.base import ContentFile

from homes.models import PropertyImage


def update_property_images(images_data, property_instance):
    """
     Replace existing property images with a new list of images.

     Args:
         property_instance: The Property instance whose images are being updated.
         images_data: A list of dictionaries containing 'filename' and Base64-encoded 'data'.
                      Example: [{"filename": "image1.jpg", "data": "...base64..."}]
     """
    if images_data:
        property_instance.images.all().delete()
        for img in images_data:
            filename = img.get("filename", "image.jpg")
            data = img.get("data")
            if data:
                image_file = ContentFile(base64.b64decode(data), name=filename)
                PropertyImage.objects.create(property=property_instance, image=image_file)


def create_property_images(property_instance, images_data):
    """
    Create PropertyImage objects for a given property from a list of Base64-encoded images.

    Args:
        property_instance: The Property instance to associate the images with.
        images_data: A list of dictionaries containing 'filename' and Base64-encoded 'data'.
                     Example: [{"filename": "image1.jpg", "data": "...base64..."}]

    Returns:
        None
    """
    for img in images_data:
        filename = img.get("filename", "image.jpg")
        data = img.get("data")
        if data:
            try:
                image_file = ContentFile(base64.b64decode(data), name=filename)
                PropertyImage.objects.create(property=property_instance, image=image_file)
            except Exception as e:
                # Optionally log the error instead of failing completely
                print(f"Failed to create image {filename}: {e}")
