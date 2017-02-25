def trim(image_path):
    """
    Takes a full path to an existing image and autotrims it to the color of the pixel in the top left corner (0, 0)
    Overwrites the old image with the newly trimmed one
    :param image_path: str
    :return: str (same as input image_path)
    """
    from PIL import Image, ImageChops
    import os
    # Make sure we're operating on a path that actually exists
    if not os.path.exists(image_path):
            raise ValueError('Path % does not exist' % image_path)

    image = Image.open(image_path)  # Open the input image with PIL
    # Build a temp image filled with the color of the input's top left corner
    base_temp_image = Image.new(image.mode, image.size, image.getpixel((0, 0)))
    # Find the difference between the two (neat trick...)
    difference_image = ImageChops.difference(image, base_temp_image)
    difference_image = ImageChops.add(difference_image, difference_image, 2.0, -100)
    # Find the bounding box of the difference image
    bounding_box = difference_image.getbbox()
    # Use the new bounding box to crop the original image and save it
    if bounding_box:
        cropped_image = image.crop(bounding_box)
        cropped_image.save(image_path)
        return image_path
