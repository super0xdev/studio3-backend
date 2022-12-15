# importing the library
from PIL import Image


def add_watermark(asset_fpath):

    # TODO make dynamic

    watermark_fpath = "./image_utils/studio3_watermark.png"

    asset_image = Image.open(asset_fpath)

    asset_height = asset_image.height
    asset_width = asset_image.width
    print(f"got asset heigh widhthj: {asset_height}, {asset_width}")

    watermark_image = Image.open(watermark_fpath)

    mark_height = watermark_image.height
    mark_width = watermark_image.width
    print(f"mark height, width, {mark_height}, {mark_width}")

    mark_ar = mark_width / mark_width

    target_height = int(asset_height/4)
    target_width = int(target_height * mark_ar)

    # TOD rever height and width?
    watermark_image.thumbnail((target_width, target_height))

    copied_image = asset_image.copy()
    copied_image.paste(watermark_image, (50, 50))

    final_image = copied_image.convert('RGB')

    # TODO error occuring here
    final_image.save(asset_fpath)

