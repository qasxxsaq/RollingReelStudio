import cv2
from PIL import Image
from moviepy.editor import VideoFileClip

def shape(video_path):
    """
    return width, height, fps, frame_count
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error opening video file")
    else:
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"Width: {width}, Height: {height}")
        print(f"FPS: {fps}, Total frames: {frame_count}")

    cap.release()
    return width, height, fps, frame_count

def resize_video(video_path, width=1280, height=720, reference_image_path=None):
    """
    Note: this function re-writes previous outputs.
    """
    if reference_image_path is not None: # Resize the video based on a reference image.
        image = Image.open(reference_image_path)
        target_width, target_height = image.size
    else:
        target_width, target_height = width, height

    print(f"Targer size: {target_width}x{target_height}")

    clip = VideoFileClip(video_path)
    resized_clip = clip.resize(newsize=(target_width, target_height))
    resized_clip.write_videofile("resized_video.mp4")


# This file can be run individually for one-time operations.
if __name__ == "__main__":
    video_path="video_20251130_062300_Scene_13_edited.mp4"
    resize_video(video_path)

