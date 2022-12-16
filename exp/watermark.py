# importing the library
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

# load
asset_fpath = "./tmp_upload/droid_alpha.png"
watermark_fpath = "./image_utils/s2_watermakrk_1.png"

asset_image = Image.open(asset_fpath)
watermark_image = Image.open(watermark_fpath)

mark_ar = watermark_image.height / watermark_image.width

target_width = int(asset_image.width / 3)
target_height = int(target_width * mark_ar)

print(f"render watermakrk")

# TOD rever height and width?
print(f"watermarker {target_width}, {target_height}")

watermark_image.thumbnail((target_width, target_height))

copied_image = asset_image.copy()
copied_image.paste(watermark_image, (50, 50), watermark_image)

plt.imshow(copied_image)
plt.show()
