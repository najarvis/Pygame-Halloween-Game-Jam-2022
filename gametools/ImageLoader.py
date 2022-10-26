import pygame

class ImageLoader:
    """Helper class to handle loading images from paths, ensuring we don't
    reload the same image multiple times (for performance reasons)"""

    # Class variable to store references to the loaded images for each unique path
    loaded_images_cache = {}

    @staticmethod
    def AddImageToAnimation(animation: list, path: str, override_size: tuple[int, int] = None) -> None:
        """Takes a string path to a file, retrieves the corresponding image,
        resizes if necessary, and adds it to the animation list."""

        image_to_add = ImageLoader.GetImage(path, override_size)
        animation.append(image_to_add)

    @staticmethod
    def GetImage(path: str, override_size: tuple[int, int] = None, alpha=False) -> pygame.Surface:
        """Given a path to an image, return the corresponding pygame.Surface

        If the image is already loaded, return the stored image in the dictionary, 
        otherwise load the corresponding image and update the internal dictonary.
        
        Will raise FileNotFoundError if file isn't found at given path
        Will raise AssertionError if the path is defined in the dictionary but there is no default size"""

        image_to_add = None
        image_sizes = ImageLoader.loaded_images_cache.get(path)
        if image_sizes is None:
            # We have not loaded this image before
            ImageLoader.loaded_images_cache[path] = {}
            image_to_add = pygame.image.load(path)
            if alpha:
                image_to_add = image_to_add.convert_alpha()
            else:
                image_to_add = image_to_add.convert()
            size = image_to_add.get_size()
            ImageLoader.loaded_images_cache[path][None] = image_to_add
            ImageLoader.loaded_images_cache[path][size] = image_to_add

            # If override_size was passed in before loading the default size we need
            # to resize and add that result.
            if override_size is not None and size != override_size:
                image_to_add = pygame.transform.scale(image_to_add, override_size)
                ImageLoader.loaded_images_cache[path][override_size] = image_to_add

        else:
            image_to_add = image_sizes.get(override_size)
            if image_to_add is None:
                # We have loaded the image, but not at this size
                image_to_resize = image_sizes[None]
                assert image_to_resize is not None

                image_to_add = pygame.transform.scale(image_to_resize, override_size)
                image_sizes[override_size] = image_to_add

        return image_to_add
