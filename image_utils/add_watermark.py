# importing the library
from PIL import Image


def add_watermark(asset_fpath):


    watermark_fpath = "./image_utils/s2_watermakrk_1.png"

    asset_image = Image.open(asset_fpath)

    asset_height = asset_image.height
    asset_width = asset_image.width
    print(f"got asset heigh widhthj: {asset_height}, {asset_width}")

    watermark_image = Image.open(watermark_fpath)

    mark_height = watermark_image.height
    mark_width = watermark_image.width
    print(f"mark height, width, {mark_height}, {mark_width}")

    mark_ar = mark_width / mark_width

    target_height = int(asset_height/3)
    target_width = int(target_height * mark_ar)

    # TOD rever height and width?
    watermark_image.thumbnail((target_width, target_height))
    result = watermark_image.putalpha(85)
    print(f"got result put alpha: {result}")

    copied_image = asset_image.copy()
    copied_image.paste(watermark_image, (asset_width-16-target_width, asset_height-16-target_height))

    final_image = copied_image.convert('RGB')

    final_image.save(asset_fpath)

