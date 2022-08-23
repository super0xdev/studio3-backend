from PIL import Image

try:
    imgPath = './forest.jpg'
    img = Image.open(imgPath)
    print('The size of img is: ', img.size)
    print('After applying thumbnail() function')
    img.thumbnail((400, 400))
    img.save('image_thumbnail.jpg')
    print('The size of thumbnail image is: ', img.size)
except FileNotFoundError:
    print('Provided image path is not found')
