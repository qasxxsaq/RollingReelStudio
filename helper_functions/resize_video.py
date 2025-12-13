from PIL import Image
from moviepy.editor import VideoFileClip

# Resize the video to match the dimension of our input image.
image = Image.open("./intermediate_files/images/input.png")

img_width, img_height = image.size
print(f"Image size: {img_width}x{img_height}")

clip = VideoFileClip("input_video_for_resize.mp4")
resized_clip = clip.resize(newsize=(img_width, img_height))

resized_clip.write_videofile("resized_video.mp4")

