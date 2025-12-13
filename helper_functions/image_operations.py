from PIL import Image
from datetime import datetime

def shape(image_path):
    img = Image.open(image_path)
    width, height = img.size
    print(f"Width: {width}, Height: {height}")
    return img.size

def resize_image(image_path, width=1280, height=720):

    img = Image.open(image_path)
    size = (width, height)
    img = img.resize(size)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # print(timestamp)
    save_path = f"img_{width}_{height}_{timestamp}.png"
    img.save(save_path)

    return save_path


# Run this file for an example.
if __name__ == "__main__":
    image_path = "aaaaa.png"
    shape(image_path)
    # resize_image(image_path)

