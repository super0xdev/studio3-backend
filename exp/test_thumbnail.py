from PIL import Image

imgPath = "/home/alphaprime8/PycharmProjects/DsAPI/tmp_download/89d222_1667111599828_ape1.png"
img = Image.open(imgPath)

width_height_ratio = img.size[0] / img.size[1]

height = 200
width = width_height_ratio * height

img.thumbnail((width, height))

img.save('./tmp_upload/image_thumbnail_1.png')


