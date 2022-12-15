# importing the library
from PIL import Image


def add_watermark(asset_fpath):
    watermark_fpath = "./image_utils/studio3_watermark.png"

    asset_image = Image.open(asset_fpath)
    watermark_image = Image.open(watermark_fpath)

    watermark_image.thumbnail((200, 200))
    copied_image = asset_image.copy()
    copied_image.paste(watermark_image, (50, 50))

    copied_image.save(asset_fpath)

