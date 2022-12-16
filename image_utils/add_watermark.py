# importing the library
import random
import time
from PIL import Image
from cairosvg import svg2png
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM


def add_watermark(asset_fpath):

    asset_dots = asset_fpath.split(".")[-2]
    asset_name = asset_dots.split("/")[-1]
    print(f"got asset name : {asset_name}")

    asset_image = Image.open(asset_fpath)
    print(f"got asset image in svg: {asset_image.width}, {asset_image.height}")

    asset_height = asset_image.height
    asset_width = asset_image.width
    print(f"got asset heigh widhthj: {asset_height}, {asset_width}")

    print(f"opening svg")
    watermark_image = Image.open('./image_utils/s2_watermakrk_1.png')
    print(f"loading watermarke svg: {watermark_image.height}, {watermark_image.width}")
    mark_height = watermark_image.height
    mark_width = watermark_image.width
    print(f"mark height, width, {mark_height}, {mark_width}")

    mark_ar = mark_height / mark_width

    target_width = int(asset_width / 3)
    target_height = int(target_width * mark_ar)

    print(f"render watermakrk")

    # TOD rever height and width?
    print(f"watermarker {target_width}, {target_height}")
    watermark_image.thumbnail((target_width, target_height))

    print(f"got thumbnail: {watermark_image}")
    # watermark_image.putalpha(80)

    copied_image = asset_image.copy()
    # copied_image.paste(watermark_image, (16, 16))
    copied_image.paste(watermark_image, (asset_width - 15 - target_width, asset_height - target_height - 16), watermark_image)

    # TODO maybe save sa jepg for alpha...
    final_image = copied_image.convert('RGB')

    final_name = f'/tmp/final_{time.time()}_{random.random()}_{asset_name}.png'
    print(f"final_name: {final_name}")
    final_image.save(final_name)
    return final_name

