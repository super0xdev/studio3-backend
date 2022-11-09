# importing the library
from PIL import Image


def generate_thumbnail(asset_fpath, thumbnail_fpath):
    asset_image = Image.open(asset_fpath)
    height = 200
    width_height_ratio = asset_image.size[0] / asset_image.size[1]
    width = width_height_ratio * height
    asset_image.thumbnail((width, height))
    asset_image.save(thumbnail_fpath)


