# importing the library
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

# load
asset_fpath = "./tmp_upload/droid_pfp.png"
watermark_fpath = "./tmp_upload/watermark.png"

asset_image = Image.open(asset_fpath)
watermark_image = Image.open(watermark_fpath)

# asset_image.show()
# plt.imshow(asset_image)

watermark_image.thumbnail((200, 200))
copied_image = asset_image.copy()
copied_image.paste(watermark_image, (50, 50))

plt.imshow(copied_image)
plt.show()
